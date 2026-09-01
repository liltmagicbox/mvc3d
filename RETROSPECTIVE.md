# mvc3d 회고 — 이 저장소가 남긴 것

> 이 저장소의 논의는 [axis3d](https://github.com/liltmagicbox/axis3d)의 `docs/`로 정리·계승되었다.
> 차기 프로젝트를 시작한다면 이 파일이 아니라 **axis3d/docs/README.md**에서 출발할 것.

## 한 줄 요약

`view-controller ----- model py 3d simulator` — 파이썬 3D 시뮬레이션에서 **경계를 어디에 긋는가**를 실험한 저장소 (2022).

## 여기서 확립되어 살아남은 것

1. **좁은 경계 계약** (`interface.py`): world는 `input/update/draw` 셋, 뷰 대리인은 `get_inputs/draw` 둘. Simulator는 그 다섯 개만 알고 tick 루프를 돌린다 (`mvsim/20_socket_world/simulator.py` — pause/resume, 실행 중 world 교체까지 동작).
2. **뷰는 소켓 건너편의 소모품** (`SocketViewController`, `threeinit/`): 시뮬은 headless로 돌고, three.js 브라우저든 로컬 창이든 상태 스트림의 구독자일 뿐이다. websocket 브로드캐스터를 4세대까지 갈아엎으며 검증했다 (`threeinit/websocket_land/`, 데모 gif 포함).
3. **이벤트는 경계에서 한 번만 변환** (`20_socket_world/event.py`): 와이어에는 `{'Key': ['k',1.0,t]}` 압축 dict, 안쪽에는 타입 있는 Event. *"let Events not cross this line."* 모든 입력장치를 (key, value)로 일반화, 키맵 `'w':'move_up*1'` 컨트롤러 (`controller.py`).
4. **받는 쪽이 결과를 정하는 이벤트 배달** (`mvsim/_concept_eventreceptor.py`): `target.hp -= x` 직접 조작 대신 Damage/Heal 이벤트를 deliver하고 수신측 receive가 해석한다. "감각기관은 전부 충돌 볼륨"이라는 관찰도 이 파일에.
5. **instanced draw** (`mvsim/rpi4_pyglet_..._instanced_snow.py`): `uniform mat4 Model[252]` + `gl_InstanceID`로 라즈베리파이4에서 눈 데모. 같은 지오메트리 N개는 draw call 하나.
6. **three.js식 씬 API 감각** (`fullcode.py`): Geo/Mat 팩토리, attrs dict 지오메트리, "BufferGeometry는 GPU 제출용 — 파이썬 안에서 흉내내지 않는다".

## 여기서 패배해서 방향을 바꾼 것

- **"pos 전쟁"** (`ver0.1_xyz_attrreport/API.py`, `xyz.py`, `actor.py`): 액터마다 파이썬 벡터 객체를 두는 모든 변형(교체 대입, 복사 반환, property in-place set, ID 벡터)을 시도하고 전부 한계를 확인했다. 결론 — 개체별 벡터 객체 자체를 버린다.
- 그 답이 이 저장소 `world.py`에 이미 이름으로 남아 있다: `self.AXIS`, `self.actorsAXIS`. 개체를 배열의 열로 눕히는 구조는 **axis3d**(2023)에서 UnitArray/UnitFactory로 실현되었고, 실측 벤치마크(속성-메이저 2배, nonzero 인덱싱 4배, 배치 생성 10배)로 확정되었다.

## 계승 지도

| mvc3d의 것 | 어디로 갔나 |
|---|---|
| interface.py / simulator.py | axis3d [docs/guides/14-view-boundary.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/guides/14-view-boundary.md) |
| event.py 와이어 포맷, controller 키맵 | [docs/guides/13-events-and-units.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/guides/13-events-and-units.md) |
| _concept_eventreceptor.py의 사고실험들 | 위 지침 13 + [docs/ideas.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/ideas.md) |
| instanced snow, 뷰 실험들 | [docs/guides/15-rendering.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/guides/15-rendering.md) |
| pos 전쟁의 결론 | [docs/guides/10-core-array.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/guides/10-core-array.md) |
| 전체 서사 | [docs/00-history-and-lessons.md](https://github.com/liltmagicbox/axis3d/blob/main/docs/00-history-and-lessons.md) |

이 저장소는 이제 **읽기 전용 참조 자료**다. 새 작업은 여기서 하지 않는다.
