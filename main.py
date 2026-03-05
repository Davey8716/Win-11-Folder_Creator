import sys
import os  

from drag_and_drop import SmartTreeWidget
from desktop_folder_manager import DesktopFolderManager
from theme_controller import ThemeController
from template_IO_layer import TemplateService
from pathlib import Path

from state_manager import StateManager
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy
from nested_folder_manager import NestedFolderManager
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
    QGridLayout

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
        self.desktop_folder_line.setFixedWidth(180)
        self.desktop_folder_line.setMinimumHeight(35)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_row.addWidget(self.desktop_folder_line)
        input_row.addStretch()

        self.desktop_layout.addLayout(input_row)

        # ---- Button + Timestamp Row ----
        self.folder_to_desktop = QPushButton("Folder To Desktop")
        self.folder_to_desktop.setFixedWidth(180)
        self.folder_to_desktop.setMinimumHeight(35)

        self.date_time_toggle = QCheckBox("Add Date Stamp")
        self.date_time_toggle.setMinimumHeight(35)
        self.date_time_toggle.setFixedWidth(180)

        self.date_time_config = QComboBox()
        self.date_time_config.setFixedWidth(160)
        self.date_time_config.setMinimumHeight(35)

        self.date_time_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])

        self.date_time_config.setEnabled(False)

        # Align dropdown items
        for i in range(self.date_time_config.count()):
            self.date_time_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        # Align displayed text
        self.date_time_config.setEditable(True)
        self.date_time_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_time_config.lineEdit().setReadOnly(True)

        # ---- Controls Grid ----
        desktop_controls = QGridLayout()
        desktop_controls.setHorizontalSpacing(10)
        desktop_controls.setVerticalSpacing(6)

        # Row 0
        desktop_controls.addWidget(self.desktop_folder_line, 0, 0)
        desktop_controls.addWidget(self.date_time_toggle, 0, 2)

        # Row 1
        desktop_controls.addWidget(self.folder_to_desktop, 1, 0)
        desktop_controls.addWidget(self.date_time_config, 1, 2)

        desktop_controls.setColumnStretch(1, 1)

        self.desktop_layout.addLayout(desktop_controls)
            













        # ---- Status Label (NOW INSIDE FRAME, BELOW CONTROLS) ----
    
        self.desktop_status_frame = QFrame()
        self.desktop_status_frame.setObjectName("statusFrame")

        desktop_status_layout = QHBoxLayout()
        desktop_status_layout.setContentsMargins(10, 6, 10, 6)
        desktop_status_layout.setSpacing(8)
        self.desktop_status_frame.setLayout(desktop_status_layout)

        self.desktop_status_icon = QLabel(">")
        self.desktop_status_text = QLabel("")
        self.desktop_status_text.setWordWrap(True)

        desktop_status_layout.addWidget(self.desktop_status_icon)
        desktop_status_layout.addWidget(self.desktop_status_text)
        desktop_status_layout.addStretch()

        self.desktop_layout.addWidget(self.desktop_status_frame)
        
        # Add entire frame to main layout
        main_layout.addWidget(self.desktop_folder_frame)
        main_layout.addSpacing(20)   # BIG separation between sections













        # ---- Smart Frame ----
        self.smart_folder_creator_frame = QFrame()
        self.smart_folder_creator_frame.setFrameShape(QFrame.StyledPanel)

        self.smart_layout = QVBoxLayout()
        self.smart_layout.setSpacing(8)
        self.smart_layout.setContentsMargins(12, 12, 12, 12)
        self.smart_folder_creator_frame.setLayout(self.smart_layout)
        
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










        # ==========================================================
        # Editing + Template + Build Controls  (GRID)
        # ==========================================================

        controls_layout = QGridLayout()
        controls_layout.setHorizontalSpacing(5)
        controls_layout.setVerticalSpacing(8)

        self.add_folder_btn = QPushButton("Add Folder")
        self.add_subfolder_btn = QPushButton("Add Subfolder")

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_all_btn = QPushButton("Remove All")

        self.create_template_btn = QPushButton("Create Template")
        self.load_user_template_dropdown = QComboBox()
        self.load_user_template_dropdown.addItems([
            "User Template"
        ])
    

        # Insert separator at end
        self.load_user_template_dropdown.insertSeparator(
            self.load_user_template_dropdown.count()
        )
        
        self.load_user_template_dropdown.setEnabled(True)

        self.load_default_template_dropdown = QComboBox()
        
        self.load_default_template_dropdown.addItem("Default Templates")
        
        
        self.load_default_template_dropdown.insertSeparator(
            self.load_default_template_dropdown.count()
        )
    
        self.load_default_template_dropdown.addItems([
            "Architects",
            "Creative Writers",
            "Data Scientists",
            "Game Developers",
            "It Administrators",
            "Photographers",
            "Project Management",
            "Researchers",
            "Software Developers",
            "Video Editing"
            
        ])
        
        
        # make the widget wide enough to show the longest entry
        self.load_default_template_dropdown.setMinimumWidth(160)
        # optional: let it grow if the layout allows
        self.load_default_template_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.load_default_template_dropdown.setEnabled(True)
        
        for i in range(self.load_default_template_dropdown.count()):
            self.load_default_template_dropdown.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )
            
        self.nested_date_toggle = QCheckBox("Add Date Stamp  To Parent Folder")
        
        self.auto_enumerate_folders = QCheckBox("Auto Number + \nName Folders/Sub Folders")
        

        self.nested_date_config = QComboBox()
        self.nested_date_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])
        self.nested_date_config.setEnabled(False)

        # Align dropdown items
        for i in range(self.nested_date_config.count()):
            self.nested_date_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        # Align the currently displayed text
        self.nested_date_config.setEditable(True)
        self.nested_date_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.nested_date_config.lineEdit().setReadOnly(True)

        self.nested_date_config.setMinimumHeight(35)

        for btn in [
            self.add_folder_btn, self.add_subfolder_btn,
            self.remove_btn, self.remove_all_btn,
            self.create_template_btn,
        ]:
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(35)

    
        self.nested_date_config.setMinimumWidth(140)
        self.nested_date_config.setMinimumHeight(35)

        controls_layout.addWidget(self.add_folder_btn,      0,1)
        controls_layout.addWidget(self.add_subfolder_btn,   1,1)
        controls_layout.addWidget(self.nested_date_toggle,  0, 2)
        controls_layout.addWidget(self.nested_date_config,  1, 2)
        controls_layout.addWidget(self.auto_enumerate_folders, 2,2,1,2)

        controls_layout.addWidget(self.remove_btn,             2,1)
        controls_layout.addWidget(self.remove_all_btn,         3,1)
        

        controls_layout.addWidget(self.create_template_btn, 0, 0)
        controls_layout.addWidget(self.load_user_template_dropdown, 1, 0)
        controls_layout.addWidget(self.load_default_template_dropdown, 2, 0)
        
        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 1)
        controls_layout.setColumnStretch(2, 1)
                

        self.smart_layout.addLayout(controls_layout)


    
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################







        
                
        # ---- Tree Widget ----
        self.tree = SmartTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)

        self.tree.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )
        
        self.tree.setPlaceholderText(
            (
                "Files can either be drag drop loaded in here\n"
                "(accepts json and txt files)\n"
                "or created/loaded using the buttons below.\n\n"
                "Tip: Drag and drop folders to change hierarchy.\n"
                "Tip: Drag a folder below another folder to create a new parent-level folder.\n\n"
                "Tip: Drag a folder onto another folder to nest it as a subfolder.\n\n"
                "Tip: Auto-numbering only applies when using the Add Folder / Add Subfolder buttons.\n"
                "Drag-and-drop only changes the folder structure."
            ),
            bold=True
        )
                
        self.tree.setAlternatingRowColors(True)
        self.smart_layout.addWidget(self.tree)
        self.nested_folder_manager = NestedFolderManager(self.tree)

################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################

        

       

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
        self.build_folders_btn = QPushButton("Build Folders")
    
        self.open_folder_build_toggle = QCheckBox("Open Folder After Build")
        self.minimize_after_build_toggle = QCheckBox("Minimized After Build")
        self.open_folder_build_toggle.setMinimumWidth(200)
        self.minimize_after_build_toggle.setMinimumWidth(200)
        
        
        base_controls = QGridLayout()
        base_controls.setHorizontalSpacing(8)
        base_controls.setVerticalSpacing(6)

        # Button sizes
        for btn in [
            self.default_to_desktop_btn,
            self.browse_btn,
            self.build_folders_btn
        ]:
            btn.setMinimumWidth(120)
            btn.setMinimumHeight(35)

        # Toggle sizes
        for toggle in [
            self.open_folder_build_toggle,
            self.minimize_after_build_toggle
        ]:
            toggle.setMinimumHeight(35)

        # Row 0
        base_controls.addWidget(self.default_to_desktop_btn, 0, 0)
        base_controls.addWidget(self.browse_btn,             0, 1)

        # expanding spacer column
        base_controls.setColumnStretch(2, 1)

        base_controls.addWidget(self.open_folder_build_toggle, 0, 3)

        # Row 1
        base_controls.addWidget(self.build_folders_btn, 1, 0)
        base_controls.addWidget(self.minimize_after_build_toggle, 1, 3)

        self.smart_layout.addLayout(base_controls)
        
        
        
        
        
        
        
        
        
        
        
        # ---- Nested Status Panel (put back if you want it visible) ----
        self.smart_status_frame = QFrame()
        self.smart_status_frame.setObjectName("statusFrame")

        smart_status_layout = QHBoxLayout(self.smart_status_frame)
        smart_status_layout.setContentsMargins(10, 6, 10, 6)
        smart_status_layout.setSpacing(8)

        self.smart_status_icon = QLabel(">")
        self.smart_status_text = QLabel("")
        self.smart_status_text.setWordWrap(True)

        smart_status_layout.addWidget(self.smart_status_icon)
        smart_status_layout.addWidget(self.smart_status_text)
        smart_status_layout.addStretch()

        self.smart_layout.addWidget(self.smart_status_frame)

        # ---- THIS is the other missing line ----
        main_layout.addWidget(self.smart_folder_creator_frame)

































































































        # Signal Connections
        self.date_time_toggle.toggled.connect(self.desktop_on_date_stamp_toggled)
        self.nested_date_toggle.toggled.connect(self.nested_on_date_stamp_toggled)
        self.folder_to_desktop.clicked.connect(self.create_desktop_folder)
        self.build_folders_btn.clicked.connect(self.build_folders_from_tree)

        self.default_to_desktop_btn.clicked.connect(self.default_to_desktop)
        self.browse_btn.clicked.connect(self.select_base_directory)
        self.auto_enumerate_folders.toggled.connect(self.toggle_auto_number_folders)
        
        self.add_folder_btn.clicked.connect(self.nested_folder_manager.add_root_folder)
        self.add_subfolder_btn.clicked.connect(self.nested_folder_manager.add_subfolder)
        self.remove_btn.clicked.connect(self.nested_folder_manager.remove_selected_folders)
        self.remove_all_btn.clicked.connect(self.nested_folder_manager.remove_all_folders)
        self.create_template_btn.clicked.connect(self.create_template)
        
        # Placeholders to connect to the user and default template drops to their respective methods.
        
        # self.load_user_template_dropdown.clicked.connect(self.load_template)
        self.load_default_template_dropdown.currentIndexChanged.connect(self.load_default_template)
        
        self.open_folder_build_toggle.toggled.connect(
            lambda v: self.state_manager.update("open_folder_after_build", v)
        )

        self.minimize_after_build_toggle.toggled.connect(
            lambda v: self.state_manager.update("minimize_after_build", v)
        )
        

        self.tree.fileDropped.connect(self.load_template_from_path)
        
        self.desktop_status_timer = QTimer(self)
        self.desktop_status_timer.setSingleShot(True)
        self.desktop_status_timer.timeout.connect(lambda: self.reset_status("desktop"))

        self.smart_status_timer = QTimer(self)
        self.smart_status_timer.setSingleShot(True)
        self.smart_status_timer.timeout.connect(lambda: self.reset_status("nested"))
                        
        # Apply initial theme
        initial_accent = self.theme_controller.apply_theme(6)
        self.apply_accent_styles(initial_accent)

        # React to dial changes
        self.colour_accent_dial.sliderReleased.connect(self.apply_selected_theme)
        
        # Loading of object instances
        self.desktop_folder_service = DesktopFolderManager()
        self.template_service = TemplateService()
        self.state_manager = StateManager()
        
        
        
        
        state = self.state_manager.load_state()
        
    
        # ---------------------------------------------------------
        # Restore Theme Dial
        # ---------------------------------------------------------
        theme_index = state.get("theme_index", 0)

        self.colour_accent_dial.setValue(theme_index)

        accent = self.theme_controller.apply_theme(theme_index)
        self.apply_accent_styles(accent)


        # ---------------------------------------------------------
        # Restore Last Base Directory
        # ---------------------------------------------------------
        last_base = state.get("last_base_dir", "")
        self.base_path_line.setText(last_base)


        # ---------------------------------------------------------
        # Desktop Timestamp
        # ---------------------------------------------------------
        desktop_enabled = state.get("desktop_date_stamp_enabled", False)
        self.date_time_toggle.setChecked(desktop_enabled)
        self.date_time_config.setEnabled(desktop_enabled)

        desktop_mode = state.get("desktop_date_stamp_mode", "ISO")

        if desktop_mode == "UK":
            self.date_time_config.setCurrentIndex(1)
        elif desktop_mode == "US":
            self.date_time_config.setCurrentIndex(2)
        else:
            self.date_time_config.setCurrentIndex(0)


        # ---------------------------------------------------------
        # Nested Timestamp
        # ---------------------------------------------------------
        nested_enabled = state.get("nested_date_stamp_enabled", False)
        self.nested_date_toggle.setChecked(nested_enabled)
        self.nested_date_config.setEnabled(nested_enabled)

        nested_mode = state.get("nested_date_stamp_mode", "ISO")

        if nested_mode == "UK":
            self.nested_date_config.setCurrentIndex(1)
        elif nested_mode == "US":
            self.nested_date_config.setCurrentIndex(2)
        else:
            self.nested_date_config.setCurrentIndex(0)


        # ---------------------------------------------------------
        # Auto Number Nested Folders
        # ---------------------------------------------------------
        auto_number = state.get("nested_auto_number_enabled", False)
        self.auto_enumerate_folders.setChecked(auto_number)
        
        open_after = state.get("open_folder_after_build", False)
        self.open_folder_build_toggle.setChecked(open_after)

        min_after = state.get("minimize_after_build", False)
        self.minimize_after_build_toggle.setChecked(min_after)
                
        
        

    def change_accent_theme(self, index: int):
        accent = self.theme_controller.apply_theme(index)
        self.apply_accent_styles(accent)
        
    def apply_selected_theme(self):
        index = self.colour_accent_dial.value()
        accent = self.theme_controller.apply_theme(index)
        self.apply_accent_styles(accent)
        self.state_manager.update("theme_index", index)
        
    def apply_accent_styles(self, accent_color: str):

        # ---- Title labels ----
        title_1 = [self.app_title]

        for lbl in title_1:
            lbl.setStyleSheet(f"""
                QLabel {{
                    font-size: 26px;
                    font-weight: 600;
                    color: {accent_color};
                }}
            """)

        # ---- Section labels ----
        title_2 = [
            self.smart_folder_creator,
            self.desktop_section_title
        ]

        for lbl in title_2:
            lbl.setStyleSheet(f"""
                QLabel {{
                    font-size: 22px;
                    font-weight: 600;
                    color: {accent_color};
                }}
            """)

        # ---- Checkboxes (default size) ----
        default_checks = [
            self.date_time_toggle
        ]

        for cb in default_checks:
            cb.setStyleSheet(f"""
                QCheckBox {{
                    font-weight: 600;
                    color: {accent_color};
                }}
            """)

        # ---- Larger checkboxes ----
        large_checks = [
            self.nested_date_toggle,
            self.auto_enumerate_folders,
            self.open_folder_build_toggle,
            self.minimize_after_build_toggle
        ]

        for cb in large_checks:
            cb.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 15px;
                    font-weight: 600;
                    color: {accent_color};
                }}
            """)

        self.current_accent_color = accent_color
    
    # shared status out function hat Qline uses for both output lines
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
            self.smart_status_timer.start(10000)
        else:
            icon_label = self.desktop_status_icon     # FIX
            text_label = self.desktop_status_text     # FIX
            frame = self.desktop_status_frame
            self.desktop_status_timer.start(10000)

        # Status styles
        if status_type == "success":
            icon_label.setText("✓")
            bg = "rgba(46, 204, 113, 0.15)"
        elif status_type == "error":
            icon_label.setText("✕")
            bg = "rgba(231, 76, 60, 0.15)"
        else:
            icon_label.setText(">")
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
        
    def reset_status(self, target: str):
        if target == "nested":
            icon_label = self.smart_status_icon
            text_label = self.smart_status_text
            frame = self.smart_status_frame
        else:
            icon_label = self.desktop_status_icon
            text_label = self.desktop_status_text
            frame = self.desktop_status_frame

        icon_label.setText(">")
        text_label.setText("")

        frame.setStyleSheet("""
            QFrame#statusFrame {
                border-radius: 6px;
                background-color: rgba(52, 152, 219, 0.10);
            }
            QLabel {
                font-size: 14px;
            }
    """)
        
        
    ####################### Desktop Folder Creator methods #################################
    
    def desktop_on_date_stamp_toggled(self, checked: bool):
        self.date_time_config.setEnabled(checked)
        self.state_manager.update(
            "desktop_date_stamp_enabled",
            checked
        )

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
                
            self.state_manager.update(
                "desktop_date_stamp_mode",
                mode
            )

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

    ###################### Nested Folder Creator methods #################################
    
    def minimize_after_build(self):
        self.showMinimized()
    
    def open_output_folder(self, path: str):
        from pathlib import Path
       

        p = Path(path)

        if not p.exists():
            return

        try:
            os.startfile(str(p))   # Windows Explorer
        except Exception:
            pass
    
    def toggle_auto_number_folders(self, checked: bool):
        self.nested_folder_manager.auto_number_enabled = checked
        self.state_manager.update(
            "nested_auto_number_enabled",
            checked
        )
    
    def nested_on_date_stamp_toggled(self, checked: bool):
        self.nested_date_config.setEnabled(checked)
        self.state_manager.update(
            "nested_date_stamp_enabled",
            checked
        )

    def default_to_desktop(self):
        desktop_path = self.desktop_folder_service.desktop_path
        self.base_path_line.setText(str(desktop_path))
        
            # persist to JSON
        self.state_manager.update("last_base_dir", str(desktop_path))

        self.set_status(
            "Base directory set to Desktop.",
            target="nested",
            status_type="info"
        )
        
    def select_base_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Base Directory"
        )

        
        if directory:
            self.base_path_line.setText(directory)

            self.state_manager.update("last_base_dir", directory)

            self.set_status(
                f"Base directory set: {directory}",
                target="nested",
                status_type="info"
            )
        else:
            self.set_status(
                "No directory selected.",
                target="nested",
                status_type="error"
        )

    def create_template(self):
        status, message = self.template_service.save_from_tree(
            self,                 # parent
            self.nested_folder_manager    # tree manager
        )

        if status == "success":
            self.set_status(message, target="nested", status_type="success")
        elif status == "empty":
            self.set_status(message, target="nested", status_type="error")
        elif status != "cancelled":
            self.set_status(message, target="nested", status_type="error")
            
            
    def load_default_template(self):

        text = self.load_default_template_dropdown.currentText()

        # Reset option
        if text == "Default Templates":
            self.tree.clear()
            return

        # Convert dropdown text → filename
        filename = text.lower().replace(" ", "_") + ".txt"

        # Build template path
        template_path = Path(r"C:\Users\davey\Desktop\Folder Creator\templates") / filename

        if not template_path.exists():
            return

        # Load template text
        with open(template_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Clear current tree
        self.tree.clear()

        # Parse template
        data = self.nested_folder_manager.parse_indented_text(text)

        # Populate tree
        self.nested_folder_manager.deserialize_tree(data)

        # Expand nodes so the structure is visible
        self.nested_folder_manager.expand_all_animated()
        
    def load_template(self):
        status, message = self.template_service.load_into_tree(
            self,                 # parent
            self.nested_folder_manager    # tree manager
        )

        if status == "success":
            self.set_status(message, target="nested", status_type="success")
        elif status != "cancelled":
            self.set_status(message, target="nested", status_type="error")
    
    # Drag and drop load
    def load_template_from_path(self, file_path):
        try:
            # Disable auto naming/numbering for imported structures
            if self.auto_enumerate_folders.isChecked():
                self.auto_enumerate_folders.setChecked(False)
            data = self.template_service.load_template(
                file_path,
                self.nested_folder_manager.parse_indented_text
            )

            self.nested_folder_manager.deserialize_tree(data)
            self.set_status("Template loaded via drag & drop", target="nested", status_type="success")

        except Exception:
            self.smart_status_text.setText("Error loading dropped file")

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
                
            self.state_manager.update(
                "nested_date_stamp_mode",
                mode
            )

        status, message = self.nested_folder_manager.build_folders(base_path, mode)

        if status == "success":
            stype = "success"

            if self.open_folder_build_toggle.isChecked():
                self.open_output_folder(base_path)
            
            
            if self.minimize_after_build_toggle.isChecked():
                self.minimize_after_build()

        elif status == "exists":
            stype = "info"
        else:
            stype = "error"

        self.set_status(message, target="nested", status_type=stype)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()