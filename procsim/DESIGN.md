# procsim 설계 — 시뮬 프로세스 분리: 전송 경로와 프레임 포맷

목표: **GIL 비용을 없애기 위해 시뮬은 별도 프로세스로 돌리고, 뷰(렌더) 쪽은
"렌더에 필요한 최신 상태"만 받는다.** 전체 스냅샷이 아니라 드로우에 필요한
배열(pos/quat/mat4)만, JSON이 아니라 고정 바이트 헤더 + numpy 원시 바이트로.

이 문서는 그 결정의 근거(측정치 포함)와 포맷 스펙이다. 코드는 이 디렉토리:

| 파일 | 역할 |
|---|---|
| `frame.py` | 바이너리 프레임 코덱 (32B 헤더 + 섹션들) |
| `shmlink.py` | SharedMemory 3-슬롯 latest-wins 채널 (로컬 기본 경로) |
| `socklink.py` | 같은 프레임을 TCP로 (원격 / 멀티뷰어 / 웹 브릿지) |
| `simproc.py` | 프로세스 호스트: shm=상태, Pipe=입력/제어 |
| `udplink.py` | UDP 전송: 청크·재조립·latest-wins (원격 네이티브 뷰어) |
| `netlab.py` | 유저스페이스 링크 에뮬레이터 (지연/지터/대역/freeze/손실) |
| `demo_local.py` | 스레드 vs 프로세스 GIL 비교 데모 |
| `bench_format.py` / `bench_transport.py` / `bench_net.py` | 아래 수치들의 출처 |

---

## 1. 왜 스레드로는 안 되나 (측정)

`_test_threadqueue.py` 시절의 의심이 맞았다. 시뮬 틱이 파이썬 루프를 도는 동안
GIL을 잡고 있으면(기본 switch interval 5ms), 렌더 스레드는 vsync 타이밍에
깨어나도 GIL을 기다린다. `python -m procsim.demo_local` (N=1000 유닛,
시뮬 ~2ms py/틱, 렌더 ~2ms py/프레임, 이 컨테이너 기준):

| | THREAD (GIL 공유) | PROCESS (shm 채널) |
|---|---|---|
| 시뮬 틱 레이트 | 473/s | **542/s** |
| 렌더 루프 fps (목표 60) | 49.7 | **59.7** |
| 최악 프레임 간격 | 44.8 ms | **17.0 ms** |
| 읽은 상태의 나이 | 4.02 ms | **0.99 ms** |

스레드 모드는 렌더가 스터터링하고(44ms 스톨) 시뮬도 같이 느려진다.
프로세스 모드는 양쪽 다 제 속도. 전송비용은 아래에서 보듯 사실상 공짜라서,
분리의 순이익이 그대로 남는다.

## 2. 전송 경로 후보 비교

프레임 = N=1000 유닛 × (pos f32×3 + quat f32×4) = 28KB 기준,
생산자는 전력 질주, 소비자는 0.5ms 간격 폴링 (`bench_transport.py`):

| 경로 | pub/s (생산측) | 나이(지연) | 특성 |
|---|---|---|---|
| **SharedMemory 3-슬롯** | 99,974/s | **0.063 ms** | 시스콜 없음, 복사 1회, 백로그 원천 불가 |
| mp.Pipe (`send_bytes`) | 10,440/s | 0.477 ms | 간단하지만 큐가 차면 시뮬이 **블록** |
| TCP localhost | 18,724/s | 0.457 ms | 원격/멀티뷰어/타언어 가능, 프레이밍 필요 |

셋 다 60~240Hz에는 차고 넘친다. 결정 기준은 속도가 아니라 **의미론**:

- **Pipe/Queue**: FIFO다. 렌더가 밀리면 오래된 프레임이 쌓이고(=지연 누적),
  가득 차면 시뮬 쪽 `send`가 블록된다. "최신만 받기"와 정반대 성질.
  드레인해서 마지막 것만 쓰면 되긴 하지만, 그럼 중간 프레임 직렬화가 전부 낭비.
- **TCP**: `20_socket_world`에서 겪은 그대로 — 연결/재접속/프레이밍 관리가 붙고,
  커널 버퍼가 곧 큐라서 느린 뷰어에게 지연이 쌓인다(→ 송신측 mailbox로 해결).
  대신 **다른 기계/브라우저/타언어 뷰어**가 되는 유일한 경로.
- **shm**: 큐라는 개념 자체가 없다. 슬롯을 돌려쓰고 읽는 쪽은 항상 최신 완성본을
  집는다. 렌더가 느려도 시뮬은 절대 안 막히고, 시뮬이 빨라도 지연이 안 쌓인다.
  단점: 로컬 전용, 용량 고정, 동기화를 직접 설계해야 함(→ §5).

