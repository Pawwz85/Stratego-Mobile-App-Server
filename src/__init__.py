"""
    This file exist for  satisfying requirements of pyclbr library,
    which relays on some old legacy code.

    We also monkey patch json module here
"""
from json import JSONEncoder


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default
JSONEncoder.default = _default