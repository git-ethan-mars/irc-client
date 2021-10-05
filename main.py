import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from LogInWindow import LogInWindow
from MainWindow import MainWindow
from client import Client


def main():
    client = Client()
    app = QApplication(sys.argv)
    log_in_window = QMainWindow()
    obj = LogInWindow(log_in_window, client)
    log_in_window.show()
    app.exec_()
    if not obj.is_manual_exit:
        main_window = QMainWindow()
        MainWindow(main_window, client)
        main_window.show()
        app.lastWindowClosed.connect(client.socket.close)
        app.exec_()


if __name__ == '__main__':
    main()