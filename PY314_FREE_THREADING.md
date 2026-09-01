# Python 3.14 free-threading (GIL 해제) 조사 요약

> 2026-09-01 Claude Code 원격 세션에서 실측·조사한 내용. 다음 세션에서 mvc3d/axis3d의
> 3.14t 마이그레이션을 진행할 때 이 문서를 출발점으로 삼을 것.
>
> 실측 환경: 4코어 Linux 컨테이너, CPython **3.14.0rc2 free-threaded** (`uv python install 3.14t`),
> 라이브러리는 당일 PyPI 최신 휠 기준. (실제 적용 시엔 3.14 최신 패치 버전 사용 권장)

## 핵심 결론

1. **순수 파이썬 `threading` 코드는 free-threaded 빌드에서 진짜 멀티코어 병렬 실행된다** (아래 실측).
2. 단, 기본 3.14 빌드는 여전히 GIL 있음. **별도 빌드 `python3.14t`가 필요**
   (`uv python install 3.14t` / python.org 인스톨러의 free-threaded 옵션 / Windows `py -3.14t`).
3. 3.13에서 "실험적"이던 free-threading이 3.14부터 **PEP 779로 공식 지원** 단계.
   GIL-off가 기본값이 되는 것은 아직 미래 단계.
4. 우리 스택 기준: numpy·glfw·PyOpenGL(순정)·pyglet·websockets·pillow·matplotlib·flask **OK**.
   **PyGLM은 import 시 GIL 재활성화**, **opencv-python은 3.14t에 설치 자체 불가**.

## 실측 벤치마크 (4코어, 4스레드)

| 워크로드 | 3.14 (GIL 빌드) | 3.14t (free-threaded) |
|---|---|---|
| 순수 파이썬 재귀(fib) | 1.04x (병렬 안 됨) | **3.54x** |
| 4x4 소형 numpy 행렬연산 (pymatrix/vec 패턴) | 0.98x | **2.96x** |

큰 배열 연산은 GIL 빌드에서도 numpy가 GIL을 풀어 어느 정도 병렬이 되지만,
**소형 연산 + 파이썬 루프** 조합(우리 코드의 주 패턴)은 3.14t에서만 스케일한다.

## C 확장 동작 규칙 (중요)

- free-threaded 빌드는 ABI가 달라 **`cp314t` 태그 전용 휠**이 필요. 일반 `cp314`/`abi3` 휠은 설치 불가.
- 설치가 되어도 모듈이 free-threading 지원 선언(`Py_mod_gil`)을 안 했으면
  **import하는 순간 인터프리터가 GIL을 자동 재활성화**한다 (RuntimeWarning 출력).
  → 미지원 라이브러리 하나가 프로세스 전체의 병렬성을 무효화함.
- 런타임 확인: `sys._is_gil_enabled()` → `False`여야 정상.
- 강제 오버라이드: `PYTHON_GIL=0` (미선언 확장도 GIL-off로 강행, 스레드 안전성은 자기 책임).
- 권장: 앱 시작부에 `assert not sys._is_gil_enabled()` 한 줄 추가 (조용한 GIL 복귀 감지).

## 라이브러리별 실측 결과 (2026-09-01, PyPI 기준)

| 라이브러리 | 3.14t 설치 | import 후 GIL | 비고 |
|---|---|---|---|
| numpy 2.5.2 | ✅ cp314t 네이티브 | off 유지 | 스레드 스케일 실측 확인 |
| glfw 2.10.2 | ✅ | off 유지 | ctypes 래퍼라 C 확장 자체가 없음 |
| PyOpenGL 3.1.10 | ✅ | off 유지 | 순수 파이썬 |
| PyOpenGL-accelerate | ✅ 휠 있음 | ⚠️ **GIL 재활성화** | 3.14t에서는 설치하지 말 것 |
| pyglet 2.1.16 | ✅ | off 유지 | |
| websockets 17.1 | ✅ | off 유지 | C speedups 확장 포함 OK |
| pillow 12.3.0 | ✅ | off 유지 | |
| matplotlib 3.11.1 | ✅ | off 유지 | |
| flask 3.1.3 | ✅ | off 유지 | |
| PyGLM (glm) | ✅ 휠 있음 | ⚠️ **GIL 재활성화** | `PYTHON_GIL=0` 강제 시 기본 동작은 확인됨(보증 없음) |
| opencv-python | ❌ **cp314t 휠 없음** | — | 일반 3.14에는 5.0.0.93(abi3) 정상 설치 |

## OpenCV 상황 (유일한 진짜 구멍)

- free-threaded 휠 미출시. 추적 이슈: <https://github.com/opencv/opencv-python/issues/1146>
  (소스 빌드를 가능하게 하는 PR #1051 존재, 공식 휠은 아직 없음)
- OpenCV는 abi3 휠 하나로 전 버전을 커버하는 전략이라, free-threaded용 안정 ABI를 정의하는
  **PEP 803 (abi3t, 3.15 목표)** 이후에 풀릴 가능성이 큼: <https://peps.python.org/pep-0803/>
- 당장 cv2가 필요하면: cv2만 일반(GIL) 빌드의 **별도 프로세스로 분리**해 IPC로 통신.

## 주의점

- **GIL 해제 ≠ 락 불필요.** `x += 1`, check-then-act 같은 복합 연산 레이스는 그대로이고,
  GIL이 우연히 가려주던 레이스가 표면화될 수 있음. 단 list/dict 등 내부 자료구조는
  per-object lock으로 보호되어 메모리가 깨지진 않음. `queue.Queue` 기반 설계는 그대로 안전.
- **GLFW/OpenGL 자체의 스레드 규칙은 GIL과 무관하게 유지됨**: 윈도 생성·이벤트 폴링은
  메인 스레드, GL 컨텍스트는 한 번에 한 스레드만 current. → 렌더 스레드는 1개 유지,
  병렬화 이득은 시뮬레이션/유닛 로직·행렬 계산·네트워킹에서 챙길 것.
- 비용: 싱글스레드 성능 약 5~10% 저하 + 메모리 사용 증가 (3.13의 ~40% 페널티에서 크게 개선).

## mvc3d / axis3d 마이그레이션 체크리스트

두 리포 모두 `threading` 사용처 20+ (mvc3d: threadqueue 패턴, axis3d: 렌더러/유닛 스레드)
→ free-threading 수혜 대상.

1. [ ] `PyOpenGL-accelerate` 제거 (또는 미설치 유지)
2. [ ] `PyGLM(glm)` 의존 제거/대체 — 순수 numpy(pymatrix.py 방식)로 대체하거나 `PYTHON_GIL=0` 감수
3. [ ] 시작부에 `assert not sys._is_gil_enabled()` 추가
4. [ ] 공유 상태에 쓰는 지점 락 점검 (`+=`, dict/list 복합 연산)
5. [ ] cv2 도입 시 별도 프로세스 분리 설계 (3.14t 휠 나올 때까지)

## 재현 명령어

```bash
uv python install 3.14t
uv venv --python 3.14t .venv-ft
uv pip install --python .venv-ft/bin/python --only-binary :all: \
    numpy glfw PyOpenGL pyglet websockets pillow
.venv-ft/bin/python -c "import sys; print(sys._is_gil_enabled())"   # False 여야 정상
```
