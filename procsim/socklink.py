"""socket transport for the same binary frames: remote / multi-viewer path.

lessons baked in from 20_socket_world + axis3d test_socket:
  - fixed 32B binary header carries payload_len -> recv EXACTLY that many
    bytes. no START/END markers, no '}{' json boundary accidents, no
    buffer-stacking surprises.
  - never queue frames: every hop is a 1-deep Mailbox, newest replaces
    oldest. a slow viewer drops frames instead of stacking latency.
  - sender runs in a thread; sim thread only does mailbox.put (never blocks).
"""
import socket
import struct
import threading

from . import frame as fr

U32 = struct.Struct('<I')


class Mailbox:
    "1-deep latest-wins slot. put replaces; take returns newest once."
    def __init__(self):
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._data = None
        self._seq = 0
        self._taken = 0

    def put(self, data):
        with self._cond:
            self._data = data
            self._seq += 1
            self._cond.notify()

    def take(self, timeout=None):
        "newest payload not yet taken, else None."
        with self._cond:
            if self._taken == self._seq and timeout:
                self._cond.wait(timeout)
            if self._taken == self._seq:
                return None
            self._taken = self._seq
            return self._data

    def peek(self):
        with self._lock:
            return self._data


def recv_exact(sock, n, out=None):
    "read exactly n bytes (kills the partial-recv class of bugs)."
    buf = out if out is not None else bytearray(n)
    mv = memoryview(buf)
    got = 0
    while got < n:
        r = sock.recv_into(mv[got:n], n - got)
        if r == 0:
            raise ConnectionError('peer closed')
        got += r
    return buf


class FrameCaster:
    """sim side: bind, accept viewers, cast frames to all. one sender thread +
    one mailbox per viewer, so one stalled viewer never stalls the others."""

    def __init__(self, host='127.0.0.1', port=30020):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(8)
        self.addr = self.server.getsockname()
        self._boxes = []            # [(sock, Mailbox)]
        self._lock = threading.Lock()
        self._closing = False
        threading.Thread(target=self._accept_forever, daemon=True).start()

    def _accept_forever(self):
        while not self._closing:
            try:
                conn, _addr = self.server.accept()
            except OSError:
                break
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            box = Mailbox()
            with self._lock:
                self._boxes.append((conn, box))
            threading.Thread(target=self._send_forever, args=(conn, box), daemon=True).start()

    def _send_forever(self, conn, box):
        try:
            while not self._closing:
                data = box.take(timeout=0.5)
                if data is None:
                    continue
                conn.sendall(data)   # blocks only this viewer's thread
        except OSError:
            pass
        finally:
            conn.close()
            with self._lock:
                self._boxes = [(c, b) for c, b in self._boxes if c is not conn]

    def cast_state(self, frame_id, sim_time, sections):
        "pack once, hand to every viewer's mailbox."
        self.cast_bytes(fr.pack_state(frame_id, sim_time, sections))

    def cast_bytes(self, data):
        with self._lock:
            boxes = list(self._boxes)
        for _c, box in boxes:
            box.put(data)

    @property
    def n_viewers(self):
        with self._lock:
            return len(self._boxes)

    def close(self):
        self._closing = True
        try:
            self.server.close()
        except OSError:
            pass


class FrameViewer:
    "viewer side: connect, recv thread fills a mailbox, render loop polls latest()."

    def __init__(self, host='127.0.0.1', port=30020, connect_timeout=5.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(connect_timeout)
        self.sock.connect((host, port))
        self.sock.settimeout(None)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.box = Mailbox()
        self.last_id = None
        self.alive = True
        threading.Thread(target=self._recv_forever, daemon=True).start()

    def _recv_forever(self):
        head = bytearray(fr.HEADER_LEN)
        try:
            while True:
                recv_exact(self.sock, fr.HEADER_LEN, head)
                _mt, _ns, _fid, payload_len, _t = fr.unpack_header(head)
                body = recv_exact(self.sock, payload_len)
                self.box.put(bytes(head) + bytes(body))
        except (ConnectionError, OSError):
            self.alive = False

    def latest(self, timeout=None):
        "-> newest Frame not yet taken, or None."
        data = self.box.take(timeout)
        if data is None:
            return None
        f = fr.unpack(data)
        self.last_id = f.frame_id
        return f

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass
