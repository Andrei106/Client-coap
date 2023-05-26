from .UiEvent import UiEvent


class FileEvent(UiEvent):
    def __init__(self, files):
        super().__init__(files, 'file')