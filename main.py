import sys

from drag_and_drop import SmartTreeWidget
from desktop_folder_manager import DesktopFolderManager
from theme_controller import ThemeController
from template_IO_layer import TemplateService

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from nested_folder_manager import NestedFolderManager
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QAbstractItemView
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
    QCheckBox,
    QComboBox,
    QDial,

)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Folder Generator")
        self.setFixedSize(700, 1000)

        # ===== Central Widget =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(3)
        central_widget.setLayout(main_layout)

        # ==========================================================
        # HEADER SECTION — Title (Left) + Dial (Right)
        # ==========================================================

        header_row = QHBoxLayout()
        header_row.setSpacing(15)
        header_row.setContentsMargins(5,5,5,5)

        # ------------------------------
        # Main Title Frame (LEFT)  ✅ now tight
        # ------------------------------
        self.title_frame = QFrame()
        self.title_frame.setFrameShape(QFrame.StyledPanel)
        

        # Key: do NOT expand horizontally
        self.title_frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(14, 10, 14, 10)  # tweak as you like
        title_layout.setSpacing(0)
        title_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_frame.setLayout(title_layout)

        self.app_title = QLabel("Folder Generator")
        self.app_title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.app_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        title_layout.addWidget(self.app_title)

        # ------------------------------
        # Dial Frame (RIGHT)
        # ------------------------------
        self.dial_frame = QFrame()
        self.dial_frame.setFrameShape(QFrame.StyledPanel)
        self.dial_frame.setFixedWidth(120)

        dial_layout = QVBoxLayout()
        dial_layout.setContentsMargins(14,10,14,10)
        dial_layout.setAlignment(Qt.AlignCenter)
        self.dial_frame.setLayout(dial_layout)

        self.theme_controller = ThemeController()

        self.colour_accent_dial = QDial()
        self.colour_accent_dial.setFixedSize(80, 80)
        self.colour_accent_dial.setRange(0, self.theme_controller.theme_count() - 1)

        dial_layout.addWidget(self.colour_accent_dial)

        # ------------------------------
        # Add to Header Row  ✅ keep wheel spacing, pin right
        # ------------------------------
        header_row.addWidget(self.title_frame, 0, Qt.AlignTop)
        header_row.addWidget(self.title_frame, 0, Qt.AlignLeft)
        header_row.addStretch(1)
        header_row.addWidget(self.dial_frame, 0, Qt.AlignRight)

        main_layout.addLayout(header_row)
        main_layout.addSpacing(15)

        # ==========================================================
        # Desktop Section Title Frame
        # ==========================================================

        self.desktop_title_frame = QFrame()
        self.desktop_title_frame.setFrameShape(QFrame.StyledPanel)

        desktop_title_layout = QVBoxLayout()
        desktop_title_layout.setContentsMargins(8, 6, 8, 6)
        desktop_title_layout.setSpacing(0)
        self.desktop_title_frame.setLayout(desktop_title_layout)

        self.desktop_section_title = QLabel("Desktop Folder Creator")
        self.desktop_section_title.setAlignment(Qt.AlignLeft)

        desktop_title_layout.addWidget(self.desktop_section_title)

        main_layout.addWidget(self.desktop_title_frame)
        main_layout.addSpacing(6)   # tight title → frame
        

        # ==========================================================
        # FRAME 1 — Desktop Folder Creator
        # ==========================================================

        self.desktop_folder_frame = QFrame()
        self.desktop_folder_frame.setFrameShape(QFrame.StyledPanel)

        self.desktop_layout = QVBoxLayout()
        self.desktop_layout.setSpacing(6)
        self.desktop_layout.setContentsMargins(12, 12, 12, 12)
        self.desktop_folder_frame.setLayout(self.desktop_layout)

        # ---- Input Row ----
        self.desktop_folder_line = QLineEdit()
        self.desktop_folder_line.setPlaceholderText("Enter folder name...")
        self.desktop_folder_line.setFixedWidth(400)
        self.desktop_folder_line.setMinimumHeight(35)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_row.addWidget(self.desktop_folder_line)
        input_row.addStretch()

        self.desktop_layout.addLayout(input_row)

        # ---- Button + Timestamp Row ----
        self.folder_to_desktop = QPushButton("Folder_To_Desktop")
        self.folder_to_desktop.setFixedWidth(180)
        self.folder_to_desktop.setMinimumHeight(35)

        self.date_time_toggle = QCheckBox("Add Date Stamp")
        self.date_time_toggle.setMinimumHeight(35)

        self.date_time_config = QComboBox()
        self.date_time_config.setFixedWidth(200)
        self.date_time_config.setMinimumHeight(35)
        self.date_time_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])

        button_row = QHBoxLayout()
        button_row.setSpacing(63)
        button_row.addWidget(self.folder_to_desktop)
        button_row.addWidget(self.date_time_toggle)
        button_row.addWidget(self.date_time_config)
        button_row.addStretch()

        self.desktop_layout.addLayout(button_row)

        # ---- Status Label (NOW INSIDE FRAME, BELOW CONTROLS) ----
    
        self.desktop_status_frame = QFrame()
        self.desktop_status_frame.setObjectName("statusFrame")

        desktop_status_layout = QHBoxLayout()
        desktop_status_layout.setContentsMargins(10, 6, 10, 6)
        desktop_status_layout.setSpacing(8)
        self.desktop_status_frame.setLayout(desktop_status_layout)

        self.desktop_status_icon = QLabel("•")
        self.desktop_status_text = QLabel("")
        self.desktop_status_text.setWordWrap(True)

        desktop_status_layout.addWidget(self.desktop_status_icon)
        desktop_status_layout.addWidget(self.desktop_status_text)
        desktop_status_layout.addStretch()

        self.desktop_layout.addWidget(self.desktop_status_frame)



        # Add entire frame to main layout
        main_layout.addWidget(self.desktop_folder_frame)
        main_layout.addSpacing(20)   # BIG separation between sections
                
        # ==========================================================
        # FRAME 2 — Nested Folder Creator
        # ==========================================================

        # ---- Section Title Frame ----
        self.smart_title_frame = QFrame()
        self.smart_title_frame.setFrameShape(QFrame.StyledPanel)

        smart_title_layout = QVBoxLayout()
        smart_title_layout.setContentsMargins(8, 6, 8, 6)
        smart_title_layout.setSpacing(8)
        self.smart_title_frame.setLayout(smart_title_layout)

        self.smart_folder_creator = QLabel("Nested Folder Creator")
        self.smart_folder_creator.setAlignment(Qt.AlignLeft)

        smart_title_layout.addWidget(self.smart_folder_creator)

        main_layout.addWidget(self.smart_title_frame)
        main_layout.addSpacing(8)   # or whatever value you want

        # ---- Smart Frame ----
        self.smart_folder_creator_frame = QFrame()
        self.smart_folder_creator_frame.setFrameShape(QFrame.StyledPanel)

        self.smart_layout = QVBoxLayout()
        self.smart_layout.setSpacing(8)
        self.smart_layout.setContentsMargins(12, 12, 12, 12)
        self.smart_folder_creator_frame.setLayout(self.smart_layout)

        # ---- Base Path Field (Full Width Row) ----
        self.base_path_line = QLineEdit()
        self.base_path_line.setPlaceholderText(
            "Select base directory for output folder location"
        )
        self.base_path_line.setReadOnly(True)
        self.base_path_line.setMinimumHeight(35)

        self.smart_layout.addWidget(self.base_path_line)


        # ---- Base Path Buttons Row ----
        base_button_row = QHBoxLayout()
        base_button_row.setSpacing(8)

        self.default_to_desktop_btn = QPushButton("Default Desktop")
        self.browse_btn = QPushButton("Browse")

        for btn in [self.default_to_desktop_btn, self.browse_btn]:
            btn.setMinimumWidth(130)
            btn.setMinimumHeight(35)

        base_button_row.addWidget(self.default_to_desktop_btn)
        base_button_row.addWidget(self.browse_btn)

        self.smart_layout.addLayout(base_button_row)
        
        # ---- Tree Widget ----
        self.tree = SmartTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)

        self.tree.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        self.tree.setAlternatingRowColors(True)
        self.smart_layout.addWidget(self.tree)
        self.nested_manager = NestedFolderManager(self.tree)

        # ==========================================================
        # Editing + Template + Build Controls
        # ==========================================================

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(12)

        # ----------------------------------------------------------
        # Row 1 — Add + Timestamp
        # ----------------------------------------------------------

        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.add_folder_btn = QPushButton("Add Folder")
        self.add_subfolder_btn = QPushButton("Add Subfolder")

        self.nested_date_toggle = QCheckBox("Add Date Stamp")
        self.nested_date_config = QComboBox()
        self.nested_date_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])
        self.nested_date_config.setEnabled(True)

        for btn in [self.add_folder_btn, self.add_subfolder_btn]:
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(35)

        self.nested_date_config.setMinimumWidth(170)
        self.nested_date_config.setMinimumHeight(20)

        add_row.addWidget(self.add_folder_btn)
        add_row.addWidget(self.add_subfolder_btn)
        add_row.addStretch()
        add_row.addWidget(self.nested_date_toggle)
        add_row.addWidget(self.nested_date_config)

        controls_layout.addLayout(add_row)

        # ----------------------------------------------------------
        # Row 2 — Remove Controls
        # ----------------------------------------------------------

        remove_row = QHBoxLayout()
        remove_row.setSpacing(8)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_all_btn = QPushButton("Remove All")

        for btn in [self.remove_btn, self.remove_all_btn]:
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(35)

        remove_row.addWidget(self.remove_btn)
        remove_row.addWidget(self.remove_all_btn)
        remove_row.addStretch()

        controls_layout.addLayout(remove_row)


        # ----------------------------------------------------------
        # Row 3 — Template Controls
        # ----------------------------------------------------------

        template_row = QHBoxLayout()
        template_row.setSpacing(8)

        self.load_template_btn = QPushButton("Load Template")
        self.create_template_btn = QPushButton("Create Template")

        for btn in [self.load_template_btn, self.create_template_btn]:
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(35)

        template_row.addWidget(self.load_template_btn)
        template_row.addWidget(self.create_template_btn)

        controls_layout.addLayout(template_row)


        # ----------------------------------------------------------
        # Row 4 — Build (Primary Action)
        # ----------------------------------------------------------

        self.build_folders_btn = QPushButton("Build Folders")
        self.build_folders_btn.setMinimumHeight(40)

        controls_layout.addWidget(self.build_folders_btn)
        

        # Add entire control section
        self.smart_layout.addLayout(controls_layout)
        
        # ---- Nested Status Panel ----
        self.smart_status_frame = QFrame()
        self.smart_status_frame.setObjectName("statusFrame")

        smart_status_layout = QHBoxLayout()
        smart_status_layout.setContentsMargins(10, 6, 10, 6)
        smart_status_layout.setSpacing(8)
        self.smart_status_frame.setLayout(smart_status_layout)

        self.smart_status_icon = QLabel(">")
        self.smart_status_text = QLabel("")
        self.smart_status_text.setWordWrap(True)

        smart_status_layout.addWidget(self.smart_status_icon)
        smart_status_layout.addWidget(self.smart_status_text)
        smart_status_layout.addStretch()

        self.smart_layout.addWidget(self.smart_status_frame)


        # Add entire Smart frame to main layout
        main_layout.addWidget(self.smart_folder_creator_frame)

        # Signal Connections
        self.date_time_toggle.toggled.connect(self.desktop_on_date_stamp_toggled)
        self.nested_date_toggle.toggled.connect(self.nested_on_date_stamp_toggled)
        self.folder_to_desktop.clicked.connect(self.create_desktop_folder)
        self.build_folders_btn.clicked.connect(self.build_folders_from_tree)

        self.default_to_desktop_btn.clicked.connect(self.default_to_desktop)
        self.browse_btn.clicked.connect(self.select_base_directory)
        
        self.add_folder_btn.clicked.connect(self.nested_manager.add_root_folder)
        self.add_subfolder_btn.clicked.connect(self.nested_manager.add_subfolder)
        self.remove_btn.clicked.connect(self.nested_manager.remove_selected_folders)
        self.remove_all_btn.clicked.connect(self.nested_manager.remove_all_folders)
        self.create_template_btn.clicked.connect(self.create_template)
        self.load_template_btn.clicked.connect(self.load_template)

        self.tree.fileDropped.connect(self.load_template_from_path)
        
        # Apply initial theme
        initial_accent = self.theme_controller.apply_theme(0)
        self.apply_accent_styles(initial_accent)

        # React to dial changes
        self.colour_accent_dial.sliderReleased.connect(self.apply_selected_theme)
        
        self.desktop_folder_service = DesktopFolderManager()
        self.template_service = TemplateService()
        
    def default_to_desktop(self):
        desktop_path = self.desktop_folder_service.desktop_path
        self.base_path_line.setText(str(desktop_path))

        self.set_status(
            "Base directory set to Desktop.",
            target="nested",
            status_type="info"
        )
                
    def change_accent_theme(self, index: int):
        accent = self.theme_controller.apply_theme(index)
        self.apply_accent_styles(accent)
        
    def apply_accent_styles(self, accent_color: str):
        self.app_title.setStyleSheet(f"""
            QLabel {{
                font-size: 26px;
                font-weight: 600;
                color: {accent_color};
            }}
        """)

        self.smart_folder_creator.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 600;
                color: {accent_color};
            }}
        """)

        self.date_time_toggle.setStyleSheet(f"""
            QCheckBox {{
                font-weight: 600;
                color: {accent_color};
            }}
        """)
        
        self.nested_date_toggle.setStyleSheet(f"""
            QCheckBox {{                             
                font-weight: 600;
                color: {accent_color}
            }}                            

        """)
        
        self.desktop_section_title.setStyleSheet(f"""
            QLabel {{
                font-size: 22px;
                font-weight: 600;
                color: {accent_color};
            }}
        """)

        self.current_accent_color = accent_color
        
    def apply_selected_theme(self):
        index = self.colour_accent_dial.value()
        accent = self.theme_controller.apply_theme(index)
        self.apply_accent_styles(accent)
            
    def create_template(self):
        status, message = self.template_service.save_from_tree(
            self,                 # parent
            self.nested_manager    # tree manager
        )

        if status == "success":
            self.set_status(message, target="nested", status_type="success")
        elif status == "empty":
            self.set_status(message, target="nested", status_type="error")
        elif status != "cancelled":
            self.set_status(message, target="nested", status_type="error")
    
    def load_template(self):
        status, message = self.template_service.load_into_tree(
            self,                 # parent
            self.nested_manager    # tree manager
        )

        if status == "success":
            self.set_status(message, target="nested", status_type="success")
        elif status != "cancelled":
            self.set_status(message, target="nested", status_type="error")
                        
    def load_template_from_path(self, file_path):
        try:
            data = self.template_service.load_template(
                file_path,
                self.nested_manager.parse_indented_text
            )

            self.nested_manager.deserialize_tree(data)
            self.set_status("Template loaded via drag & drop", target="nested", status_type="success")

        except Exception:
            self.smart_status_text.setText("Error loading dropped file")

    def create_desktop_folder(self):
        mode = None

        if self.date_time_toggle.isChecked():
            text = self.date_time_config.currentText()

            if "ISO" in text:
                mode = "ISO"
            elif "UK" in text:
                mode = "UK"
            elif "US" in text:
                mode = "US"

        status, message = self.desktop_folder_service.create_folder(
            self.desktop_folder_line.text(),
            mode
        )

        if status == "success":
            stype = "success"
        elif status == "exists":
            stype = "info"
        else:  # "invalid" or "error"
            stype = "error"

        self.set_status(message, target="desktop", status_type=stype)
        
    def build_folders_from_tree(self):
        base_path = self.base_path_line.text().strip()

        if not base_path:
            self.set_status("No base directory selected.", target="nested", status_type="error")
            return

        mode = None
        if self.nested_date_toggle.isChecked():
            text = self.nested_date_config.currentText()
            if "ISO" in text:
                mode = "ISO"
            elif "UK" in text:
                mode = "UK"
            elif "US" in text:
                mode = "US"

        result = self.nested_manager.build_folders(base_path, mode)
        if result == "empty":
            self.set_status("Tree is empty.", target="nested", status_type="error")
        else:
            self.set_status("Folder structure created successfully.", target="nested", status_type="success")
            
        
    def select_base_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Base Directory"
        )

        if directory:
            self.base_path_line.setText(directory)
        

    def desktop_on_date_stamp_toggled(self, checked: bool):
        self.date_time_config.setEnabled(checked)
        
    def nested_on_date_stamp_toggled(self, checked: bool):
        self.nested_date_config.setEnabled(checked)
        
    def set_status(self, message: str, target: str = "desktop", status_type: str = "info"):
        """
        target: "desktop" or "nested"
        status_type: "info", "success", "error"
        """

        accent = getattr(self, "current_accent_color", "#2196F3")

        if target == "nested":
            icon_label = self.smart_status_icon
            text_label = self.smart_status_text
            frame = self.smart_status_frame
        else:
            icon_label = self.desktop_status_icon     # FIX
            text_label = self.desktop_status_text     # FIX
            frame = self.desktop_status_frame

        # Status styles
        if status_type == "success":
            icon_label.setText("✓")
            bg = "rgba(46, 204, 113, 0.15)"
        elif status_type == "error":
            icon_label.setText("✕")
            bg = "rgba(231, 76, 60, 0.15)"
        else:
            icon_label.setText("•")
            bg = "rgba(52, 152, 219, 0.10)"

        frame.setStyleSheet(f"""
            QFrame#statusFrame {{
                border-radius: 6px;
                background-color: {bg};
            }}
            QLabel {{
                font-size: 14px;
            }}
        """)

        # Make the icon follow the dial accent color
        icon_label.setStyleSheet(f"font-weight: 700; color: {accent};")
        text_label.setText(message)
        


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()