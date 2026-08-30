"""binary frame codec: sim -> renderer draw-state transfer.

design rule: hot path (per-frame state) is fixed struct header + raw numpy bytes,
cold path (schema/handshake/rare events) may be json inside the same envelope.

wire layout, little-endian, fixed offsets:

    FrameHeader  32B
        0   magic       4s   b'MVS1'
        4   version     u8
        5   msg_type    u8   1=STATE 2=SCHEMA 3=EVENT
        6   section_n   u16
        8   frame_id    u32  monotonic, wraps
        12  payload_len u32  bytes after this header
        16  sim_time    f64  producer clock (time.perf_counter)
        24  reserved    8B

    STATE payload = section_n x section:
        SectionHeader 16B
            0   kind     u32  drawtype / meshid  (what batch this is)
            4   count    u32  instances
            8   dtype    u8   see DTYPES
            9   comps    u8   floats per instance: 3=pos 4=quat 7=pos+quat 16=mat4
            10  flags    u16  0 for now
            12  byte_len u32  raw data bytes following
        raw bytes count*comps*itemsize  (numpy C-order)

    SCHEMA/EVENT payload = utf-8 json bytes.

count*comps*itemsize stays 4-aligned as long as dtype >= 4 bytes or count*comps
is even; keep f32 on hot path and this never matters.
"""
import json
import struct

import numpy as np

MAGIC = b'MVS1'
VERSION = 1

STATE = 1
SCHEMA = 2
EVENT = 3

HEADER = struct.Struct('<4sBBHIId8x')   # 32 bytes
SECTION = struct.Struct('<IIBBHI')      # 16 bytes
HEADER_LEN = HEADER.size
SECTION_LEN = SECTION.size

# dtype code <-> numpy. hot path should stay '<f4'.
DTYPES = {0: '<f4', 1: '<f2', 2: '<i4', 3: '<u4', 4: 'u1', 5: '<i2', 6: '<u2', 7: '<f8'}
DTYPE_CODES = {np.dtype(v): k for k, v in DTYPES.items()}


class Frame:
    __slots__ = ('msg_type', 'frame_id', 'sim_time', 'sections', 'obj')

    def __init__(self, msg_type, frame_id, sim_time, sections=None, obj=None):
        self.msg_type = msg_type
        self.frame_id = frame_id
        self.sim_time = sim_time
        self.sections = sections if sections is not None else []  # [(kind, ndarray), ..]
        self.obj = obj  # SCHEMA/EVENT json object

    def __repr__(self):
        if self.msg_type == STATE:
            secs = ','.join(f'{k}:{a.shape}' for k, a in self.sections)
            return f'<Frame STATE id={self.frame_id} t={self.sim_time:.4f} [{secs}]>'
        return f'<Frame {self.msg_type} id={self.frame_id} {self.obj!r:.60}>'


def _as_packable(arr):
    "-> (contiguous 2d-ish array, count, comps, dtype_code, byte_len)"
    arr = np.ascontiguousarray(arr)
    if arr.ndim == 1:
        count, comps = arr.shape[0], 1
    elif arr.ndim == 2:
        count, comps = arr.shape
    else:  # (n, 4, 4) mat -> (n, 16)
        count = arr.shape[0]
        comps = arr.size // count if count else 0
        arr = arr.reshape(count, comps)
    code = DTYPE_CODES[arr.dtype]
    return arr, count, comps, code, arr.nbytes


def state_nbytes(sections):
    "total frame size for buffer pre-check."
    n = HEADER_LEN
    for _kind, arr in sections:
        n += SECTION_LEN + np.ascontiguousarray(arr).nbytes
    return n


def pack_state_into(buf, frame_id, sim_time, sections):
    """write STATE frame into writable buffer at offset 0, no intermediate copies.
    buf: writable buffer (memoryview of shm, bytearray..). returns total bytes."""
    off = HEADER_LEN
    n_sec = 0
    for kind, arr in sections:
        arr, count, comps, code, nbytes = _as_packable(arr)
        SECTION.pack_into(buf, off, kind, count, code, comps, 0, nbytes)
        off += SECTION_LEN
        dst = np.frombuffer(buf, dtype=np.uint8, count=nbytes, offset=off)
        dst[:] = arr.reshape(-1).view(np.uint8)  # straight memcpy
        off += nbytes
        n_sec += 1
    HEADER.pack_into(buf, 0, MAGIC, VERSION, STATE, n_sec,
                     frame_id & 0xFFFFFFFF, off - HEADER_LEN, sim_time)
    return off


def pack_state(frame_id, sim_time, sections):
    "-> bytes. convenience for socket path."
    buf = bytearray(state_nbytes(sections))
    n = pack_state_into(buf, frame_id, sim_time, sections)
    return bytes(memoryview(buf)[:n])


def pack_json(msg_type, frame_id, sim_time, obj):
    "SCHEMA/EVENT: cold path, json is fine here."
    payload = json.dumps(obj).encode('utf-8')
    head = HEADER.pack(MAGIC, VERSION, msg_type, 0,
                       frame_id & 0xFFFFFFFF, len(payload), sim_time)
    return head + payload


def unpack_header(buf, offset=0):
    "-> (msg_type, section_n, frame_id, payload_len, sim_time). raises on bad magic."
    magic, ver, msg_type, n_sec, frame_id, payload_len, sim_time = HEADER.unpack_from(buf, offset)
    if magic != MAGIC:
        raise ValueError(f'bad magic {magic!r}')
    if ver != VERSION:
        raise ValueError(f'version mismatch {ver}')
    return msg_type, n_sec, frame_id, payload_len, sim_time


def unpack(buf, offset=0, copy=False):
    """buffer -> Frame. STATE arrays are zero-copy views into buf unless copy=True.
    pass copy=True when buf is reused (shm slot) and frame outlives the read."""
    msg_type, n_sec, frame_id, payload_len, sim_time = unpack_header(buf, offset)
    off = offset + HEADER_LEN

    if msg_type != STATE:
        obj = json.loads(bytes(buf[off:off + payload_len]).decode('utf-8'))
        return Frame(msg_type, frame_id, sim_time, obj=obj)

    sections = []
    for _ in range(n_sec):
        kind, count, code, comps, _flags, byte_len = SECTION.unpack_from(buf, off)
        off += SECTION_LEN
        arr = np.frombuffer(buf, dtype=DTYPES[code], count=count * comps, offset=off)
        arr = arr.reshape(count, comps)
        if copy:
            arr = arr.copy()
        sections.append((kind, arr))
        off += byte_len
    return Frame(STATE, frame_id, sim_time, sections=sections)


# their renderer uses meshid strings like '00010001' (matid+geoid, 4+4 hex chars)
def meshid_to_kind(meshid):
    return int(meshid, 16)

def kind_to_meshid(kind):
    return f'{kind:08x}'
