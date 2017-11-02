#
# Simple tasks object prototype.
#

from threading import Thread, Lock
from shared_signal import SharedSignal
from iutils import synchronized


class BaseTask(object):

    def __init__(self, loop, name, description=""):
        super().__init__()
        self._loop = loop
        self._name = name
        self._description = description
        self._thread = None
        self._lock = Lock()

        self._progress = (0, "")
        self._error = ""
        self._task_running = False

        self._progress_signal = SharedSignal()
        self._error_signal = SharedSignal()
        self._task_running_signal = SharedSignal()

        self._progress_signal.connect(self._progress_callback)
        self._error_signal.connect(self._error_callback)
        self._task_running_signal.connect(self._task_running_callback)

    @property
    def name(self) -> str:
        """Get name of the task."""
        return self._name

    @property
    def description(self) -> str:
        """Get short description of this task."""
        return ""

    @synchronized
    def is_running(self) -> bool:
        """Is this task running right now?"""
        return self._task_running

    @synchronized
    def _set_is_running(self, task_running):
        """Set is running thread safe."""
        self._task_running = task_running

    def is_running_changed(self, running: bool):
        """Property task_running have changed."""
        pass

    @property
    def progress_steps_count(self) -> int:
        """How many steps this task has?

        More is always better.
        This should be read just before the `run()` method is called because number of steps can change during the
        configuration.

        :returns: Complete count of steps of a progress.
        :rtype: int
        """
        return 0

    def is_cancelable(self) -> bool:
        """Could this task be canceled?"""
        return True

    def cancel(self):
        """Cancel this task in progress."""
        self._set_is_running(False)

    def error_raised(self, error: str):
        """Signal error to DBus."""
        pass

    def progress(self) -> (int, str):
        """Progress of this task.

        :returns: Actual progress step and message with short description what is happening in this step.
        :rtype: (int, str)
        """
        return self._progress

    def progress_changed(self, step: int, message: str):
        """Signal change of the progress."""
        pass

    def run(self):
        """Start thread and run this task in it.

        :returns: Tuple (success, error_message).
        """
        self._thread = Thread(target=self._run, daemon=True)
        self._set_is_running(True)
        self._thread.run()

    def _run(self):
        """This method will everything required for mark running process and similar.

        Do not override this method!!! Task should be done in self._run() method which is called here!

        This is running in separate thread! Use synchronization object here.

        :returns: Tuple (success, error_message).
        """
        self._task_running = True

        try:
            self.run_task()
        except Exception as e:
            # If anything goes wrong return False and exception string
            self._error_signal.emit(str(e))

        self._task_running_signal.emit(False)

    def _progress_callback(self, data):
        self._progress = data
        self.progress_changed(data[0], data[1])

    def _task_running_callback(self, data):
        self._task_running = data
        self.is_running_changed(data)

    def _error_callback(self, data):
        self._set_is_running(False)
        self._error = data
        self.error_raised(data)

    def run_task(self) -> str:
        """Override this method to run this tasks work.

        This will run in a separate thread??
        """
        # do sub tasks
        # emit signals when step progress or error raised
        # test if task_running don't want to cancel this task
        raise NotImplementedError
