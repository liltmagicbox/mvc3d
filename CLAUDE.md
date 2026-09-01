# CLAUDE.md

## 이 저장소는 무엇인가

mvc3d — 파이썬 3D 시뮬레이션의 MVC 분리 실험 (2022). **아카이브/참조 전용.**

- 이 저장소의 논의와 결론은 [RETROSPECTIVE.md](RETROSPECTIVE.md)에 정리되어 있고,
  살아있는 설계 문서는 [axis3d 저장소의 docs/](https://github.com/liltmagicbox/axis3d/blob/main/docs/README.md)에 있다.
- 차기 프로젝트 관련 작업 요청이 오면 axis3d 쪽에서 진행하는 것이 맞는지 먼저 확인할 것.

## 작업 규칙

- 여기의 코드는 탐색 기록이다: 미완성 함수, 주석 독백, 실험 폴더(`mvsim/`, `threeinit/`, `ver0.1_xyz_attrreport/`)가 의도된 상태다. **리팩터링·린트·정리를 시도하지 말 것** — 지침서들이 이 파일들을 원형 그대로 인용한다.
- 허용되는 변경: 문서 추가/갱신 (RETROSPECTIVE.md, 이 파일), 자료 발굴을 위한 읽기.
- 대화·문서는 한국어, 코드·커밋 메시지는 영어.

## 길잡이

| 찾는 것 | 위치 |
|---|---|
| 시뮬 루프, pause/resume | `mvsim/20_socket_world/simulator.py` |
| 경계 인터페이스 원형 | `interface.py` |
| 이벤트 와이어 포맷과 파싱 | `mvsim/20_socket_world/event.py` |
| 이벤트 배달 사고실험 (Damage/Heal, 감각=충돌) | `mvsim/_concept_eventreceptor.py` |
| 키맵 컨트롤러 | `controller.py` |
| "pos 전쟁" (개체별 벡터 객체의 한계) | `ver0.1_xyz_attrreport/API.py` |
| three.js식 씬 API 스케치 | `fullcode.py` |
| 브라우저 뷰(three.js+websocket) 실험 | `threeinit/` |
| instanced draw 데모 | `mvsim/rpi4_pyglet_23.8_vao_4x4batch_instanced_snow.py` |
