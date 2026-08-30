"""shared-memory state channel: sim process publishes, render process reads latest.

no queue, no backlog: N slots rotate, reader always grabs the newest complete
frame ("latest wins"). sim never blocks on a slow viewer, viewer never falls
behind a fast sim.

segment layout:
    Ctrl 32B: magic 'MVSH', ver u8, nslots u8, pad u16, slot_cap u32,
              latest_slot u32, latest_id u32, pad 12B
    nslots x [ Slot 16B: seq u32, nbytes u32, pad 8B | data slot_cap B ]

publish (per slot, seqlock):
    seq -> odd, write frame bytes, write nbytes, seq -> even(+2), ctrl.latest_slot = slot
read:
    s1 = seq (odd -> busy, try older slot), copy nbytes out, s2 = seq,
    s1 == s2 -> frame ok, else retry.

when both ends come from one parent (SimProcess), pass a multiprocessing.Lock:
the seqlock then only guards against bugs and the channel is correct on any
memory model (ARM included). name-attached strangers fall back to pure seqlock,
which is fine on x86 and near-fine on ARM (window is ns per lap of 3 slots).

capacity is fixed at create time. size for max units; a bigger world needs a
new segment (announce the new name over the control pipe).
"""
import secrets
import struct
from multiprocessing import shared_memory

from . import frame as fr

SHM_MAGIC = b'MVSH'
SHM_VER = 1

CTRL = struct.Struct('<4sBBHIII12x')   # 32B
SLOT = struct.Struct('<II8x')          # 16B
U32 = struct.Struct('<I')


def _attach(name, untrack):
    """attach an existing segment. only the creator should own unlink.

    untrack=True is for a STRANGER process (own resource tracker): stops its
    tracker from unlinking the segment when the stranger exits.
    untrack=False is for a CHILD of the creator: spawn/fork children share the
    parent's tracker, where register() is a set-add no-op and an extra
    unregister would erase the parent's own registration (KeyError at unlink).
    """
    if not untrack:
        return shared_memory.SharedMemory(name=name)
    try:
        return shared_memory.SharedMemory(name=name, track=False)  # py3.13+
    except TypeError:
        shm = shared_memory.SharedMemory(name=name)
        try:
            from multiprocessing import resource_tracker
            resource_tracker.unregister(shm._name, 'shared_memory')
        except Exception:
            pass
        return shm


class ShmChannel:
    """one writer, one reader (per channel). create() on the owner side,
    attach(name) on the other."""

    def __init__(self, shm, owner, lock=None):
        self.shm = shm
        self.owner = owner
        self.lock = lock                 # optional mp.Lock, shared by both ends
        buf = shm.buf
        magic, ver, nslots, _pad, slot_cap, _ls, _li = CTRL.unpack_from(buf, 0)
        if magic != SHM_MAGIC or ver != SHM_VER:
            raise ValueError('not a ShmChannel segment')
        self.nslots = nslots
        self.slot_cap = slot_cap
        self._slot_stride = SLOT.size + slot_cap
        self._cur = 0                    # writer: next slot to use
        self._frame_id = 0               # writer counter
        self.last_id = None              # reader: id of last frame returned

    # ---------- lifecycle
    @classmethod
    def create(cls, slot_cap=1 << 20, nslots=3, name=None, lock=None):
        if name is None:
            name = f'mvsim_{secrets.token_hex(4)}'
        size = CTRL.size + nslots * (SLOT.size + slot_cap)
        shm = shared_memory.SharedMemory(name=name, create=True, size=size)
        CTRL.pack_into(shm.buf, 0, SHM_MAGIC, SHM_VER, nslots, 0, slot_cap, 0, 0)
        for i in range(nslots):
            SLOT.pack_into(shm.buf, cls._slot_off_static(i, slot_cap), 0, 0)
        return cls(shm, owner=True, lock=lock)

    @classmethod
    def attach(cls, name, lock=None, child_of_creator=False):
        "child_of_creator=True when attaching from a spawn/fork child of the owner."
        return cls(_attach(name, untrack=not child_of_creator), owner=False, lock=lock)

    @property
    def name(self):
        return self.shm.name

    def close(self):
        try:
            self.shm.close()
        except BufferError:
            pass  # numpy views still alive; let gc handle it
        if self.owner:
            try:
                self.shm.unlink()   # no-op concept on windows: freed at last close
            except FileNotFoundError:
                pass

    # ---------- layout helpers
    @staticmethod
    def _slot_off_static(i, slot_cap):
        return CTRL.size + i * (SLOT.size + slot_cap)

    def _slot_off(self, i):
        return CTRL.size + i * self._slot_stride

    # ---------- writer side
    def publish(self, sim_time, sections, frame_id=None):
        """pack STATE straight into the next slot and flip it live.
        returns frame_id. raises ValueError if frame exceeds slot_cap."""
        if frame_id is None:
            self._frame_id += 1
            frame_id = self._frame_id
        need = fr.state_nbytes(sections)
        if need > self.slot_cap:
            raise ValueError(f'frame {need}B > slot_cap {self.slot_cap}B')

        buf = self.shm.buf
        slot = self._cur
        self._cur = (slot + 1) % self.nslots
        off = self._slot_off(slot)

        if self.lock is not None:
            self.lock.acquire()
        try:
            seq = U32.unpack_from(buf, off)[0]
            U32.pack_into(buf, off, seq + 1)                      # odd: writing
            nbytes = fr.pack_state_into(buf[off + SLOT.size: off + SLOT.size + self.slot_cap],
                                        frame_id, sim_time, sections)
            SLOT.pack_into(buf, off, seq + 2, nbytes)             # even: done
            # publish pointer last
            U32.pack_into(buf, 12, slot)      # ctrl.latest_slot
            U32.pack_into(buf, 16, frame_id & 0xFFFFFFFF)         # ctrl.latest_id
        finally:
            if self.lock is not None:
                self.lock.release()
        return frame_id

    # ---------- reader side
    def read_latest(self, retries=4):
        """-> Frame (arrays own their memory) or None if nothing published yet.
        also None if the only stable frame is the one already returned last time
        is NOT checked here -- use read_new() for that."""
        buf = self.shm.buf
        latest = U32.unpack_from(buf, 12)[0]
        for k in range(self.nslots):
            slot = (latest - k) % self.nslots
            off = self._slot_off(slot)
            for _ in range(retries):
                if self.lock is not None:
                    self.lock.acquire()
                try:
                    s1, nbytes = SLOT.unpack_from(buf, off)
                    if s1 == 0 or s1 % 2 == 1 or nbytes == 0:
                        break               # empty or mid-write: try older slot
                    data = bytes(buf[off + SLOT.size: off + SLOT.size + nbytes])
                    s2 = U32.unpack_from(buf, off)[0]
                finally:
                    if self.lock is not None:
                        self.lock.release()
                if s1 == s2:
                    f = fr.unpack(data)     # views onto our private copy: safe
                    self.last_id = f.frame_id
                    return f
                # torn read (writer lapped us): retry same slot
        return None

    def read_new(self):
        "read_latest, but None when the newest frame was already returned."
        prev = self.last_id
        f = self.read_latest()
        if f is not None and f.frame_id == prev:
            return None
        return f
