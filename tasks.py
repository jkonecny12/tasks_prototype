#
# Simple tasks object prototype.
#

from threading import Thread
from shared_vars import SharedVars


class BaseTask(object):

    def __init__(self, loop, name, description=""):
        super().__init__()
        self._loop = loop
        self._name = name
        self._description = description

        self._shared = None

    @property
    def name(self) -> str:
        """Get name of the task."""
        return self._name

    @property
    def description(self) -> str:
        """Get short description of this task."""
        return ""

    @property
    def is_running(self) -> bool:
        """Is this task running right now?"""
        return self._shared.get_task_running()

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

    def error_raised(self, error: str):
        """Signal error to DBus."""
        pass

    def progress(self) -> (int, str):
        """Progress of this task.

        :returns: Actual progress step and message with short description what is happening in this step.
        :rtype: (int, str)
        """
        return self._shared.get_progress()

    def progress_changed(self, step: int, message: str):
        """Signal change of the progress."""
        pass

    def run(self):
        """Start thread and run this task in it.

        :returns: Tuple (success, error_message).
        """
        self._shared = SharedVars(self._name + " SharedVars")
        self.prepare()
        thread = Thread(target=self._run, daemon=True, args=[self._shared])
        thread.run()

    def _run(self):
        """This method will everything required for mark running process and similar.

        Do not override this method!!! Task should be done in self._run() method which is called here!

        This is running in separate thread! Use synchronization object here.

        :returns: Tuple (success, error_message).
        """
        if self._shared.task_running:
            return False, ("Error, task %s is already running!" % self._name)

        self._shared.task_running = True

        try:
            result, error = self.run_task()
        except Exception as e:
            # If anything goes wrong return False and exception string
            error = str(e)
            result = False

        self._shared.store_result = result
        self._shared.store_error = error
        self._shared.store_task_running = False

    def _progress_callback(self, data):
        self.progress_changed(*data)

    def _task_running_callback(self, data):
        self.is_running_changed(data)

    def _error_callback(self, data):
        self.error_raised(data)

    def prepare(self):
        """Prepare before the thread with task will run.

        This could be overridden to set self._shared value. This original implementation must be called!
        """
        self._shared.add_variable("error", self._error_callback)
        self._shared.add_variable("task_running", self._task_running_callback)
        self._shared.add_variable("progress", self._progress_callback)

    def run_task(self) -> (bool, str):
        """Override this method to run this tasks work.

        This will run in a separate thread??

        :returns: Tuple (success, error_message).
        """
        raise NotImplementedError
