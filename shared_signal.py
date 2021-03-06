""" A signal/slot implementation

File:    isignal.py
Author:  Thiago Marcos P. Santos
Author:  Christopher S. Case
Author:  David H. Bronke
Created: August 28, 2008
Updated: December 12, 2011
License: MIT

"""
import inspect
from weakref import WeakKeyDictionary

import gi

gi.require_version("GLib", "2.0")

from gi.repository import GLib


class SharedSignal(object):
    def __init__(self):
        # The original implementation used WeakSet to store functions,
        # but that causes lambdas without any other reference to be
        # garbage collected. So we use a normal set to avoid that.
        self._functions = set()
        self._methods = WeakKeyDictionary()

    # The original implementation used __call__, so one would just call the signal itself:
    #
    # my_signal("foo")
    #
    # This has been changed to the emit() method to both be more consistent with how signals/slots
    # work in Qt & GTK and to make it more easily apparent that a signal is being triggered.
    # The correct way to trigger a signal is therefore:
    #
    # my_signal.emit("foo")
    def emit(self, *args, **kargs):
        # Call handler functions
        for func in self._functions:
            GLib.idle_add(func, args)
            #func(*args, **kargs)

        # Call handler methods
        for obj, funcs in self._methods.items():
            for func in funcs:
                #func(obj, *args, **kargs)
                GLib.idle_add(func, args)

    def connect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ not in self._methods:
                self._methods[slot.__self__] = set()

            self._methods[slot.__self__].add(slot.__func__)

        else:
            self._functions.add(slot)

    def disconnect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ in self._methods:
                self._methods[slot.__self__].remove(slot.__func__)
        else:
            if slot in self._functions:
                self._functions.remove(slot)

    def clear(self):
        self._functions.clear()
        self._methods.clear()
