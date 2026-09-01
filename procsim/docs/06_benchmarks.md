# 06. 벤치마크 — 수치와 재현법

모든 수치는 **이 개발 컨테이너(리눅스) 기준**이다. 결론의 방향은 옮겨가지만
절대값은 실기기(Windows PC, 공유기, 헤드셋)에서 재측정할 것.

```
python -m procsim.demo_local        # 스레드 vs 프로세스 (GIL)
python -m procsim.bench_format      # JSON vs 바이너리 코덱
python -m procsim.bench_transport   # shm vs pipe vs tcp (로컬)
python -m procsim.bench_net         # tcp vs udp(+f16/fec) x 링크 프로파일
python -m procsim.bench_net wifi-bad   # 프로파일 하나만
```

## GIL (demo_local, N=1000, 시뮬 2ms py/틱 + 렌더 2ms py/프레임)

| | THREAD | PROCESS |
|---|---|---|
| 렌더 fps | 49.7 | 59.7 |
| 최악 간격 | 44.8ms | 17.0ms |
| 상태 나이 | 4.02ms | 0.99ms |

## 코덱 (bench_format, N=1000 pos+quat)

| | binary | json |
|---|---|---|
| 크기 | 28,064B | 145,910B (x5.2) |
| pack | 0.007ms | 3.3ms (x466) |
| unpack | 0.003ms | 1.9ms (x729) |

## 로컬 전송 (bench_transport, 28KB 프레임 전력 생산)

| | pub/s | 나이 |
|---|---|---|
| shm 3-slot | 99,974 | 0.063ms |
| mp.Pipe | 10,440 | 0.48ms |
| tcp localhost | 18,724 | 0.46ms |

## 네트워크 (bench_net, 28KB×60Hz, 뷰어 2ms 틱 staleness)

```
[wifi]      4±3ms, 200Mbit, loss 0.5%
  tcp          got 60.1/s   p50 16  p95  23   max  26ms   stalls 0
  udp          got 52.8/s   p50 18  p95  36   max  74ms   stalls 0
  udp-f16-fec  got 59.6/s   p50 16  p95  24   max  41ms   stalls 0

[wifi-bad]  12±8ms, 60Mbit, loss 2%, freeze 150ms/2s
  tcp          got 56.0/s   p50 30  p95  79   max 191ms   stalls 4
  udp          got 35.1/s   p50 38  p95 117   max 254ms   stalls 4
  udp-f16-fec  got 55.0/s   p50 31  p95  77   max 173ms   stalls 4
```

읽기: FEC가 UDP를 TCP 동급으로 올린다. 스톨 4회는 freeze 자체(전송 무관,
보간의 몫). lan 프로파일에선 tcp/udp 모두 p95 ~17ms로 구분 불가.

## netlab 프로파일과 모델의 한계

`netlab.py`는 실소켓 사이의 유저스페이스 릴레이로 지연/지터/직렬화(대역)/
freeze/손실을 주입한다. 순수 파이썬이라 Windows에서도 그대로 돈다.

| 프로파일 | 값 |
|---|---|
| lan | 0.2±0.05ms, 1Gbit |
| wifi | 4±3ms, 200Mbit, loss 0.5% |
| wifi-bad | 12±8ms, 60Mbit, loss 2%, freeze 150ms/2s |

**TCP에 낙관적인 모델임을 알 것**: WiFi MAC 재전송이 손실을 가려준다는
가정으로 TCP 경로엔 손실을 주입하지 않는다(커널 TCP가 릴레이 아래에서
복구해버려 주입 자체가 불가능하기도 하다). IP 손실이 TCP를 직접 때리는
환경(인터넷)의 RTO 스톨은 이 모델 밖 — §04의 타임라인이 그 설명이다.

## 기타 실측 조각

- IP 단편화: MTU 1500 링크에 28KB 데이터그램 → FragCreates +19 (커널이
  조용히 쪼갬), DF 설정 시 EMSGSIZE. 1204B는 통과.
- FEC 단위검증: 24청크 프레임의 모든 드롭 위치에서 복구 성공.
- 손실 가시성: 6% 손실 80프레임 → 전달 38 + 감지 스킵 39 = 77 (잔여 3 =
  맨끝 프레임 사각지대).
- 클록오프셋: 동일 호스트에서 ~1ms 이내 수렴 (2±1ms 에뮬 링크 경유).
