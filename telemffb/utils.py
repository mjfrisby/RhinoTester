import math
import random
import time


def millis() -> int:
    """return millisecond timer"""
    return time.perf_counter_ns() // 1000000


def clamp(n, minn, maxn):
    return type(n)(sorted((minn, n, maxn))[1])


def clamp_minmax(n, max):
    return clamp(n, -max, max)


class Destroyable:
    def destroy(self):
        raise NotImplementedError


class Dispenser:
    def __init__(self, cls) -> None:
        self.cls = cls
        self.dict = {}

    def get(self, name, *args, **kwargs):
        v = self.dict.get(name)
        if not v:
            v = self.cls(*args, **kwargs)
            v.name = name
            self.dict[name] = v
        return v

    def remove(self, name):
        self.dispose(name)

    def __contains__(self, name):
        return name in self.dict

    def __getitem__(self, name):
        return self.get(name)

    def __iter__(self):
        return self.dict.__iter__()

    def __delitem__(self, name):
        v = self.dict[name]
        if isinstance(v, Destroyable):
            v.destroy()
        del self.dict[name]

    def clear(self):
        for k, v in self.dict.items():
            if isinstance(v, Destroyable):
                v.destroy()
        self.dict.clear()

    def values(self):
        return self.dict.values()

    def dispose(self, *names):
        for name in names:
            if name in self.dict:
                v = self.dict[name]
                if isinstance(v, Destroyable):
                    v.destroy()
                del self.dict[name]

    def foreach(self, func):
        for i in self.values():
            func(i)


class LowPassFilter:
    def __init__(self, cutoff_freq_hz, init_val=0.0, **kwargs):
        self.cutoff_freq_hz = cutoff_freq_hz
        self.alpha = 0.0
        self.x_filt = init_val
        self.last_update = time.perf_counter()

    def __call__(self, x):
        return self.update(x)

    def update(self, x):
        now = time.perf_counter()
        dt = now - self.last_update
        if dt > 1:
            self.x_filt = x
        self.last_update = now
        self.alpha = dt / (1.0 / self.cutoff_freq_hz + dt)
        self.x_filt = self.alpha * x + (1.0 - self.alpha) * self.x_filt
        return self.x_filt

    @property
    def value(self):
        return self.x_filt


class DirectionModulator:
    pass


class RandomDirectionModulator(DirectionModulator):
    def __init__(self, *args, period=0.1, **kwargs):
        self.prev_upd = time.perf_counter()
        self.value = 0
        self.period = period

    def update(self):
        now = time.perf_counter()
        if now - self.prev_upd > self.period:
            self.prev_upd = now
            random.seed()
            self.value = random.randint(0, 360)
        return self.value
