import sys

from app_service import AppService
from smart_tree_widget import SmartTreeWidget
from nested_ui_controller import NestedUIController
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QTreeWidgetItemIterator
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
    QGridLayout,QSpinBox,QHeaderView

)

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tree = SmartTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)

        self.tree.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        # ---- Horizontal scroll support for wide trees ----
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.service = AppService(self.tree)
        state = self.service.state
        
        self.setWindowTitle("Folder Generator")
        
        self.desktop_mode_height = 340
        self.nested_mode_height = 1000
        
        self.desktop_mode_width = 650
        self.nested_mode_width = 1075
        
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
        # Theme Selector
        # ==========================================================

        header_grid = QGridLayout()
        header_grid.setContentsMargins(5, 5, 5, 5)
        header_grid.setHorizontalSpacing(12)
        header_grid.setVerticalSpacing(0)
        
        # ------------------------------
        # Title Frame (LEFT)
        # ------------------------------
        self.desktop_title_frame = QFrame()
        self.desktop_title_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )
    
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
            font-size: 25px;
            font-weight: 1000;
            text-align: left;
        }
        """)

        self.desktop_section_title.clicked.connect(self.toggle_mode)

        desktop_title_layout.addWidget(self.desktop_section_title)
        
        self.theme_selector_frame = QFrame()
        self.theme_selector_frame.setFrameShape(QFrame.StyledPanel)
        # self.theme_selector_frame.setMinimumWidth(2)
        self.theme_selector_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        theme_layout = QGridLayout()
        theme_layout.setSpacing(4)
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
        self.desktop_folder_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        self.desktop_layout = QVBoxLayout()
        self.desktop_layout.setSpacing(6)
        self.desktop_layout.setContentsMargins(12, 12, 12, 12)
        self.desktop_folder_frame.setLayout(self.desktop_layout)

        # ==========================================================
        # Parent controls frame
        # ==========================================================
        self.desktop_controls_frame = QFrame()
        self.desktop_controls_frame.setFrameShape(QFrame.StyledPanel)
        self.desktop_controls_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )
        

        desktop_controls_layout = QGridLayout()
        desktop_controls_layout.setContentsMargins(10,10,10,10)
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
        
        self.rename_desktop_line_shortcut = QShortcut(QKeySequence("F2"), self)
        self.rename_desktop_line_shortcut.activated.connect(self.rename_desktop_input)

        self.clear_desktop_line_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.clear_desktop_line_shortcut.activated.connect(self.clear_desktop_input)

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
        desktop_input_layout.setContentsMargins(10,10,10,10)
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
        enumerator_layout.setContentsMargins(10,10,10,10)
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
        desktop_date_layout.setContentsMargins(10,10,10,10)
        desktop_date_layout.setSpacing(8)
        self.desktop_date_frame.setLayout(desktop_date_layout)
        self.desktop_date_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        self.desktop_status_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        self.smart_folder_creator_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )


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
        main_controls_layout.setContentsMargins(10,10,10,10)
        main_controls_layout.setHorizontalSpacing(8)
        main_controls_layout.setVerticalSpacing(0)
        self.controls_frame.setLayout(main_controls_layout)
        self.controls_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        
        # Style separator thickness
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
        template_layout.setContentsMargins(10,10,10,10)
        template_layout.setSpacing(6)
        self.template_controls_frame.setLayout(template_layout)
        self.template_controls_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        template_layout.addWidget(self.create_template_btn)
        template_layout.addWidget(self.load_user_template_dropdown)
        template_layout.addWidget(self.load_default_template_dropdown)
        

        # ==========================================================
        # Column 2 — Folder buttons frame
        # ==========================================================
        self.folder_buttons_frame = QFrame()
        self.folder_buttons_frame.setFrameShape(QFrame.StyledPanel)

        folder_buttons_layout = QVBoxLayout()
        folder_buttons_layout.setContentsMargins(10,10,10,10)
        folder_buttons_layout.setSpacing(8)
        self.folder_buttons_frame.setLayout(folder_buttons_layout)
        self.folder_buttons_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        self.date_controls_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )
        
        
        date_layout.addWidget(self.auto_enumerate_folders,)
        date_layout.addWidget(self.nested_date_toggle,)
        date_layout.addWidget(self.nested_date_config,)
        
        # ---- Output Frame ----
        self.out_put_frame = QFrame()
        self.out_put_frame.setFrameShape(QFrame.StyledPanel)

        # ----------------------------------------------------------
        # Create path fields FIRST
        # ----------------------------------------------------------
        self.base_path_line = QLineEdit()
        self.base_path_line.setPlaceholderText(
            "Select base directory for output folder location"
        )
        self.base_path_line.setReadOnly(True)
        self.base_path_line.setMinimumHeight(35)

        self.template_path_line = QLineEdit()
        self.template_path_line.setPlaceholderText(
            "Output Location For User Made Templates"
        )
        self.template_path_line.setReadOnly(True)
        self.template_path_line.setMinimumHeight(35)

        # ----------------------------------------------------------
        # Paths row
        # ----------------------------------------------------------
        self.paths_frame = QFrame()
        paths_layout = QHBoxLayout()
        paths_layout.setContentsMargins(10,10,10,10)
        paths_layout.setSpacing(8)
        self.paths_frame.setLayout(paths_layout)
        self.paths_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        self.template_path_column = QFrame()
        self.template_path_column.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        template_col_layout = QVBoxLayout()
        template_col_layout.setContentsMargins(10,10,10,10)
        template_col_layout.setSpacing(6)
        self.template_path_column.setLayout(template_col_layout)

        self.template_path_title = QLabel("Template Save Location")
        template_col_layout.addWidget(self.template_path_title)
        template_col_layout.addWidget(self.template_path_line)
        
        self.base_path_column = QFrame()
        self.base_path_column.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
        base_col_layout = QVBoxLayout()
        base_col_layout.setContentsMargins(10,10,10,10)
        base_col_layout.setSpacing(6)
        self.base_path_column.setLayout(base_col_layout)
        

        self.base_path_title = QLabel("Output Folder Location")
        base_col_layout.addWidget(self.base_path_title)
        base_col_layout.addWidget(self.base_path_line)
        
        paths_layout.addWidget(self.template_path_column)
        paths_layout.addStretch()
        paths_layout.addWidget(self.base_path_column)
        
        # ----------------------------------------------------------
        # Status frame
        # ----------------------------------------------------------
        
        self.out_put_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.base_path_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.base_path_line.setMinimumWidth(400)
        
        self.template_path_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.template_path_line.setMinimumWidth(400)
        

        frame_layout_output = QVBoxLayout()
        frame_layout_output.setContentsMargins(10,10,10,10)
        frame_layout_output.setSpacing(6)
        frame_layout_output.addWidget(self.paths_frame)
        self.out_put_frame.setLayout(frame_layout_output)
        self.out_put_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        self.tree_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )
        
        
        
        tree_layout = QVBoxLayout()
        tree_layout.setContentsMargins(10,10,10,10)
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
                "Files can either be drag drop loaded in here.\n"
                "Or created/loaded using the buttons above.\n"
                "(accepts .json, .txt, .md files)\n"
                "Folder trees can be copy pasted in here using ctrl + v as plain text.\n\n"
                
                "Template creation tip:\n The templates can be saved as either .json, .txt or .md on the save template dialog.\n"
                "Click the save as type dropdown to do this.\n\n"
                
                
                
                "Tip: Drag and drop folders to change hierarchy.\n"
                "Tip: Drag a folder below another folder to create a new parent-level folder.\n"
                "Tip: Drag a folder onto another folder to nest it as a subfolder.\n\n"
                "Tip: Auto-numbering only applies when using the Add Folder / Add Subfolder buttons.\n"
                
                "Tip: Auto-numbering is disabled for default templates.\n"
                "Drag-and-drop only changes the folder structure."
            ),
            bold=True
        )
        
        # IMPORTANT: put the tree inside the frame
        tree_layout.addWidget(self.tree)
        
        # add the frame instead of the tree
        self.smart_layout.addWidget(self.tree_frame)
        
        # ==========================================================
        # Tree Controls Frame (Expand / Find / Sort)
        # ==========================================================
        self.tree_controls_frame = QFrame()
        self.tree_controls_frame.setFrameShape(QFrame.StyledPanel)

        tree_controls_layout = QHBoxLayout()
        tree_controls_layout.setContentsMargins(10,10,10,10)
        tree_controls_layout.setSpacing(8)
        self.tree_controls_frame.setLayout(tree_controls_layout)
        self.tree_controls_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        # Buttons
        self.expand_collapse_btn = QPushButton("Expand All")
        self.sort_btn = QPushButton("Sort A/Z")
        self.find_btn = QPushButton("Find")
        self.find_output_line = QLineEdit()
        self.find_output_line.setPlaceholderText("Input For Finding Folders.")
        self.find_output_line.setEnabled(False)
      

        for btn in [
            self.expand_collapse_btn,
            self.find_btn,
            self.sort_btn
        ]:
            btn.setMinimumHeight(35)
            btn.setMinimumWidth(120)

        tree_controls_layout.addWidget(self.expand_collapse_btn)
        
        tree_controls_layout.addWidget(self.sort_btn)
        tree_controls_layout.addWidget(self.find_btn)
        tree_controls_layout.addWidget(self.find_output_line)
        tree_controls_layout.addStretch()
        
        self.expand_collapse_btn.setEnabled(False)
        self.find_btn.setEnabled(False)
        self.sort_btn.setEnabled(False)

        # Add frame BELOW the tree
        self.smart_layout.addWidget(self.tree_controls_frame)
        
        self.tree.setAlternatingRowColors(True)
        


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
        self.build_buttons_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

        build_layout = QVBoxLayout()
        build_layout.setContentsMargins(10,10,10,10)
        build_layout.setSpacing(2)
        self.build_buttons_frame.setLayout(build_layout)

        self.default_to_desktop_btn = QPushButton("Default Desktop")
        self.output_location_btn = QPushButton("Output Location")
        self.build_folders_btn = QPushButton("Build Folders")

        for btn in [
            self.default_to_desktop_btn,
            self.output_location_btn,
            self.build_folders_btn
        ]:
            btn.setMinimumHeight(35)
            
        # btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        build_layout.addWidget(self.default_to_desktop_btn)
        build_layout.addWidget(self.output_location_btn)
        build_layout.addWidget(self.build_folders_btn)
        
        self.update_build_button_state()

        self.post_build_frame = QFrame()
        self.post_build_frame.setFrameShape(QFrame.StyledPanel)
        
        self.sep1 = self.make_vline()
        self.sep4 = self.make_vline()
    

        post_build_layout = QVBoxLayout()
        post_build_layout.setContentsMargins(10,10,10,10)
        post_build_layout.setSpacing(8)
        self.post_build_frame.setLayout(post_build_layout)

        self.open_folder_build_toggle = QCheckBox("Open Folder Location\n After Build")

        self.minimize_after_build_toggle = QCheckBox("Minimize App\n After Build")
        
        
        min_after = state.get("minimize_after_build", False)
        self.minimize_after_build_toggle.setChecked(min_after)
        
        post_build_layout.addWidget(self.open_folder_build_toggle, alignment=Qt.AlignTop)
        post_build_layout.addWidget(self.minimize_after_build_toggle, alignment=Qt.AlignTop)
        
        self.nested_ui = NestedUIController(self)
        self.nested_ui.connect_signals()

        main_controls_layout.setHorizontalSpacing(6)
        main_controls_layout.setVerticalSpacing(5)

        # group 1
        main_controls_layout.addWidget(self.folder_buttons_frame,   0, 0)
        main_controls_layout.addWidget(self.date_controls_frame,    0, 1)

        # separators after frame 2
        main_controls_layout.addWidget(self.sep1,                   0, 2)
        

        # group 2
        main_controls_layout.addWidget(self.template_controls_frame, 0, 6)
        main_controls_layout.addWidget(self.out_put_frame,           0, 4)
        main_controls_layout.addWidget(self.build_buttons_frame,     0, 9)

        # separators AFTER build frame
    
        main_controls_layout.addWidget(self.sep4,                   0, 8)

        # final frame
        main_controls_layout.addWidget(self.post_build_frame,       0, 5)


        for frame in [
            self.folder_buttons_frame,
            self.date_controls_frame,
            self.template_controls_frame,
            self.out_put_frame,
            self.build_buttons_frame,
            self.post_build_frame
        ]:
            frame.setMinimumWidth(170)
            frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # ---- Nested Status Panel ----
        self.smart_status_frame = QFrame()
        self.smart_status_frame.setObjectName("statusFrame")
        

        smart_status_layout = QHBoxLayout()
        smart_status_layout.setContentsMargins(10, 6, 10, 6)
        smart_status_layout.setSpacing(8)

        self.smart_status_frame.setLayout(smart_status_layout)
        self.smart_status_frame.setStyleSheet(
            "border: 2px solid 4D4D4DFF;"
        )

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
        self.folder_to_desktop.clicked.connect(self.create_desktop_folder)
        
        self.enumerate_toggle.toggled.connect(self.on_enumerate_toggle)
        self.date_time_config.currentIndexChanged.connect(self.desktop_on_date_mode_changed)
        
        
        self.expand_collapse_btn.clicked.connect(self.toggle_tree_expand)
        
    
        self.tree.itemExpanded.connect(self.update_expand_button_text)
        self.tree.itemCollapsed.connect(self.update_expand_button_text)
        self.tree.addFolderShortcut.connect(self.add_folder_btn.click)
        self.tree.addSubfolderShortcut.connect(self.add_subfolder_btn.click)
        self.tree.saveTemplateShortcut.connect(self.create_template_btn.click)
        self.sort_btn.clicked.connect(self.service.nested_manager.sort_tree)
        self.desktop_folder_line.returnPressed.connect(self.folder_to_desktop.click)
        
        
        self.open_folder_build_toggle.toggled.connect(
            lambda v: self.service.state_manager.update("open_folder_after_build", v)
        )

        self.remove_all_btn.clicked.connect(
            lambda: (self.service.nested_manager.remove_all_folders(), self.update_build_button_state())
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
        self.state = self.service.state
                

       
        
        self.desktop_status_timer = QTimer(self)
        self.desktop_status_timer.setSingleShot(True)
        self.desktop_status_timer.timeout.connect(lambda: self.reset_status("desktop"))

        self.smart_status_timer = QTimer(self)
        self.smart_status_timer.setSingleShot(True)
        self.smart_status_timer.timeout.connect(lambda: self.reset_status("nested"))
                        

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
        self.update_build_button_state()

        
        # Desktop Timestamp
        self.restore_timestamp_state(
            self.date_time_toggle,
            self.date_time_config,
            "desktop_date_stamp_enabled",
            "desktop_date_stamp_mode"
        )

        # Nested Timestamp
        self.restore_timestamp_state(
            self.nested_date_toggle,
            self.nested_date_config,
            "nested_date_stamp_enabled",
            "nested_date_stamp_mode"
        )


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
        
        self.desktop_folder_line.textChanged.connect(self.update_desktop_build_state)
        
        
        self.update_desktop_build_state()
        
    def rename_desktop_input(self):
        if self.current_mode != "desktop":
            return

        self.desktop_folder_line.setFocus()
        self.desktop_folder_line.selectAll()


    def clear_desktop_input(self):
        if self.current_mode != "desktop":
            return
        
        self.desktop_folder_line.setFocus()
        self.desktop_folder_line.clear()
        
        self.update_desktop_build_state()
        
    def restore_timestamp_state(self, toggle, combo, enabled_key, mode_key):
        enabled = self.state.get(enabled_key, False)
        toggle.setChecked(enabled)
        combo.setEnabled(enabled)

        mode = self.state.get(mode_key, "ISO")

        index_map = {
            "ISO": 0,
            "UK": 1,
            "US": 2
        }

        combo.setCurrentIndex(index_map.get(mode, 0))
        
    def make_vline(self):
        line = QFrame()
        line.setFixedWidth(10)  # thickness
        line.setStyleSheet("border: 2px solid 4D4D4DFF;"
        )
        return line
        
    def toggle_tree_expand(self):

        if self.tree_has_collapsed_nodes():
            self.tree.expandAll()
        else:
            self.tree.collapseAll()

        self.update_expand_button_text()
        
    
    def update_desktop_build_state(self):
        text = self.desktop_folder_line.text().strip()
        self.folder_to_desktop.setEnabled(bool(text))
        
    def update_build_button_state(self):
        
        default_template_loaded = (
            self.load_default_template_dropdown.currentIndex() != 0
        )

        has_items = self.tree.topLevelItemCount() > 0
        has_selection = self.tree.currentItem() is not None

        # Detect if nesting exists
        has_children = any(
            self.tree.topLevelItem(i).childCount() > 0
            for i in range(self.tree.topLevelItemCount())
        )
        
        # ---------------------------------------------------------
        # Pure parent structure → sorting not useful
        # ---------------------------------------------------------
        if not has_children:
            self.sort_btn.setEnabled(False)

        

        # Detect desktop path
        desktop_path = str(self.service.desktop_manager.desktop_path)
        current_path = self.base_path_line.text().strip()
        is_desktop = current_path == desktop_path

        # Desktop button
        self.default_to_desktop_btn.setEnabled(not is_desktop)

        # Search
        
        # Search
        visible_items = self.get_visible_tree_item_count()
        total_items = self.get_total_tree_item_count()

        can_find = visible_items > 8 or total_items > 8

        self.find_btn.setEnabled(can_find)
        self.find_output_line.setEnabled(can_find)

        # Build/remove
        self.build_folders_btn.setEnabled(has_items)
        self.remove_all_btn.setEnabled(has_items)
    

        # Build/remove
        self.build_folders_btn.setEnabled(has_items)
        self.remove_all_btn.setEnabled(has_items)

        # Tree utilities
        self.create_template_btn.setEnabled(has_items)
        # self.load_default_template_dropdown.setDisabled(has_items)
        
        # ---------------------------------------------------------
        # Auto-number override
        # ---------------------------------------------------------
        if self.auto_enumerate_folders.isChecked():
            self.sort_btn.setEnabled(False)
        else:
            # Detect if sorting is actually meaningful
            can_sort = self.tree.topLevelItemCount() > 1

            if not can_sort:
                for i in range(self.tree.topLevelItemCount()):
                    item = self.tree.topLevelItem(i)
                    if item.childCount() > 1:
                        can_sort = True
                        break

            self.sort_btn.setEnabled(can_sort)

        # ---------------------------------------------------------
        # Detect if sorting is actually meaningful
        # ---------------------------------------------------------
        def names_would_change(names):
            normalized = [n.strip().lower() for n in names]
            return normalized != sorted(normalized)

        can_sort = False

        # If tree has no nesting, sorting is not useful
        if not has_children:
            can_sort = False
        else:

            # ---- Check top level ----
            root_names = [
                self.tree.topLevelItem(i).text(0)
                for i in range(self.tree.topLevelItemCount())
            ]

            if len(root_names) > 1 and names_would_change(root_names):
                can_sort = True

            # ---- Check child groups ----
            if not can_sort:
                for i in range(self.tree.topLevelItemCount()):
                    parent = self.tree.topLevelItem(i)

                    child_names = [
                        parent.child(j).text(0)
                        for j in range(parent.childCount())
                    ]

                    if len(child_names) > 1 and names_would_change(child_names):
                        can_sort = True
                        break

        self.sort_btn.setEnabled(can_sort)


        # Expand/collapse only useful if nesting exists
        self.expand_collapse_btn.setEnabled(has_children)

        # Selection-dependent buttons
        self.remove_btn.setEnabled(has_selection)
        self.add_subfolder_btn.setEnabled(has_selection)
        
        # ---------------------------------------------------------
        # Auto-number rule
        # ---------------------------------------------------------
        if default_template_loaded:
            self.auto_enumerate_folders.setChecked(False)
            self.auto_enumerate_folders.setEnabled(False)
        else:
            self.auto_enumerate_folders.setEnabled(True)
            
            
    def get_total_tree_item_count(self):
        count = 0
        iterator = QTreeWidgetItemIterator(self.tree)

        while iterator.value():
            count += 1
            iterator += 1

        return count

    def get_visible_tree_item_count(self):
        def count_visible(item):
            total = 1

            if item.isExpanded():
                for i in range(item.childCount()):
                    total += count_visible(item.child(i))

            return total

        total = 0

        for i in range(self.tree.topLevelItemCount()):
            total += count_visible(self.tree.topLevelItem(i))

        return total
        
    def tree_has_collapsed_nodes(self):

        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)

            if not item.isExpanded() and item.childCount() > 0:
                return True

            stack = [item]

            while stack:
                node = stack.pop()

                for j in range(node.childCount()):
                    child = node.child(j)

                    if not child.isExpanded() and child.childCount() > 0:
                        return True

                    stack.append(child)

        return False
        
    def toggle_mode(self):

        if self.current_mode == "desktop":
            self.current_mode = "nested"
            self.service.set_state("ui_mode", self.current_mode)

            self.desktop_section_title.setText(
                "Nested Folder Creator\n(click to switch)"
            )

            self.smart_folder_creator_frame.show()
            self.desktop_folder_frame.hide()

            self.setFixedSize(self.nested_mode_width, self.nested_mode_height)

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
        

    def apply_accent_styles(self, accent_color: str):


        # ---- Section labels ----
        title_2 = [
            # self.smart_folder_creator,
            self.desktop_section_title,
            self.base_path_title,
            self.template_path_title
        ]

        for lbl in title_2:
            lbl.setStyleSheet(f"""
                QLabel {{
                    font-size: 15px;
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
                QCheckBox:disabled {{
                    color: rgba(140,140,140,0.6);
                }}
            """)

        self.current_accent_color = accent_color
        
        
        # ---- Status icons ----
        for icon in [
            self.desktop_status_icon,
            self.smart_status_icon
        ]:
            icon.setStyleSheet(f"font-weight: 700; color: {accent_color};")
    
    # shared status out function hat Qline uses for both output lines
    def set_status(self, message: str, target: str = "desktop", status_type: str = "info"):
        """
        target: "desktop" or "nested"
        status_type: "info", "success", "error"
        """

        accent = self.service.theme_controller.current_accent

        if target == "nested":
            icon_label = self.smart_status_icon
            text_label = self.smart_status_text
            frame = self.smart_status_frame
            self.smart_status_timer.start(10000)
        else:
            icon_label = self.desktop_status_icon
            text_label = self.desktop_status_text
            frame = self.desktop_status_frame
            self.desktop_status_timer.start(10000)

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
                border-radius: 1px;
                background-color: {bg};
            }}
            QLabel {{
                font-size: 15px;
            }}
        """)

        icon_label.setStyleSheet(f"font-weight: 700; color: {accent};")
        text_label.setText(message)


    def reset_status(self, target: str):

        accent = self.service.theme_controller.current_accent

        if target == "nested":
            icon_label = self.smart_status_icon
            text_label = self.smart_status_text
            frame = self.smart_status_frame
        else:
            icon_label = self.desktop_status_icon
            text_label = self.desktop_status_text
            frame = self.desktop_status_frame

        icon_label.setText(">")
        icon_label.setStyleSheet(f"font-weight: 700; color: {accent};")
        text_label.setText("")

        frame.setStyleSheet("""
            QFrame#statusFrame {
                border-radius: 6px;
                background-color: rgba(52, 152, 219, 0.10);
            }
            QLabel {
                font-size: 15px;
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
    
    def update_expand_button_text(self):

        if self.tree_has_collapsed_nodes():
            self.expand_collapse_btn.setText("Expand All")
        else:
            self.expand_collapse_btn.setText("Collapse All")

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
