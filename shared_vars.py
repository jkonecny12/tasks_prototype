#
# Shared variables helps synchronize threads.
#
# Thread safe.
#
# This object will create methods to access to variables and automatic callback if required.
# The main method is add_variable which should be called before the instance is passed to a thread.
# The add_variable method will create three methods for the given instance. If required this will use
# GLib event loop to automatically call callback on the main thread where the get method can read
# saved data.
#
# send_"name"(self, data) - store data which can be read by other thread safely
# get_"name"(self)        - read data
# empty_"name"(self)      - is the data queue empty?
#
# Usage:
#
# shared_list = SharedList()
# shared_list.add_variable("progress", callback_when_progress_changed)
# shared_list.add_variable("warning")
# ...
# # in different thread
# shared_list.send_progress(10) # callback_when_progress_changed is called in the main thread.
# shared_list.send_warning("User is not sufficient!")
# shared_list.send_warning("Ops that was developers mistake!")
#
# # in main thread after
# shared_list.empty_warning() # 2
# shared_list.get_warning() # "User is not sufficient!"
# shared_list.get_warning() # "Ops that was developers mistake!"
#

from queue import Queue

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
        self._queues = {}
        self._variables = set()

    def __str__(self):
        return self._name + " " + str(self._variables)

    @property
    def name(self):
        """Name of this data instance."""
        return self._name

    def add_variable(self, name, get_callback=None):
        """Add new variable to this instance.

        :param name: Name of this variable. From this name the send_"name", get_"name" and empty_"name" names
                     will be created.
        :type name: str

        :param get_callback: This callback will be automatically called from a send_"name" method if the GLib
                             event loop is running.
        :type get_callback: Function callback(data)
        """
        self._queues[name] = Queue()
        self._variables.add(name)

        self._make_send_method(name, get_callback)
        self._make_get_method(name)
        self._make_empty_method(name)

    def list_variables(self):
        """Get list of all variables in this instance."""
        return self._variables

    def _make_send_method(self, name, callback):

        def __method(self, data):
            self._queues[name].put(data)
            if callback is not None:
                GLib.idle_add(callback, self)

        send_method_name = "send_" + name
        setattr(self, send_method_name, __method)

    def _make_get_method(self, name):

        def __method(self, name):
            return self._queues[name].get_nowait()

        get_method_name = "get_" + name
        setattr(self, get_method_name, __method)

    def _make_empty_method(self, name):

        def __method(self, name):
            return self._queues[name].empty()

        empty_method_name = "empty_" + name
        setattr(self, empty_method_name, __method)
