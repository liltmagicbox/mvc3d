# glTF 씬 전달/재현 호환성 리포트

> 질문: "glTF로 씬을 전달하고 재현하는 게 어느 정도나 될까? 언리얼이나 자체 엔진에서도 호환되고, 블렌더로 렌더까지 되면 좋겠다."
>
> 답: **시각적인 씬(지오메트리·계층·트랜스폼·PBR 머티리얼·조명·카메라)은 glTF 하나로 거의 전부 전달된다.**
> 이번에 코드로 직접 검증했고, 블렌더 렌더까지 확인했다. 물리·파티클·게임 로직 같은
> 엔진 상태는 표준 밖이지만, `extras`(JSON 자유 필드)로 실어 나르는 우회로가 동작한다.

## 이번에 실제로 검증한 것

순수 파이썬(표준 라이브러리만) glTF 2.0 writer/reader `gltf.py`를 만들고,
axis3d의 cylinder.py 지오메트리로 데모 씬(분대 9유닛 + 오벨리스크 + 조명 3종 + 카메라)을
`.glb`로 뽑아 아래를 전부 통과시켰다.

| 검증 항목 | 방법 | 결과 |
|---|---|---|
| 스펙 준수 | Khronos 공식 validator (gltf-validator 2.0.0-dev.3.10) | **에러 0, 경고 0** (demo_scene.glb, world.glb 둘 다) |
| 라운드트립 | gltf.py writer → reader | 지오메트리 좌표 오차 0 (byte-exact), TRS/재질/extras 복원 |
| 서드파티 파서 | pygltflib 1.16.5, trimesh 5.0 | 정상 파싱, 지오메트리 개수 일치 |
| **블렌더 임포트** | Blender 5.0.1 (bpy) `import_scene.gltf` | 36오브젝트/조명3/카메라1 전부 도착. **엔진 Z-up 좌표 그대로 복원** (unit4: (-2.9, 0, 0)) |
| **블렌더 렌더** | Cycles CPU, 830x500 | 성공 → `gltf_out/blender_render.png` |
| extras 전달 | 리더 유닛에 `{'hp':100,'speed':[0,1,0],'simulate_physics':True}` | 블렌더 커스텀 프로퍼티로 도착, three.js userData로 도착 |
| three.js | r143 GLTFLoader (뷰어에 번들된 것과 같은 버전) | 메시 21 + Points 1 + 조명 3 + 카메라(fov 70.00) 전부 로드 |
| **역방향** | 블렌더가 만든 씬 export → 우리 reader | 큐브(24버텍스)/조명/카메라 → attrs dict로 도착, VAO에 바로 넣을 수 있는 형태 |
| 버텍스 컬러 | COLOR_0 (오벨리스크 높이 그라디언트) | 블렌더/three 모두 도착·렌더 |
| 반투명 | baseColor alpha + BLEND | 블렌더 Principled Alpha로 도착, 렌더 확인 |

데모 씬 파일 크기: **27KB** (버텍스 477, 삼각형 912, 드로우콜 7).

언리얼은 이 환경에서 실행할 수 없어서 문서 기반 평가다(아래 상세).
다만 공식 검증기 에러 0인 파일이므로 임포트 실패 가능성은 낮다. UE 에디터에
드래그&드롭 한 번이면 확정된다.

## glTF 2.0이 실어 나르는 것 / 못 나르는 것

**코어 스펙으로 되는 것**
- 씬 그래프: 노드 트리 + TRS(위치/쿼터니언/스케일) 또는 4x4 행렬(column-major, 렌더러와 같은 관례)
- 메시: POSITION / NORMAL / TANGENT / TEXCOORD_n / COLOR_n / JOINTS·WEIGHTS(스킨), 인덱스, 서브메시(primitive)별 머티리얼, POINTS/LINES/TRIANGLES 모드
- 머티리얼: PBR metallic-roughness (baseColor·metallic·roughness·emissive·normal/AO/emissive 텍스처, 알파, 양면)
- 카메라: perspective(yfov/aspect/near/far) / orthographic
- 애니메이션: TRS 키프레임 + 스킨(본) + 모프타깃, 보간(LINEAR/STEP/CUBICSPLINE)
- 텍스처: PNG/JPEG 내장(glb) 또는 외부 파일
- `extras`: 모든 오브젝트에 JSON 자유 필드 → **엔진 커스텀 데이터 통로 (검증됨)**

