import logging


class MessageLogger:
    def __init__(self):
        self._logger = logging.getLogger("MessageLogger")
        self._logger.setLevel(logging.INFO)
        self._formatter = logging.Formatter('%(asctime)s - %(message)s')

    def set_filename(self, filename: str):
        if self._logger.handlers:
            self._logger.handlers.clear()
        fh = logging.FileHandler(filename)
        fh.setFormatter(self._formatter)
        self._logger.addHandler(fh)

    def info(self, text: str):
        self._logger.info(text)
