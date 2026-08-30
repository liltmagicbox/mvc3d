"""network benchmark: tcp vs udp for VR world-state streaming, through the
netlab link emulator (delay/jitter/rate/freeze/loss).

what the viewer measures is what a VR frame experiences: every ~2ms tick,
"how old is the newest state I have?" (staleness) and "how long since a new
frame last arrived?" (stall). mean latency is NOT the point -- a VR viewer
interpolates happily at 30-60ms constant delay, but a 300ms stall is a
visible world-freeze.

run:  python -m procsim.bench_net           (~90s)
      python -m procsim.bench_net wifi-bad  (one profile only)
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
from .socklink import FrameCaster, FrameViewer
from .udplink import UDPCaster, UDPViewer
from .netlab import PROFILES, TcpRelay, UdpRelay

N_UNITS = 1000
HZ = 60
DURATION = 8.0
STALL_MS = 120.0


def make_sections(n, dtype='float32'):
    pos = np.random.rand(n, 3).astype(dtype)
    quat = np.random.rand(n, 4).astype(dtype)
    return [(1, pos), (2, quat)]


def producer(conn, transport, port, sndbuf, n_units, hz, duration, dtype):
    "child process: publish state at a fixed rate, like the sim's net thread."
    if transport == 'tcp':
        caster = FrameCaster(host='127.0.0.1', port=port, sndbuf=sndbuf)
    else:
        caster = UDPCaster(host='127.0.0.1', port=port)
    while caster.n_viewers == 0:
        time.sleep(0.005)
    sections = make_sections(n_units, dtype)
    pos = sections[0][1]
    period = 1.0 / hz
    count = 0
    t0 = time.perf_counter()
    t_next = t0
    while True:
        now = time.perf_counter()
        if now - t0 >= duration:
            break
        if now < t_next:
            time.sleep(min(t_next - now, period))
            continue
        t_next += period
        count += 1
        pos[:, 0] = count * 1e-6
        caster.cast_state(count, time.perf_counter(), sections)
    conn.send({'published': count, 'secs': time.perf_counter() - t0})
    time.sleep(0.5)
    caster.close()


def sample(latest, duration):
    "VR-tick sampling: staleness of newest state + stalls in arrivals."
    stale = []
    seen = 0
    last_frame_t = None
    last_arrival = time.perf_counter()
    worst_gap = 0.0
    stalls = 0
    in_stall = False
    t_end = time.perf_counter() + duration
    while time.perf_counter() < t_end:
        f = latest()
        now = time.perf_counter()
        if f is not None:
            seen += 1
            last_frame_t = f.sim_time
            last_arrival = now
            in_stall = False
        gap = now - last_arrival
        worst_gap = max(worst_gap, gap)
        if gap * 1000 > STALL_MS and not in_stall:
            stalls += 1
            in_stall = True
        if last_frame_t is not None:
            stale.append(now - last_frame_t)
        time.sleep(0.002)
    stale = np.array(stale) * 1000
    return {'seen_s': seen / duration,
            'p50': float(np.percentile(stale, 50)) if len(stale) else float('nan'),
            'p95': float(np.percentile(stale, 95)) if len(stale) else float('nan'),
            'max': float(stale.max()) if len(stale) else float('nan'),
            'stalls': stalls,
            'worst_gap_ms': worst_gap * 1000}


def run_scenario(profile_name, variant, base_port):
    prof = PROFILES[profile_name]
    cport, rport = base_port, base_port + 1
    transport = 'udp' if variant.startswith('udp') else 'tcp'
    sndbuf = 65536 if variant == 'tcp-64k' else None
    dtype = 'float16' if variant.endswith('f16') else 'float32'

    ctx = mp.get_context('spawn')
    parent, child = ctx.Pipe()
    proc = ctx.Process(target=producer,
                       args=(child, transport, cport, sndbuf, N_UNITS, HZ,
                             DURATION + 1.5, dtype),
                       daemon=True)
    proc.start()
    child.close()
    time.sleep(0.3)                      # caster bound

    if transport == 'tcp':
        relay = TcpRelay(rport, ('127.0.0.1', cport), prof)
        viewer = FrameViewer(host='127.0.0.1', port=rport)
    else:
        relay = UdpRelay(rport, ('127.0.0.1', cport), prof)
        viewer = UDPViewer('127.0.0.1', rport)

    # wait for first frame, then measure
    t_give_up = time.time() + 5
    while viewer.box.peek() is None and time.time() < t_give_up:
        time.sleep(0.005)
    cons = sample(viewer.latest, DURATION)
    stats = parent.recv() if parent.poll(4) else {'published': 0, 'secs': 1}

    viewer.close()
    relay.close()
    proc.join(3)
    if proc.is_alive():
        proc.terminate()

    pub_s = stats['published'] / stats['secs']
    delivered = f"{cons['seen_s']:5.1f}/s"
    print(f"  {variant:8s} | pub {pub_s:5.1f}/s  got {delivered} | "
          f"stale p50 {cons['p50']:6.1f}  p95 {cons['p95']:7.1f}  "
          f"max {cons['max']:7.1f} ms | stalls>120ms: {cons['stalls']:2d} "
          f"(worst {cons['worst_gap_ms']:6.0f} ms)")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    blob = fr.pack_state(1, 0.0, make_sections(N_UNITS))
    print(f'frame {len(blob):,}B x {HZ}Hz = '
          f'{len(blob) * HZ * 8 / 1e6:.1f} Mbit/s, {DURATION:.0f}s per run, '
          f'viewer ticks every 2ms\n')
    port = 31000
    for name, prof in PROFILES.items():
        if only and name != only:
            continue
        print(f'[{name}]  {prof!r}')
        for variant in ('tcp', 'tcp-64k', 'udp', 'udp-f16'):
            if name == 'lan' and variant in ('tcp-64k', 'udp-f16'):
                continue
            run_scenario(name, variant, port)
            port += 10
        print()


if __name__ == '__main__':
    main()
