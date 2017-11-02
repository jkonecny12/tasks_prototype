#
# Code from Anaconda iutils.py
# 

import functools

def synchronized(wrapped):
    """A locking decorator for methods.

    The decorator is only intended for methods and the class providing
    the method also needs to have a Lock/RLock instantiated in self._lock.

    The decorator prevents the wrapped method from being executed until
    self._lock can be acquired. Once available, it acquires the lock and
    prevents other decorated methods & other users of self._lock from
    executing until the wrapped method finishes running.
    """

    @functools.wraps(wrapped)
    def _wrapper(self, *args, **kwargs):
        with self._lock:
            return wrapped(self, *args, **kwargs)
    return _wrapper

