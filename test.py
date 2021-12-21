import socket
import threading
import unittest
from unittest.mock import patch, MagicMock

from Client import Client
from Controller import Controller


class TestController(unittest.TestCase):
    def create_simple_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("localhost", 8080))
        s.settimeout(1)
        s.listen(1)
        self.barrier.wait()
        try:
            client_socket, address = s.accept()
            buffer = ""
            while True:
                if f"NICK {self.controller._client.nick}" in buffer:
                    buffer = buffer[buffer.find(f"NICK {self.controller._client.nick}") + len(
                        f"NICK {self.controller._client.nick}"):]
                    client_socket.sendall(b":server.chat 376 wda132 :End of /MOTD command.\r\n")
                if f"JOIN {self.controller._client.channel}" in buffer:
                    buffer = buffer[buffer.find(f"JOIN {self.controller._client.channel}") + len(
                        f"JOIN {self.controller._client.channel}"):]
                    client_socket.sendall(b"End of /NAMES list\r\n")
                if "LIST " in buffer:
                    buffer = buffer[buffer.find(f"LIST ") + len(f"LIST "):]
                    client_socket.sendall(b":server.chat 322 test123 #c 8 :\r\n")
                    client_socket.sendall(b":server.chat 322 test123 #python 3 :\r\n")
                    client_socket.sendall(b":server.chat 323 test123 :End of /LIST\r\n")
                if f"MODE {self.controller._client.channel}" in buffer:
                    buffer = buffer[buffer.find(f"MODE {self.controller._client.channel}") + len(
                        f"MODE {self.controller._client.channel}"):]
                    client_socket.sendall(b":server.chat 324 test123 #test +Cnst\r\n")
                    client_socket.sendall(b":server.chat 329 test123 #test 1622176711\r\n")
                if f"NAMES {self.controller._client.channel}" in buffer:
                    buffer = buffer[buffer.find(f"NAMES {self.controller._client.channel}") + len(
                        f"NAMES {self.controller._client.channel}"):]
                    client_socket.sendall(
                        b":server.chat 353 test123 = #test :test123 Guest62 Leonhardt ptl-tab grys ")
                    client_socket.sendall(b"ivanhoe\r\n")
                    client_socket.sendall(b":server.chat 366 test123 #test :End of /NAMES list.\r\n")
                if f"QUIT :Bye!" in buffer:
                    client_socket.sendall(b":channel!~channel31 QUIT :Client Quit\r\n")
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
        self.barrier = threading.Barrier(2, timeout=5)
        self.controller = Controller(Client(), MagicMock())
        self.thread = threading.Thread(target=self.create_simple_server)
        self.thread.start()
        self.barrier.wait()


    def tearDown(self) -> None:
        self.thread.join()

    @patch('Controller.create_warning')
    def test_try_join_with_empty_nick(self, mock_create_warning):
        self.controller.try_join_server("localhost:8080", "")
        self.controller._client.socket.close()
        mock_create_warning.assert_called_with("Type your nick")

    @patch('Controller.create_warning')
    def test_try_join_incorrect_server(self, mock_create_warning):
        self.controller.try_join_server("localhost:1", "test123")
        self.controller._client.socket.close()
        mock_create_warning.assert_called_with("Invalid server")

    def test_try_join_server(self):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.close_connection()

    @patch('Controller.create_warning')
    def test_try_join_server_with_wrong_format(self, mock_create_warning):
        self.controller.try_join_server("wrongformat:", "test123")
        self.controller._client.socket.close()
        mock_create_warning.assert_called_with("Invalid server format")

    @patch('Controller.create_warning')
    def test_connect_to_wrong_channel(self, mock_create_warning):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("")
        self.controller.close_connection()
        mock_create_warning.assert_called_with("Invalid channel")

    @patch.object(Controller, 'show_users')
    @patch('Controller.create_warning')
    def test_connect_to_same_channel(self, mock_create_warning, mock_show_users):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("#python")
        self.controller.connect("#python")
        self.controller.close_connection()
        mock_create_warning.assert_called_with("You are already on this channel")
        mock_show_users.assert_called_once()

    @patch.object(Controller, 'show_users')
    def test_connect_to_channel(self, mock_show_users):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("cocking ko ko ko")
        self.controller.close_connection()
        mock_show_users.assert_called_once()

    def test_get_users(self):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("test")
        self.controller.close_connection()

    def test_send_text(self):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("test")
        mock_text = MagicMock()
        mock_text.text.return_value = "Hello"
        self.controller.send_text(MagicMock(), mock_text)
        self.controller.close_connection()

    def test_send_list(self):
        self.controller.try_join_server("localhost:8080", "test123")
        self.controller.connect("test")
        mock_text = MagicMock()
        mock_text.text.return_value = "/list"
        self.controller.send_text(MagicMock(), mock_text)
        self.controller.close_connection()

    def test_get_channels(self):
        self.controller.try_join_server("localhost:8080", "test123")
        expected_value = self.controller.get_channels()
        self.controller.close_connection()
        self.assertSetEqual(set(expected_value), {'#python', '#c'})


if __name__ == '__main__':
    unittest.main()
