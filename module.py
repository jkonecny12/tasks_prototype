#
# Installation dummy module.
#


class BaseModule(object):

    def __init__(self):
        super().__init__()
        self._tasks = []

    @property
    def tasks(self):
        """In the pydbus we need to return list of dbus paths and caller needs to create a proxy objects from them.
        However in this simple prototype we will return objects directly.
        """
        return self._tasks
