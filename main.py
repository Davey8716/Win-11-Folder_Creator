import sys
import json
import ctypes
from ctypes import wintypes
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QPushButton
from smart_folder_manager import SmartFolderManager
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QTreeWidget, QAbstractItemView
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFrame,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QLabel,
    QSizePolicy,
    
    
)
from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Folder Generator")
        self.setFixedSize(650,800)

        # ===== Central Widget =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)

        # ===== Title =====
        self.app_title = QLabel("Desktop Folder Generator")
        self.app_title.setAlignment(Qt.AlignCenter)
        self.app_title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 600;
                color: #FCF900;
                padding: 0px;
                margin: 0px;
            }
        """)
        main_layout.addWidget(self.app_title)
        
   

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        hwnd = self.winId().__int__()
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )
                
        # ==========================================================
        # FRAME 1 — Desktop Folder Creator
        # ==========================================================


        # ---- Status Label (NOW BELOW TITLE, ABOVE FRAME) ----
        self.desktop_label = QLabel("")
        self.desktop_label.setStyleSheet("color: #888;")
        self.desktop_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.desktop_label)


        # ---- Desktop Folder Frame ----
        self.desktop_folder_frame = QFrame()
        self.desktop_folder_frame.setFrameShape(QFrame.StyledPanel)

        self.desktop_layout = QVBoxLayout()
        self.desktop_layout.setSpacing(8)
        self.desktop_folder_frame.setLayout(self.desktop_layout)

        # Input Row
        self.desktop_folder_line = QLineEdit()
        self.desktop_folder_line.setPlaceholderText("Enter folder name...")
        self.desktop_folder_line.setFixedWidth(175)
        self.desktop_folder_line.setMinimumHeight(35)
        self.desktop_folder_line.setSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.Fixed
        )

        input_row = QHBoxLayout()
        input_row.addWidget(self.desktop_folder_line)
        input_row.addStretch()

        self.desktop_layout.addLayout(input_row)

        # Button
        self.folder_to_desktop = QPushButton("Folder_To_Desktop")
        self.folder_to_desktop.setFixedWidth(175)
        self.desktop_layout.addWidget(self.folder_to_desktop)

        main_layout.addWidget(self.desktop_folder_frame)


        # ---- Section Title (Between Frames) ----
        self.smart_folder_creator = QLabel("Nested Folder Creator")
        self.smart_folder_creator.setAlignment(Qt.AlignCenter)

        self.smart_folder_creator.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #FCF900;
                margin-top: 10px;
            }
        """)

        main_layout.addWidget(self.smart_folder_creator)
                
        # ==========================================================
        # FRAME 2 — Smart Folder Creator
        # ==========================================================
        self.smart_folder_creator_frame = QFrame()
        self.smart_folder_creator_frame.setFrameShape(QFrame.StyledPanel)
        
        self.smart_layout = QVBoxLayout()
        self.smart_layout.setSpacing(8)
        self.smart_folder_creator_frame.setLayout(self.smart_layout)

        # ---- Base Path Row ----
        path_row = QHBoxLayout()

        self.base_path_line = QLineEdit()
        self.base_path_line.setPlaceholderText("Select base directory...")
        self.base_path_line.setReadOnly(True)

        self.browse_btn = QPushButton("Browse")
    
        path_row.addWidget(self.base_path_line)
        path_row.addWidget(self.browse_btn)

        self.smart_layout.addLayout(path_row)

        # ---- Tree Widget ----
        self.tree = SmartTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)

        # Enable drag + drop reordering
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)

        # Enable inline editing
        self.tree.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        # Optional: nicer visuals
        self.tree.setAlternatingRowColors(True)
        
        self.tree.fileDropped.connect(self.load_template_from_path)

        self.smart_layout.addWidget(self.tree)

        self.smart_manager = SmartFolderManager(self.tree)
        
        # Add Frame 2 to the main layout (THIS IS MISSING)
        main_layout.addWidget(self.smart_folder_creator_frame)
        
        
        # Create grid layout
        button_grid = QGridLayout()

        # Create buttons
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_subfolder_btn = QPushButton("Add Subfolder")
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_all_btn = QPushButton("Remove All")
        self.create_template_btn = QPushButton("Create Template")
        self.build_structure_btn = QPushButton("Build Structure")
        self.load_template_btn = QPushButton("Load Template")

        # Optional: make all columns expand evenly
        for col in range(4):
            button_grid.setColumnStretch(col, 1)

        # Row 0
        button_grid.addWidget(self.add_folder_btn,      0, 0)
        button_grid.addWidget(self.remove_btn,          0, 1)
        button_grid.addWidget(self.create_template_btn, 0, 2)

        # Row 1
        button_grid.addWidget(self.add_subfolder_btn,   1, 0)
        button_grid.addWidget(self.load_template_btn,   1, 2)
        button_grid.addWidget(self.remove_all_btn,      1, 1)
        button_grid.addWidget(self.build_structure_btn, 1, 3)
        
        for btn in [
            self.add_folder_btn,
            self.add_subfolder_btn,
            self.remove_btn,
            self.remove_all_btn,
            self.create_template_btn,
            self.build_structure_btn,
            self.load_template_btn
        ]:
            btn.setMinimumWidth(150)
            
        self.smart_status_label = QLabel("")
        self.smart_status_label.setStyleSheet("color: #888;")
        self.smart_status_label.setAlignment(Qt.AlignLeft)

        main_layout.addWidget(self.smart_status_label)
                
        main_layout.addLayout(button_grid)


        # Connections (THESE ARE MISSING)
        self.folder_to_desktop.clicked.connect(self.create_desktop_folder)

        self.add_folder_btn.clicked.connect(self.smart_manager.add_root_folder)
        self.add_subfolder_btn.clicked.connect(self.smart_manager.add_subfolder)
        self.remove_btn.clicked.connect(self.smart_manager.remove_selected_folders)
        self.remove_all_btn.clicked.connect(self.smart_manager.remove_all_folders)

        self.create_template_btn.clicked.connect(self.create_template)
        self.load_template_btn.clicked.connect(self.load_template)
        self.build_structure_btn.clicked.connect(self.build_structure_from_tree)
        self.browse_btn.clicked.connect(self.select_base_directory)
        
    def build_structure_from_tree(self):
        base_path = self.base_path_line.text().strip()

        if not base_path:
            self.smart_status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    margin-top: 10px;
                }
            """)
            self.smart_status_label.setText("No base directory selected.")
            return

        result = self.smart_manager.build_structure(base_path)

        if result == "empty":
            self.smart_status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    margin-top: 10px;
                }
            """)
            self.smart_status_label.setText("Tree is empty.")
        else:
            self.smart_status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    margin-top: 10px;
                }
            """)
            self.smart_status_label.setText("Folder structure created successfully.")

    # ==============================================================
    # Logic
    # ==============================================================
    
    def create_template(self):
        if self.tree.topLevelItemCount() == 0:
            self.smart_status_label.setText("Tree is empty.")
            self.smart_status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    margin-top: 10px;
                }
            """)
                
            return

        # Ask user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return
        
        template_data = self.smart_manager.serialize_tree()

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template_data, f, indent=4)

            self.smart_status_label.setText("Template saved successfully")

        except Exception:
            self.smart_status_label.setText("Error saving template")

    def load_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Template",
            "",
            "Templates (*.json *.txt);;JSON Files (*.json);;Text Outline (*.txt)"
        )

        if not file_path:
            return

        try:
            data = self.load_template_any(file_path)
            self.smart_manager.deserialize_tree(data)
            self.smart_status_label.setText("Template loaded")
            self.smart_status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    padding: 0px;
                    margin: 0px;
                }
            """)
        except Exception as e:
            print(e)
            self.smart_status_label.setText("Error loading template")

    def create_desktop_folder(self):
        folder_name = self.desktop_folder_line.text().strip()

        if not folder_name:
            self.desktop_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.desktop_label.setText("No folder name was entered.")
            return

        desktop_path = Path.home() / "Desktop"
        new_folder_path = desktop_path / folder_name

        try:
            new_folder_path.mkdir(exist_ok=False)

            self.desktop_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;   /* success */
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.desktop_label.setText(
                f'The folder "{folder_name}" was created on Desktop.'
            )

        except FileExistsError:
            self.desktop_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #FCF900;   /* warning */
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.desktop_label.setText("Folder already exists.")

        except Exception:
            self.desktop_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: 600;
                    color: #F44336;   /* error */
                    padding: 0px;
                    margin: 0px;
                }
            """)
            self.desktop_label.setText("Error creating folder")

    def select_base_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Base Directory"
        )

        if directory:
            self.base_path_line.setText(directory)
            
            
    
    def load_template_from_path(self, file_path):
        try:
            data = self.load_template_any(file_path)
            self.smart_manager.deserialize_tree(data)
            self.smart_status_label.setText("Template loaded via drag & drop")
            self.smart_status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #FCF900;
                padding: 0px;
                margin: 0px;
            }
        """)
        except Exception as e:
            print(e)
            self.desktop_label.setText("Error loading dropped file")
        



    def load_template_any(self,file_path: str):
        p = Path(file_path)
        ext = p.suffix.lower()

        if ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        if ext in (".txt", ".tree", ".outline"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return self.smart_manager.parse_indented_text(text)

        raise ValueError(f"Unsupported template file type: {ext}")

class SmartTreeWidget(QTreeWidget):

    fileDropped = Signal(str)

    def __init__(self):
        super().__init__()

        self.setColumnCount(1)
        self.setHeaderHidden(True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)

        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event):
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

            

def main():
    app = QApplication(sys.argv)

    apply_stylesheet(app, theme="dark_yellow.xml")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()