"""
Utilities
"""

import os
import tempfile


def lazy_property(fn):
    attr_name = '_lazy_' + fn.__name__

    def getter(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    def setter(self, value):
        setattr(self, attr_name, value)

    def deleter(self):
        delattr(self, attr_name)

    return property(fget=getter, fset=setter, fdel=deleter, doc=fn.__doc__)


def get_random_ipc_socket():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.sock') as s:
        os.unlink(s.name)
    return 'ipc://{0}'.format(s.name)
