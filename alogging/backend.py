import logging
import signal
import sys
from queue import Empty

from alogging.helpers import unpickled


class AsyncLoggerBackend:
    RUNNING = False

    @classmethod
    def stop(cls, *args, **kwargs):
        cls.RUNNING = False

    @classmethod
    def add_signals(cls):
        """Add signals to stop the logger."""

        for sig in (signal.SIGQUIT, signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, cls.stop)

    @classmethod
    def sync_logger(cls, logger_info: dict) -> logging.Logger:
        if logger_info["name"] == "root":
            logger = logging.getLogger()
        else:
            logger = logging.getLogger(logger_info["name"])

        logger.setLevel(logger_info["level"])

        logger.handlers = []
        logger.filters = []

        for handler in logger_info["handlers"]:
            wrapped_handler = unpickled(handler)
            handler = wrapped_handler()

            if wrapped_handler.formatter:
                handler.setFormatter(wrapped_handler.formatter)

            if wrapped_handler.level:
                handler.setLevel(wrapped_handler.level)

            logger.addHandler(handler)

        for log_filter in logger_info["filters"]:
            logger.addFilter(unpickled(log_filter))

        return logger

    @classmethod
    def process(cls, queue: "Queue"):
        cls.RUNNING = True

        cls.add_signals()

        while cls.RUNNING:
            try:
                try:
                    message = queue.get(timeout=0.1)
                except Empty:
                    continue
                except EOFError:
                    sys.exit(1)

                if message.get("internal"):
                    cls.sync_logger(message["logger"])
                    continue

                logger_name = message.pop("logger")

                logging.getLogger(logger_name)._log(  # noqa
                    message["level"],
                    message["msg"],
                    *message["args"],
                )
            except Exception as e:
                logging.exception(e)
            except BrokenPipeError:
                sys.exit(1)
