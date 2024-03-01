import asyncio
import logging
import logging.handlers
import multiprocessing
import threading
from asyncio import CancelledError
from multiprocessing import Manager, Process
from queue import Queue
from typing import Any, Callable, Optional, TypeVar, Union

import alogging.handlers
from alogging.backend import AsyncLoggerBackend
from alogging.helpers import pickled

QUEUE: Union[Queue, multiprocessing.Queue] = Queue()
LOCK = threading.Lock()

F = TypeVar("F", bound=Callable[..., Any])


def sync_logger(f: F) -> F:
    """Decorator to sync logger params after function call.

    Sends logger params to the backend for synchronization.
    """

    def wrapper(logger: "AsyncLogger", *args, **kwargs):
        result = f(logger, *args, **kwargs)
        logger.sync_logger()
        return result

    return wrapper


class AsyncLogger(logging.Logger):
    """Logger that logs messages asynchronously."""

    _BACKEND_PROCESS = None

    def _log(self, level: int, msg: str, *args, **kwargs):
        """Log messages to the queue."""

        if self._BACKEND_PROCESS is None:
            logging.warning("Backend not started, messages are queued.")

        QUEUE.put_nowait(
            {
                "logger": self.name,
                "level": level,
                "msg": msg,
                "args": args,
                "kwargs": kwargs,
            },
        )

    @classmethod
    async def _start_backend(cls):
        """Start backend process."""

        if cls._BACKEND_PROCESS is not None:
            return

        global QUEUE  # pylint: disable=global-statement

        try:
            with Manager() as manager:
                messages = []
                while not QUEUE.empty():
                    messages.append(QUEUE.get_nowait())

                QUEUE = manager.Queue()

                for message in messages:
                    QUEUE.put(message)

                cls._BACKEND_PROCESS = Process(target=AsyncLoggerBackend.process, args=(QUEUE,))
                cls._BACKEND_PROCESS.start()

                await asyncio.Future()
        except Exception as e:
            logging.exception(e)

        except CancelledError:
            logging.warning("Backend process cancelled")
            if cls._BACKEND_PROCESS is not None:
                cls._BACKEND_PROCESS.terminate()
                cls._BACKEND_PROCESS.join()
                cls._BACKEND_PROCESS = None

            QUEUE = Queue()

    @classmethod
    def start_backend(cls):
        """Start backend process."""

        threading.Thread(target=asyncio.run, args=[cls._start_backend()]).start()

    @sync_logger
    def addHandler(self, hdlr: alogging.handlers.HandlerWrapper):
        """Add handler to logger."""

        if not isinstance(hdlr, alogging.handlers.HandlerWrapper):
            raise RuntimeError("Cant add not wrapped handler")

        super().addHandler(hdlr)

    @sync_logger
    def removeHandler(self, hdlr: alogging.handlers.HandlerWrapper):
        """Remove handler from logger."""

        super().removeHandler(hdlr)

    @sync_logger
    def setLevel(self, level: int):
        """Set logger level."""

        super().setLevel(level)

    @sync_logger
    def addFilter(self, filter):  # pylint: disable=redefined-builtin
        """Add filter to logger."""

        super().addFilter(filter)

    @sync_logger
    def removeFilter(self, filter):  # pylint: disable=redefined-builtin
        """Remove filter from logger."""

        super().removeFilter(filter)

    def sync_logger(self):
        """Sync logger with backend."""

        QUEUE.put_nowait(
            {
                "internal": True,
                "logger": {
                    "name": self.name,
                    "level": self.level,
                    "handlers": [pickled(handler) for handler in self.handlers],
                    "filters": [pickled(filter) for filter in self.filters],
                },
            }
        )


root = AsyncLogger("root", logging.WARNING)


def getLogger(name: Optional[str] = None) -> AsyncLogger:  # pylint: disable=invalid-name
    """Get logger with given name."""

    return AsyncLogger(name or "root")


def basicConfig(**kwargs):  # pylint: disable=invalid-name
    """Configure logger. Copy of `logging.basicConfig` with wrapped handlers."""

    with LOCK:
        if len(root.handlers) == 0:
            handlers = kwargs.pop("handlers", None)

            if handlers is None:
                if "stream" in kwargs and "filename" in kwargs:
                    raise ValueError("'stream' and 'filename' should not be specified together")
            else:
                if "stream" in kwargs or "filename" in kwargs:
                    raise ValueError(
                        "'stream' or 'filename' should not be specified together with 'handlers'"
                    )

            if handlers is None:
                filename = kwargs.pop("filename", None)
                mode = kwargs.pop("filemode", "a")

                if filename:
                    h = alogging.handlers.FileHandler(filename, mode)
                else:
                    stream = kwargs.pop("stream", None)
                    h = alogging.handlers.StreamHandler(stream)

                handlers = [h]

            dfs = kwargs.pop("datefmt", None)
            style = kwargs.pop("style", "%")

            if style not in logging._STYLES:
                raise ValueError(f"Style must be one of: {','.join(logging._STYLES.keys())}")

            fs = kwargs.pop("format", logging._STYLES[style][1])
            fmt = logging.Formatter(fs, dfs, style)

            for wh in handlers:
                if wh.formatter is None:
                    h.setFormatter(fmt)
                root.addHandler(h)

            level = kwargs.pop("level", None)
            if level is not None:
                root.setLevel(level)

            if kwargs:
                keys = ", ".join(kwargs.keys())
                raise ValueError(f"Unrecognised argument(s): {keys}")


AsyncLogger.manager = logging.Manager(root)
AsyncLogger.manager.setLoggerClass(AsyncLogger)
