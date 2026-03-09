from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QPainter,QColor
from PySide6.QtWidgets import QTreeWidget, QAbstractItemView, QHeaderView

class SmartTreeWidget(QTreeWidget):

    fileDropped = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Animation method for the drag and drop functionality
        self.setAnimated(True)

        # ---- Drag & Drop configuration ----
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDrop)
        self.setDefaultDropAction(Qt.CopyAction)

        # ---- Placeholder state ----
        self._placeholder = ""
        self._placeholder_bold = False
        
        


    def setPlaceholderText(self, text: str, bold: bool = False):
        self._placeholder = text
        self._placeholder_bold = bold
        self.viewport().update()


    def paintEvent(self, event):
        super().paintEvent(event)

        if self.topLevelItemCount() != 0:
            return

        if not self._placeholder:
            return

        painter = QPainter(self.viewport())

        font = painter.font()
        font.setBold(self._placeholder_bold)
        painter.setFont(font)

        painter.setPen(QColor(140, 140, 140))

        painter.drawText(
            self.viewport().rect(),
            Qt.AlignCenter | Qt.TextWordWrap,
            self._placeholder
        )


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)


    def dragMoveEvent(self, event):
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
            
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            item = self.currentItem()

            if item:
                parent = item.parent()

                if parent:
                    parent.removeChild(item)
                else:
                    index = self.indexOfTopLevelItem(item)
                    self.takeTopLevelItem(index)

            return

        super().keyPressEvent(event)