import asyncio
import logging
import time
from asyncio import Queue
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import pytest
import pytest_asyncio
from aiosmtpd.controller import Controller

import alogging
from alogging.handlers import HTTPHandler, RotatingFileHandler, SysLogHandler

TEST_FILE_PATH = Path("test.log")


@pytest_asyncio.fixture
async def start_backend():
    """Start the backend process."""

    future = asyncio.ensure_future(alogging.start_backend())
    yield
    future.cancel()


@pytest.fixture
def clean_file():
    """Clean the test log file."""

    with open(TEST_FILE_PATH, "w"):
        pass

    yield

    TEST_FILE_PATH.unlink()


@pytest.mark.asyncio
async def test_RotatingFileHandler(start_backend, clean_file):
    log = alogging.getLogger("alogging")
    log.getChild("logger")

    handler = RotatingFileHandler("test.log", maxBytes=10000, backupCount=5)

    formatter = alogging.Formatter("%(name)s.%(levelname)s:%(message)s")
    handler.setFormatter(formatter)

    log.addHandler(handler)

    log.debug("123")
    log.info("345")
    log.warning("567")
    log.error("789")
    log.exception(Exception("0123"))

    # Wait for the log to be written
    time.sleep(0.5)

    with open(TEST_FILE_PATH, "r") as file:
        lines = file.readlines()

    assert len(lines) == 5, "Incorrect number of lines"

    assert lines[0].startswith("alogging.DEBUG:"), "Incorrect log level"
    assert lines[1].startswith("alogging.INFO:"), "Incorrect log level"
    assert lines[2].startswith("alogging.WARNING:"), "Incorrect log level"
    assert lines[3].startswith("alogging.ERROR:"), "Incorrect log level"
    assert lines[4].startswith("alogging.ERROR:"), "Incorrect log level"

    assert lines[0].endswith("123\n"), "Incorrect message"
    assert lines[1].endswith("345\n"), "Incorrect message"
    assert lines[2].endswith("567\n"), "Incorrect message"
    assert lines[3].endswith("789\n"), "Incorrect message"
    assert lines[4].endswith("0123\n"), "Incorrect message"


@pytest.mark.asyncio
async def test_basicConfig(start_backend, clean_file):
    alogging.basicConfig(
        filename="test.log",
        level=alogging.DEBUG,
        format="%(name)s - %(levelname)s - %(message)s",
    )

    log = alogging.getLogger(__name__)

    log.debug("1235")
    log.info("1236")
    log.warning("1237")
    log.error("1238")
    log.exception(Exception("1239"))

    time.sleep(0.5)

    with open(TEST_FILE_PATH, "r") as file:
        lines = file.readlines()

    assert len(lines) == 5, "Incorrect number of lines"

    assert lines[0].startswith("tests.test_logger - DEBUG -"), "Incorrect log level"
    assert lines[1].startswith("tests.test_logger - INFO -"), "Incorrect log level"
    assert lines[2].startswith("tests.test_logger - WARNING -"), "Incorrect log level"
    assert lines[3].startswith("tests.test_logger - ERROR -"), "Incorrect log level"
    assert lines[4].startswith("tests.test_logger - ERROR -"), "Incorrect log level"

    assert lines[0].endswith("1235\n"), "Incorrect message"
    assert lines[1].endswith("1236\n"), "Incorrect message"
    assert lines[2].endswith("1237\n"), "Incorrect message"
    assert lines[3].endswith("1238\n"), "Incorrect message"
    assert lines[4].endswith("1239\n"), "Incorrect message"


class MockServerRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        self.server.request_payload = post_data.decode("utf-8")


class MockServer(HTTPServer):
    def __init__(self, address, handler):
        super().__init__(address, handler)
        self.request_payload = None


@pytest.mark.asyncio
async def test_HTTPHandler(start_backend):
    server = MockServer(("localhost", 8080), MockServerRequestHandler)
    thread = Thread(target=server.serve_forever)
    thread.setDaemon(True)
    thread.start()

    handler = HTTPHandler("localhost:8080", "/post", method="POST")
    formatter = alogging.Formatter("%(name)s.%(levelname)s:%(message)s")
    handler.setFormatter(formatter)

    log = alogging.getLogger("alogging")
    log.addHandler(handler)

    log.debug("Test_message")

    time.sleep(0.5)

    assert server.request_payload is not None
    assert "Test_message" in server.request_payload

    server.shutdown()
    thread.join()
