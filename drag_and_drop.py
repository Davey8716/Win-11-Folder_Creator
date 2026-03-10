from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QPainter,QColor
from PySide6.QtWidgets import QTreeWidget,QApplication
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, Signal


class SmartTreeWidget(QTreeWidget):

    fileDropped = Signal(str)
    addFolderShortcut = Signal()
    addSubfolderShortcut = Signal()
    saveTemplateShortcut = Signal()
    loadTemplateShortcut = Signal()

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

            window = self.window()

            for url in event.mimeData().urls():
                path = url.toLocalFile()
                low = path.lower()

                # ----------------------------
                # Template files (.json/.txt)
                # ----------------------------
                if low.endswith(".json") or low.endswith(".txt"):
                    self.fileDropped.emit(path)
                    continue

                # ----------------------------
                # Folder import
                # ----------------------------
                try:
                    from pathlib import Path

                    p = Path(path)

                    if p.is_dir():
                        window.service.nested_manager.import_folder_tree(path)

                        if hasattr(window, "update_build_button_state"):
                            window.update_build_button_state()

                except Exception:
                    pass

            event.acceptProposedAction()

        else:
            super().dropEvent(event)
                

    def keyPressEvent(self, event: QKeyEvent):

        window = self.window()

        # ---------------------------------------------------------
        # Paste indented text
        # ---------------------------------------------------------
        if event.matches(QKeySequence.Paste):
            clipboard = QApplication.clipboard()
            text = clipboard.text().strip()

            if text:
                try:
                    data = window.service.nested_manager.parse_indented_text(text)

                    self.clear()
                    window.service.nested_manager.deserialize_tree(data)

                    if hasattr(window, "update_build_button_state"):
                        window.update_build_button_state()

                except Exception:
                    pass

            return


        # ---------------------------------------------------------
        # Delete key support
        # ---------------------------------------------------------
        if event.key() == Qt.Key_Delete:
            item = self.currentItem()

            if item:
                parent = item.parent()

                if parent:
                    parent.removeChild(item)
                else:
                    index = self.indexOfTopLevelItem(item)
                    self.takeTopLevelItem(index)

                # refresh UI state
                if hasattr(window, "update_build_button_state"):
                    window.update_build_button_state()

            return


        # ---------------------------------------------------------
        # Ctrl + N  → Add Folder
        # ---------------------------------------------------------
        if (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_N and not (event.modifiers() & Qt.ShiftModifier):
            self.addFolderShortcut.emit()
            return


        # ---------------------------------------------------------
        # Ctrl + Shift + N → Add Subfolder
        # ---------------------------------------------------------
        if (event.modifiers() & Qt.ControlModifier) and (event.modifiers() & Qt.ShiftModifier) and event.key() == Qt.Key_N:
            self.addSubfolderShortcut.emit()
            return


        # ---------------------------------------------------------
        # Ctrl + S → Save Template
        # ---------------------------------------------------------
        if (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_S:
            self.saveTemplateShortcut.emit()
            return


        # ---------------------------------------------------------
        # Ctrl + O → Load Template
        # ---------------------------------------------------------
        if (event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_O:
            self.loadTemplateShortcut.emit()
            return


        # ---------------------------------------------------------
        # F2 → Rename
        # ---------------------------------------------------------
        if event.key() == Qt.Key_F2:
            item = self.currentItem()
            if item:
                self.editItem(item, 0)
            return


        super().keyPressEvent(event)