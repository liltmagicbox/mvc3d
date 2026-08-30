"""udp transport for STATE frames: the network path that matches latest-wins.

why udp here: tcp is a reliable ORDERED byte stream -- one late/lost packet
holds back every newer frame behind it (head-of-line blocking), which is the
exact opposite of "only the newest state matters". with udp each frame stands
alone: lost -> skipped, superseded -> discarded. VR world-state streaming is
the textbook case.

a frame (28KB at N=1000) exceeds the ~1500B MTU, and IP fragmentation is a
trap (any lost fragment kills the whole datagram), so we chunk at the app
layer and reassemble by offset:

    ChunkHeader 20B, little-endian
        0  magic     4s  'MVSU'
        4  frame_id  u32
        8  offset    u32  where this chunk's payload sits in the frame
        12 total_len u32  full frame size
        16 n_chunks  u16
        18 (pad)     u16
    payload <= CHUNK_PAYLOAD (1184B -> datagram 1204B, safe under any MTU)

reassembly is latest-wins: a frame completes -> everything older is dropped,
incomplete stays pending until superseded. no retransmit, no ack.

viewers register by sending any datagram (HELLO) to the caster and keep
sending one every second (doubles as NAT/liveness keepalive).
"""
import math
import socket
import struct
import threading
import time

from . import frame as fr
from .socklink import Mailbox

CHUNK = struct.Struct('<4sIIIH2x')     # 20B
CHUNK_MAGIC = b'MVSU'
CHUNK_PAYLOAD = 1184                   # + 20B header = 1204B datagram
HELLO = b'MVS?'
VIEWER_TTL = 5.0


def split_frame(blob, frame_id, chunk_payload=CHUNK_PAYLOAD):
    "-> list of datagrams for one frame."
    total = len(blob)
    n = max(1, math.ceil(total / chunk_payload))
    grams = []
    for i in range(n):
        off = i * chunk_payload
        head = CHUNK.pack(CHUNK_MAGIC, frame_id & 0xFFFFFFFF, off, total, n)
        grams.append(head + blob[off:off + chunk_payload])
    return grams


class UDPCaster:
    "sim side. cast_state() sprays chunks to every viewer that said HELLO recently."

    def __init__(self, host='0.0.0.0', port=30030):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.addr = self.sock.getsockname()
        self.viewers = {}              # addr -> last_seen
        self._lock = threading.Lock()
        self._closing = False
        threading.Thread(target=self._hello_forever, daemon=True).start()

    def _hello_forever(self):
        while not self._closing:
            try:
                _data, addr = self.sock.recvfrom(2048)
            except OSError:
                break
            with self._lock:
                self.viewers[addr] = time.monotonic()

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
        for gram in split_frame(blob, frame_id):
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
    "viewer side: HELLO keepalive + reassemble chunks, keep newest complete frame."

    MAX_PENDING = 4                    # in-flight partial frames to remember

    def __init__(self, host, port, hello_interval=1.0):
        self.caster = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(hello_interval)
        self.hello_interval = hello_interval
        self.box = Mailbox()
        self.last_id = None
        self.newest_done = 0
        self.alive = True
        self.stat_datagrams = 0
        self.stat_frames = 0
        self.sock.sendto(HELLO, self.caster)
        threading.Thread(target=self._recv_forever, daemon=True).start()

    def _recv_forever(self):
        pending = {}                   # frame_id -> [got, total, buf, seen_offsets]
        last_hello = time.monotonic()
        while self.alive:
            now = time.monotonic()
            if now - last_hello >= self.hello_interval:
                try:
                    self.sock.sendto(HELLO, self.caster)
                except OSError:
                    break
                last_hello = now
            try:
                gram, _addr = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            except OSError:
                break
            if len(gram) < CHUNK.size:
                continue
            magic, fid, off, total, _n = CHUNK.unpack_from(gram, 0)
            if magic != CHUNK_MAGIC or fid <= self.newest_done:
                continue               # not ours / superseded -> drop
            self.stat_datagrams += 1

            slot = pending.get(fid)
            if slot is None:
                slot = pending[fid] = [0, total, bytearray(total), set()]
                if len(pending) > self.MAX_PENDING:     # forget the oldest partial
                    pending.pop(min(pending))
            got, _t, buf, seen = slot
            if off in seen:
                continue
            payload = gram[CHUNK.size:]
            buf[off:off + len(payload)] = payload
            seen.add(off)
            slot[0] = got + len(payload)

            if slot[0] >= total:       # frame complete
                self.newest_done = fid
                self.stat_frames += 1
                self.box.put(bytes(buf))
                for k in [k for k in pending if k <= fid]:
                    pending.pop(k)

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
