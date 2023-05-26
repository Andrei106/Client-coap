import logging


class ExceptionBase(Exception):
    def __init__(self, message="Something wrong happened"):
        self.message = message
        logging.exception(self.message)
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


