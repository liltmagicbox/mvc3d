"""udp transport for STATE frames: the network path that matches latest-wins.

why udp here: tcp is a reliable ORDERED byte stream -- one late/lost packet
holds back every newer frame behind it (head-of-line blocking), which is the
exact opposite of "only the newest state matters". with udp each frame stands
alone: lost -> skipped, superseded -> discarded. no retransmit, no ack.

a frame (28KB at N=1000) exceeds the ~1500B MTU, and IP fragmentation is a
trap (any lost fragment kills the whole datagram, some middleboxes drop
fragments outright), so we chunk at the app layer and reassemble by offset.
1204B datagrams stay under every common path MTU (ethernet 1500, pppoe 1492,
vpn/tunnel overhead) -- same budget QUIC picked (~1200).

chunk loss compounds per frame: survival = (1-p)^n_chunks. the fix is one
XOR parity chunk per frame (+1/n overhead): any SINGLE lost chunk is
reconstructed, lifting survival to (1-p)^n + n*p*(1-p)^n. at 2% loss and 12
chunks that is 78% -> 97%.

    ChunkHeader 20B, little-endian
        0  magic     4s  'MVSU'
        4  frame_id  u32
        8  offset    u32  payload position in the frame (parity: 0)
        12 total_len u32  full frame size
        16 n_chunks  u16  DATA chunk count (parity not included)
        18 flags     u16  1 = parity chunk
    payload <= CHUNK_PAYLOAD (data), == CHUNK_PAYLOAD (parity, zero-padded xor)

viewers register by sending PING (also NAT/liveness keepalive, ~1/s); caster
answers PONG with both timestamps, giving the viewer RTT and the clock offset
between machines -- required to compute state age across hosts, since
sim_time in the frame header is the CASTER's perf_counter:

    age_on_viewer = now_viewer - (frame.sim_time - clock_offset)
    PING 12B: 'MVSP' + f64 t_viewer
    PONG 20B: 'MVSQ' + f64 t_viewer(echo) + f64 t_caster
    offset = t_caster - (t_send + t_recv)/2, kept from the min-RTT sample
"""
import math
import socket
import struct
import threading
import time

import numpy as np

from . import frame as fr
from .socklink import Mailbox

CHUNK = struct.Struct('<4sIIIHH')      # 20B
CHUNK_MAGIC = b'MVSU'
CHUNK_PAYLOAD = 1184                   # + 20B header = 1204B datagram
FLAG_PARITY = 1
PING = b'MVSP'
PONG = b'MVSQ'
PING_S = struct.Struct('<4sd')
PONG_S = struct.Struct('<4sdd')
VIEWER_TTL = 5.0


def split_frame(blob, frame_id, fec=True, chunk_payload=CHUNK_PAYLOAD):
    "-> list of datagrams for one frame (+ optional parity datagram)."
    total = len(blob)
    n = max(1, math.ceil(total / chunk_payload))
    fid = frame_id & 0xFFFFFFFF
    grams = []
    for i in range(n):
        off = i * chunk_payload
        head = CHUNK.pack(CHUNK_MAGIC, fid, off, total, n, 0)
        grams.append(head + blob[off:off + chunk_payload])
    if fec and n >= 2:
        parity = np.zeros(chunk_payload, dtype=np.uint8)
        view = np.frombuffer(blob, dtype=np.uint8)
        for i in range(n):
            part = view[i * chunk_payload:(i + 1) * chunk_payload]
            parity[:len(part)] ^= part
        head = CHUNK.pack(CHUNK_MAGIC, fid, 0, total, n, FLAG_PARITY)
        grams.append(head + parity.tobytes())
    return grams


class UDPCaster:
    "sim side. cast_state() sprays chunks to every viewer that pinged recently."

    def __init__(self, host='0.0.0.0', port=30030, fec=True):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.addr = self.sock.getsockname()
        self.fec = fec
        self.viewers = {}              # addr -> last_seen
        self._lock = threading.Lock()
        self._closing = False
        threading.Thread(target=self._hello_forever, daemon=True).start()

    def _hello_forever(self):
        "any datagram registers the sender; PING additionally gets a PONG."
        while not self._closing:
            try:
                data, addr = self.sock.recvfrom(2048)
            except OSError:
                break
            with self._lock:
                self.viewers[addr] = time.monotonic()
            if data[:4] == PING and len(data) >= PING_S.size:
                _m, t_viewer = PING_S.unpack_from(data, 0)
                try:
                    self.sock.sendto(PONG_S.pack(PONG, t_viewer, time.perf_counter()), addr)
                except OSError:
                    pass

    def cast_state(self, frame_id, sim_time, sections):
        self.cast_bytes(fr.pack_state(frame_id, sim_time, sections), frame_id)

    def cast_bytes(self, blob, frame_id):
        now = time.monotonic()
        with self._lock:
            self.viewers = {a: t for a, t in self.viewers.items()
                            if now - t < VIEWER_TTL}
            targets = list(self.viewers)
        if not targets:
            return
        for gram in split_frame(blob, frame_id, fec=self.fec):
            for addr in targets:
                try:
                    self.sock.sendto(gram, addr)
                except OSError:
                    pass               # fire and forget

    @property
    def n_viewers(self):
        now = time.monotonic()
        with self._lock:
            return sum(1 for t in self.viewers.values() if now - t < VIEWER_TTL)

    def close(self):
        self._closing = True
        try:
            self.sock.close()
        except OSError:
            pass


