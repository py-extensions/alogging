import io
import logging.handlers
from typing import Callable, Optional, Type

from typing_extensions import ParamSpec

P = ParamSpec("P")
H = Callable[[P], logging.Handler]


def wrap(
    cls: Callable[[P], logging.Handler],
    wrapper: Optional[Type["HandlerWrapper"]] = None,
) -> Callable[P, "HandlerWrapper"]:
    """Wrap logging.Handler with HandlerWrapper to allow pickling."""

    def inner(*args: P.args, **kwargs: P.kwargs) -> "HandlerWrapper":
        wrap_cls = wrapper or HandlerWrapper
        return wrap_cls(cls, args, kwargs)

    return inner


class HandlerWrapper:
    """Base wrapper for logging.Handler-s that allows pickling for passing to backend."""

    def __init__(self, handler, args, kwargs):
        self.handler = handler
        self.args = args
        self.kwargs = kwargs
        self.formatter = None
        self.level = 0

    def __call__(self):
        return self.handler(*self.args, **self.kwargs)

    def __getstate__(self):
        return {
            "handler": self.handler,
            "args": self.args,
            "kwargs": self.kwargs,
            "formatter": self.formatter,
            "level": self.level,
        }

    def setFormatter(self, formatter) -> None:  # pylint: disable=invalid-name
        """Set formatter for the handler."""

        self.formatter = formatter

    def setLevel(self, level: int) -> None:  # pylint: disable=invalid-name
        """Set level for the handler."""

        self.level = level

    def __setstate__(self, state):
        self.handler = state["handler"]
        self.args = state["args"]
        self.kwargs = state["kwargs"]
        self.formatter = state["formatter"]
        self.level = state["level"]

        return self.handler


class StreamHandlerWrapper(HandlerWrapper):
    """Wrapper for StreamHandler that allows pickling."""

    def __getstate__(self):
        return {
            "handler": self.handler,
            "args": (self.args[0].buffer.__dict__,),
            "kwargs": {},
            "formatter": self.formatter,
        }

    def __setstate__(self, state):
        self.handler = state["handler"]
        self.args = (io.TextIOWrapper(io.FileIO(state[0]["name"])),)
        self.kwargs = {}
        self.formatter = state["formatter"]

        return self.handler


BaseRotatingHandler = wrap(logging.handlers.BaseRotatingHandler)
RotatingFileHandler = wrap(logging.handlers.RotatingFileHandler)
HTTPHandler = wrap(logging.handlers.HTTPHandler)
SMTPHandler = wrap(logging.handlers.SMTPHandler)
SysLogHandler = wrap(logging.handlers.SysLogHandler)
NTEventLogHandler = wrap(logging.handlers.NTEventLogHandler)
MemoryHandler = wrap(logging.handlers.MemoryHandler)
SocketHandler = wrap(logging.handlers.SocketHandler)
DatagramHandler = wrap(logging.handlers.DatagramHandler)
FileHandler = wrap(logging.FileHandler)
NullHandler = wrap(logging.NullHandler)
WatchedFileHandler = wrap(logging.handlers.WatchedFileHandler)
QueueHandler = wrap(logging.handlers.QueueHandler)
StreamHandler = wrap(logging.StreamHandler, wrapper=StreamHandlerWrapper)
