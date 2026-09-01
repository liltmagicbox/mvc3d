# 01. 시뮬 프로세스 분리 (GIL 회피)

**결론: 시뮬은 별도 프로세스. 상태는 shm 3-슬롯 latest-wins 채널로 내려받고,
입력/제어는 Pipe로 올려보낸다.** 스레드는 GIL을 나눠 쓰므로 해법이 아니다.

근거 (`python -m procsim.demo_local`, 시뮬 ~2ms py/틱 + 렌더 ~2ms py/프레임):

| | THREAD (GIL 공유) | PROCESS (shm) |
|---|---|---|
| 렌더 fps (목표 60) | 49.7 | **59.7** |
| 최악 프레임 간격 | 44.8 ms | **17.0 ms** |
| 시뮬 틱 레이트 | 473/s | **542/s** |
| 상태 나이 @읽기 | 4.02 ms | **0.99 ms** |

전송비용이 사실상 0(나이 63µs, §06)이라 분리의 이득이 그대로 남는다.

## 가이드

시뮬 함수는 **모듈 최상위**에 두고(spawn이 임포트로 찾는다), `ctx`만 쓴다:

```python
# mysim.py (모듈 최상위!)
def my_sim(ctx, n_units):
    world = make_world(n_units)
    while not ctx.stopping:
        for i in ctx.inputs():          # Pipe에서 입력 드레인
            world.input(i)
        world.update(dt)
        ctx.publish(time.perf_counter(),
                    [(KIND_UNITS, world.pos_f32)])   # (kind, ndarray) 목록
        # 드문 사건은 ctx.emit({'type': 'spawn', ...})
```

부모(뷰) 쪽:

```python
from procsim import SimProcess

if __name__ == '__main__':              # Windows spawn 필수 가드
    host = SimProcess(my_sim, args=(1000,), slot_cap=1 << 20)
    while running:                      # 렌더 루프
        f = host.read_new()             # 새 프레임 없으면 None, 블록 없음
        if f:
            upload(f.sections)
        host.send(('key', 'W', 1.0))    # 입력 (콜드패스, pickle 허용)
        for ev in host.events():        # 시뮬발 사건
            ...
    host.stop()
```

## 내부 (shmlink)

```
[Ctrl 32B: latest_slot ...][slot0][slot1][slot2]
slot = [seq u32][nbytes u32][pad][data slot_cap]
쓰기: seq 홀수 → 데이터 → seq 짝수 → latest_slot 갱신
읽기: seq 확인 → 복사 → seq 재확인 (다르면 재시도)
```

- 큐가 아니다: 렌더가 느려도 시뮬 안 막히고, 시뮬이 빨라도 지연 안 쌓인다.
- SimProcess가 mp.Lock을 양쪽에 물려줘 torn read 원천 차단(ARM/rpi4 포함).
- 이름으로 `ShmChannel.attach()`한 남남 프로세스는 seqlock만으로 동작.

## 함정

- 메인 스크립트에 `if __name__ == '__main__':` 없으면 Windows에서 무한 재귀.
- `slot_cap`은 생성 시 고정 — 최대 유닛 기준으로 잡을 것. 초과 시 ValueError.
- 자식이 attach할 때는 `child_of_creator=True`(SimProcess가 알아서) —
  안 그러면 부모와 공유하는 resource_tracker 등록이 꼬여 unlink 때 KeyError.
- Windows엔 unlink 개념이 없고 마지막 핸들이 닫히면 해제 — 종료는 stop 이벤트로.
