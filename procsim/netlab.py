"""userspace link emulator: put a fake radio between two real sockets.

sch_netem needs kernel support; this runs anywhere (windows/rpi included) and
is honest for the failure modes that matter on a VR LAN: real bytes move
through real sockets, only the relay adds delay / jitter / serialization
(rate) / periodic freezes / loss.

modeling note: on wifi the 802.11 MAC retransmits lost frames itself, so the
IP layer above mostly sees jitter spikes + throughput collapse + short
freezes rather than raw loss. that's why the tcp path here gets delay/rate/
freeze but no loss injection (kernel tcp below the relay would "repair" fake
app-level loss anyway), while the udp path gets loss too (what survives MAC
retry limits really is gone).

tcp gets one extra honest behavior: a finite link buffer with backpressure.
when the shaped queue is full the relay STOPS reading from the caster --
exactly what a full AP/kernel buffer does -- so the caster's sendall blocks
and its mailbox starts dropping. that chain is the real "tcp on bad wifi"
story (bufferbloat), and it is measurable here.
"""
import random
import socket
import threading
import time


class LinkProfile:
    def __init__(self, delay_ms=0.0, jitter_ms=0.0, rate_mbit=0.0, loss=0.0,
                 freeze_ms=0.0, freeze_every_ms=0.0, buf_bytes=256 * 1024):
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.rate_mbit = rate_mbit          # 0 = unlimited
        self.loss = loss                    # udp only
        self.freeze_ms = freeze_ms          # link outage length
        self.freeze_every_ms = freeze_every_ms
        self.buf_bytes = buf_bytes          # link/AP queue size

    def __repr__(self):
        return (f'{self.delay_ms:g}±{self.jitter_ms:g}ms '
                f'{self.rate_mbit:g}Mbit loss={self.loss:.1%} '
                f'freeze={self.freeze_ms:g}/{self.freeze_every_ms:g}ms')


PROFILES = {
    # one-way values, applied to the state (down) direction only
    'lan':      LinkProfile(0.2, 0.05, 1000),
    'wifi':     LinkProfile(4.0, 3.0, 200, loss=0.005),
    'wifi-bad': LinkProfile(12.0, 8.0, 60, loss=0.02,
                            freeze_ms=150, freeze_every_ms=2000),
}


class Shaper:
    """delay/rate/freeze queue. enqueue() returns False when the link buffer
    is full (tcp relay uses that as backpressure; udp relay drops instead)."""

    def __init__(self, profile, deliver):
        self.p = profile
        self.deliver = deliver              # callback(bytes)
        self.q = []                         # [(due, data)] FIFO, due non-decreasing
        self.q_bytes = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.busy_until = 0.0               # serialization (rate) model
        self.last_due = 0.0
        self.t0 = time.perf_counter()
        self.alive = True
        threading.Thread(target=self._run, daemon=True).start()

    def _freeze_end(self, now):
        "if the link is frozen at `now`, when does it come back? else None."
        p = self.p
        if not p.freeze_every_ms:
            return None
        phase = ((now - self.t0) * 1000.0) % p.freeze_every_ms
        if phase < p.freeze_ms:
            return now + (p.freeze_ms - phase) / 1000.0
        return None

    def enqueue(self, data):
        p = self.p
        now = time.perf_counter()
        with self.cond:
            if self.q_bytes + len(data) > p.buf_bytes:
                return False                # link buffer full
            due = max(now, self.busy_until)
            if p.rate_mbit:
                self.busy_until = due + len(data) * 8 / (p.rate_mbit * 1e6)
                due = self.busy_until
            due += p.delay_ms / 1000.0 + random.random() * p.jitter_ms / 1000.0
            due = max(due, self.last_due)   # a link never reorders itself
            self.last_due = due
            self.q.append((due, data))
            self.q_bytes += len(data)
            self.cond.notify()
        return True

    def _run(self):
        while self.alive:
            with self.cond:
                while self.alive and not self.q:
                    self.cond.wait(0.2)
                if not self.alive:
                    return
                due, data = self.q[0]
            now = time.perf_counter()
            fz = self._freeze_end(now)      # outage stalls the head of the line
            wake = max(due, fz or 0.0)
            if wake > now:
                time.sleep(min(wake - now, 0.02))
                continue
            with self.cond:
                self.q.pop(0)
                self.q_bytes -= len(data)
                self.cond.notify_all()      # room for backpressured writer
            try:
                self.deliver(data)
            except OSError:
                self.alive = False

    def wait_room(self, nbytes, timeout=1.0):
        "block until enqueue(nbytes) would fit (tcp backpressure)."
        end = time.monotonic() + timeout
        with self.cond:
            while self.q_bytes + nbytes > self.p.buf_bytes:
                if not self.alive or time.monotonic() > end:
                    return False
                self.cond.wait(0.05)
        return True

    def close(self):
        self.alive = False
        with self.cond:
            self.cond.notify_all()


