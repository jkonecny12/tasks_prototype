#!/usr/bin/python3


class DummyBoss(object):

    def __init__(self, modules):
        super(DummyBoss, self).__init__()
        self._modules = modules
        self._available_tasks = []
        self._completed_tasks = []

        self._running_task = None

    def run_tasks(self):
        """Dummy run tasks method.

        This method will collect all the tasks, sort them and run them one by one.
        """
        self._collect_tasks()
        self._sort_tasks()
        self._run_tasks()

    def _collect_tasks(self):
        for m in self._modules:
            self._available_tasks.append(m.tasks)

    def _sort_tasks(self):
        pass

    def _run_tasks(self):
        for task in self._available_tasks:
            self._running_task = task
            success, error_msg = task.run()
            self.task_completed_signal(success, error_msg)

    def task_completed_signal(self, success: bool, error_message: str):
        """Signal that the task is completed."""
        pass

    @property
    def total_progress_steps(self) -> int:
        """Get progress of all the available tasks.

        This progress can give you overview on how much time everything will takes.
        """
        steps = 0

        for task in self._available_tasks:
            steps += task.progress_steps

        return steps

    @property
    def task_progress_steps(self) -> int:
        """How many steps have the running task?"""
        if self._running_task:
            return self._running_task.progress_steps
        else:
            return 0

    @property
    def task_progress(self) -> int:
        """Progress of the running task."""
        if self._running_task:
            return self._running_task.progress_signal
        else:
            return 0


if __name__ == "__main__":
    boss = DummyBoss([])
    boss.run_tasks()
