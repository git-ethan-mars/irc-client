import socket
import threading
import unittest
from unittest.mock import patch, MagicMock

import State
from Client import Client
from Controller import Controller


class TestController(unittest.TestCase):
    def create_simple_server(self):
        with threading.Lock():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("localhost", 8080))
            s.settimeout(1)
            s.listen(1)
        try:
            client_socket, address = s.accept()
            buffer = ""
            while True:
                if f"NICK {self.controller._client.nick}" in buffer:
                    self.controller._client.state = State.State.LISTENING
                    self.controller._client.on_server = True
                    buffer = buffer[buffer.find(f"NICK {self.controller._client.nick}") + len(
                        f"NICK {self.controller._client.nick}"):]
                if f"JOIN {self.controller._client.channel}" in buffer:
                    self.controller._client.state = State.State.LISTENING
                    self.controller._client.is_problem_happen = False
                    buffer = buffer[buffer.find(f"JOIN {self.controller._client.channel}") + len(
                        f"JOIN {self.controller._client.channel}"):]
                if f"QUIT :Bye!" in buffer:
                    break
                else:
                    buffer += client_socket.recv(1024).decode('utf-8')
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
        except socket.timeout:
            pass
        finally:
            s.close()

    def setUp(self) -> None:
        self.controller = Controller(Client(), MagicMock())
        self.thread = threading.Thread(target=self.create_simple_server)
        self.thread.start()

    def tearDown(self) -> None:
        self.thread.join()

    @patch.object(threading.Thread, 'start')
    @patch('Controller.create_warning')
    def test_try_join(self, mock_create_warning, mock_thread_start):
        self.controller._client.create_socket()
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.close_connection()
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
        self.controller._client.create_socket()
        self.controller.try_join_server("localhost:1", "test123")
        self.controller._client.socket.close()
        mock_create_warning.assert_called_with("Invalid server")
        mock_thread_start.assert_not_called()

    @patch('Controller.create_warning')
    def test_connect_to_wrong_channel(self, mock_create_warning):
        self.controller.connect("")
        mock_create_warning.assert_called_with("Invalid channel")

    @patch('Controller.create_warning')
    def test_connect_to_same_channel(self, mock_create_warning):
        self.controller._client.channel = "#python"
        self.controller.connect("#python")
        mock_create_warning.assert_called_with("You are already on this channel")

    @patch.object(Controller, 'show_users')
    @patch.object(threading.Thread, 'start')
    def test_connect_to_channel(self, mock_thread_start, mock_show_users):
        self.controller._client.create_socket()
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("cocking ko ko ko")
        self.controller.close_connection()
        mock_thread_start.assert_called_once()
        mock_show_users.assert_called_once()


if __name__ == '__main__':
    unittest.main()
