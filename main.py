#!/usr/bin/python3


class DummyBoss(object):

    def __init__(self, modules):
        super(DummyBoss, self).__init__()
        self._modules = modules
        self._available_tasks = []
        self._completed_tasks = []

    def run_tasks(self):
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
            task.run()


if __name__ == "__main__":
    boss = DummyBoss([])
    boss.run_tasks()