**확장(extension)으로 되는 것 — 지원처 표기**
- `KHR_lights_punctual` (해/점/스팟 조명): 블렌더 O, UE O, three O — **이번에 사용·검증**
- `KHR_materials_emissive_strength`, `KHR_materials_clearcoat/transmission/ior` 등 재질 확장: 블렌더 O, three O, UE 부분적
- `KHR_texture_transform`, `KHR_materials_variants`(스킨 교체), `KHR_draco_mesh_compression`(압축)
- `EXT_mesh_gpu_instancing`: 같은 메시 대량 배치를 인스턴스 배열로 — **test_renderer.py의 instanced draw 계획과 정확히 대응**. three O, 블렌더 O(임포트), UE 부분적

**표준으로 안 되는 것 (= 엔진마다 다시 세팅하거나 extras로 우회)**
- 물리: 콜라이더/강체/중력 (`KHR_physics_rigid_bodies`가 표준화 진행 중이지만 임포터 지원이 아직 거의 없음)
- 파티클, 지형/포리지 시스템, 포스트프로세스(블룸/톤매핑 설정), 스카이/환경광 IBL(`EXT_lights_image_based`는 지원처 드묾), 오디오, 게임 로직/스크립트
- 엔진 전용 머티리얼 그래프(UE 머티리얼, 블렌더 노드트리) — PBR 파라미터로 근사만 됨

정리하면: **"보이는 것"은 다 가고, "움직이는 규칙"은 안 간다.** 우리의 경우
움직임은 어차피 Model(파이썬 월드)이 소유하니까, glTF는 view 스냅샷 + 자산 포맷으로 정확히 맞는 역할이다.

## 좌표계 / 단위 — 제일 먼저 부딪히는 것

| | up | 손좌표계 | 단위 |
|---|---|---|---|
| axis3d/mvc3d (우리) | **Z-up** | RH | m |
| glTF | **Y-up** | RH | m |
| three.js | Y-up | RH | m |
| Blender | Z-up | RH | m |
| Unreal | Z-up | **LH** | **cm** |

- 해법(구현됨): 씬 루트에 `zup_root` 노드 하나(X축 -90도 회전). **메시 버퍼는 바이트 그대로**,
  노드 하나로 좌표계를 선언한다. 블렌더는 임포트 시 자기가 +90도를 다시 걸어서
  **결과적으로 엔진 좌표가 그대로 복원**된다(실측: (-2.9, 0, 0) → (-2.9, 0, 0)).
- UE 임포터는 Y-up→Z-up, m→cm(x100), RH→LH를 알아서 처리한다. 우리는 m 단위만 지키면 됨.
- front 축 주의: 엔진은 front=+X(vector.py), glTF 카메라/조명은 **-Z가 정면**.
  `gltf.look_at_quat(pos, target, up=(0,0,1))`로 배치하면 끝 (구현·검증됨).

## 조명 단위 — 실측 포함

glTF 조명은 **측광 단위(photometric)**: 해=lux, 점/스팟=candela. 여기서 삽질 포인트:

- 블렌더 임포터는 와트로 환산(대략 ÷683)한다. 실측: `sun 4 lux → 화면 암흑`,
  `12000 lux → AgX 톤매핑에서 과노출로 색 날아감`, `1800 lux + 점 800cd + 스팟 2500cd → 적정`.
- UE는 원래 photometric(디렉셔널=lux, 점/스팟=cd)이라 glTF 값이 더 직관적으로 맞는다.
- 결론: **조명 값은 현실 물리 단위 기준으로 넣되, 수천 lux대에서 시작**하는 게 뷰어들 기본 톤매퍼에 무난하다.
  (gltf.py의 add_light 기본값을 이 기준으로 잡아둠)

