from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QFormLayout, QWidget, QLabel, QSizePolicy, QLineEdit, QPushButton


class LogInWindow(QMainWindow):
    def try_log_in(self):
        self.client.join_server(self.server_line.text(), self.nick_line.text())
        if self.client.on_server:
            self.is_manual_exit = False
            self.main_window.close()

    def __init__(self, main_window, client):
        super(LogInWindow, self).__init__()
        self.is_manual_exit = True
        self.main_window = main_window
        self.client = client
        self.main_window.setObjectName("IRC-client")
        self.main_window.resize(320, 81)
        self.central_widget = QWidget(self.main_window)
        self.central_widget_init()
        self.form_layout = QFormLayout(self.central_widget)
        self.form_layout.setObjectName("formLayout")
        self.server_text = QLabel(self.central_widget)
        self.server_text_init()
        self.form_layout.setWidget(0, QFormLayout.LabelRole, self.server_text)
        self.nick_text = QLabel(self.central_widget)
        self.nick_text_init()
        self.form_layout.setWidget(2, QFormLayout.LabelRole, self.nick_text)
        self.server_line = QLineEdit(self.central_widget)
        self.server_line_init()
        self.form_layout.setWidget(0, QFormLayout.FieldRole, self.server_line)
        self.nick_line = QLineEdit(self.central_widget)
        self.nick_line_init()
        self.form_layout.setWidget(2, QFormLayout.FieldRole, self.nick_line)
        self.push_button = QPushButton(self.central_widget)
        self.push_button_init()
        self.form_layout.setWidget(3, QFormLayout.SpanningRole, self.push_button)
        self.main_window.setCentralWidget(self.central_widget)
        self.translate = QtCore.QCoreApplication.translate
        self.set_translate()
        QtCore.QMetaObject.connectSlotsByName(self.main_window)

    def central_widget_init(self):
        self.central_widget.setStyleSheet("background-color: rgb(199, 255, 201);")
        self.central_widget.setObjectName("centralwidget")


    def server_text_init(self):
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.server_text.sizePolicy().hasHeightForWidth())
        self.server_text.setSizePolicy(size_policy)
        self.server_text.setObjectName("server_text")

    def nick_text_init(self):
        size_policy = QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.nick_text.sizePolicy().hasHeightForWidth())
        self.nick_text.setSizePolicy(size_policy)
        self.nick_text.setObjectName("nick_text")

    def server_line_init(self):
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.server_line.sizePolicy().hasHeightForWidth())
        self.server_line.setSizePolicy(size_policy)
        self.server_line.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.server_line.setObjectName("server_line")

    def nick_line_init(self):
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.nick_line.sizePolicy().hasHeightForWidth())
        self.nick_line.setSizePolicy(size_policy)
        self.nick_line.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.nick_line.setObjectName("nick_line")

    def push_button_init(self):
        self.push_button.setObjectName("pushButton")
        self.push_button.setStyleSheet("background-color: rgb(84, 218, 100);")
        self.push_button.clicked.connect(lambda: self.try_log_in())

    def set_translate(self):
        self.main_window.setWindowTitle(self.translate("MainWindow", "Log in"))
        self.server_text.setText(self.translate("MainWindow", "Server"))
        self.nick_text.setText(self.translate("MainWindow", "Nick"))
        self.push_button.setText(self.translate("MainWindow", "Log in"))