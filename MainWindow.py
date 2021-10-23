from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy, \
    QLineEdit, QListView, QTextEdit


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.controller = None
        self.setObjectName('MainWindow')
        self.resize(826, 449)
        self.setStyleSheet('background-color: rgb(202, 255, 201);')
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName('centralwidget')
        self.horizontalLayout_3 = QHBoxLayout(self.central_widget)
        self.horizontalLayout_3.setObjectName('horizontalLayout_3')
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName('verticalLayout')
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.connect_button = QPushButton(self.central_widget)
        self.connect_button_init()
        self.channel_line = QLineEdit(self.central_widget)
        self.channel_line_init()
        self.horizontalLayout.addWidget(self.channel_line)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName('horizontalLayout_2')
        self.chat = QTextEdit(self.central_widget)
        self.chat_init()
        self.horizontalLayout_2.addWidget(self.chat)
        self.user_list = QListView(self.central_widget)
        self.user_list_init()
        self.horizontalLayout_2.addWidget(self.user_list)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName('verticalLayout_3')
        self.input_line = QLineEdit(self.central_widget)
        self.verticalLayout_3.addWidget(self.input_line)
        self.input_line_init()
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 18)
        self.verticalLayout.setStretch(2, 1)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.setCentralWidget(self.central_widget)
        self._translate = QtCore.QCoreApplication.translate
        self.set_translate()

    def set_translate(self):
        self.setWindowTitle(self._translate('MainWindow', 'IRC-client'))
        self.connect_button.setText(self._translate('MainWindow', 'Connect'))
        self.channel_line.setText(self._translate('MainWindow', 'Type your channel'))
        self.input_line.setText(self._translate('MainWindow', 'Type your message'))
        QtCore.QMetaObject.connectSlotsByName(self)

    def connect_button_init(self):
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.connect_button.sizePolicy().hasHeightForWidth())
        self.connect_button.setSizePolicy(size_policy)
        font = QtGui.QFont()
        font.setFamily('Arial')
        font.setPointSize(12)
        self.connect_button.setFont(font)
        self.connect_button.setStyleSheet('background-color: rgb(170, 170, 127);\n'
                                          'background-color: rgb(0, 170, 127);')
        self.connect_button.setObjectName('connect_button')
        self.horizontalLayout.addWidget(self.connect_button)
        self.connect_button.clicked.connect(
            lambda: self.controller.connect(self.channel_line))

    def channel_line_init(self):
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.channel_line.sizePolicy().hasHeightForWidth())
        self.channel_line.setSizePolicy(size_policy)
        font = QtGui.QFont()
        font.setFamily('Arial')
        font.setPointSize(16)
        self.channel_line.setFont(font)
        self.channel_line.setStyleSheet('background-color: rgb(255, 255, 255);')
        self.channel_line.setObjectName('channel_line')

    def chat_init(self):
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.chat.setObjectName("chat")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.chat.setFont(font)

    def user_list_init(self):
        self.user_list.setStyleSheet('border-color: rgb(0, 170, 255);\n'
                                     'background-color: rgb(255, 255, 255);')
        self.user_list.setObjectName('user_list')
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.user_list.setFont(font)

    def input_line_init(self):
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.input_line.sizePolicy().hasHeightForWidth())
        self.input_line.setSizePolicy(size_policy)
        font = QtGui.QFont()
        font.setFamily('Arial')
        font.setPointSize(16)
        self.input_line.setFont(font)
        self.input_line.setStyleSheet('background-color: rgb(255, 255, 255);')
        self.input_line.setObjectName('input_line')
        self.input_line.returnPressed.connect(lambda: self.controller.send_text(self.input_line, self.chat))

    def fill_user_list(self, users):
        model = QtGui.QStandardItemModel()
        self.user_list.setModel(model)
        for elem in users:
            model.appendRow(QtGui.QStandardItem(elem))


