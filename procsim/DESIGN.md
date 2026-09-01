# procsim — 시뮬 프로세스 분리 & 상태 스트리밍

시뮬은 별도 프로세스(GIL 회피), 뷰는 "렌더에 필요한 최신 상태"만 받는다.
매 프레임 경로는 고정 바이트 헤더 + numpy 원시 바이트, JSON은 콜드패스 전용.

```
 [sim process]                                   [view process / 뷰어]
   world.update() ──▶ publish()
        │                  같은 기계 ── shm 3-slot ──▶ read_new() → 렌더
        │                  네트워크  ── UDP+FEC ─────▶ 네이티브 뷰어
        │                  브라우저  ── ws / WebTransport ▶ three.js(WebXR)
        ◀────────── 입력·이벤트: 신뢰 채널(Pipe/TCP) ──────────┘
```

## 문서 (주제별, docs/)

| 문서 | 주제 | 핵심 결론 |
|---|---|---|
| [01_process.md](docs/01_process.md) | 프로세스 분리, shm 채널 | 스레드=49.7fps vs 프로세스=59.7fps. SimProcess 사용법 |
| [02_frame_format.md](docs/02_frame_format.md) | 와이어 포맷 | 32B 헤더+섹션. JSON 대비 pack x466. 코덱 API |
| [03_data_model.md](docs/03_data_model.md) | 무엇을 싣나 | 자산(glTF)/상태/게임 3평면, id로 연결. 스켈레탈은 애니상태만 |
| [04_transport.md](docs/04_transport.md) | 전송 | 네트워크 구간 UDP+FEC 통일. MTU 1204, XOR 패리티, 클록싱크 |
| [05_browser_vr.md](docs/05_browser_vr.md) | 브라우저/VR | 헤드포즈는 로컬. 어댑터 ws→WebTransport→WebRTC. 보간 가이드 |
| [06_benchmarks.md](docs/06_benchmarks.md) | 수치·재현 | 모든 표 + 실행 커맨드 + netlab 프로파일/한계 |
| [07_roadmap.md](docs/07_roadmap.md) | 구현 순서 | ①렌더러 연결 ②ws 브릿지 ③보간기 ④신뢰 이벤트 ⑤다이어트 ⑥WebTransport ⑦계측 |

## 코드

| 파일 | 역할 |
|---|---|
| `frame.py` | 프레임 코덱 (헤더/섹션, STATE/SCHEMA/EVENT) |
| `shmlink.py` | 로컬 shm 3-슬롯 latest-wins 채널 |
| `simproc.py` | SimProcess/SimContext — 프로세스 호스트 배선 |
| `udplink.py` | UDP 전송: 청크 1204B, XOR FEC, PING/PONG 클록, 로스 계수 |
| `socklink.py` | TCP 전송: ws 어댑터 밑단·컨트롤 소켓·간이 뷰어 |
| `netlab.py` | 링크 에뮬레이터 (지연/지터/대역/freeze/손실) |
| `demo_local.py` `bench_*.py` | §06의 수치 재현 |

## 결정 로그

| 결정 | 근거 (상세는 해당 문서) |
|---|---|
| 시뮬 = 별도 프로세스, 로컬 채널 = shm latest-wins | GIL 실측, 전송비용 63µs — 01 |
| 핫패스 바이너리 / 콜드패스 JSON | pack x466, unpack x729 차이 — 02 |
| 게임 데이터는 공간 노드가 아니라 EVENT+id | 3평면 분리 — 03 |
| 네트워크 구간 = UDP+FEC 단일 코드 | 로컬 동급 + 원격 RTO 리스크 제거 — 04 |
| 제어·이벤트 = 신뢰 채널 병행 | 사건은 드랍=소실 — 04 |
| 데이터그램 1204B, IP 단편화 금지 | 단편화 실측(19조각), 중간장비 — 04 |
| 브라우저 어댑터 ws → WebTransport → WebRTC | "UDP 웹소켓" 부재, WebTransport Baseline — 05 |
| 큐 금지: 모든 홉 latest-wins | 20_socket_world의 백로그 교훈 — 04 |
| 전환은 계측(stall/skipped)으로만 | 감이 아니라 계기판 — 05, 07 |
