"""format benchmark: json vs binary header+raw for per-frame draw state.

run:  python -m procsim.bench_format
"""
import sys
import os
import json
import time

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'procsim'

import numpy as np

from . import frame as fr

REPS = 200


def timeit(fn, reps=REPS):
    best = float('inf')
    for _ in range(3):
        t = time.perf_counter()
        for _ in range(reps):
            fn()
        best = min(best, (time.perf_counter() - t) / reps)
    return best * 1000  # ms


def bench(n):
    pos = np.random.rand(n, 3).astype('float32')
    quat = np.random.rand(n, 4).astype('float32')
    sections = [(1, pos), (2, quat)]

    # --- binary
    blob = fr.pack_state(1, 0.0, sections)
    t_pack = timeit(lambda: fr.pack_state(1, 0.0, sections))
    t_unpack = timeit(lambda: fr.unpack(blob))

    # --- binary, in-place into a reused buffer (the shm path)
    buf = bytearray(len(blob) + 64)
    t_pack_into = timeit(lambda: fr.pack_state_into(buf, 1, 0.0, sections))

    # --- json (what 20_socket_world did)
    def jpack():
        return json.dumps({'pos': pos.tolist(), 'quat': quat.tolist()}).encode()
    jblob = jpack()
    t_jpack = timeit(jpack, reps=max(REPS // 10, 5))
    t_junpack = timeit(lambda: json.loads(jblob), reps=max(REPS // 10, 5))

    print(f'N={n:6d} | binary {len(blob):9,}B  json {len(jblob):9,}B '
          f'(x{len(jblob)/len(blob):.1f})')
    print(f'         | pack   binary {t_pack:7.3f}ms  into-buf {t_pack_into:7.3f}ms '
          f' json {t_jpack:8.3f}ms  (x{t_jpack/t_pack:.0f})')
    print(f'         | unpack binary {t_unpack:7.3f}ms '
          f'                    json {t_junpack:8.3f}ms  (x{t_junpack/t_unpack:.0f})')


def main():
    print('per-frame payload: N units x (pos f32x3 + quat f32x4)\n')
    for n in (100, 1000, 10000):
        bench(n)
        print()


if __name__ == '__main__':
    main()
