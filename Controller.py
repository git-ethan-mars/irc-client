import re
import socket
from threading import Thread
from time import localtime, strftime

from PyQt5.QtWidgets import QMessageBox, QLineEdit, QTextEdit

from Client import Client
from MessageLogger import MessageLogger
from State import State


def create_warning(message):
    warning = QMessageBox()
    warning.setText(message)
    warning.setWindowTitle("Warning")
    warning.setIcon(QMessageBox.Warning)
    warning.setStandardButtons(QMessageBox.Ok)
    warning.show()
    warning.exec_()


class Controller:
    def __init__(self, client: Client, window):
        self._client = client
        self.window = window
        self._listener = None
        self._warning_text = None
        self._users = []
        self._channels = []
        self._data = []
        self._logger = MessageLogger()

    def try_join_server(self, server: str, nick: str):
        if nick:
            regex = re.compile("[\w.]*?:[\d]+")
            try:
                if regex.fullmatch(server):
                    server = server.split(":")
                    self._client.state = State.JOINING_SERVER
                    self._client.join_server(server, nick)
                    self._listener = Thread(target=self.listen_server)
                    self._listener.start()
                    while self._client.state == State.JOINING_SERVER:
                        pass
                    self._client.state = State.LISTENING
                    if self._client.on_server:
                        self.window.is_manual_exit = False
                        self.window.close()
                    else:
                        create_warning(self._warning_text)
                        self.close_connection()
                        self._client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self._client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                else:
                    create_warning("Invalid server format")
            except (socket.gaierror, OSError):
                create_warning("Invalid server")
        else:
            create_warning("Type your nick")

    def get_channels(self):
        self._client.request_channels()
        self._client.state = State.RECEIVING_CHANNELS
        while self._client.state == State.RECEIVING_CHANNELS:
            pass
        channels = re.findall(re.compile("(?<=322 {0} )[#\w\n]*".format(self._client.nick)), " ".join(self._channels)
                              .replace("\n", ""))
        self._channels = []
        self._data = []
        return channels

    def send_text(self, chat: QTextEdit, input_line: QLineEdit):
        if input_line.text() and self._client.channel and not self._client.is_problem_happen:
            if input_line.text() == "/list" or input_line.text() == "/LIST":
                channels = sorted(set(self.get_channels()))[1::]
                chat.append(" ".join(channels))
            else:
                self._client.send_message(input_line.text())
                self.append_text_to_chat(self._client.nick, input_line.text())
            input_line.setText("")

    def get_users(self) -> list:
        self._client.state = State.RECEIVING_USERS
        self._client.request_users()
        while self._client.state == State.RECEIVING_USERS:
            pass
        regex = re.compile(f"(?<={self._client.channel} :)([^:]*)")
        for line in self._data:
            for users in re.findall(regex, line)[:-1]:
                for user in users.replace("\r\n", "").split():
                    self._users.append(user)

    def show_users(self):
        self.get_users()
        self.window.fill_user_list(self._users)
        self._users = []
        self._data = []

    def connect(self, channel: str):
        if channel:
            channel = channel.split()[0].lower()
            if not channel.startswith('#'):
                channel = '#' + channel
            if self._client.channel == channel:
                create_warning("You are already on this channel")
            else:
                self._client.channel = channel
                self._client.state = State.JOINING_CHANNEL
                self._client.join_channel(channel)
                while self._client.state == State.JOINING_CHANNEL:
                    pass
                self.window.channel_line.setText(self._client.channel)
                self.window.chat.clear()
                self._logger.set_filename(f"log/{channel}.txt")
                self._client.state = State.LISTENING
                if not self._client.is_problem_happen:
                    self.show_users()
                else:
                    create_warning(self._warning_text)
        else:
            create_warning('Invalid channel')

    def listen_server(self):
        while True:
            try:
                line = self._client.socket.recv(1024).decode('utf-8')
            except ConnectionAbortedError:
                break
            except UnicodeDecodeError:
                continue
            if self._client.state == State.CLOSE_CONNECTION or not line:
                break
            elif self._client.state == State.JOINING_SERVER:
                if "This nickname is registered" in line:
                    self._client.on_server = False
                    self._warning_text = "This nickname is registered"
                    self._client.state = State.LISTENING
                elif "No nickname given" in line:
                    self._client.on_server = False
                    self._warning_text = "No nickname given"
                    self._client.state = State.LISTENING
                elif "Erroneous Nickname" in line:
                    self._client.on_server = False
                    self._warning_text = "Invalid nickname"
                    self._client.state = State.LISTENING
                elif "Nickname is already in use" in line:
                    self._client.on_server = False
                    self._warning_text = "Nickname is already in use"
                    self._client.state = State.LISTENING
                elif "End of /MOTD" in line or "End of MOTD" in line:
                    self._client.on_server = True
                    self._client.state = State.LISTENING
            elif self._client.state == State.JOINING_CHANNEL:
                if line.split()[1] == "470":
                    self._client.channel = line.split()[4]
                elif "Invite only channel" in line or "you must be invited" in line:
                    self._client.is_problem_happen = True
                    self._warning_text = "Invite only channel"
                    self._client.state = State.LISTENING
                elif "you are banned" in line:
                    self._client.is_problem_happen = True
                    self._warning_text = "You have been banned!"
                    self._client.state = State.LISTENING
                elif "End of /NAMES list" or "End of NAMES list" in line:
                    self._client.is_problem_happen = False
                    self._client.state = State.LISTENING

            elif self._client.state == State.RECEIVING_USERS:
                self._data.append(line)
                if "End of /NAMES" or "End of NAMES list" in line:
                    self._client.state = State.LISTENING
            elif self._client.state == State.LISTENING:
                if line.startswith("PING"):
                    self._client.pong()
                elif line.split()[1] == "PRIVMSG":
                    user = str(line.split()[0].split("!")[0][1::])
                    text = str(line.split(f"PRIVMSG {self._client.channel} :")[-1].strip("\r\n"))
                    self.append_text_to_chat(user, text)
            elif self._client.state == State.RECEIVING_CHANNELS:
                if "End of /LIST" in line or "End of LIST" in line:
                    self._data.append(line)
                    self._channels = self._data
                    self._client.state = State.LISTENING
                else:
                    self._data.append(line)

    def close_connection(self):
        self._client.quit()
        self._client.state = State.CLOSE_CONNECTION
        self._listener.join()
        self._client.socket.shutdown(socket.SHUT_RDWR)
        self._client.socket.close()

    def append_text_to_chat(self, user: str, text: str):
        self.window.chat.append(f"{strftime('%H:%M:%S', localtime())} {user}: {text}")
        self._logger.info(f"{self._client.nick}: {text}")
