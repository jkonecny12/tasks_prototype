#
# Shared variables helps synchronize threads.
#
# Thread safe.
#
# This object will create methods to access to variables and automatic callback if required.
# The main method is add_variable which should be called before the instance is passed to a thread.
# The add_variable method will create methods for the given instance. If required this will use
# GLib event loop to automatically call callback on the main thread where the get method can read
# saved data.
#
# store_"name"(self, data) - store data which can be read by other thread safely
# get_"name"(self)         - read data
# pop_"name"(self)         - read and clear data
# is_set_"name"(self)      - is the data queue empty?
#
# Usage:
#
# shared_list = SharedList()
# shared_list.add_variable("progress", callback_when_progress_changed)
# shared_list.add_variable("warning")
# ...
# # in different thread
# shared_list.store_progress(10) # callback_when_progress_changed is called in the main thread.
# shared_list.store_warning("User is not sufficient!")
# shared_list.store_warning("Ops that was developers mistake!")
#
# # in main thread after
# shared_list.is_set_warning() # True
# shared_list.get_warning() # "User is not sufficient!"
# shared_list.get_warning() # "Ops that was developers mistake!"
#

from threading import Lock
from collections import namedtuple

import gi

gi.require_version("GLib", "2.0")

from gi.repository import GLib


class SharedVars(object):

    def __init__(self, name):
        """Thread safe synchronization mechanism.

        One instance of this class can be used to synchronize many variables.

        :param name: Name of this data object.
        :type name: str
        """
        super(SharedVars, self).__init__()
        self._name = name
        self._var_values = {}
        self._variables = set()

    def __str__(self):
        return self._name + " " + str(self._variables)

    @property
    def name(self):
        """Name of this data instance."""
        return self._name

    def add_variable(self, name, get_callback=None):
        """Add new variable to this instance.

        This method is NOT thread safe.

        :param name: Name of this variable. From this name the store_"name", get_"name" and empty_"name" names
                     will be created.
        :type name: str

        :param get_callback: This callback will be automatically called from a send_"name" method if the GLib
                             event loop is running.
        :type get_callback: Function callback(data)
        """
        self._var_values[name] = namedtuple("SyncValue", ("value", "lock"))
        self._var_values[name].lock = Lock()
        self._var_values[name].value = None
        self._variables.add(name)

        self._make_store_method(name, get_callback)
        self._make_get_method(name)
        self._make_pop_method(name)
        self._make_is_set_method(name)

    def list_variables(self):
        """Get list of all variables in this instance."""
        return self._variables

    def _make_store_method(self, name, callback):

        def __method(data):
            lock = self._var_values[name].lock

            with lock:
                self._var_values[name].value = data

            if callback is not None:
                GLib.idle_add(callback, data)

        send_method_name = "store_" + name
        setattr(self, send_method_name, __method)

    def _make_get_method(self, name):

        def __method():
            lock = self._var_values[name].lock

            with lock:
                return self._var_values[name].value

        get_method_name = "get_" + name
        setattr(self, get_method_name, __method)

    def _make_pop_method(self, name):

        def __method():
            lock = self._var_values[name].lock

            with lock:
                val = self._var_values[name].value
                self._var_values[name].value = None

                return val

        pop_method_name = "pop_" + name
        setattr(self, pop_method_name, __method)

    def _make_is_set_method(self, name):

        def __method():
            lock = self._var_values[name].lock

            with lock:
                return self._var_values[name].value is not None

        is_set_method_name = "is_set_" + name
        setattr(self, is_set_method_name, __method)
