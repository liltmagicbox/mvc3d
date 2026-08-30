"""demo: same toy sim as a thread (GIL shared) vs as a process (GIL avoided).

the toy sim burns python-loop cpu per tick (like per-actor logic does) and
publishes N unit positions+quats as one STATE frame. the "renderer" here is a
60Hz loop that reads the newest frame and measures how well it holds 60fps.

run:  python -m procsim.demo_local        (from mvc3d/)
"""
import sys
import os
import time
import threading

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'procsim'

import numpy as np

from .simproc import SimProcess
from .socklink import Mailbox
from . import frame as fr

N_UNITS = 1000
SIM_MS = 2.0           # python-loop cost per sim tick (per-actor logic stand-in)
RENDER_MS = 2.0        # python-loop cost per render frame (draw submission stand-in)
DURATION = 3.0
KIND_UNITS = fr.meshid_to_kind('00010001')


def calibrate(ms):
    "-> loop iterations that burn ~ms of pure-python time on this machine."
    n = 0
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 0.05:
        for _ in range(10_000):
            pass
        n += 10_000
    iters_per_ms = n / ((time.perf_counter() - t0) * 1000)
    return max(int(iters_per_ms * ms), 1)


def toy_sim(ctx, n_units=N_UNITS, spin=100_000):
    "runs in the sim process. ~free-running tick."
    rng = np.random.default_rng(7)
    phase = rng.uniform(0, 6.28, n_units).astype('float32')
    radius = rng.uniform(1, 30, n_units).astype('float32')
    pos = np.zeros((n_units, 3), dtype='float32')
    quat = np.zeros((n_units, 4), dtype='float32')
    quat[:, 3] = 1.0

    t0 = time.perf_counter()
    ticks = 0
    while not ctx.stopping:
        for i in ctx.inputs():
            pass                      # demo: ignore, but drain
        t = time.perf_counter() - t0
        # "physics"
        for _ in range(spin):         # pure-python cost, holds THIS process's GIL
            pass
        pos[:, 0] = np.cos(phase + t) * radius
        pos[:, 2] = np.sin(phase + t) * radius
        quat[:, 1] = np.sin((phase + t) * 0.5)
        quat[:, 3] = np.cos((phase + t) * 0.5)

        ctx.publish(time.perf_counter(), [(KIND_UNITS, pos), (KIND_UNITS + 1, quat)])
        ticks += 1
    ctx.emit({'ticks': ticks, 'secs': time.perf_counter() - t0})


def render_loop(read_new, duration=DURATION, target_fps=60, spin=0):
    "fake renderer: hold target fps, burn python cpu like a real frame, consume newest."
    period = 1.0 / target_fps
    frames = ages = 0
    seen = set()
    worst_gap = 0.0
    t_end = time.perf_counter() + duration
    t_prev = time.perf_counter()
    age_sum = 0.0
    while time.perf_counter() < t_end:
        t_frame = time.perf_counter()
        worst_gap = max(worst_gap, t_frame - t_prev)
        t_prev = t_frame

        for _ in range(spin):          # draw-list building, uniforms, event pump..
            pass
        f = read_new()
        if f is not None:
            seen.add(f.frame_id)
            age_sum += time.perf_counter() - f.sim_time
            ages += 1
            # pretend to upload: touch the arrays like glBufferSubData would
            for _kind, arr in f.sections:
                _ = arr.sum()
        frames += 1

        rest = period - (time.perf_counter() - t_frame)
        if rest > 0:
            time.sleep(rest)
    return {'loop_fps': frames / duration,
            'unique_frames': len(seen),
            'mean_age_ms': (age_sum / ages * 1000) if ages else float('nan'),
            'worst_gap_ms': worst_gap * 1000}


# ---------------- thread mode: same sim, same process, mailbox instead of shm
class ThreadCtx:
    def __init__(self, box, stop_event):
        self.box = box
        self._stop = stop_event
        self.stats = None
        self._id = 0
    @property
    def stopping(self):
        return self._stop.is_set()
    def publish(self, sim_time, sections):
        self._id += 1
        self.box.put(fr.pack_state(self._id, sim_time, sections))
        return self._id
    def inputs(self):
        return iter(())
    def emit(self, obj):
        self.stats = obj


def run_thread_mode(sim_spin, render_spin):
    box = Mailbox()
    stop = threading.Event()
    ctx = ThreadCtx(box, stop)
    th = threading.Thread(target=toy_sim, args=(ctx, N_UNITS, sim_spin), daemon=True)
    th.start()

    def read_new():
        data = box.take()
        return fr.unpack(data) if data is not None else None

    stats = render_loop(read_new, spin=render_spin)
    stop.set()
    th.join(2)
    return stats, ctx.stats


def run_process_mode(sim_spin, render_spin):
    host = SimProcess(toy_sim, args=(N_UNITS, sim_spin), slot_cap=1 << 20)
    while host.read_latest() is None:      # wait first frame
        time.sleep(0.005)
    stats = render_loop(host.read_new, spin=render_spin)
    sim_stats = None
    host._stop.set()
    t_wait = time.time() + 2
    while sim_stats is None and time.time() < t_wait:
        for ev in host.events():
            sim_stats = ev
        time.sleep(0.01)
    host.stop()
    return stats, sim_stats


def report(title, stats, sim_stats):
    tick_rate = sim_stats['ticks'] / sim_stats['secs'] if sim_stats else float('nan')
    print(f'--- {title}')
    print(f'  sim tick rate   : {tick_rate:8.1f} /s')
    print(f'  render loop fps : {stats["loop_fps"]:8.1f}  (target 60)')
    print(f'  worst frame gap : {stats["worst_gap_ms"]:8.2f} ms')
    print(f'  frames consumed : {stats["unique_frames"]:5d} unique')
    print(f'  state age @read : {stats["mean_age_ms"]:8.2f} ms')


def main():
    sim_spin = calibrate(SIM_MS)
    render_spin = calibrate(RENDER_MS)
    print(f'N={N_UNITS} units (pos f32x3 + quat f32x4), '
          f'sim ~{SIM_MS}ms py/tick, render ~{RENDER_MS}ms py/frame, '
          f'{DURATION}s each mode\n')
    stats, sim = run_thread_mode(sim_spin, render_spin)
    report('THREAD mode (shared GIL)', stats, sim)
    stats, sim = run_process_mode(sim_spin, render_spin)
    report('PROCESS mode (own GIL, shm channel)', stats, sim)


if __name__ == '__main__':
    main()
