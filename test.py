import socket
import threading
import unittest

from Client import Client


def create_simple_server():
    with socket.create_server(("localhost", 8888)) as s:
        s.listen(1)
        client_socket, address = s.accept()
        while True:
            data = client_socket.recv(1024)
            client_socket.send(data)
            if b"END SERVER\r\n" in data:
                break
        client_socket.close()


class ClientTest(unittest.TestCase):

    def setUp(self) -> None:
        self.client = Client()
        threading.Thread(target=create_simple_server).start()

    def tearDown(self) -> None:
        self.client.socket.close()

    def get_result(self):
        buffer = b""
        while b"END SERVER\r\n" not in buffer:
            data = self.client.socket.recv(1024)
            buffer += data
        return buffer.decode('utf-8').replace("END SERVER\r\n", "")

    def test_join_server(self):
        self.client.join_server(["localhost", 8888], "test")
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("USER test test test test\r\nNICK test\r\n", self.get_result())

    def test_join_channel(self):
        self.client.socket.connect(("localhost", 8888))
        channel = "#test"
        self.client.join_channel(channel)
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("JOIN " + channel + "\r\n", self.get_result())

    def test_get_users(self):
        self.client.socket.connect(("localhost", 8888))
        self.client.channel = "#qwerty"
        self.client.get_users()
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("NAMES #qwerty\r\n", self.get_result())

    def test_send_message(self):
        self.client.socket.connect(("localhost", 8888))
        self.client.channel = "#drive"
        self.client.send_message("KEKW")
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("PRIVMSG #drive :KEKW\r\n", self.get_result())

    def test_pong(self):
        self.client.socket.connect(("localhost", 8888))
        self.client.channel = "#qwer"
        self.client.pong()
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("PONG\r\n", self.get_result())

    def test_get_channels(self):
        self.client.socket.connect(("localhost", 8888))
        self.client.channel = "#pizza"
        self.client.get_channels_list()
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertEqual("LIST \r\n", self.get_result())

    def test_quit(self):
        self.client.socket.connect(("localhost", 8888))
        self.client.channel = "#pizza"
        self.client.quit()
        self.client.socket.send("END SERVER\r\n".encode('utf-8'))
        self.assertTrue(self.get_result().startswith("QUIT"))


if __name__ == '__main__':
    unittest.main()