class UDPViewer:
    "viewer side: PING keepalive + reassemble chunks, keep newest complete frame."

    MAX_PENDING = 4                    # in-flight partial frames to remember

    def __init__(self, host, port, ping_interval=1.0):
        self.caster = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(min(ping_interval, 0.5))
        self.ping_interval = ping_interval
        self.box = Mailbox()
        self.last_id = None
        self.newest_done = 0
        self.alive = True
        self.clock_offset = None       # caster_perf_counter - viewer_perf_counter
        self.rtt_ms = None             # from the sample that set clock_offset
        self._best_rtt = float('inf')
        self.stat_datagrams = 0
        self.stat_frames = 0
        self.stat_fec_recovered = 0
        self._ping()
        threading.Thread(target=self._recv_forever, daemon=True).start()

    def _ping(self):
        try:
            self.sock.sendto(PING_S.pack(PING, time.perf_counter()), self.caster)
        except OSError:
            pass

    def _on_pong(self, gram):
        t_recv = time.perf_counter()
        _m, t_send, t_caster = PONG_S.unpack_from(gram, 0)
        rtt = t_recv - t_send
        if rtt < self._best_rtt:       # min-RTT sample = least queue noise
            self._best_rtt = rtt
            self.rtt_ms = rtt * 1000
            self.clock_offset = t_caster - (t_send + t_recv) / 2

    def age_of(self, frame, now=None):
        "state age in seconds, correct across machines once a PONG arrived."
        now = time.perf_counter() if now is None else now
        off = self.clock_offset or 0.0
        return now - (frame.sim_time - off) if off else now - frame.sim_time

    def _recv_forever(self):
        pending = {}       # frame_id -> [got, total, buf, {off: len}, parity|None, n]
        last_ping = time.monotonic()
        while self.alive:
            now = time.monotonic()
            if now - last_ping >= self.ping_interval:
                self._ping()
                last_ping = now
            try:
                gram, _addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            if gram[:4] == PONG and len(gram) >= PONG_S.size:
                self._on_pong(gram)
                continue
            if len(gram) < CHUNK.size:
                continue
            magic, fid, off, total, n, flags = CHUNK.unpack_from(gram, 0)
            if magic != CHUNK_MAGIC or fid <= self.newest_done:
                continue               # not ours / superseded -> drop
            self.stat_datagrams += 1

            slot = pending.get(fid)
            if slot is None:
                slot = pending[fid] = [0, total, bytearray(total), {}, None, n]
                if len(pending) > self.MAX_PENDING:     # forget the oldest partial
                    pending.pop(min(pending))
            payload = gram[CHUNK.size:]

            if flags & FLAG_PARITY:
                slot[4] = payload
            elif off not in slot[3]:
                slot[2][off:off + len(payload)] = payload
                slot[3][off] = len(payload)
                slot[0] += len(payload)

            done = slot[0] >= total or self._try_fec(slot)
            if done:
                self.newest_done = fid
                self.stat_frames += 1
                self.box.put(bytes(slot[2]))
                for k in [k for k in pending if k <= fid]:
                    pending.pop(k)

    def _try_fec(self, slot):
        "exactly one data chunk missing + parity present -> rebuild it."
        got, total, buf, seen, parity, n = slot
        if parity is None or len(seen) != n - 1:
            return False
        missing = next(o for o in (i * CHUNK_PAYLOAD for i in range(n))
                       if o not in seen)
        recon = np.frombuffer(parity, dtype=np.uint8).copy()
        bufv = np.frombuffer(buf, dtype=np.uint8)
        for off, ln in seen.items():
            recon[:ln] ^= bufv[off:off + ln]
        miss_len = min(CHUNK_PAYLOAD, total - missing)
        buf[missing:missing + miss_len] = recon[:miss_len].tobytes()
        slot[0] = got + miss_len
        self.stat_fec_recovered += 1
        return slot[0] >= total

    def latest(self, timeout=None):
        data = self.box.take(timeout)
        if data is None:
            return None
        f = fr.unpack(data)
        self.last_id = f.frame_id
        return f

    def close(self):
        self.alive = False
        try:
            self.sock.close()
        except OSError:
            pass
