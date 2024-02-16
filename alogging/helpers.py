import pickle
import threading
from logging import Filter
from typing import Union

import alogging.handlers

P = Union[alogging.handlers.HandlerWrapper, Filter]
LT = threading._RLock


def pickled(obj: P) -> bytes:
    if not isinstance(obj, (alogging.handlers.HandlerWrapper, Filter)):
        raise ValueError("Only HandlerWrapper and Filters can set.")

    return pickle.dumps(obj)


def unpickled(value: bytes) -> P:
    return pickle.loads(value)
