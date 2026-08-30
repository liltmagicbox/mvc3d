"""transport benchmark: mp.Pipe vs tcp socket vs shared memory.

producer process publishes STATE frames (N units pos+quat, ~28KB at N=1000)
as fast as it can for a few seconds; consumer polls "give me the newest"
every ~0.5ms. what we care about for a renderer:

  pub/s     how hard the sim side can push (publish cost)
  seen/s    distinct frames the viewer actually observed
  age       how stale the newest frame is at read time (latency)

run:  python -m procsim.bench_transport
"""
import sys
import os
import time
import multiprocessing as mp

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'procsim'

import numpy as np

from . import frame as fr
from .simproc import SimProcess
from .socklink import FrameCaster, FrameViewer

N_UNITS = 1000
DURATION = 3.0


def make_sections(n):
    pos = np.random.rand(n, 3).astype('float32')
    quat = np.random.rand(n, 4).astype('float32')
    return [(1, pos), (2, quat)]


def sample(get_new, duration):
    "consumer loop: poll newest every ~0.5ms."
    unique = 0
    age_sum = 0.0
    t_end = time.perf_counter() + duration
    while time.perf_counter() < t_end:
        f = get_new()
        if f is not None:
            unique += 1
            age_sum += time.perf_counter() - f.sim_time
        time.sleep(0.0005)
    return {'seen_s': unique / duration,
            'age_ms': (age_sum / unique * 1000) if unique else float('nan')}


def report(name, pub_s, cons, note=''):
    print(f'{name:22s} pub {pub_s:9.0f}/s   seen {cons["seen_s"]:7.0f}/s   '
          f'age {cons["age_ms"]:7.3f} ms   {note}')


# ---------------- shm ----------------
def shm_producer(ctx, n_units, duration):
    sections = make_sections(n_units)
    pos = sections[0][1]
    t0 = time.perf_counter()
    count = 0
    while time.perf_counter() - t0 < duration and not ctx.stopping:
        pos[:, 0] = count * 1e-6      # mutate so frames differ
        ctx.publish(time.perf_counter(), sections)
        count += 1
    ctx.emit({'pub': count, 'secs': time.perf_counter() - t0})


def bench_shm():
    host = SimProcess(shm_producer, args=(N_UNITS, DURATION + 0.5), slot_cap=1 << 20)
    while host.read_latest() is None:
        time.sleep(0.002)
    cons = sample(host.read_new, DURATION)
    stats = None
    t_wait = time.time() + 3
    while stats is None and time.time() < t_wait:
        for ev in host.events():
            stats = ev
        time.sleep(0.01)
    host.stop()
    pub_s = stats['pub'] / stats['secs'] if stats else float('nan')
    report('shm 3-slot (lock)', pub_s, cons, 'zero-queue, latest-wins')


# ---------------- pipe ----------------
def pipe_producer(conn, n_units, duration):
    sections = make_sections(n_units)
    pos = sections[0][1]
    t0 = time.perf_counter()
    count = 0
    while time.perf_counter() - t0 < duration:
        pos[:, 0] = count * 1e-6
        blob = fr.pack_state(count + 1, time.perf_counter(), sections)
        conn.send_bytes(blob)          # blocks when pipe is full -> throttled
        count += 1
    conn.send_bytes(b'DONE')
    conn.close()


def bench_pipe():
    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe()
    proc = ctx.Process(target=pipe_producer, args=(child, N_UNITS, DURATION + 0.5),
                       daemon=True)
    proc.start()
    child.close()
    while not parent.poll(0.01):
        pass

    state = {'done': False, 'drained': 0}

    def get_new():
        "drain everything queued, keep only the newest (renderer semantics)."
        blob = None
        try:
            while parent.poll():
                b = parent.recv_bytes()
                if b == b'DONE':
                    state['done'] = True
                    break
                blob = b
                state['drained'] += 1
        except (EOFError, OSError):
            state['done'] = True
        return fr.unpack(blob) if blob is not None else None

    cons = sample(get_new, DURATION)
    pub_s = state['drained'] / DURATION   # producer is throttled by the drain
    proc.terminate(); proc.join(1)
    report('mp.Pipe (pickle-free)', pub_s, cons,
           f'drained {state["drained"]} total, kept newest')


# ---------------- tcp ----------------
def sock_producer(conn, n_units, duration):
    caster = FrameCaster(port=0)
    conn.send(caster.addr[1])
    while caster.n_viewers == 0:
        time.sleep(0.002)
    sections = make_sections(n_units)
    pos = sections[0][1]
    t0 = time.perf_counter()
    count = 0
    while time.perf_counter() - t0 < duration:
        pos[:, 0] = count * 1e-6
        caster.cast_state(count + 1, time.perf_counter(), sections)
        count += 1
    conn.send({'pub': count, 'secs': time.perf_counter() - t0})
    time.sleep(0.5)
    caster.close()


def bench_tcp():
    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe()
    proc = ctx.Process(target=sock_producer, args=(child, N_UNITS, DURATION + 0.5),
                       daemon=True)
    proc.start()
    child.close()
    port = parent.recv()
    viewer = FrameViewer(port=port)
    while viewer.box.peek() is None:
        time.sleep(0.002)
    cons = sample(viewer.latest, DURATION)
    stats = parent.recv() if parent.poll(3) else None
    viewer.close()
    proc.join(2)
    if proc.is_alive():
        proc.terminate()
    pub_s = stats['pub'] / stats['secs'] if stats else float('nan')
    report('tcp localhost', pub_s, cons, 'mailbox latest-wins per viewer')


def main():
    blob = fr.pack_state(1, 0.0, make_sections(N_UNITS))
    print(f'frame = {len(blob):,}B (N={N_UNITS} units, pos+quat f32), '
          f'{DURATION}s per transport, poll every 0.5ms\n')
    bench_shm()
    bench_pipe()
    bench_tcp()


if __name__ == '__main__':
    main()
