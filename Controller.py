import re
import socket
import time
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
        self._modes = None

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
                        time.sleep(0.1)
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
            time.sleep(0.1)
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

    def show_users(self):
        regex = re.compile(f"(?<=353 {self._client.nick} [=@] {self._client.channel} :)([^:]*)")
        for line in self._data:
            for users in re.findall(regex, line):
                for user in users.replace("\r\n", "").split():
                    self._users.append(user)
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
                if self._client.channel:
                    self._client.depart_channel(self._client.channel)
                self._client.channel = channel
                self._client.state = State.JOINING_CHANNEL
                self._client.join_channel(channel)
                while self._client.state == State.JOINING_CHANNEL:
                    time.sleep(0.1)
                self.window.channel_line.setText(self._client.channel)
                self.window.chat.clear()
                self._client.state = State.RECEIVING_MODES
                self._client.get_channel_modes(self._client.channel)
                while self._client.state == State.RECEIVING_MODES:
                    time.sleep(0.1)
                if "i" in self._modes:
                    self._client.is_problem_happen = True
                    self._warning_text = "Invite only channel"
                self.show_users()
                if not self._client.is_problem_happen:
                    self._logger.set_filename(f"log/{channel}.txt")
                else:
                    create_warning(self._warning_text)


        else:
            create_warning('Invalid channel')

    def listen_server(self):
        buffer = ""
        while True:
            try:
                if "\r\n" in buffer:
                    temp = buffer.split("\r\n")
                    message = temp[0]
                    buffer = "\r\n".join(temp[1:])
                else:
                    buffer += self._client.socket.recv(1024).decode('utf-8')
                    if "\r\n" in buffer:
                        temp = buffer.split("\r\n")
                        message = temp[0]
                        buffer = "\r\n".join(temp[1:])
                    else:
                        continue
            except ConnectionAbortedError:
                break
            except UnicodeDecodeError:
                continue
            print(message)
            if self._client.state == State.CLOSE_CONNECTION:
                break
            elif self._client.state == State.JOINING_SERVER:
                if "This nickname is registered" in message:
                    self._client.on_server = False
                    self._warning_text = "This nickname is registered"
                    self._client.state = State.LISTENING
                elif "No nickname given" in message:
                    self._client.on_server = False
                    self._warning_text = "No nickname given"
                    self._client.state = State.LISTENING
                elif "Erroneous Nickname" in message:
                    self._client.on_server = False
                    self._warning_text = "Invalid nickname"
                    self._client.state = State.LISTENING
                elif "Nickname is already in use" in message:
                    self._client.on_server = False
                    self._warning_text = "Nickname is already in use"
                    self._client.state = State.LISTENING
                elif "End of /MOTD" in message or "End of MOTD" in message:
                    self._client.on_server = True
                    self._client.state = State.LISTENING
            elif self._client.state == State.JOINING_CHANNEL:
                if message.split()[1] == "470":
                    self._client.channel = message.split()[4]
                elif "you are banned" in message:
                    self._client.is_problem_happen = True
                    self._warning_text = "You have been banned!"
                    self._client.state = State.LISTENING
                elif "End of /NAMES list" in message or "End of NAMES list" in message:
                    self._client.is_problem_happen = False
                    self._client.state = State.LISTENING
                elif "you must be invited" in message:  # 473
                    self._client.is_problem_happen = True
                    self._warning_text = "You must be invited"
                    self._client.state = State.LISTENING
                else:
                    self._data.append(message)
            elif self._client.state == State.RECEIVING_MODES:
                if message.split()[1] == "324":
                    self._modes = message.split()[4]
                self._client.state = State.LISTENING
            elif self._client.state == State.LISTENING:
                if message.startswith("PING"):
                    self._client.pong()
                elif message.split()[1] == "PRIVMSG":
                    user = str(message.split()[0].split("!")[0][1::])
                    text = message.split(f"PRIVMSG {self._client.channel} :")[-1]
                    self.append_text_to_chat(user, text)
            elif self._client.state == State.RECEIVING_CHANNELS:
                if "End of /LIST" in message or "End of LIST" in message:
                    self._channels = self._data
                    self._client.state = State.LISTENING
                else:
                    self._data.append(message)

    def close_connection(self):
        self._client.quit()
        self._client.state = State.CLOSE_CONNECTION
        self._listener.join()
        self._client.socket.shutdown(socket.SHUT_RDWR)
        self._client.socket.close()

    def append_text_to_chat(self, user: str, text: str):
        self.window.chat.append(f"{strftime('%H:%M:%S', localtime())} {user}: {text}")
        self._logger.info(f"{self._client.nick}: {text}")
