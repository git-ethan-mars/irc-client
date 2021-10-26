import logging
import re
import socket
from threading import Thread

from PyQt5.QtWidgets import QMessageBox
from MessageLogger import MessageLogger
from Client import Client
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
        self.client = client
        self.window = window
        self.listener = None
        self.warning_text = None
        self._users = []
        self._channels = []
        self._data = []
        self._logger = MessageLogger()

    def try_join_server(self, server, nick):
        if nick:
            regex = re.compile("[\w.]*?:[\d]+")
            try:
                if regex.fullmatch(server):
                    server = server.split(":")
                    self.client.join_server(server, nick)
                    self.client.state = State.JOINING_SERVER
                    self.listener = Thread(target=self.listen_server)
                    self.listener.start()
                    while self.client.state == State.JOINING_SERVER:
                        pass
                    self.client.state = State.LISTENING
                    if self.client.on_server:
                        self.window.is_manual_exit = False
                        self.window.close()
                    else:
                        create_warning(self.warning_text)
                        self.client.state = State.CLOSE_CONNECTION
                        self.client.disconnect()
                        self.client.socket.close()
                        self.client.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                else:
                    create_warning("Invalid server format")
            except (socket.gaierror, OSError):
                # print(e)
                create_warning("Invalid server")
        else:
            create_warning("Type your nick")

    def get_channels(self):
        regex = re.compile("(?<=322 {0} )[#\w]*".format(self.client.nick))
        self.client.get_channels_list()
        self.client.state = State.RECEIVING_CHANNELS
        while self.client.state == State.RECEIVING_CHANNELS:
            pass
        channels = re.findall(regex, " ".join(self._channels))
        self._channels = []
        self._data = []
        return channels

    def send_text(self, chat, input_line):
        if input_line.text() and self.client.channel and not self.client.is_problem_happen:
            if input_line.text() == "/list":
                channels = sorted(set(self.get_channels()))[1::]
                chat.append(" ".join(channels))
            else:
                self.client.send_message(input_line.text())
                chat.append(f"{self.client.nick}: {input_line.text()}")
            logging.info(f"{self.client.nick}: {input_line.text()}")
            input_line.setText("")

    def connect(self, channel_line):
        if channel_line.text():
            channel = channel_line.text().split()[0].lower()
            if not channel.startswith('#'):
                channel = '#' + channel
            if self.client.channel == channel:
                create_warning("You are already on this channel")
            else:
                self.client.channel = channel
                self.client.state = State.JOINING_CHANNEL
                self.client.join_channel(channel)
                while self.client.state == State.JOINING_CHANNEL:
                    pass
                self.window.channel_line.setText(self.client.channel)
                self.window.chat.clear()
                self._logger.filename = f"log/{channel}.txt"
                self.client.state = State.LISTENING
                if not self.client.is_problem_happen:
                    self.client.state = State.RECEIVING_USERS
                    self.client.get_users()
                    while self.client.state == State.RECEIVING_USERS:
                        pass
                    self.window.fill_user_list(self._users)
                    self._users = []
                    self._data = []
                else:
                    create_warning(self.warning_text)
        else:
            create_warning('Invalid channel')

    def listen_server(self):
        while True:
            try:
                line = self.client.socket.recv(1024).decode('utf-8')
                print(line)
            except ConnectionAbortedError:
                break
            except UnicodeDecodeError:
                continue
            # print(self.client.state)
            if self.client.state == State.JOINING_SERVER:
                if "This nickname is registered" in line:
                    self.client.on_server = False
                    self.warning_text = "This nickname is registered"
                    self.client.state = State.LISTENING
                elif "No nickname given" in line:
                    self.client.on_server = False
                    self.warning_text = "No nickname given"
                    self.client.state = State.LISTENING
                elif "Erroneous Nickname" in line:
                    self.client.on_server = False
                    self.warning_text = "Invalid nickname"
                    self.client.state = State.LISTENING
                elif "End of /MOTD" in line or "End of MOTD" in line:
                    self.client.on_server = True
                    self.client.state = State.LISTENING
            elif self.client.state == State.JOINING_CHANNEL:
                if line.split()[1] == "470":
                    self.client.channel = line.split()[4]
                elif "End of /NAMES list" in line:
                    self.client.is_problem_happen = False
                    self.client.state = State.LISTENING
                elif "Invite only channel" in line or "you must be invited" in line:
                    self.client.is_problem_happen = True
                    self.warning_text = "Invite only channel"
                    self.client.state = State.LISTENING
                elif "you are banned" in line:
                    self.client.is_problem_happen = True
                    self.warning_text = "You have been banned!"
                    self.client.state = State.LISTENING
            elif self.client.state == State.RECEIVING_USERS:
                self._data.append(line)
                if "End of /NAMES" in line:
                    regex = re.compile(f"(?<={self.client.channel} :)([^:]*)")
                    for line in self._data[:-1]:
                        for users in re.findall(regex, line):
                            for user in users.replace("\r\n", "").split():
                                self._users.append(user)
                    # print(self._users)
                    self.client.state = State.LISTENING
            elif self.client.state == State.LISTENING:
                if line.startswith("PING"):
                    self.client.pong()
                elif line.split()[1] == "PRIVMSG":
                    self.window.chat.append(str(line.split()[0].split("!")[0][1::]) + ": " +
                                            str(line.split(f"PRIVMSG {self.client.channel} :")[-1].strip("\r\n")))
                    logging.info(str(line.split()[0].split("!")[0][1::]) + ": " +
                                 str(line.split(f"PRIVMSG {self.client.channel} :")[-1].strip("\r\n")))
            elif self.client.state == State.RECEIVING_CHANNELS:
                if "End of /LIST" in line:
                    self._data.append(line)
                    self._channels = self._data
                    self.client.state = State.LISTENING
                else:
                    self._data.append(line)
            elif self.client.state == State.CLOSE_CONNECTION:
                break

    def end_program(self):
        self.client.socket.shutdown(socket.SHUT_RDWR)
        self.client.state = State.CLOSE_CONNECTION
