import re
import socket
import sys
import threading

from create_warning import create_warning


class Client:
    def __init__(self):
        self.nick = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = None
        self.channel = None
        self.on_server = False
        self.is_problem_happen = False
        self.thread = None

    def join_channel(self, channel):
        self.socket.send((f"JOIN " + channel + "\r\n").encode('utf-8'))
        self.channel = channel
        irc_message = ""
        while "End of /NAMES list" not in irc_message:
            irc_message = self.socket.recv(1024).decode("UTF-8")
            print(irc_message)
            if "Invite only channel" in irc_message or "you must be invited" in irc_message:
                create_warning("Invite only channel")
                self.is_problem_happen = True
                break
            elif "you are banned" in irc_message:
                create_warning("You have been banned!")
                self.is_problem_happen = True
                break
        else:
            self.is_problem_happen = False

    def join_server(self, server, nick):
        if nick:
            self.nick = nick
            regex = re.compile("[\w.]*?:[\d]+")
            try:
                if regex.fullmatch(server):
                    server = server.split(":")
                    self.socket.connect((server[0], int(server[1])))
                    self.server = server
                    self.socket.send(
                        (f"USER " + self.nick + " " + self.nick + " " + self.nick + " " + self.nick + "\r\n").encode(
                            'utf-8'))
                    self.socket.send((f"NICK " + self.nick + "\r\n").encode('utf-8'))

                    while True:
                        line = self.socket.recv(1024).decode('utf-8')
                        print(line)
                        if "This nickname is registered" in line:
                            create_warning("This nickname is registered")
                            return
                        elif "No nickname given" in line:
                            create_warning("No nickname given")
                            return
                        elif "Erroneous Nickname" in line:
                            create_warning("Invalid nickname")
                            return
                        elif "End of /MOTD" in line or "End of MOTD" in line:
                            break
                    self.on_server = True
                else:
                    create_warning("Invalid server format")
            except (socket.gaierror, OSError) as e:
                print(e)
                create_warning("Invalid server")
        else:
            create_warning("Type your nick")

    def send_message(self, message):
        self.socket.send((f"PRIVMSG " + self.channel + " " + message + "\r\n").encode('utf-8'))

    def get_users(self):
        self.socket.send((f"NAMES " + self.channel + "\r\n").encode('utf-8'))
        retry = ""
        data = ""
        while "End of /NAMES" not in data:
            data = self.socket.recv(1024).decode('utf-8').strip('\r\n')
            retry += data
        regex = re.compile(f"(?<={self.channel} :)([^:]*)")
        data = regex.findall(retry)[:-1]
        users = []
        for elem in data:
            users += elem.split()
        return users

    def get_channels(self):
        regex = re.compile("(?<=322 {0} )[#\w]*".format(self.nick))
        try:
            self.socket.send((f"LIST " + "\r\n").encode('utf-8'))
        except AttributeError:
            sys.exit()
        channels = []
        data = ""
        while "End of /LIST" not in data:
            data = regex.findall(data)
            channels += data
            reply = self.socket.recv(16384)
            try:
                data = reply.decode("utf-8").strip('\r\n')
            except UnicodeDecodeError:
                data = ""
        return channels

    def listen(self, chat):
        while True:
            try:
                retry = self.socket.recv(1024).decode('utf-8')
                if retry.startswith('PING'):
                    self.socket.send(f"PONG {self.channel}\r\n".encode('utf-8'))
                elif "PRIVMSG" in retry:
                    temp = retry.split()
                    chat.append(f"{temp[0].split('!')[0][1::]}: {' '.join(temp[3::])[1::]}")
            except UnicodeDecodeError:
                pass
            except ConnectionAbortedError:
                break

    def send_text(self, input_line, chat):
        if input_line.text() and self.channel and not self.is_problem_happen:
            if input_line.text() == "/list":
                channels = sorted(set(self.get_channels()))[1::]
                chat.append(" ".join(channels))
            else:
                self.socket.send(f"PRIVMSG {self.channel} :{input_line.text()}\r\n".encode("utf-8"))
                chat.append(f"{self.nick}: {input_line.text()}")
            input_line.setText("")

    def connect(self, fill_user_list, chat, channel_line):
        if not self.channel:
            if channel_line.text():
                channel = channel_line.text().split()[0].lower()
                if not channel.startswith('#'):
                    channel = '#' + channel
                if self.channel == channel:
                    create_warning("You are already on this channel")
                else:
                    self.join_channel(channel)
                    if not self.is_problem_happen:
                        users = sorted(list(set(self.get_users())))
                        fill_user_list(users)
                        self.thread = threading.Thread(target=self.listen, args=(chat,))
                        self.thread.start()
                    channel_line.setText(channel)
                    chat.clear()
            else:
                create_warning('Invalid channel')
        else:
            create_warning("You can choose the channel only once during the session")