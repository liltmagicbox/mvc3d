# 04. 전송 — 네트워크 구간은 UDP+FEC로 통일

**결론: 같은 기계 = shm(§01). 네트워크 구간 = UDP+FEC(udplink) 단일 코드
— 공유기든 인터넷이든 동일. 브라우저 뷰어 구간만 어댑터(§05). 제어·이벤트는
신뢰 채널 병행.** 근거: 로컬에서 UDP는 TCP와 동급(p95 17ms)이고, 원격의
TCP RTO/head-of-line 동결 리스크가 구조적으로 없다 (§06 표).

```
 sim ──shm──▶ view(같은 기계)
 sim ──UDP+FEC──▶ 네이티브 뷰어 (공유기/인터넷 동일)
 sim ──ws/WebTransport 어댑터──▶ 브라우저 뷰어      ← 프레임 바이트 동일
 입력·점수·스폰 ──신뢰 채널(TCP 컨트롤 소켓 or ack 미니레이어)──▶ 양방향
```

## 가이드 (udplink)

```python
from procsim import UDPCaster, UDPViewer

# 시뮬 쪽
caster = UDPCaster(port=30030)               # fec=True 기본
caster.cast_state(frame_id, time.perf_counter(), sections)

# 뷰어 쪽
viewer = UDPViewer('192.168.0.10', 30030)    # PING 자동(등록+keepalive+클록)
f = viewer.latest()                          # 최신 완성 프레임 or None
age = viewer.age_of(f)                       # 클록오프셋 보정된 상태 나이(s)
viewer.rtt_ms, viewer.stat_skipped, viewer.stat_fec_recovered  # 계기판
```

## 왜 이 모양인가 (기제 요약)

- **MTU**: 데이터그램은 1204B(페이로드 1184+헤더 20). 이더넷 1500 − IP/UDP
  헤더 − 터널 여유 = QUIC과 같은 ~1200 안전선. 큰 데이터그램을 보내면
  커널이 **조용히 IP 단편화**한다(28KB→19조각 실측) — 조각 1개 손실이면
  전체 폐기 + FEC 불가 + 단편 버리는 중간장비 + PMTUD 블랙홀. 절대 금지.
- **청크 손실은 지수로 증폭**: 생존율=(1-p)^n. 2%×25청크=60%.
- **XOR 패리티 1청크(+8%)**: 청크 1개까지 복구 → 생존율 ≈ (1-p)^n +
  n·p·(1-p)^n. 2%×12청크 78%→**97%** (측정 일치). `fec=True` 기본.
- **latest-wins**: 어디에도 큐 없음. 프레임이 죽으면 16ms 뒤 다음 프레임이
  대체. TCP처럼 "복구시간=동결시간"이 되지 않는다.
- **클록**: PING/PONG으로 `offset = t_caster - (t₀+t₁)/2` (최소 RTT 샘플).
  sim_time은 시뮬 기계의 perf_counter라 보정 없인 타기계에서 나이 계산 불가.

## 로스는 감지된다 (자동 수리와 ACK가 없을 뿐)

| 층 | 수단 | 노출 |
|---|---|---|
| 프레임 | frame_id 구멍 | `stat_skipped` |
| 청크 | offset 집합 + n_chunks | FEC가 이걸로 복구 |
| 시간 | sim_time + 클록오프셋 | `age_of()` |

사각지대 2개와 처방: ① 맨 끝 프레임(뒤가 없어 구멍이 안 보임) → 고정 Hz
발행 유지, 정지 시 하트비트. ② 이벤트류 → 신뢰 채널로.

## TCP(socklink)의 남은 자리

FrameCaster/FrameViewer는 폐기가 아니다: ws 어댑터의 밑단, 컨트롤 소켓,
그리고 "히컵 몇 번 참을 수 있는" 간단한 뷰어용. 쓸 때 수칙: `TCP_NODELAY`
(켜져 있음), 양끝 1칸 mailbox(구현돼 있음) — 이 둘이 빠지면 "TCP는
실시간에 못 쓴다"는 통념이 현실이 된다. TCP는 느린 도로가 아니라 **사고
나면 전 차선이 멈추는 도로**다: 평시 속도는 UDP와 같고, 손실 순간에만
RTO(최소 ~200ms) 동결이 온다. LAN에선 그 사고가 거의 없다.

## 함정

- 상태 스트림에 이벤트를 태우지 말 것(드랍=소실). ALVR도 control=TCP 고정.
- 검증은 실기기 전에 `netlab`으로: 릴레이가 지연/지터/대역/freeze/손실을
  실소켓 사이에 주입한다 (§06).