### 결론 구조

```
 [sim process]                              [view/render process]
   world.update(dt)                            매 프레임:
   ctx.publish(t, sections) ──▶ shm 3-slot ──▶ read_new() → VBO 업로드
        ▲                                            │
        └──────────── mp.Pipe ◀──────────────────────┘
                      (키입력/제어/스키마 — 콜드패스, pickle 허용)

 원격·멀티뷰어(옵션): 같은 프레임 바이트를 FrameCaster ──TCP──▶ FrameViewer
```

- **로컬 기본 경로 = shm** (`SimProcess`가 전부 배선해 줌)
- **원격/웹 = TCP**, 포맷은 동일 바이트라 시뮬 코드는 `publish` 한 줄 그대로
- **입력·제어 = Pipe**. 초당 몇 건짜리 콜드패스라 pickle/JSON 아무거나 써도 됨.
  "핫패스만 바이너리, 콜드패스는 편한 걸로"가 원칙.

## 3. 프레임 포맷 (바이트 헤더)

JSON 대비 (`bench_format.py`):

| N | 크기 (binary / json) | pack (binary / json) | unpack (binary / json) |
|---|---|---|---|
| 100 | 2.9KB / 14.6KB (×5.1) | 0.005 / 0.32 ms | 0.002 / 0.18 ms |
| 1000 | 28KB / 146KB (×5.2) | 0.007 / 3.3 ms (×466) | 0.003 / 1.9 ms (×729) |
| 10000 | 280KB / 1.46MB (×5.2) | 0.027 / 37.8 ms | 0.003 / 19.6 ms |

N=1000이면 JSON은 인코딩+디코딩만으로 프레임당 5ms — 60fps 예산의 1/3을
직렬화에 태운다. 바이너리는 10µs. 논쟁 끝.

리틀엔디언 고정, 오프셋 고정 (`struct` 모듈):

```
FrameHeader 32B
  0  magic       4s   'MVS1'
  4  version     u8
  5  msg_type    u8   1=STATE  2=SCHEMA  3=EVENT
  6  section_n   u16
  8  frame_id    u32  단조증가 (렌더가 스킵/중복/역행 감지)
  12 payload_len u32  ← 소켓에서 "정확히 이만큼 recv"의 근거
  16 sim_time    f64  생산 시각 (perf_counter) → 지연 측정·보간에 사용
  24 (예약)      8B

STATE payload = section_n × 섹션:
  SectionHeader 16B
    0  kind      u32  드로우 배치 식별자 (meshid '00010001' → 0x00010001)
    4  count     u32  인스턴스 수
    8  dtype     u8   0=f32 1=f16 2=i32 ...
    9  comps     u8   3=pos  4=quat  7=pos+quat  16=mat4
    10 flags     u16
    12 byte_len  u32
  raw bytes = count × comps × itemsize   (numpy C-order 그대로)

SCHEMA/EVENT payload = UTF-8 JSON
```

핵심 규칙:

- **섹션 = 인스턴스드 드로우 배치 하나.** `kind`(meshid)별로 배열 하나 →
  렌더 쪽은 `np.frombuffer(...).reshape(count, comps)` 후 그대로
  `glBufferSubData`. 파싱 비용 제로, viewmodel의 ViewTable과 1:1 대응.
- **스냅샷이 아니라 렌더 정보만.** 매 프레임 가는 건 움직이는 수치뿐.
  메쉬 등록, 이름, 텍스처 경로 같은 정적/저빈도 데이터는 `SCHEMA` 메시지로
  접속 시 1회(+변경 시). 그래서 JSON을 완전히 버리는 게 아니라 **매 프레임
  경로에서만 추방**하는 것.
- 송수신은 `frame.pack_state[_into]` / `frame.unpack`만 쓴다. 헤더 손대는
  코드는 한 파일(`frame.py`)에만 존재.

## 4. "최신만 받기" (latest-wins)

과거 버그 일지의 두 문제를 규칙으로 봉인:

1. **`}{` / START·END 경계 사고** → 고정 32B 헤더의 `payload_len`만큼
   `recv_into`로 **정확히** 읽는다 (`socklink.recv_exact`). 마커 불필요.
2. **버퍼/큐에 프레임이 쌓여 지연 누적** → 어디에도 큐를 두지 않는다.
   소켓 경로는 1칸짜리 `Mailbox`(새 게 오면 덮어씀), shm 경로는 슬롯 회전.
   느린 뷰어는 프레임을 "놓치는" 거지 "밀리는" 게 아니다.