## 타깃별 상세

### Blender — 검증 완료
- 임포트: 코어 + 주요 KHR 확장 완전 지원. 카메라 fov, 조명 3종, 버텍스 컬러, 알파, 계층, extras(커스텀 프로퍼티)까지 전부 확인.
- 렌더: 임포트 직후 Cycles로 바로 렌더됨 (`test_gltf_blender.py`가 자동으로 수행). EEVEE도 동일하게 가능(GPU 필요).
- **주의 1**: 블렌더에서 씬을 만들어 내보낼 땐 **카메라/조명 export가 기본 꺼져 있다**.
  `export_cameras=True, export_lights=True` 플래그 필요 (실측으로 확인).
- **주의 2**: POINTS/LINES 프리미티브는 데이터는 들어오지만(루즈 버텍스) 렌더에는 안 나온다.
  (three.js는 실제로 그려줌 — 뷰어별 차이)
- 환경광/월드 배경은 glTF에 없으므로 렌더 스크립트에서 따로 깔아야 한다.

### Unreal 5 — 문서 기반 (직접 실행은 못 했음)
- UE5는 glTF 임포트가 기본 내장이다(5.2+부터 Interchange 프레임워크 경유, 이전엔 glTF Importer 플러그인).
  `.glb`를 콘텐츠 브라우저에 드래그&드롭하면 StaticMesh(또는 SkeletalMesh+AnimSequence),
  MaterialInstance, 카메라, punctual 조명으로 변환된다.
- 단위·좌표 자동 변환(m→cm, Y-up→Z-up). 우리가 신경 쓸 것 없음.
- **주의 1**: 머티리얼은 에픽이 제공하는 glTF 부모 머티리얼의 **인스턴스**로 생성된다.
  커스텀 셰이더 그래프가 가는 게 아니라 PBR 파라미터가 가는 것.
- **주의 2**: `extras`는 기본 임포트 파이프라인이 버린다. 받으려면 Interchange 파이프라인
  (파이썬/블루프린트 커스터마이즈)을 써야 한다. 게임 데이터는 glTF에 싣기보다 별도 채널(웹소켓/JSON) 권장.
- **주의 3**: POINTS/LINES 무시됨. 스켈레탈은 스킨 데이터가 있어야 한다.
- 역방향: 에픽 공식 glTF Exporter 플러그인으로 UE 씬을 glTF로 내보낼 수도 있다.
- Datasmith와 비교: Datasmith는 UE 전용 단방향 파이프라인. 개방 포맷 + 3사 호환이 목적이면 glTF가 맞다.

### three.js (mvc3d 뷰어) — 검증 완료
- 번들된 three.js **r143과 같은 버전의 GLTFLoader로 데모 씬 완전 로드 확인**
  (메시 21, Points 1, 조명 3종이 THREE.DirectionalLight/PointLight/SpotLight로, 카메라 fov 70.00, extras→userData).
- 단, GLTFLoader는 three.js 본체에 없다. r143 기준 `examples/js/loaders/GLTFLoader.js`를
  스크립트로 하나 더 얹으면 된다.
- 역할 분담 제안: **정적 씬 = .glb 한 번 로드, 동적 상태 = 웹소켓 스트림**.
  extras에 actor `id`를 실어뒀으므로(gltfview.py) 스트림 패킷과 오브젝트 매칭이 바로 된다.

### 자체 엔진 (axis3d / mvc3d) — 검증 완료
- `gltf.load(path)` → 메시가 **attrs dict** (`{'position':[...], 'normal':[...], 'uv':[...], 'index':[...]}`)로
  나온다. **vao.VAO(attrs), Geometry(attrs)에 그대로 들어가는 형태다** (양쪽 저장소가 이미 이 구조).
- 노드는 pos / quat / rot(euler xyz) / scale로 나온다 → Actor.pos/rot/scale에 바로 대입.
  (Euler.to_quat 스텁이 하던 일을 gltf.euler_to_quat/quat_to_euler가 해결)
