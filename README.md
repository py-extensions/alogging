# alogging

`alogging` is a Python library that provides asynchronous logging capabilities. It is designed to work with the standard Python `logging` module, but adds asynchronous functionality to improve performance in applications that make heavy use of logging.

## Features

- Asynchronous logging: Log messages are processed in a separate process to avoid blocking the main application.
- Compatibility: Works with the standard Python `logging` module, so you can use all the features and handlers you're familiar with.
- Flexibility: Provides a variety of handlers, including `RotatingFileHandler`, `HTTPHandler`, `SMTPHandler`, `SysLogHandler`, and more.

## Usage

To use `alogging`, you first need to start the backend process. This can be done using the `start_backend` method:

```python
import asyncio
import alogging

asyncio.run(alogging.start_backend())
```

You can then get a logger and use it just like you would with the standard `logging` module:

```python3
log = alogging.getLogger("my_logger")
log.info("This is an info message")
```

You can also configure the logger using the `basicConfig` function:

```python3
alogging.basicConfig(
    filename="test.log",
    level=alogging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s",
)
```

## Handlers

`alogging` provides a variety of handlers that you can use to control where your log messages go. These include:

- `RotatingFileHandler`: Writes log messages to a file, with support for automatic rotation when the file reaches a certain size.
- `HTTPHandler`: Sends log messages to a web server as HTTP POST requests.
- `SMTPHandler`: Sends log messages to an email address using SMTP.
- `SysLogHandler`: Sends log messages to a Unix syslog daemon.

To use a handler, you need to create an instance of it and add it to your logger:

```python3
handler = alogging.handlers.RotatingFileHandler("test.log", maxBytes=10000, backupCount=5)
log.addHandler(handler)
```

## Installation

You can install `alogging` using pip:

```
pip install py-extensions-alogging
```

Or add it using poetry:

```
poetry add py-extensions-alogging
```

## Contributing

Contributions to `alogging` are welcome. Please submit a pull request or create an issue on GitHub.

## License

`alogging` is licensed under the MIT License. See [LICENSE](LICENSE) for more information.
