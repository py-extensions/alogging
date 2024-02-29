import pickle
import threading
from logging import Filter
from typing import Union

import alogging.handlers

P = Union[alogging.handlers.HandlerWrapper, Filter]  # pylint: disable=invalid-name
LT = threading._RLock


def pickled(obj: P) -> bytes:
    """Pickle HandlerWrapper or Filter."""

    if not isinstance(obj, (alogging.handlers.HandlerWrapper, Filter)):
        raise ValueError("Only HandlerWrapper and Filters can set.")

    return pickle.dumps(obj)


def unpickled(value: bytes) -> P:
    """Unpickle HandlerWrapper or Filter."""

    return pickle.loads(value)
