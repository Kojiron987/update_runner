import json
import struct
from unittest.mock import MagicMock, call

from update_runner.server import JsonRpcServer


def test_read_correct_request():
    sut = JsonRpcServer()

    request = {
        "jsonrpc": "2.0",
        "method": "install",
        "params": {
            "package_path": "/tmp/package.tar.gz",
            "id": 1,
        },
    }

    data = json.dumps(request).encode()
    data_length = struct.pack(">I", len(data))

    def recv_side_effect():
        call_count = 0

        def impl(_: int):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return data_length
            if call_count == 2:
                return data
            raise Exception("Unexpected call count")

        return impl

    conn = MagicMock()
    conn.recv.side_effect = recv_side_effect()

    actual = sut._receive(conn)

    conn.assert_has_calls([call.recv(4), call.recv(len(data))])

    assert actual == request
