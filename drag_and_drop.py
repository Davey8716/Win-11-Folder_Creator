
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget

class SmartTreeWidget(QTreeWidget):

    fileDropped = Signal(str)

    def __init__(self):
        super().__init__()

        self.setColumnCount(1)
        self.setHeaderHidden(True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event):
        print("drag enter")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
            
    def dragMoveEvent(self, event):  # ← ADD THIS
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                low = file_path.lower()
                if low.endswith(".json") or low.endswith(".txt"):
                    self.fileDropped.emit(file_path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)