import socket
import threading
import time
import unittest
from unittest.mock import patch

import State
from Client import Client
from Controller import Controller


class FakeWindow:
    def __init__(self):
        self.is_manual_exit = True

    def close(self):
        pass


class TestController(unittest.TestCase):
    def create_simple_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 8080))
            s.settimeout(3)
            s.listen(1)
            try:
                self.server_running = True
                client_socket, address = s.accept()
                buffer = ""
                while True:
                    if f"NICK {self.controller._client.nick}" in buffer:
                        self.controller._client.state = State.State.LISTENING
                        self.controller._client.on_server = True
                        break
                    else:
                        buffer += client_socket.recv(1024).decode('utf-8')
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
            except socket.timeout:
                pass

    def setUp(self) -> None:
        self.controller = Controller(Client(), FakeWindow())
        threading.Thread(target=self.create_simple_server).start()

    @patch.object(threading.Thread, 'start')
    @patch('Controller.create_warning')
    def test_try_join(self, mock_create_warning,mock_thread_start):
        self.server_running = False
        while not self.server_running:
            time.sleep(1)
        self.controller.try_join_server("localhost:8080", "test123")
        mock_thread_start.assert_called_once()
        mock_create_warning.assert_not_called()

    @patch.object(threading.Thread, 'start')
    @patch('Controller.create_warning')
    def test_try_join_with_incorrect_nick(self, mock_create_warning, mock_thread_start):
        self.controller.try_join_server("localhost:8080", "")
        mock_create_warning.assert_called_once()
        mock_thread_start.assert_not_called()

    @patch.object(threading.Thread, 'start')
    @patch('Controller.create_warning')
    def test_try_join_incorrect_server(self, mock_create_warning, mock_thread_start):
        self.controller.try_join_server("localhost:1", "test123")
        self.assertEqual(len(mock_create_warning.call_args.args), 1)
        self.assertEqual(mock_create_warning.call_args.args[0], "Invalid server")


if __name__ == '__main__':
    unittest.main()
