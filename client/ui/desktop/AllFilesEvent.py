from .UiEvent import UiEvent


class AllFilesEvent(UiEvent):
    def __init__(self, files):
        super().__init__(files, 'allFiles')