- 블렌더가 만든 파일도 읽힌다(실측): byteStride(인터리브), matrix 노드 분해,
  uint8/16/32 인덱스, 정규화 정수 컬러 모두 처리.
- 미구현(다음 단계): 텍스처 이미지 로드(참조 인덱스만 전달), 스킨/모프 재생, sparse accessor, Draco 압축 해제.

## 스킨/애니메이션 (SKMesh·smd 계획 대비)

fullcode.py의 `SKMesh`, "obj/smd/gltf loader" 메모 기준으로:
- glTF는 스킨(JOINTS_0/WEIGHTS_0 + inverseBindMatrices), TRS 키프레임, 모프타깃을 표준 지원하고
  블렌더/UE/three 전부 재생한다. **smd로 하려던 것의 상위호환**이라 그쪽에 시간 쓸 이유가 없다.
- 현재 gltf.py는 정적 씬까지. 애니메이션 채널(writer에 samplers/channels 추가)이 다음 단계.
  포맷 지식은 다 갖춰져 있어서 증분 작업이다.

## 권장 파이프라인

```
                    ┌→ Blender  (자산 제작 / 최종 렌더)     ← 검증됨
engine  ←gltf.py→  .glb ─→ Unreal 5  (레벨 조립 / 게임)      ← 드래그&드롭
  (z-up, attrs)     └→ three.js (웹 뷰어, mvc3d)            ← 검증됨

동적 상태(pos/rot 스트림, hp 등)는 지금처럼 웹소켓으로. glb의 extras.id로 매칭.
```

- 배포 포맷은 `.glb` 단일 파일 권장(텍스처 내장 가능, 웹 전송/드래그&드롭 친화). `.gltf`(json)는 디버깅용.
- 씬 하나 = **glb(정적 배치) + 상태 스트림(동적)** 이중 구조가 MVC 구도와도 맞는다.

## 저장소에 추가된 것

**axis3d**
- `gltf.py` — writer/reader 본체 (표준 라이브러리만, numpy 입력도 받음)
- `test_gltf.py` — 라운드트립 테스트 + 데모 씬 생성 (`python3 test_gltf.py` → `gltf_out/demo_scene.glb`)
- `test_gltf_blender.py` — 진짜 블렌더로 임포트 검증 + Cycles 렌더 (`pip install bpy` 필요, 블렌더 스크립팅 탭에서도 동작)
- `gltf_out/demo_scene.glb` — 완성 샘플 (블렌더/UE/웹뷰어에 바로 던져볼 것)
- `gltf_out/blender_render.png` — 블렌더 Cycles 렌더 결과물

**mvc3d**
- `gltf.py` — 동일 모듈
- `gltfview.py` — `export_actors(actors, path)`: Actor 월드 스냅샷 → .glb
- `test_gltf.py` — Actor(pos/rot/scale/geo/mat) 라운드트립 테스트

빠른 확인:
```
cd axis3d && python3 test_gltf.py            # 데모 glb 생성 + 검증
python3 test_gltf_blender.py                  # 블렌더 임포트 + 렌더 (bpy 필요)
# gltf_out/demo_scene.glb 를 https://gltf-viewer.donmccurdy.com 에 드래그해도 됨
```

## 한계 요약 (정직 버전)

1. 언리얼은 실기 검증을 못 했다 — 스펙 검증 0 에러 + UE 기본 내장 임포터라 리스크는 낮지만, 드래그&드롭 확인 한 번 필요.
2. 텍스처/스킨/애니메이션은 포맷은 지원하지만 우리 writer/reader엔 아직 없다 (증분 추가 가능).
3. 물리/게임 상태는 표준 밖 — extras 통로는 되지만 UE 기본 파이프라인은 extras를 버린다.
4. 점/선 프리미티브 재현은 뷰어마다 다르다 (three O / 블렌더 데이터만 / UE 무시).
5. 조명 밝기는 뷰어 톤매퍼에 따라 체감이 달라서 한 번은 눈으로 맞춰야 한다 (기준값은 위 실측 참고).
