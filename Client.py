import socket


class Client:
    def __init__(self):
        self.nick = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server = None
        self.channel = None
        self.on_server = False
        self.is_problem_happen = False
        self.state = None
        self.users = None

    def join_server(self, server: list, nick: str):
        self.socket.connect((server[0], int(server[1])))
        self.server = server
        self.nick = nick
        self.socket.sendall(
            (
                    f"USER " + self.nick + " " + self.nick + " " + self.nick + " " + self.nick + "\r\n").encode(
                'utf-8'))
        self.socket.sendall((f"NICK " + self.nick + "\r\n").encode('utf-8'))

    def join_channel(self, channel: str):
        self.socket.sendall((f"JOIN " + channel + "\r\n").encode('utf-8'))

    def get_users(self):
        self.socket.sendall((f"NAMES " + self.channel + "\r\n").encode('utf-8'))

    def send_message(self, message: str):
        self.socket.sendall((f"PRIVMSG " + self.channel + " :" + message + "\r\n").encode('utf-8'))


    def pong(self):
        self.socket.sendall((f"PONG" + "\r\n").encode('utf-8'))

    def get_channels_list(self):
        self.socket.sendall((f"LIST " + "\r\n").encode('utf-8'))

    def quit(self):
        self.socket.sendall((f"QUIT :Bye!" + "\r\n").encode('utf-8'))