## 5. shm 채널 내부 (3-슬롯 + seqlock)

```
[Ctrl 32B: latest_slot, latest_id ...][slot0][slot1][slot2]
slot = [seq u32][nbytes u32][pad][data slot_cap B]

쓰기: seq를 홀수로 → 데이터 기록 → seq 짝수(+2) → ctrl.latest_slot 갱신
읽기: latest_slot의 seq(s1) 확인(홀수면 이전 슬롯) → 복사 → seq(s2) 재확인
      s1==s2면 완성본, 아니면 재시도
```

- `SimProcess`로 띄우면 부모가 만든 `mp.Lock`을 양쪽에 물려줘서 **찢어진
  읽기(torn read)가 원천 차단**된다. 락 구간은 28KB memcpy 수준(수십 µs)이라
  경합 걱정 없음. ARM(rpi4)처럼 메모리 순서가 약한 기계에서도 안전.
- 이름으로 `attach`한 남남 프로세스끼리는 락 공유가 안 되므로 seqlock만으로
  동작(x86에선 사실상 충분, 재시도로 방어).
- 용량은 생성 시 고정(`slot_cap`). 유닛 최대치 기준으로 잡고, 더 커지면
  새 세그먼트를 만들어 Pipe로 이름을 알린다.

## 6. 함정 노트 (플랫폼)

- **Windows = spawn**: 시뮬 함수는 모듈 최상위(importable)여야 하고, 메인
  스크립트는 반드시 `if __name__ == '__main__':` 가드. 리눅스에서도 동일하게
  동작하도록 `SimProcess`는 기본 spawn.
- **resource_tracker**: 이 3.11 계열은 attach만 해도 register된다. spawn
  자식은 부모와 트래커를 **공유**하므로 자식이 unregister하면 부모 등록까지
  지워져 unlink 때 KeyError가 난다. 그래서 `ShmChannel.attach(...,
  child_of_creator=True)` (SimProcess가 알아서 함) / 남남 프로세스는 기본값
  (untrack)으로. 3.13+는 `track=False`로 깔끔히 해결됨.
- **Windows의 shm 수명**: unlink 개념이 없고 마지막 핸들이 닫히면 해제.
  창이 닫혀도 시뮬이 살아있으면 세그먼트도 살아있음 — 종료는 stop 이벤트로.
- 소켓 경로 부활 시 `TCP_NODELAY` 필수(이미 켜둠) — 안 그러면 Nagle이 소형
  프레임을 40ms씩 묶는다.

## 7. 네트워크 경로 (VR) — 로컬호스트 수치는 잊어라

§2의 TCP 수치는 루프백(손실 0, 지연 0.05ms, 대역 무한)이라 원격 뷰어(VR
헤드셋)에는 무의미하다. 커널 netem이 없는 환경에서도 돌아가는 유저스페이스
링크 에뮬레이터(`netlab.py`: 실제 소켓 사이에 지연/지터/직렬화/freeze/손실을
넣는 릴레이)를 만들어 재측정했다. WiFi에서는 802.11 MAC 재전송이 손실을
지터·처리율붕괴·freeze로 바꿔 보여주므로 TCP 경로에는 손실 대신 그걸 주고,
UDP 경로에는 (MAC 재시도 한계를 넘어 정말 사라지는) 손실도 준다.

### 대전제: VR에서 네트워크를 타는 것은 "월드 상태"뿐이다

- **헤드 포즈는 절대 왕복하지 않는다.** 헤드셋(브라우저 WebXR 포함)이 로컬
  트래킹으로 로컬 렌더. 그래서 월드 상태는 30~80ms 지연도 보간으로 흡수된다.
- 진짜 적은 평균 지연이 아니라 **수백 ms 스톨**(월드가 얼어붙는 순간)이다.
- PC VR(Quest Link/AirLink, SteamVR)은 렌더가 PC에서 돌므로 **네트워크 논의
  자체가 불필요** — §2의 로컬 shm 경로 그대로다. 이 절은 스탠드얼론
  뷰어(Quest 브라우저 three.js 등)용.

### 측정 (`bench_net.py`, 28KB×60Hz=13.5Mbit/s, 뷰어는 2ms마다 staleness 샘플)

