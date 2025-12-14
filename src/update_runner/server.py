import json
import os
import socket
import struct
import threading
from typing import Any


class JsonRpcServer:
    def __init__(self) -> None:
        if os.name == "posix":
            self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            # todo: skip windows environment
            pass
        self._is_running = threading.Event()
        self._is_running.set()

    def start(self, socket_path: str) -> None:
        """
        引数のソケットパスをリッスンし、UDSサーバを起動します。

        Args:
            socket_path(str): ソケットファイルパス
        """

        self._server.bind(socket_path)
        self._server.listen(1)
        self._server.settimeout(1.0)

        while self._is_running.is_set():
            try:
                conn, _ = self._server.accept()
                with conn:
                    pass
                    # request = self.receive(conn)
                    # handle request
            except TimeoutError:
                continue
        self._server.close()

    def stop(self) -> None:
        self._is_running.clear()

    def _receive(self, conn: socket.socket) -> dict[Any, Any]:
        """クライアントから受けとったリクエストをjsonオブジェクトにして返します。"""
        raw_len = conn.recv(4)
        msg_len = struct.unpack(">I", raw_len)[0]  # big-endian
        data = conn.recv(msg_len)
        req = json.loads(data.decode())

        return req  # type: ignore
