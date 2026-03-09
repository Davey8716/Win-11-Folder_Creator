import sys
import os  
from app_service import AppService
from pathlib import Path
from drag_and_drop import SmartTreeWidget
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy
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
    QGridLayout,QSpinBox,

)

from PySide6.QtCore import Qt

from pathlib import Path




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tree = SmartTreeWidget()

        self.service = AppService(self.tree)
        state = self.service.state
        
        self.setWindowTitle("Folder Generator")
        
        self.desktop_mode_height = 340
        self.nested_mode_height = 975
        
        self.desktop_mode_width = 650
        self.nested_mode_width = 1200
        
        self.setFixedSize(self.nested_mode_width, self.nested_mode_height)


        # ===== Central Widget =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)
        

        # ==========================================================
        # Slider
        # ==========================================================

        header_grid = QGridLayout()
        header_grid.setContentsMargins(5, 5, 5, 5)
        header_grid.setHorizontalSpacing(12)
        header_grid.setVerticalSpacing(0)
        
        
        

        # ------------------------------
        # Title Frame (LEFT)
        # ------------------------------
        self.desktop_title_frame = QFrame()
        self.desktop_title_frame.setFrameShape(QFrame.StyledPanel)
        self.desktop_title_frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        desktop_title_layout = QVBoxLayout()
        desktop_title_layout.setContentsMargins(10,10,10,10)
        desktop_title_layout.setSpacing(0)
        self.desktop_title_frame.setLayout(desktop_title_layout)

        self.current_mode = "desktop"

        self.desktop_section_title = QPushButton(
            "Desktop Folder Creator\n(click to switch)"
        )

        self.desktop_section_title.setCursor(Qt.PointingHandCursor)
        self.desktop_section_title.setFlat(True)
        self.desktop_section_title.setStyleSheet("""
        QPushButton {
            font-size: 26px;
            font-weight: 600;
            text-align: left;
        }
        """)

        self.desktop_section_title.clicked.connect(self.toggle_mode)

        desktop_title_layout.addWidget(self.desktop_section_title)
        
        self.theme_selector_frame = QFrame()
        self.theme_selector_frame.setFrameShape(QFrame.StyledPanel)

        theme_layout = QGridLayout()
        theme_layout.setSpacing(6)
        theme_layout.setContentsMargins(6,6,6,6)

        self.theme_selector_frame.setLayout(theme_layout)

        self.theme_buttons = []

        theme_count = self.service.theme_count()
        cols = (theme_count + 1) // 2

        for i in range(theme_count):

            btn = QPushButton()
            btn.setFixedSize(20,20)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)

            btn.clicked.connect(lambda _, idx=i: self.select_theme(idx))

            row = i // cols
            col = i % cols

            theme_layout.addWidget(btn, row, col)

            self.theme_buttons.append(btn)
            
    
            
        for btn in self.theme_buttons:
            btn.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                border: 2px solid rgba(120,120,120,0.4);
            }
            QPushButton:checked {
                border: 3px solid white;
            }
            """)

        # ------------------------------
        # Grid placement
        # ------------------------------
        header_grid.addWidget(self.desktop_title_frame, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        header_grid.addWidget(self.theme_selector_frame, 0, 1, Qt.AlignRight | Qt.AlignBottom)
        header_grid.setColumnStretch(0, 1)
        header_grid.setColumnStretch(1, 0)
                
        main_layout.addLayout(header_grid)
        main_layout.addSpacing(5)
                
        # ==========================================================
        # FRAME 1 — Desktop Folder Creator
        # ==========================================================

        self.desktop_folder_frame = QFrame()
        self.desktop_folder_frame.setFrameShape(QFrame.StyledPanel)

        self.desktop_layout = QVBoxLayout()
        self.desktop_layout.setSpacing(6)
        self.desktop_layout.setContentsMargins(12, 12, 12, 12)
        self.desktop_folder_frame.setLayout(self.desktop_layout)

        # ==========================================================
        # Parent controls frame
        # ==========================================================
        self.desktop_controls_frame = QFrame()
        self.desktop_controls_frame.setFrameShape(QFrame.StyledPanel)

        desktop_controls_layout = QGridLayout()
        desktop_controls_layout.setContentsMargins(6, 6, 6, 6)
        desktop_controls_layout.setHorizontalSpacing(8)
        desktop_controls_layout.setVerticalSpacing(0)
        self.desktop_controls_frame.setLayout(desktop_controls_layout)

        # ==========================================================
        # Create widgets
        # ==========================================================
        self.desktop_folder_line = QLineEdit()
        self.desktop_folder_line.setPlaceholderText("Enter Folder Name...")
        self.desktop_folder_line.setFixedWidth(180)
        self.desktop_folder_line.setMinimumHeight(35)

        self.folder_to_desktop = QPushButton("Folder To Desktop")
        self.folder_to_desktop.setFixedWidth(180)
        self.folder_to_desktop.setMinimumHeight(35)

        # ---- Enumeration controls ----
        self.enumerate_toggle = QCheckBox("Create Multiple\nNumbered Folders")
        self.enumerate_toggle.setMinimumHeight(35)
        self.enumerate_toggle.setFixedWidth(155)

        self.desktop_folder_number_enumerator = QSpinBox()
        self.desktop_folder_number_enumerator.setMinimumHeight(35)
        self.desktop_folder_number_enumerator.setFixedWidth(155)
        self.desktop_folder_number_enumerator.setRange(1, 100)
        self.desktop_folder_number_enumerator.setEnabled(False)

        # ---- Timestamp controls ----
        self.date_time_toggle = QCheckBox("Add Date Stamp")
        self.date_time_toggle.setMinimumHeight(35)
        self.date_time_toggle.setFixedWidth(155)

        self.date_time_config = QComboBox()
        self.date_time_config.setFixedWidth(155)
        self.date_time_config.setMinimumHeight(35)
        self.date_time_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])
        self.date_time_config.setEnabled(False)

        for i in range(self.date_time_config.count()):
            self.date_time_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.date_time_config.setEditable(True)
        self.date_time_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_time_config.lineEdit().setReadOnly(True)


        # ==========================================================
        # Column 1 — Input frame (Create Folder)
        # ==========================================================
        self.desktop_input_frame = QFrame()
        self.desktop_input_frame.setFrameShape(QFrame.StyledPanel)

        desktop_input_layout = QVBoxLayout()
        desktop_input_layout.setContentsMargins(6, 6, 6, 6)
        desktop_input_layout.setSpacing(8)
        self.desktop_input_frame.setLayout(desktop_input_layout)

        desktop_input_layout.addWidget(self.desktop_folder_line)
        desktop_input_layout.addWidget(self.folder_to_desktop)


        # ==========================================================
        # Column 2 — Enumeration frame
        # ==========================================================
        self.desktop_enumerator_frame = QFrame()
        self.desktop_enumerator_frame.setFrameShape(QFrame.StyledPanel)

        enumerator_layout = QVBoxLayout()
        enumerator_layout.setContentsMargins(6, 6, 6, 6)
        enumerator_layout.setSpacing(8)
        self.desktop_enumerator_frame.setLayout(enumerator_layout)

        enumerator_layout.addWidget(self.enumerate_toggle, 0, Qt.AlignCenter)
        enumerator_layout.addWidget(self.desktop_folder_number_enumerator, 0, Qt.AlignCenter)


        # ==========================================================
        # Column 3 — Date controls frame
        # ==========================================================
        self.desktop_date_frame = QFrame()
        self.desktop_date_frame.setFrameShape(QFrame.StyledPanel)

        desktop_date_layout = QVBoxLayout()
        desktop_date_layout.setContentsMargins(6, 6, 6, 6)
        desktop_date_layout.setSpacing(8)
        self.desktop_date_frame.setLayout(desktop_date_layout)

        desktop_date_layout.addWidget(self.date_time_toggle, 0, Qt.AlignCenter)
        desktop_date_layout.addWidget(self.date_time_config, 0, Qt.AlignCenter)

        # ==========================================================
        # Add subframes into parent controls frame
        # ==========================================================
        desktop_controls_layout.addWidget(self.desktop_input_frame, 0, 0)
        desktop_controls_layout.addWidget(self.desktop_enumerator_frame, 0, 1)
        desktop_controls_layout.addWidget(self.desktop_date_frame, 0, 2)

        desktop_controls_layout.setColumnStretch(0, 1)
        desktop_controls_layout.setColumnStretch(1, 1)
        desktop_controls_layout.setColumnStretch(2, 1)


        # Add controls frame to desktop section
        self.desktop_layout.addWidget(self.desktop_controls_frame)
        
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
        main_layout.addSpacing(10)   # BIG separation between sections













        # ---- Smart Frame ----
        self.smart_folder_creator_frame = QFrame()
        self.smart_folder_creator_frame.setFrameShape(QFrame.StyledPanel)


        self.smart_layout = QVBoxLayout()
        self.smart_layout.setSpacing(6)
        self.smart_layout.setContentsMargins(6,6,6,6)
        self.smart_folder_creator_frame.setLayout(self.smart_layout)
        
        self.controls_frame = QFrame()
        self.controls_frame.setFrameShape(QFrame.StyledPanel)

        # ==========================================================
        # Parent layout inside controls_frame
        # ==========================================================
        main_controls_layout = QGridLayout()
        main_controls_layout.setContentsMargins(6, 6, 6, 6)
        main_controls_layout.setHorizontalSpacing(8)
        main_controls_layout.setVerticalSpacing(0)
        self.controls_frame.setLayout(main_controls_layout)

        # ==========================================================
        # Create all widgets first
        # ==========================================================
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_subfolder_btn = QPushButton("Add Subfolder")

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_all_btn = QPushButton("Remove All")

        self.create_template_btn = QPushButton("Create Template")
        

        self.load_user_template_dropdown = QComboBox()
        self.load_user_template_dropdown.addItems([
            "User Template"
        ])
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

        self.load_default_template_dropdown.setMinimumWidth(160)
        self.load_default_template_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.load_default_template_dropdown.setEnabled(True)

        for i in range(self.load_default_template_dropdown.count()):
            self.load_default_template_dropdown.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.nested_date_toggle = QCheckBox("Add Date Stamp\n To Parent Folder")
        self.auto_enumerate_folders = QCheckBox("Auto Number + Name\n Folders Sub Folders")

        self.nested_date_config = QComboBox()
        self.nested_date_config.addItems([
            "ISO (YYYY-MM-DD)",
            "UK (DD-MM-YYYY)",
            "US (MM-DD-YYYY)"
        ])
        self.nested_date_config.setEnabled(False)
        self.nested_date_config.setMaximumWidth(155)
        self.nested_date_config.setMaximumHeight(35)
        # self.nested_date_config.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        for i in range(self.nested_date_config.count()):
            self.nested_date_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.nested_date_config.setEditable(True)
        self.nested_date_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.nested_date_config.lineEdit().setReadOnly(True)
    

        for btn in [
            self.add_folder_btn,
            self.add_subfolder_btn,
            self.remove_btn,
            self.remove_all_btn,
            self.create_template_btn
        ]:
            btn.setMinimumWidth(100)
            btn.setMinimumHeight(35)

        # ==========================================================
        # Column 1 — Template frame
        # ==========================================================
        self.template_controls_frame = QFrame()
        self.template_controls_frame.setFrameShape(QFrame.StyledPanel)

        template_layout = QVBoxLayout()
        template_layout.setContentsMargins(6,6,6,6)
        template_layout.setSpacing(6)
        self.template_controls_frame.setLayout(template_layout)

        template_layout.addWidget(self.create_template_btn)
        template_layout.addWidget(self.load_user_template_dropdown)
        template_layout.addWidget(self.load_default_template_dropdown)
        

        # ==========================================================
        # Column 2 — Folder buttons frame
        # ==========================================================
        self.folder_buttons_frame = QFrame()
        self.folder_buttons_frame.setFrameShape(QFrame.StyledPanel)

        folder_buttons_layout = QVBoxLayout()
        folder_buttons_layout.setContentsMargins(6, 6, 6, 6)
        folder_buttons_layout.setSpacing(8)
        self.folder_buttons_frame.setLayout(folder_buttons_layout)

        folder_buttons_layout.addWidget(self.add_folder_btn)
        folder_buttons_layout.addWidget(self.add_subfolder_btn)
        folder_buttons_layout.addWidget(self.remove_btn)
        folder_buttons_layout.addWidget(self.remove_all_btn)
        

        # ==========================================================
        # Column 3 — Date / auto-number frame
        # ==========================================================
        self.date_controls_frame = QFrame()
        self.date_controls_frame.setFrameShape(QFrame.StyledPanel)

        date_layout = QVBoxLayout()
        date_layout.setContentsMargins(10,10,10,10)
        date_layout.setSpacing(15)
        self.date_controls_frame.setLayout(date_layout)
        
        
        date_layout.addWidget(self.auto_enumerate_folders,)
        date_layout.addWidget(self.nested_date_toggle,)
        date_layout.addWidget(self.nested_date_config,)
        
        # ---- Output Frame ----
        self.out_put_frame = QFrame()
        self.out_put_frame.setFrameShape(QFrame.StyledPanel)

        frame_layout_output = QVBoxLayout()
        frame_layout_output.setContentsMargins(6,6,6,6)
        frame_layout_output.setSpacing(6)
        self.out_put_frame.setLayout(frame_layout_output)

        # ==========================================================
        # Add parent frame to smart layout
        # ==========================================================
        self.smart_layout.addWidget(self.controls_frame)

    
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################


        # # # # # # # # # # # # # # # # # # # # # # # Ouput Folder Creator # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        self.tree_frame = QFrame()
        self.tree_frame.setFrameShape(QFrame.StyledPanel)
        
        
        tree_layout = QVBoxLayout()
        tree_layout.setContentsMargins(6, 6, 6, 6)
        tree_layout.setSpacing(0)
        self.tree_frame.setLayout(tree_layout)
        
        # ---- Tree Widget ----
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
        
        # IMPORTANT: put the tree inside the frame
        tree_layout.addWidget(self.tree)
        
        # add the frame instead of the tree
        self.smart_layout.addWidget(self.tree_frame)
        
        self.tree.setAlternatingRowColors(True)
        
        # ----------------------------------------------------------
        # Base Path Field (UNCHANGED)
        # ----------------------------------------------------------
        self.base_path_line = QLineEdit()
        self.base_path_line.setPlaceholderText(
            "Select base directory for output folder location"
        )
        self.base_path_line.setReadOnly(True)
        self.base_path_line.setMinimumHeight(35)

        frame_layout_output.addWidget(self.base_path_line)

################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################

        # ==========================================================
        # Full Frame
        # ==========================================================
        self.build_buttons_frame = QFrame()
        self.build_buttons_frame.setFrameShape(QFrame.StyledPanel)

        build_layout = QVBoxLayout()
        build_layout.setContentsMargins(6,6,6,6)
        build_layout.setSpacing(2)
        self.build_buttons_frame.setLayout(build_layout)

        self.default_to_desktop_btn = QPushButton("Default Desktop")
        self.browse_btn = QPushButton("Output Location")
        self.build_folders_btn = QPushButton("Build Folders")

        for btn in [
            self.default_to_desktop_btn,
            self.browse_btn,
            self.build_folders_btn
        ]:
            btn.setMinimumHeight(35)
            
        # btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        build_layout.addWidget(self.default_to_desktop_btn)
        build_layout.addWidget(self.browse_btn)
        build_layout.addWidget(self.build_folders_btn)
        
        self.update_build_button_state()
    


        self.post_build_frame = QFrame()
        self.post_build_frame.setFrameShape(QFrame.StyledPanel)
        
        self.sep1 = self.make_vline()
        self.sep2 = self.make_vline()
        self.sep3 = self.make_vline()
        self.sep4 = self.make_vline()
    

        post_build_layout = QVBoxLayout()
        post_build_layout.setContentsMargins(6,6,6,6)
        post_build_layout.setSpacing(8)
        self.post_build_frame.setLayout(post_build_layout)

        self.open_folder_build_toggle = QCheckBox("Open Folder Location\n After Build")
        self.minimize_after_build_toggle = QCheckBox("Minimize After Build")
        
        post_build_layout.addWidget(self.open_folder_build_toggle, alignment=Qt.AlignHCenter)
        post_build_layout.addWidget(self.minimize_after_build_toggle, alignment=Qt.AlignHCenter)
        

        main_controls_layout.setHorizontalSpacing(6)
        main_controls_layout.setVerticalSpacing(0)

        # group 1
        main_controls_layout.addWidget(self.folder_buttons_frame,   0, 0)
        main_controls_layout.addWidget(self.date_controls_frame,    0, 1)

        # separators after frame 2
        main_controls_layout.addWidget(self.sep1,                   0, 2)
        main_controls_layout.addWidget(self.sep2,                   0, 3)

        # group 2
        main_controls_layout.addWidget(self.template_controls_frame, 0, 4)
        main_controls_layout.addWidget(self.out_put_frame,           0, 5)
        main_controls_layout.addWidget(self.build_buttons_frame,     0, 6)

        # separators AFTER build frame
        main_controls_layout.addWidget(self.sep3,                   0, 7)
        main_controls_layout.addWidget(self.sep4,                   0, 8)

        # final frame
        main_controls_layout.addWidget(self.post_build_frame,       0, 9)


        for frame in [
            self.folder_buttons_frame,
            self.date_controls_frame,
            self.template_controls_frame,
            self.out_put_frame,
            self.build_buttons_frame,
            self.post_build_frame
        ]:
            frame.setMinimumWidth(170)
            frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            
        self.out_put_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.out_put_frame.setMinimumWidth(0)

















        # ----------------------------------------------------------
        # Status frame (UNCHANGED)
        # ----------------------------------------------------------
        
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



        frame_layout_output.addWidget(self.smart_status_frame)

        # Add entire section to smart layout
        self.smart_layout.addWidget(self.out_put_frame)

        
  
        # ---- THIS is the other missing line ----
        main_layout.addWidget(self.smart_folder_creator_frame)
        
        
































































































        # Signal Connections
        self.date_time_toggle.toggled.connect(self.desktop_on_date_stamp_toggled)
        self.nested_date_toggle.toggled.connect(self.nested_on_date_stamp_toggled)
        self.folder_to_desktop.clicked.connect(self.create_desktop_folder)
        self.build_folders_btn.clicked.connect(self.build_folders_from_tree)
        self.enumerate_toggle.toggled.connect(self.on_enumerate_toggle)
        self.date_time_config.currentIndexChanged.connect(self.desktop_on_date_mode_changed)
        self.default_to_desktop_btn.clicked.connect(self.default_to_desktop)
        self.browse_btn.clicked.connect(self.select_base_directory)
        self.auto_enumerate_folders.toggled.connect(self.toggle_auto_number_folders)
        self.create_template_btn.clicked.connect(self.create_template)
        self.remove_all_btn.clicked.connect(self.remove_all_folders)
        
        
        
        # Placeholders to connect to the user and default template drops to their respective methods.
        
        # self.load_user_template_dropdown.clicked.connect(self.load_template)
        self.load_default_template_dropdown.currentIndexChanged.connect(self.load_default_template)
        
        self.open_folder_build_toggle.toggled.connect(
            lambda v: self.service.state_manager.update("open_folder_after_build", v)
        )

        self.minimize_after_build_toggle.toggled.connect(
            lambda v: self.service.state_manager.update("minimize_after_build", v)
        )
        
        self.desktop_folder_number_enumerator.valueChanged.connect(
            lambda v: self.service.set_state("desktop_enumeration_count", v)
        )
        
        self.add_folder_btn.clicked.connect(
            lambda: (self.service.nested_manager.add_root_folder(), self.update_build_button_state())
        )
        
        self.add_subfolder_btn.clicked.connect(
            lambda: (self.service.nested_manager.add_subfolder(), self.update_build_button_state())
        )
                
        self.remove_btn.clicked.connect(
            lambda: (self.service.nested_manager.remove_selected_folders(), self.update_build_button_state())
        )
        
        
        
        self.tree.itemSelectionChanged.connect(self.update_build_button_state)
        
        
        theme_index = state.get("theme_index", 0)

        self.select_theme(theme_index)
                

        self.tree.fileDropped.connect(self.load_template_from_path)
        
        self.desktop_status_timer = QTimer(self)
        self.desktop_status_timer.setSingleShot(True)
        self.desktop_status_timer.timeout.connect(lambda: self.reset_status("desktop"))

        self.smart_status_timer = QTimer(self)
        self.smart_status_timer.setSingleShot(True)
        self.smart_status_timer.timeout.connect(lambda: self.reset_status("nested"))
                        
        # Apply initial theme



        # # React to slider changes
        # self.colour_accent_slider.sliderReleased.connect(self.apply_selected_theme)
        
        # Loading of object instances
        
        state = self.service.state
        self.current_mode = state.get("ui_mode", "desktop")
        
        # ---------------------------------------------------------
        # Initial UI mode
        # ---------------------------------------------------------
        if self.current_mode == "nested":
            self.desktop_section_title.setText(
                "Nested Folder Creator\n(click to switch)"
            )
            self.desktop_folder_frame.hide()
            self.smart_folder_creator_frame.show()
            self.setFixedSize(self.nested_mode_width, self.nested_mode_height)
            
        else:
            self.desktop_section_title.setText(
                "Desktop Folder Creator\n(click to switch)"
            )
            self.smart_folder_creator_frame.hide()
            self.desktop_folder_frame.show()
            self.setFixedSize(650, self.desktop_mode_height)

        # ---------------------------------------------------------
        # Restore Theme
        # ---------------------------------------------------------
        theme_index = state.get("theme_index", 0)

        # self.colour_accent_slider.setValue(theme_index)

        accent = self.service.apply_theme(theme_index)
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
        
        enum_count = state.get("desktop_enumeration_count", 2)
        self.desktop_folder_number_enumerator.setValue(enum_count)

        enum_enabled = state.get("desktop_enumeration_enabled", False)
        self.enumerate_toggle.setChecked(enum_enabled)
        self.desktop_folder_number_enumerator.setEnabled(enum_enabled)
        
    def make_vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Plain)
        line.setLineWidth(1)
        line.setMidLineWidth(0)
        line.setFixedWidth(6)
        return line
            
        
    def update_build_button_state(self):
        has_items = self.tree.topLevelItemCount() > 0
        has_selection = self.tree.currentItem() is not None
        
        self.build_folders_btn.setEnabled(has_items)
        self.remove_all_btn.setEnabled(has_items)
        
        # Requires a selected item
        self.remove_btn.setEnabled(has_selection)
        self.add_subfolder_btn.setEnabled(has_selection)

                            
        
        
        
    def toggle_mode(self):

        if self.current_mode == "desktop":
            self.current_mode = "nested"
            self.service.set_state("ui_mode", self.current_mode)

            self.desktop_section_title.setText(
                "Nested Folder Creator\n(click to switch)"
            )

            self.smart_folder_creator_frame.show()
            self.desktop_folder_frame.hide()

            self.setFixedSize(650, self.nested_mode_height)

        else:
            self.current_mode = "desktop"
            self.service.set_state("ui_mode", self.current_mode)

            self.desktop_section_title.setText(
                "Desktop Folder Creator\n(click to switch)"
            )

            self.desktop_folder_frame.show()
            self.smart_folder_creator_frame.hide()

            self.setFixedSize(650, self.desktop_mode_height)

    
    def change_accent_theme(self, index: int):
        accent = self.service.apply_theme(index)
        self.apply_accent_styles(accent)
        
    def preview_theme(self, index):
        accent = self.service.apply_theme(index)
        self.apply_accent_styles(accent)

    def commit_theme(self):
        index = self.colour_accent_slider.value()
        self.service.set_state("theme_index", index)
        
    def apply_selected_theme(self):
        index = self.colour_accent_slider.value()
        accent = self.service.apply_theme(index)
        self.apply_accent_styles(accent)
        self.service.set_state("theme_index", index)
        
        
    def apply_accent_styles(self, accent_color: str):


        # ---- Section labels ----
        title_2 = [
            # self.smart_folder_creator,
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
            self.date_time_toggle,
            self.enumerate_toggle
        ]

        for cb in default_checks:
            cb.setStyleSheet(f"""
                QCheckBox {{
                    font-size: 15px;
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

        # Make the icon follow the slider accent color
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
    
    def select_theme(self, index):

        accent = self.service.apply_theme(index)

        self.apply_accent_styles(accent)

        self.service.set_state("theme_index", index)

        for i, btn in enumerate(self.theme_buttons):
            btn.setChecked(i == index)
    
    def desktop_on_date_stamp_toggled(self, checked: bool):
        self.date_time_config.setEnabled(checked)

        self.service.set_state(
            "desktop_date_stamp_enabled",
            checked
        )
    
    def on_enumerate_toggle(self, checked: bool):

        self.desktop_folder_number_enumerator.setEnabled(checked)

        if checked and self.desktop_folder_number_enumerator.value() == 1:
            self.desktop_folder_number_enumerator.setValue(2)

        self.service.set_state(
            "desktop_enumeration_enabled",
            checked
        )
        
    def desktop_on_date_mode_changed(self, index: int):

        text = self.date_time_config.currentText()

        if "ISO" in text:
            mode = "ISO"
        elif "UK" in text:
            mode = "UK"
        elif "US" in text:
            mode = "US"
        else:
            mode = "ISO"

        self.service.set_state(
            "desktop_date_stamp_mode",
            mode
        )
                    
    def create_desktop_folder(self):

        base_name = self.desktop_folder_line.text().strip()

        if not base_name:
            self.set_status(
                "No folder name entered.",
                target="desktop",
                status_type="error"
            )
            return

        # ----------------------------------
        # Timestamp mode
        # ----------------------------------
        mode = None

        if self.date_time_toggle.isChecked():
            text = self.date_time_config.currentText()

            if "ISO" in text:
                mode = "ISO"
            elif "UK" in text:
                mode = "UK"
            elif "US" in text:
                mode = "US"

            self.service.set_state(
                "desktop_date_stamp_mode",
                mode
            )

        # ----------------------------------
        # Determine how many folders
        # ----------------------------------
        if self.enumerate_toggle.isChecked():
            count = self.desktop_folder_number_enumerator.value()
        else:
            count = 1

        created = 0

        # ----------------------------------
        # Create folders
        # ----------------------------------
        for i in range(1, count + 1):

            if count == 1:
                name = base_name
            else:
                name = f"{base_name}_{i}"

            status, _ = self.service.create_desktop_folder(name, mode)

            if status == "success":
                created += 1

        # ----------------------------------
        # Status output
        # ----------------------------------
        if created == 1:
            self.set_status(
                f'Folder "{base_name}" created on Desktop.',
                target="desktop",
                status_type="success"
            )

        elif created > 1:
            self.set_status(
                f"{created} folders created on Desktop.",
                target="desktop",
                status_type="success"
            )

        else:
            self.set_status(
                "Folders already exist or could not be created.",
                target="desktop",
                status_type="error"
            )
        

    ###################### Nested Folder Creator methods #################################
    
    def minimize_after_build(self):
        self.showMinimized()
        
    def remove_all_folders(self):

        self.service.nested_manager.remove_all_folders()

        # reset template dropdown
        self.load_default_template_dropdown.setCurrentIndex(0)

        # disable build button
        self.update_build_button_state()
    
    def open_output_folder(self, path: str):
        
       

        p = Path(path)

        if not p.exists():
            return

        try:
            os.startfile(str(p))   # Windows Explorer
        except Exception:
            pass
    
    def toggle_auto_number_folders(self, checked: bool):
        self.service.nested_manager.auto_number_enabled = checked

        self.service.set_state(
            "nested_auto_number_enabled",
            checked
        )


    def nested_on_date_stamp_toggled(self, checked: bool):
        self.nested_date_config.setEnabled(checked)

        self.service.set_state(
            "nested_date_stamp_enabled",
            checked
        )


    def default_to_desktop(self):
        desktop_path = self.service.desktop_manager.desktop_path
        self.base_path_line.setText(str(desktop_path))

        self.service.set_state("last_base_dir", str(desktop_path))

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

            self.service.set_state("last_base_dir", directory)

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
        status, message = self.service.save_template(self)

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
            self.update_build_button_state()
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
        data = self.service.nested_manager.parse_indented_text(text)

        # Populate tree
        self.service.nested_manager.deserialize_tree(data)

        # Expand nodes so the structure is visible
        self.service.nested_manager.expand_all_animated()
        
        
        self.update_build_button_state()
        
    def load_template(self):
        status, message = self.service.load_template_dialog(self)

        if status == "success":
            self.set_status(message, target="nested", status_type="success")
        elif status != "cancelled":
            self.set_status(message, target="nested", status_type="error")


    # Drag and drop load
    def load_template_from_path(self, file_path):
        try:
            # Disable auto numbering for imported structures
            if self.auto_enumerate_folders.isChecked():
                self.auto_enumerate_folders.setChecked(False)

            self.service.load_template_from_path(file_path)
            
            self.update_build_button_state()

            self.set_status(
                "Template loaded via drag & drop",
                target="nested",
                status_type="success"
            )

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
                

            self.service.state_manager.update(
                "nested_date_stamp_mode",
                mode
            )

        status, message = self.service.build_tree(base_path, mode)

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