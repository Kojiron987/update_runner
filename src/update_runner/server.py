import json
import socket
import struct
from typing import Any

SOCKET_PATH = "/run/update_runner/uds.sock"

class JsonRpcServer:

    def receive(self, conn: socket.socket) -> dict[Any, Any]:
        """クライアントから受けとったリクエストをjsonオブジェクトにして返します。"""
        raw_len = conn.recv(4)
        msg_len = struct.unpack(">I", raw_len)[0] # big-endian
        data = conn.recv(msg_len)
        req = json.loads(data.decode())

        return req
