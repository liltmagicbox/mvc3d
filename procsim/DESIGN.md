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

### 참고: 실제 H.264 VR 스트리머들은 뭘 쓰나

"영상은 당연히 UDP" 아니냐는 직관 점검. [ALVR 위키](https://github.com/alvr-org/ALVR/wiki/How-ALVR-works)
기준(공개된 유일한 사례): 제어 소켓은 **TCP 고정**, 영상 스트림 소켓은
TCP/UDP 선택인데 **현재 기본값이 TCP**고 250Mbps까지 잘 동작한다고 명시.
UDP는 <30Mbps에서 최저지연, ~100Mbps는 throttled UDP. Moonlight(NVIDIA
GameStream계열)·Steam Link·WebRTC 영상은 UDP 계열(+FEC/NACK), Air Link와
Virtual Desktop은 비공개 프로토콜. 즉 **"clean LAN + 규율이면 TCP도 영상
250Mbps까지 감당"이 실전에서 검증된 사실**이고, 우리 측정과도 일치한다.

와이어 패킷에 대한 오해 하나: 어떤 스트리머도 24KB를 한 패킷으로 안 보낸다.
인코더가 뱉는 프레임(수십~수백KB)을 **MTU 크기(~1.2-1.4KB)로 패킷화**해서
보낸다(우리 청크와 동일한 구조). 24MB/s(=192Mbit)는 AirLink급 영상
비트레이트로, 5GHz WiFi 실효 한계권이 맞다 — 그리고 우리 상태 스트림은
다이어트 후 2~4Mbit로 **그 1/100**이라 대역폭은 애초에 쟁점이 아니다.

### MTU 예산: 왜 1204B인가

```
ethernet/wifi MTU 1500 - IP 20 - UDP 8               = 1472 사용가능
인터넷 경로 여유: PPPoE(1492), VPN/터널, IPv6(+20)    → ~1400도 위험할 수 있음
QUIC이 고른 안전선                                    ≈ 1200
우리 데이터그램: 페이로드 1184 + 청크헤더 20          = 1204  ✓
```
IP 단편화에 절대 기대지 않는다: 단편 하나 손실 = 데이터그램 전체 손실이고,
단편을 그냥 버리는 중간장비도 흔하다. 큰 데이터그램(예: 24KB)을 보내면
커널이 조용히 이 함정으로 밀어넣는다.

### 측정 (`bench_net.py`, 28KB×60Hz=13.5Mbit/s, 뷰어는 2ms마다 staleness 샘플)

```
[wifi]      4±3ms, 200Mbit, loss 0.5%
  tcp          got 60.1/s   stale p50  16  p95  23   max  26ms   stalls 0
  udp          got 52.8/s   stale p50  18  p95  36   max  74ms   stalls 0
  udp-f16      got 56.0/s   stale p50  17  p95  28   max 104ms   stalls 0
  udp-f16-fec  got 59.6/s   stale p50  16  p95  24   max  41ms   stalls 0

[wifi-bad]  12±8ms, 60Mbit, loss 2%, freeze 150ms/2s
  tcp          got 56.0/s   stale p50  30  p95  79   max 191ms   stalls 4
  tcp-64k      got 55.9/s   stale p50  30  p95  81   max 188ms   stalls 4
  udp          got 35.1/s   stale p50  38  p95 117   max 254ms   stalls 4
  udp-f16      got 42.8/s   stale p50  33  p95 103   max 204ms   stalls 4
  udp-f16-fec  got 55.0/s   stale p50  31  p95  77   max 173ms   stalls 4
```

읽는 법:

1. **이 규모에선 TCP+mailbox(latest-wins)가 잘 버틴다.** wifi에서 p95 23ms.
   "TCP는 VR에 못 쓴다"는 통념은 **큐잉 규율이 없을 때** 얘기다 — 우리는
   양끝이 1칸 mailbox라 백로그가 원천적으로 안 쌓인다.
2. **순정 UDP가 오히려 나빴다: 청크 수가 손실을 지수로 증폭한다.**
   생존율 = (1-p)^청크수: 2%손실×25청크 → 60% (측정 35/60 일치),
   f16 12청크 → 78% (측정 43/60 근사).
3. **XOR 패리티 1청크(FEC, +8% 오버헤드)로 UDP가 TCP와 동급이 된다.**
   청크 하나까지의 손실은 복구되므로 생존율 ≈ (1-p)^n + n·p·(1-p)^n:
   2%×12청크 → 97% (측정 55/60 일치). udplink에 구현됨(fec=True 기본).
   → 순서: **다이어트 → FEC → 그 다음에야 UDP가 의미**.
4. **스톨 4회는 freeze 자체다** — 어떤 전송계층도 링크 단절 150ms는 못
   숨긴다. 이걸 가리는 건 전송이 아니라 **뷰어의 보간/외삽**이다.
5. 단, 이 모델은 TCP에 낙관적이다: IP 레벨 손실이 TCP까지 뚫고 오는
   환경(혼잡한 2.4GHz, 인터넷 경유)에선 재전송 대기(RTO 최소 ~200ms)가
   head-of-line 스톨을 만든다. 같은 조건에서 UDP+FEC는 튜닝 없이 동급
   성능에 그 꼬리 리스크가 없으므로, 원격 경로의 종착지는 UDP+FEC다.

### 시계 문제: sim_time은 시뮬 기계의 시계다

다른 기계에서 staleness/보간을 하려면 클록 오프셋이 필요하다. udplink의
PING/PONG이 이를 겸한다: 뷰어가 1초마다 PING(t₀ 동봉) → 캐스터가
PONG(t₀, t_caster) → 뷰어가 `offset = t_caster - (t₀+t₁)/2`를 **최소 RTT
샘플에서** 채택(큐잉 노이즈 최소인 샘플이 가장 정확). `viewer.age_of(frame)`
이 보정된 나이를 돌려주고, `viewer.rtt_ms`는 적응형 전송률의 입력이 된다.

### 로컬 공유기(WiFi) 설계 체크리스트

**결론부터: 로컬 공유기는 TCP(브라우저면 WebSocket)로 확정.** 우리 벤치에서
wifi 프로파일의 TCP는 p95 23ms로 사실상 이상치였고, ALVR은 같은 조건에서
TCP로 **영상 250Mbps**를 실증했다. 우리는 f32 60Hz를 그대로 쏴도
13.5Mbit — 실증치의 1/18이다. 즉 **로컬에선 다이어트·FEC·저Hz 스냅샷이
필수가 아니다.** (그것들은 N이 만 단위로 커지거나 인터넷 경로로 나갈 때
꺼내는 옵션. 5~8KB/2~4Mbit 숫자는 그 옵션을 다 켠 경우의 값이다.)

TCP가 이렇게 동작하는 전제 세 가지(모두 구현/수칙에 반영됨):
`TCP_NODELAY`(Nagle off — 안 끄면 소형 프레임이 ~40ms씩 묶인다), 양끝
1칸 mailbox(백로그 금지 — 이게 없으면 "TCP는 실시간에 못 쓴다"는 통념이
현실이 된다), 무선 홉 1개(PC는 유선).

```
토폴로지   PC(시뮬) ──유선── 공유기 ──무선── 헤드셋   ← 무선 홉은 딱 하나
라디오     5GHz(가능하면 6E/전용 SSID), 2.4GHz 금지(BT/전자레인지 간섭)
전송       TCP(ws) + 양끝 latest-wins, f32 60Hz 그대로 (13.5Mbit)
멀티뷰어   유니캐스트 per-viewer (WiFi 멀티캐스트는 최저속도·무ACK라 함정)
뷰어       보간 버퍼 = 스냅주기 x 1.5 (60Hz면 ~25ms), 끊기면 ~150ms까지 외삽
입력       컨트롤러/헤드 '조작' 이벤트만 상향, 60~72Hz, 수십B — 아무 경로나
발견       고정IP 또는 mDNS. PING keepalive가 등록/생존확인 겸함(구현됨)
공존       영상 스트림(AirLink 등 192Mbit)이 같이 떠도 상태 13.5Mbit는 여유
```

### 인터넷 경로(원격 뷰어)일 때 추가로

- **여기서부터가 UDP+FEC의 본진이다**: IP 손실이 실제로 TCP를 때리고
  RTO(≥~200ms) 스톨이 현실이 되는 구간. RTT 20~80ms만큼 보간 버퍼를 키운다.
- **NAT**: 뷰어→캐스터 단방향 접속이면 캐스터 쪽 포트포워딩 하나로 끝
  (PING이 밖→안으로 먼저 나가므로 뷰어 쪽 NAT는 자동 통과). P2P가 필요해지면
  STUN/릴레이 대신 **WireGuard/Tailscale로 묶고 LAN처럼 취급**이 취미 규모의
  정답 — udplink 코드 변경 zero.
- **혼잡 예의**: 고정 2~4Mbit는 이미 예의 바른 수준. 지속 서비스로 키우면
  전달률·rtt_ms 피드백으로 스냅샷 Hz를 낮추는 적응 로직(간단한 knob) 추가.
- **브라우저 뷰어(WebXR)**: raw UDP 불가 → WebSocket으로 시작, 스톨이
  보이면 WebRTC DataChannel(ordered=false, maxRetransmits=0, python은
  aiortc)이 브라우저의 UDP. WebTransport(HTTP/3 datagram)는 차기 후보.
- **보안**: 평문 UDP를 인터넷에 그대로 노출하지 말 것 — Tailscale/WireGuard
  터널이 인증+암호화를 공짜로 준다.

### 결론: 단계적 사다리

1)이 로컬 공유기의 확정안이고, 2)~4)는 **인터넷/열악 링크로 확장할 때만**
순서대로 꺼내는 예비 경로다.

```
0) PC VR            : 네트워크 없음. 로컬 shm 그대로.
1) 로컬 공유기 [확정] : WebSocket(=TCP) + 양끝 latest-wins + 뷰어 보간.
                      f32 60Hz 그대로. 프레임 바이트는 binary message로.
2) 프레임 다이어트    : f16(코덱 지원됨), smallest-three quat,
                      스켈레탈은 애니상태만(§스켈레탈 (c)). 28KB → 5~8KB.
3) 스냅샷 20~30Hz + 보간: 대역 절반, 손실표면 절반, staleness 균일화.
4) 원격/열악 링크     : UDP+FEC(udplink.py 그대로, fec 기본 on).
                      브라우저면 WebRTC DataChannel(aiortc).
                      인터넷이면 Tailscale로 묶어 LAN 취급 + 버퍼 확대.
```

- 전송 스택: `udplink.py` = 청크(≤1204B)+오프셋 재조립+XOR FEC+latest-wins
  +PING/PONG(keepalive·RTT·클록오프셋). 프레임 포맷은 TCP/UDP/ws 어디서나
  동일 바이트.
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
