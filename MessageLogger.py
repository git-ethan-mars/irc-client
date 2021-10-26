import logging


class MessageLogger:
    def __init__(self):
        self._filename = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value
        logging.basicConfig(filename=self.filename, filemode='a+', format='%(asctime)s - %(message)s',
                            level=logging.INFO)
