# 05. 브라우저 / VR 경로

**원칙: 헤드 포즈는 절대 네트워크를 타지 않는다.** 헤드셋(브라우저 WebXR
포함)이 로컬 트래킹으로 로컬 렌더하고, 네트워크로 오는 건 월드 상태뿐 —
그래서 30~80ms 지연은 보간으로 흡수되고, 진짜 적은 평균 지연이 아니라
**수백 ms 스톨**이다. PC VR(Quest Link/AirLink/SteamVR)은 렌더가 PC라
네트워크 논의 자체가 불필요 — §01의 로컬 shm 그대로.

## 로컬 공유기 체크리스트

```
토폴로지   PC(시뮬) ──유선── 공유기 ──무선── 헤드셋   ← 무선 홉은 딱 하나
라디오     5GHz(가능하면 전용 SSID), 2.4GHz 금지
전송       UDP+FEC(네이티브) / ws(브라우저 시작점). f32 60Hz 그대로 OK
멀티뷰어   유니캐스트 per-viewer (WiFi 멀티캐스트는 최저속도·무ACK 함정)
발견       고정 IP 또는 mDNS. PING keepalive가 등록/생존 겸함
공존       영상 스트림(AirLink 192Mbit)과 동거해도 상태 13.5Mbit는 여유
```

## 브라우저 어댑터 사다리 (프레임 바이트는 동일)

```
① WebSocket (지금)        복잡성 0. LAN에선 TCP 히컵 자체가 희귀
② WebTransport (필요시)   브라우저의 진짜 데이터그램. 2026-03부터 Baseline
③ WebRTC DataChannel      ②가 안 되는 브라우저 전용 비상구
```

- **"UDP 웹소켓"은 없다** — WebSocket은 RFC 6455가 TCP 위로 정의(HTTP
  업그레이드로 시작). 브라우저가 일반 페이지에 raw UDP를 안 주는 이유는
  스푸핑/증폭 공격 방지고, WebRTC/WebTransport는 핸드셰이크로 "상대가
  수신에 동의했음"을 증명한 '허가받은 UDP'다.
- ws 게임이 느린 게 아니다: 평시 속도는 UDP와 동일, 손실 순간의 히컵만
  다르며 LAN에선 그 사건이 희귀하다 (agar.io류가 전부 ws인 이유).
- **WebTransport**(②): `new WebTransport("https://ip:4433", {serverCertificateHashes})`
  — 시그널링/ICE/SDP 없음, datagram API가 우리 1204B 청크와 1:1, 서버는
  aioquic. 귀찮음은 인증서 하나: ECDSA 자가서명 + 해시 전달, 유효 14일
  제한이라 재생성 스크립트 필요. 퀘스트 브라우저는 Chromium 기반 —
  `'WebTransport' in window`로 피처 디텍션 후 ws 폴백.
- **WebRTC**(③)가 비상구인 이유: P2P NAT 관통용 4층 스택(ICE+DTLS+SCTP+DC),
  시그널링 자작(아이러니하게 보통 ws), SDP/ICE 디버깅, aiortc의 av(FFmpeg)
  의존성. 우리 토폴로지(클라→고정 서버)엔 대부분 낭비. 그래도 가야 하면
  최소구성(호스트 후보만, 논-트리클, HTTP POST 시그널링)으로 서버 ~70줄.

## 뷰어 보간 (스톨을 가리는 진짜 담당자)

- 재생 시각 = `최신 sim_time - 보간버퍼`, 버퍼 = 스냅주기 × 1.5
  (60Hz 스냅이면 ~25ms, 30Hz면 ~50ms; 인터넷이면 +RTT/2).
- 버퍼 안의 두 스냅샷 사이를 sim_time 기준 선형(quat은 slerp) 보간.
- 새 프레임이 끊기면 마지막 속도로 **외삽하되 ~150ms 상한** — 그 이상은
  차라리 멈추는 게 덜 이상하다.
- 링크 freeze(전송계층 무관)를 가리는 건 이 계층이다. §04의 어떤 전송도
  150ms 단절 자체는 못 숨긴다.

## 인터넷으로 나갈 때 추가

- 캐스터 쪽 포트포워딩 하나면 됨(PING이 뷰어 NAT를 밖→안으로 먼저 뚫음).
- 평문 UDP를 인터넷에 노출하지 말 것 — **Tailscale/WireGuard로 묶어 LAN
  취급**이 취미 규모 정답(암호화+NAT 해결, udplink 코드 변경 0).
- 다이어트(f16, §02; 애니상태만, §03)로 청크 수를 줄이면 생존율이 지수로
  좋아진다 (§04).
- 전환 판단은 계측으로: stall(>120ms) 빈도와 `stat_skipped`가 분당 수 회
  이상 찍히면 사다리를 한 단 올린다.