```
[wifi]      4±3ms, 200Mbit, loss 0.5%
  tcp      got 59.9/s   stale p50  16  p95  23   max  57ms   stalls 0
  udp      got 52.8/s   stale p50  18  p95  36   max  73ms   stalls 0
  udp-f16  got 56.4/s   stale p50  17  p95  28   max  61ms   stalls 0

[wifi-bad]  12±8ms, 60Mbit, loss 2%, freeze 150ms/2s
  tcp      got 56.2/s   stale p50  30  p95  75   max 174ms   stalls 4
  tcp-64k  got 56.1/s   stale p50  30  p95  79   max 188ms   stalls 4
  udp      got 36.5/s   stale p50  37  p95 107   max 239ms   stalls 4
  udp-f16  got 45.6/s   stale p50  32  p95  83   max 189ms   stalls 4
```

읽는 법:

1. **이 규모에선 TCP+mailbox(latest-wins)가 잘 버틴다.** wifi에서 p95 23ms.
   "TCP는 VR에 못 쓴다"는 통념은 **큐잉 규율이 없을 때** 얘기다 — 우리는
   양끝이 1칸 mailbox라 백로그가 원천적으로 안 쌓인다.
2. **순정 UDP가 오히려 나빴다: 청크 수가 손실을 지수로 증폭한다.**
   28KB=25청크, 청크 하나만 죽어도 프레임 전체가 죽는다.
   생존율 = (1-p)^청크수: 2%손실×25청크 → 60% (측정 36.5/60 일치),
   f16으로 14KB=12청크 → 78% (측정 45.6/60 일치).
   → **UDP 도입보다 프레임 다이어트가 선행 과제다.**
3. **스톨 4회는 freeze 자체다** — 어떤 전송계층도 링크 단절 150ms는 못
   숨긴다. 이걸 가리는 건 전송이 아니라 **뷰어의 보간/외삽**이다.
4. tcp-64k(SO_SNDBUF 축소)는 이 비트레이트에선 차이 미미. 대역을 꽉 채우는
   스트림(수십 Mbit↑)에서 백로그 절단용으로 의미가 생긴다.
5. 단, 이 모델은 TCP에 낙관적이다: IP 레벨 손실이 TCP까지 뚫고 오는
   환경(혼잡한 2.4GHz, 인터넷 경유)에선 재전송 대기(RTO 최소 ~200ms)가
   head-of-line 스톨을 만든다. 그 위험이 실측되는 환경이면 UDP(작은 프레임
   전제)로 넘어갈 근거가 된다.

### 결론: 단계적 사다리

```
0) PC VR            : 네트워크 없음. 로컬 shm 그대로.
1) 지금 (Quest 브라우저): WebSocket(=TCP) + 양끝 latest-wins + 뷰어 보간.
                      프레임 바이트는 binary message로 그대로. (브라우저는
                      raw UDP/TCP 불가 → 어차피 ws가 유일한 즉시 선택지)
2) 프레임 다이어트    : f16(코덱 지원됨, dtype=1), smallest-three quat,
                      스켈레탈은 애니상태만(§스켈레탈 (c)). 28KB → 5~8KB.
3) 스냅샷 20~30Hz + 보간: 60Hz로 쏠 이유가 없다. 대역 절반, 손실표면 절반,
                      staleness는 보간 버퍼(스냅주기 1.5배)로 균일화.
4) 그래도 스톨이 보이면: WebRTC DataChannel(ordered=false, maxRetransmits=0,
                      python은 aiortc) = 브라우저에서 쓸 수 있는 UDP.
                      네이티브 뷰어면 udplink.py 그대로.
```

- 전송 스택: `udplink.py` = 청크(≤1204B)+오프셋 재조립+latest-wins+HELLO
  keepalive. 프레임 포맷은 TCP/UDP/ws 어디서나 동일 바이트.
- 입력(컨트롤러→시뮬)은 작으니(수십B) 뭘로 보내도 된다. 같은 채널 역방향이면
  충분.
- 에뮬레이터(`netlab.py`)는 Windows에서도 도는 순수 파이썬이라, 실제 배포 전
  나쁜 링크 시나리오를 언제든 재현할 수 있다.

## 8. 다음 단계

- 렌더 연결: `f = host.read_new()` → `for kind, arr in f.sections:` →
  kind로 VAO/셰이더 찾고 `arr`을 인스턴스 버퍼로 업로드 (axis3d
  `test_renderer.py`의 instanced draw 자리).
- 입력: pyglet/glfw 키 콜백에서 `host.send(('key', 'W', 1.0))` →
  시뮬 루프 `for i in ctx.inputs():`.
- 대역 아끼고 싶으면 dtype=f16(코드 1)로 pos를 절반으로 — 포맷은 이미 지원.
- 웹뷰어(three.js `dd/`)는 FrameCaster 옆에 websocket 브릿지 하나면 됨.
  프레임 바이트를 그대로 binary message로 흘리고 JS에서 DataView로 파싱.
