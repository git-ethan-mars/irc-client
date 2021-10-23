import sys

from PyQt5.QtWidgets import QApplication

from Client import Client
from Controller import Controller
from LogInWindow import LogInWindow
from MainWindow import MainWindow



def main():
    client = Client()
    app = QApplication(sys.argv)
    current_window = LogInWindow()
    controller = Controller(client, current_window)
    current_window.controller = controller
    current_window.show()
    app.exec_()
    if not current_window.is_manual_exit:
        current_window = MainWindow()
        controller.window = current_window
        current_window.controller = controller
        current_window.show()
        app.lastWindowClosed.connect(lambda: current_window.controller.end_program())
        app.exec_()


if __name__ == '__main__':
    main()
