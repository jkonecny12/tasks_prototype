#
# Simple tasks object prototype.
#


class BaseTask(object):

    def __init__(self, name, description=""):
        super(BaseTask, self).__init__()
        self._name = name
        self._description = description
        self._running = False
        self._completed = False

        self._progress = 0

    @property
    def name(self) -> str:
        """Get name of the task."""
        return self._name

    @property
    def description(self) -> str:
        """Get short description of this task."""
        return ""

    @property
    def is_completed(self) -> bool:
        """Was this task completed successfully?"""
        return self._completed

    @property
    def is_running(self) -> bool:
        """Is this task running right now?"""
        return self._running

    @property
    def progress_steps(self) -> int:
        """How many steps this task has?

        More is always better.
        This should be read just before the `run()` method is called because number of steps can change during the
        configuration.

        :returns: Complete count of steps of a progress.
        :rtype: int
        """
        return 0

    def progress_signal(self) -> (int, str):
        """Signal progress of this task.

        :returns: Actual progress step and message with short description what is happening in this step.
        :rtype: (int, str)
        """
        return self._progress, ""

    def run(self) -> (bool, str):
        """This method will everything required for mark running process and similar.

        Do not override this method!!! Task should be done in self._run() method which is called here!

        :returns: Tuple (success, error_message).
        """
        if self._running:
            return False, ("Error, task %s is already running!" % self._name)

        self._running = True

        try:
            result, error = self._run()
        except Exception as e:
            # If anything goes wrong return False and exception string
            error = str(e)
            result = False

        self._completed = result
        self._running = False
        return result, error

    def _run(self) -> (bool, str):
        """Override this method to run this tasks work.

        :returns: Tuple (success, error_message).
        """
        raise NotImplementedError
