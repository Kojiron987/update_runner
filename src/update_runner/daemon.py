import signal
import threading
import time
from threading import Thread
from typing import Any

from update_runner.server import JsonRpcServer

SOCKET_PATH = "/run/update_runner/uds.sock"


class Daemon:
    def __init__(self) -> None:
        self._server = JsonRpcServer()
        self._server_thread = Thread(
            args=(self._server.start, SOCKET_PATH), daemon=True
        )
        self._is_running = threading.Event()

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def run(self) -> None:
        self._is_running.set()

        self._server_thread.run()

        # main thread listens signal
        while self._is_running.is_set():
            time.sleep(0.5)

    def _handle_signal(self, signum: int, frame: Any) -> None:
        self._server.stop()
        self._server_thread.join()

        self._is_running.clear()
