"""procsim: sim runs in its own process, view receives draw-state frames.

frame.py    binary frame codec (32B header + raw numpy sections)
shmlink.py  shared-memory latest-wins channel (local, zero-queue)
socklink.py same frames over tcp (remote / multi-viewer / web bridge)
simproc.py  process host: shm for draw state, pipe for input/control

see DESIGN.md for the whole discussion + benchmark numbers.
"""
from .frame import (STATE, SCHEMA, EVENT, Frame,
                    pack_state, pack_state_into, pack_json, unpack,
                    meshid_to_kind, kind_to_meshid)
from .shmlink import ShmChannel
from .socklink import FrameCaster, FrameViewer, Mailbox
from .simproc import SimProcess, SimContext
