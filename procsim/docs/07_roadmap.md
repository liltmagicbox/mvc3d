# 07. 구현 로드맵

순서대로. 각 항목은 앞 항목 없이도 동작하도록 잘라져 있다.

## ① axis3d 렌더러 연결 (로컬 완성)

- SimProcess로 시뮬 분리, `read_new()` → kind별 VAO/셰이더 매칭 →
  인스턴스 버퍼 업로드 (test_renderer.py의 instanced draw 자리).
- 입력: pyglet/glfw 콜백 → `host.send(...)` → 시뮬 `ctx.inputs()`.
- 완료 기준: demo_local 수준의 fps/나이가 실제 렌더러에서 재현.

## ② ws 브릿지 (브라우저 뷰어 개통)

- `websockets` 라이브러리로 ~20줄: shm에서 `read_new()` → binary message로
  그대로 송신. 뷰어 수만큼 태스크, 각자 latest-wins.
- three.js(dd/) 쪽: `ws.binaryType='arraybuffer'` → DataView로 §02 헤더
  파싱 → InstancedMesh.instanceMatrix 갱신.
- 완료 기준: 퀘스트 브라우저에서 1000유닛이 60fps로 움직임.

## ③ 뷰어 보간기 (스톨 은폐)

- 링버퍼에 최근 스냅샷 2~4개, 재생시각 = 최신 sim_time − 1.5×스냅주기.
- pos 선형 / quat slerp, 끊기면 외삽 ~150ms 상한.
- 완료 기준: netlab wifi-bad 경유에도 시각적 끊김이 freeze 구간에만 국한.

## ④ 신뢰 이벤트 채널 (게임플레이 전제)

- 입력·점수·스폰용. 간단한 쪽부터: TCP 컨트롤 소켓(=ws 재활용) 하나.
  UDP 단일화가 필요해지면 seq+ack+재전송 미니레이어로 교체.
- 완료 기준: 6% 손실 netlab 경유에도 이벤트 무손실·순서 보존.

## ⑤ 다이어트 (인터넷 준비)

- f16 섹션(astype 한 줄), IDS 섹션(u32), 스켈레탈 애니상태만(§03-(c)).
- 원거리 배치 저Hz 차등 전송(kind별 스냅레이트).
- 완료 기준: 프레임 5~8KB(6~7청크), bench_net 생존율 99%+.

## ⑥ WebTransport 어댑터 (브라우저 데이터그램)

- aioquic 서버 + ECDSA 자가서명 cert 재생성 스크립트(14일 제한) +
  `serverCertificateHashes` 클라이언트. 피처 디텍션 후 ws 폴백.
- 트리거: 실기기 계측에서 ws 히컵(stall>120ms)이 분당 수 회.

## ⑦ 계측 (전환 판단의 근거)

- 뷰어에 상시 로깅: fps, `age_of` p50/p95, stall 횟수, `stat_skipped`,
  `stat_fec_recovered`, `rtt_ms`.
- 이 수치가 §05 사다리의 단을 올리는 유일한 트리거다 — 감으로 올리지 않는다.

## 하지 않기로 한 것

- 영상 스트리밍 자작(AirLink/ALVR의 영역), IP 단편화 의존, WiFi 멀티캐스트,
  프레임 큐(모든 홉은 latest-wins), 상태 스트림에 이벤트 태우기,
  STUN/TURN 자작(필요해지면 Tailscale).