class UdpRelay:
    "viewer <-> relay <-> caster. uplink (hello) direct, downlink shaped+lossy."

    def __init__(self, listen_port, caster_addr, profile):
        self.p = profile
        self.down = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.down.bind(('127.0.0.1', listen_port))
        self.up = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.up.connect(caster_addr)
        self.viewer_addr = None
        self.dropped = 0
        self.shaper = Shaper(profile, self._to_viewer)
        self.alive = True
        threading.Thread(target=self._up_pump, daemon=True).start()
        threading.Thread(target=self._down_pump, daemon=True).start()

    def _to_viewer(self, data):
        if self.viewer_addr:
            self.down.sendto(data, self.viewer_addr)

    def _up_pump(self):
        while self.alive:
            try:
                data, addr = self.down.recvfrom(2048)
            except OSError:
                break
            self.viewer_addr = addr
            self.up.send(data)

    def _down_pump(self):
        while self.alive:
            try:
                data = self.up.recv(4096)
            except OSError:
                break
            if random.random() < self.p.loss:
                self.dropped += 1
                continue
            if not self.shaper.enqueue(data):
                self.dropped += 1           # tail-drop, like a full AP queue

    def close(self):
        self.alive = False
        self.shaper.close()
        for s in (self.down, self.up):
            try:
                s.close()
            except OSError:
                pass


class TcpRelay:
    "same idea for a tcp stream. no loss (MAC hides it), but finite buffer + backpressure."

    def __init__(self, listen_port, caster_addr, profile):
        self.p = profile
        self.caster_addr = caster_addr
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', listen_port))
        self.server.listen(1)
        self.alive = True
        self.shaper = None
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        try:
            viewer, _ = self.server.accept()
        except OSError:
            return
        viewer.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        caster = socket.create_connection(self.caster_addr)
        caster.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.shaper = Shaper(self.p, viewer.sendall)

        def up():
            try:
                while self.alive:
                    d = viewer.recv(4096)
                    if not d:
                        break
                    caster.sendall(d)
            except OSError:
                pass
        threading.Thread(target=up, daemon=True).start()

        try:
            while self.alive:
                d = caster.recv(16384)
                if not d:
                    break
                if not self.shaper.wait_room(len(d), timeout=5.0):
                    break                   # emulation dead, not a real path
                self.shaper.enqueue(d)
                # while the queue is full we simply stop recv()ing: caster's
                # kernel sndbuf fills, its sendall blocks, mailbox drops. that
                # IS the backpressure chain of a congested link.
        except OSError:
            pass
        finally:
            self.shaper.close()
            for s in (viewer, caster):
                try:
                    s.close()
                except OSError:
                    pass

    def close(self):
        self.alive = False
        if self.shaper:
            self.shaper.close()
        try:
            self.server.close()
        except OSError:
            pass
