"""SimProcess: run a sim loop in its own process, GIL fully out of the way.

path layout (why two channels):
  draw state  sim -> view : ShmChannel, 60+Hz, big-ish, latest-wins, binary
  input/ctrl  view -> sim : mp.Pipe, few events/s, tiny  -> pickle is fine here
  events      sim -> view : same Pipe, rare (sounds, spawns, schema announce)

hot path binary, cold path convenient. spawn context everywhere so behavior
matches windows even when developing on linux.

usage:
    def my_sim(ctx, n):
        world = make_world(n)
        while not ctx.stopping:
            for i in ctx.inputs():
                world.input(i)
            world.update(dt)
            ctx.publish(time.perf_counter(), [(kind, world.positions)])

    host = SimProcess(my_sim, args=(1000,))     # <- under if __name__ == '__main__'!
    ...
    f = host.read_new()          # newest Frame or None, never blocks
    ...
    host.stop()

my_sim must be importable (module top-level) for spawn to find it.
"""
import multiprocessing as mp

from .shmlink import ShmChannel


class SimContext:
    "what the sim function gets to talk to the outside."

    def __init__(self, channel, conn, stop_event):
        self.channel = channel
        self.conn = conn
        self._stop = stop_event

    @property
    def stopping(self):
        return self._stop.is_set()

    def publish(self, sim_time, sections):
        "push draw state (list of (kind, ndarray)). never blocks, never queues."
        return self.channel.publish(sim_time, sections)

    def inputs(self):
        "drain pending input/control events from the view side."
        try:
            while self.conn.poll():
                yield self.conn.recv()
        except (EOFError, OSError):
            return

    def emit(self, obj):
        "rare sim -> view event (cold path)."
        self.conn.send(obj)


def _sim_entry(sim_target, shm_name, conn, stop_event, lock, args, kwargs):
    channel = ShmChannel.attach(shm_name, lock=lock, child_of_creator=True)
    try:
        sim_target(SimContext(channel, conn, stop_event), *args, **kwargs)
    finally:
        channel.close()
        conn.close()


class SimProcess:
    """parent-side handle. owns the shm segment and the child process."""

    def __init__(self, sim_target, args=(), kwargs=None, slot_cap=1 << 20,
                 nslots=3, start_method='spawn'):
        ctx = mp.get_context(start_method)
        self._lock = ctx.Lock()          # makes the shm channel torn-read proof
        self.channel = ShmChannel.create(slot_cap=slot_cap, nslots=nslots,
                                         lock=self._lock)
        self._stop = ctx.Event()
        self.conn, child_conn = ctx.Pipe()   # duplex: input down, events up
        self.proc = ctx.Process(
            target=_sim_entry,
            args=(sim_target, self.channel.name, child_conn, self._stop,
                  self._lock, args, kwargs or {}),
            daemon=True)
        self.proc.start()
        child_conn.close()

    # ---- draw state (hot)
    def read_latest(self):
        return self.channel.read_latest()

    def read_new(self):
        return self.channel.read_new()

    # ---- input / events (cold)
    def send(self, obj):
        self.conn.send(obj)

    def events(self):
        try:
            while self.conn.poll():
                yield self.conn.recv()
        except (EOFError, OSError):
            return

    # ---- lifecycle
    @property
    def alive(self):
        return self.proc.is_alive()

    def stop(self, timeout=3.0):
        self._stop.set()
        self.proc.join(timeout)
        if self.proc.is_alive():
            self.proc.terminate()
            self.proc.join(1.0)
        self.channel.close()
        try:
            self.conn.close()
        except OSError:
            pass
