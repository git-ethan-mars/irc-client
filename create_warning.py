from PyQt5.QtWidgets import QMessageBox


def create_warning(message):
    warning = QMessageBox()
    warning.setText(message)
    warning.setWindowTitle("Warning")
    warning.setIcon(QMessageBox.Warning)
    warning.setStandardButtons(QMessageBox.Ok)
    warning.exec_()


