import sys,os
from app_service import AppService
from smart_tree_widget import SmartTreeWidget
from nested_ui_controller import NestedUIController
from ui_state_controller import UIStateController
from status_controller import StatusController
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QShortcut, QKeySequence,QFont
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
    QComboBox,
    QGridLayout,QSpinBox,QHeaderView
)

INVALID_FOLDER_CHARS = '<>:"/\\|?*'
MAX_NESTED_FOLDER_NAME_LENGTH = 64

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.tree = SmartTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)

        self.tree.setEditTriggers(QAbstractItemView.DoubleClicked |QAbstractItemView.EditKeyPressed)

        # ---- Horizontal scroll support for wide trees ----
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.tree.header().setStretchLastSection(False)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.service = AppService(self.tree)
        state = self.service.state
        self.status = StatusController(self, self.service)
        
        self.setWindowTitle("Folder Generator")
        
        self.desktop_mode_height = 310
        self.nested_mode_height = 995
        
        self.desktop_mode_width = 700
        self.nested_mode_width = 900
        
        self.setFixedSize(self.nested_mode_width, self.nested_mode_height)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(8,8,8,8)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)
        
        # ==========================================================
        # Theme Selector
        # ==========================================================

        header_grid = QGridLayout()
        header_grid.setContentsMargins(5,5,5,5)
        header_grid.setHorizontalSpacing(15)
    
        # Title Frame (LEFT) NO
        self.desktop_title_frame = QFrame() #NO
        self.desktop_title_frame.setStyleSheet("border: 5px solid 4D4D4DFF;")
    
        self.desktop_title_frame.setFrameShape(QFrame.StyledPanel)
        self.desktop_title_frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        desktop_title_layout = QVBoxLayout()
        desktop_title_layout.setContentsMargins(8,8,8,8)
        desktop_title_layout.setSpacing(5)
        self.desktop_title_frame.setLayout(desktop_title_layout)

        self.current_mode = "desktop"
        self.desktop_section_title = QPushButton("Desktop Folder Creator\n(click to switch)")
        self.desktop_section_title.setFixedSize(215,45)

        self.desktop_section_title.setCursor(Qt.PointingHandCursor)
        self.desktop_section_title.setFlat(True)
        self.desktop_section_title.setStyleSheet("""
        QPushButton {
            font-size: 13px;
            font-weight: 1000;
            text-align: center;
        }
        """)
        
        self.desktop_section_title.clicked.connect(self.toggle_mode)
        desktop_title_layout.addWidget(self.desktop_section_title)
        
        self.theme_selector_frame = QFrame() #NO
        self.theme_selector_frame.setFrameShape(QFrame.StyledPanel)
        self.theme_selector_frame.setStyleSheet("border: 5px solid 4D4D4DFF;")

        theme_layout = QGridLayout()
        theme_layout.setSpacing(5)
        theme_layout.setContentsMargins(5,5,5,5)

        self.theme_selector_frame.setLayout(theme_layout)
        self.theme_buttons = []

        for i in range(2):

            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)

            if i == 0:
                btn.clicked.connect(
                    lambda _, idx=-2: (
                        None if self.service.theme_controller.current_index == idx
                        else self.service.theme_controller.select_theme(idx, self.service, self)
                    )
                )
                # 👇 WHITE THEME PREVIEW ONLY
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e8e8e8;
                        border: 2px solid #bdbdbd;
                        border-radius: 6px;
                    }
                    QPushButton:checked {
                        border: 3px solid black;
                    }
                """)

            else:
                btn.clicked.connect(
                    lambda _, idx=-1: (
                        None if self.service.theme_controller.current_index == idx
                        else self.service.theme_controller.select_theme(idx, self.service, self)
                    )
                )
                # 👇 BLACK THEME PREVIEW ONLY
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        border: 2px solid #444;
                        border-radius: 6px;
                    }
                    QPushButton:checked {
                        border: 3px solid white;
                    }
                """)

            theme_layout.addWidget(btn, 0, i)
            self.theme_buttons.append(btn)
                
        # ========================================
        # GRID FOR GUI CHANGER AND THEME SELECTOR
        # =========================================
        
        header_grid.addWidget(self.desktop_title_frame, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        header_grid.addWidget(self.theme_selector_frame, 0, 1, Qt.AlignRight | Qt.AlignBottom)
        header_grid.setColumnStretch(0, 1)
        header_grid.setColumnStretch(1, 0)
                
        main_layout.addLayout(header_grid)
        main_layout.addSpacing(5)
        
        # ===================================================================
        # FRAME 1 — FULL OUTER FRAME INCLUDES 3 INNER FRAMES + STATUS FRAMES
        # ===================================================================

        self.desktop_folder_frame = QFrame()
        self.desktop_folder_frame.setMinimumHeight(200)
        self.desktop_folder_frame.setFixedWidth(613)
        self.desktop_folder_frame.setFrameShape(QFrame.StyledPanel)
 
        self.desktop_layout = QVBoxLayout()
        self.desktop_layout.setSpacing(5)
        self.desktop_layout.setContentsMargins(4,4,4,4)
        self.desktop_folder_frame.setLayout(self.desktop_layout)
        
        desktop_controls_layout = QGridLayout()
        desktop_controls_layout.setContentsMargins(4,4,4,4)
        desktop_controls_layout.setHorizontalSpacing(5)

        # ==========================================================
        # Create widgets
        # ==========================================================

        self.desktop_folder_line = QLineEdit()
        self.desktop_folder_line.setPlaceholderText("ENTER FOLDER NAME...")
        self.desktop_folder_line.setFixedWidth(175)
        self.desktop_folder_line.setFixedHeight(40)
        self.desktop_folder_line.setMaxLength(64)
        
        self.rename_desktop_line_shortcut = QShortcut(QKeySequence("F2"), self.desktop_folder_line)
        self.rename_desktop_line_shortcut.activated.connect(self.rename_desktop_input)
        
        self.clear_desktop_line_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.desktop_folder_line)
        self.clear_desktop_line_shortcut.activated.connect(self.clear_desktop_input)

        self.folder_to_desktop = QPushButton("📁 To Desktop")


        # ---- Enumeration controls ----
        self.enumerate_toggle = QPushButton("CREATE MULTIPLE\nNUMBERED FOLDERS")
        self.enumerate_toggle.setCheckable(True)
    
        self.desktop_folder_number_enumerator = QSpinBox()
        self.desktop_folder_number_enumerator.setRange(1, 100)
        self.desktop_folder_number_enumerator.setEnabled(False)

        # ---- Timestamp controls ----
        self.date_time_toggle = QPushButton("ADD DATE STAMP")
        self.date_time_toggle.setCheckable(True)
   

        self.date_time_config = QComboBox()
        self.date_time_config.addItems([
            "ISO YYYY-MM-DD",
            "UK DD-MM-YYYY",
            "US MM-DD-YYYY"
        ])
        self.date_time_config.setEnabled(False)

        for buttons_combo_box_line in [
            self.date_time_config,
            self.date_time_toggle,
            self.desktop_folder_number_enumerator,
            self.enumerate_toggle,
            self.folder_to_desktop,
            self.desktop_folder_line,
        ]:
            buttons_combo_box_line.setFixedSize(160,45)
        
        
        for i in range(self.date_time_config.count()):
            self.date_time_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.date_time_config.setEditable(True)
        self.date_time_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.date_time_config.lineEdit().setReadOnly(True)

        # =========================================================
        # Column 1 — Input frame  FOLDER TO DESKTOP 
        # ==========================================================
        self.desktop_input_frame = QFrame() #NO
        self.desktop_input_frame.setFrameShape(QFrame.StyledPanel)

        desktop_input_layout = QVBoxLayout()
        self.desktop_input_frame.setLayout(desktop_input_layout)

        desktop_input_layout.addWidget(self.desktop_folder_line)
        desktop_input_layout.addWidget(self.folder_to_desktop)
        desktop_input_layout.setAlignment(Qt.AlignCenter)

        # ==========================================================
        # Column 2 — Enumeration frame
        # ==========================================================
        self.desktop_enumerator_frame = QFrame() #NO
        self.desktop_enumerator_frame.setFrameShape(QFrame.StyledPanel)

        enumerator_layout = QVBoxLayout()
        self.desktop_enumerator_frame.setLayout(enumerator_layout)

        enumerator_layout.addWidget(self.enumerate_toggle)
        enumerator_layout.addWidget(self.desktop_folder_number_enumerator)
        enumerator_layout.setAlignment(Qt.AlignCenter)

        # ==========================================================
        # Column 3 — Date controls frame
        # ==========================================================
        self.desktop_date_frame = QFrame() #NO
        self.desktop_date_frame.setFrameShape(QFrame.StyledPanel)
        
        desktop_date_layout = QVBoxLayout()
        self.desktop_date_frame.setLayout(desktop_date_layout)
    
        desktop_date_layout.addWidget(self.date_time_toggle)
        desktop_date_layout.addWidget(self.date_time_config)
        desktop_date_layout.setAlignment(Qt.AlignCenter)

        for desktop_layouts in[
            enumerator_layout,
            desktop_date_layout,
            desktop_input_layout,

        ]:
            desktop_layouts.setContentsMargins(5,5,5,5)
            desktop_layouts.setSpacing(5)


        # ==========================================================
        # Add subframes into parent controls frame
        # ==========================================================
        desktop_controls_layout.addWidget(self.desktop_input_frame, 0, 0)
        desktop_controls_layout.addWidget(self.desktop_enumerator_frame, 0, 1)
        desktop_controls_layout.addWidget(self.desktop_date_frame, 0, 2)

        desktop_controls_layout.setColumnStretch(0, 1)
        desktop_controls_layout.setColumnStretch(1, 1)
        desktop_controls_layout.setColumnStretch(2, 1)
        
        self.desktop_layout.addLayout(desktop_controls_layout)
        
        # ---- STATUS LABEL FRAME +  OUT PUT ----
    
        self.desktop_status_frame = QFrame() #NO
        self.desktop_status_frame.setObjectName("statusFrame")
        self.desktop_status_frame.setMaximumHeight(50)

        desktop_status_layout = QHBoxLayout()
        desktop_status_layout.setContentsMargins(8,8,8,8)
        desktop_status_layout.setSpacing(5)
        self.desktop_status_frame.setLayout(desktop_status_layout)

        for desktop_frames in [
            self.desktop_status_frame,
            self.desktop_date_frame,
            self.desktop_enumerator_frame,
            self.desktop_input_frame,
            self.desktop_folder_frame
        ]:
            desktop_frames.setStyleSheet("border: 5px solid 4D4D4DFF;")
        
        self.desktop_status_frame.setFixedWidth(587)
        self.desktop_status_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.desktop_status_icon = QLabel(">")
        self.desktop_status_text = QLabel("")
        self.desktop_status_text.setMaximumWidth(500)

        desktop_status_layout.addWidget(self.desktop_status_icon)
        desktop_status_layout.addWidget(self.desktop_status_text)
        desktop_status_layout.addStretch()

        self.desktop_layout.addWidget(self.desktop_status_frame,alignment=Qt.AlignHCenter)
        
        # Add entire frame to main layout
        main_layout.addWidget(self.desktop_folder_frame, alignment=Qt.AlignCenter)
        main_layout.addSpacing(5)# BIG separation between sections

################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
# END OF DESKTOP FOLDER CREATOR GUI
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################

        # ====== Parent Frame to EVerything on Nested folder creator
        self.smart_folder_creator_frame = QFrame()
        self.smart_folder_creator_frame.setFrameShape(QFrame.StyledPanel)
        self.smart_folder_creator_frame.setStyleSheet("border: 5px solid 4D4D4DFF;")
        self.smart_folder_creator_frame.setFixedWidth(875)
        self.smart_folder_creator_frame.setFixedHeight(880)

        self.smart_layout = QVBoxLayout()
        self.smart_layout.setSpacing(0)
        self.smart_layout.setContentsMargins(2,2,2,2)
        self.smart_folder_creator_frame.setLayout(self.smart_layout)

        # # ==========================================================
        # # Parent layout inside controls_frame
        # # ==========================================================
        main_controls_layout = QGridLayout()
        main_controls_layout.setContentsMargins(5,5,5,5)
        self.smart_layout.addLayout(main_controls_layout)
        

        # ==========================================================
        # Create all widgets first
        # ==========================================================
        self.add_folder_btn = QPushButton("Add\nFolder")
        self.add_subfolder_btn = QPushButton("Add\nSubfolder")

        self.remove_btn = QPushButton("Remove\nSelected")
        self.remove_all_btn = QPushButton("Remove\nAll")

        self.load_template_btn = QPushButton("Load Templates")
        self.save_template_btn= QPushButton("Save Templates")

        self.load_user_template_dropdown = QComboBox()
        self.load_user_template_dropdown.addItems(["User Templates"])
        self.load_user_template_dropdown.insertSeparator(self.load_user_template_dropdown.count())

        self.load_user_template_dropdown.setEnabled(True)
        
        self.load_default_template_dropdown = QComboBox()
        self.load_default_template_dropdown.addItem("Default Templates")
        self.load_default_template_dropdown.insertSeparator(self.load_default_template_dropdown.count())
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

        self.load_default_template_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.load_default_template_dropdown.setEnabled(True)

        for i in range(self.load_default_template_dropdown.count()):
            if self.load_default_template_dropdown.itemText(i) == "":
                continue

            self.load_default_template_dropdown.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.auto_enumerate_folders = QPushButton("AUTO NUMBER\nFOLDERS AND\n SUB FOLDERS\n(IF DUPLICATED)")
        self.nested_date_toggle = QPushButton("ADD DATE\n STAMP TO\nPARENT FOLDERS")

        for button in [
            self.auto_enumerate_folders,
            self.nested_date_toggle
        ]:
            button.setFixedWidth(160)
            button.setCheckable(True)
            button.setFixedHeight(80)

        self.nested_date_config = QComboBox()
        self.nested_date_config.addItems([
            "ISO YYYY-MM-DD",
            "UK DD-MM-YYYY",
            "US MM-DD-YYYY"
        ])
        self.nested_date_config.setEnabled(False)
        self.nested_date_config.setMaximumWidth(175)
        self.nested_date_config.setFixedHeight(40)

        for i in range(self.nested_date_config.count()):
            self.nested_date_config.setItemData(
                i,
                Qt.AlignLeft | Qt.AlignVCenter,
                Qt.TextAlignmentRole
            )

        self.nested_date_config.setEditable(True)
        self.nested_date_config.lineEdit().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.nested_date_config.lineEdit().setReadOnly(True)
    
        # ==========================================================
        # Column 1 — Template frame NO
        # ==========================================================

        self.template_controls_frame = QFrame()
        self.template_controls_frame.setFrameShape(QFrame.StyledPanel)
        self.template_controls_frame.setFixedWidth(165)

        template_layout = QVBoxLayout()
        template_layout.setContentsMargins(5,5,5,5)
        template_layout.setSpacing(5)
        self.template_controls_frame.setLayout(template_layout)
        
        template_layout.addWidget(self.load_template_btn)
        template_layout.addWidget(self.save_template_btn)
        template_layout.addWidget(self.load_user_template_dropdown)
        template_layout.addWidget(self.load_default_template_dropdown)
        template_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop) 
        
        # ==========================================================
        # Column 2 — Folder buttons frame NO
        # ==========================================================

        self.folder_buttons_frame = QFrame()
        self.folder_buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.folder_buttons_frame.setFixedWidth(200)

        folder_buttons_layout = QVBoxLayout()
        folder_buttons_layout.setContentsMargins(5,5,5,5)
        folder_buttons_layout.setSpacing(5)
        self.folder_buttons_frame.setLayout(folder_buttons_layout)

        # ---- ROW 1 (Add / Sub) ----
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.add_folder_btn.setText("📁 Add")
        self.add_subfolder_btn.setText("📂 Sub")

        self.add_folder_btn.setFixedSize(80,40)
        self.add_subfolder_btn.setFixedSize(80,40)

        top_row.addStretch()
        top_row.addWidget(self.add_folder_btn)
        top_row.addWidget(self.add_subfolder_btn)
        top_row.addStretch()

        # ---- ROW 2 (File dropdown) ----
        file_row = QHBoxLayout()
        file_row.setSpacing(10)

        self.file_dropdown = QComboBox()
        self.file_dropdown.addItems([
                "Add Blank File",
                "──────────",
                "Python (.py)",
                "JavaScript (.js)",
                "HTML (.html)",
                "CSS (.css)",
                "──────────",
                "Text (.txt)",
                "Markdown (.md)",
                "README.md",
                "──────────",
                "JSON (.json)",
                "YAML (.yaml)",
                "ENV (.env)",
                "──────────",
                "Batch (.bat)",
                "PowerShell (.ps1)"
        ])

        self.file_dropdown.setFixedSize(170, 40)

        file_row.addStretch()
        file_row.addWidget(self.file_dropdown)
        file_row.addStretch()

        # ---- ROW 3 (Remove / Remove All) ----
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(5)

        self.remove_btn.setFixedSize(85,50)
        self.remove_all_btn.setFixedSize(85,50)

        bottom_row.addStretch()
        bottom_row.addWidget(self.remove_btn)
        bottom_row.addWidget(self.remove_all_btn)
        bottom_row.addStretch()

        # ---- FINAL LAYOUT ----
        folder_buttons_layout.addLayout(top_row)
        folder_buttons_layout.addLayout(file_row)
        folder_buttons_layout.addLayout(bottom_row)
        folder_buttons_layout.addStretch()

        # ==========================================================
        # Column 2 — Date / auto-number frame NO
        # ==========================================================

        self.date_controls_frame = QFrame()
        self.date_controls_frame.setFrameShape(QFrame.StyledPanel)
        self.date_controls_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.date_controls_frame.setFixedWidth(190)

        date_layout = QVBoxLayout()
        date_layout.setContentsMargins(5,5,5,5)
        date_layout.setSpacing(5)
        date_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.date_controls_frame.setLayout(date_layout)

        date_layout.addWidget(self.auto_enumerate_folders, alignment=Qt.AlignHCenter)
        date_layout.addWidget(self.nested_date_toggle, alignment=Qt.AlignHCenter)
        date_layout.addWidget(self.nested_date_config, alignment=Qt.AlignHCenter)

        # ----------------------------------------------------------
        # Create path fields FIRST
        # ----------------------------------------------------------
        self.base_path_line = QLineEdit()
        self.base_path_line.setPlaceholderText("Select base directory for output folder location")
        
        self.template_path_line = QLineEdit()
        self.template_path_line.setPlaceholderText("OUTPUT LOCATION FOR USER MADE TEMPLATES.")

        # ----------------------------------------------------------
        # Paths row
        # ----------------------------------------------------------

        paths_layout = QHBoxLayout()
        paths_layout.setContentsMargins(5,5,5,5)
        paths_layout.setSpacing(5)

        self.template_path_column = QFrame() # NO
        self.template_path_column.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.template_path_column.setFixedWidth(360)
        template_col_layout = QVBoxLayout()
        template_col_layout.setContentsMargins(5,5,5,5)
        template_col_layout.setSpacing(2)
        self.template_path_column.setLayout(template_col_layout)

        self.base_path_column = QFrame() # NO
        self.base_path_column.setFixedWidth(400)
        self.base_path_column.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        base_col_layout = QVBoxLayout()
        base_col_layout.setContentsMargins(5,5,5,5)
        base_col_layout.setSpacing(2)
        self.base_path_column.setLayout(base_col_layout)
        
        self.template_path_title = QLabel("TEMPLATE SAVE LOCATION")
        self.base_path_title = QLabel("OUTPUT FOLDER LOCATION")

        for location_lines in [
            self.template_path_line,
            self.base_path_line
        ]:

            location_lines.setFixedSize(300,40)
            location_lines.setReadOnly(True)
            location_lines.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        template_col_layout.addWidget(self.template_path_title)
        template_col_layout.addWidget(self.template_path_line)

        for title in [
            self.template_path_title,
            self.base_path_title
        ]:
            title.setFixedWidth(200)
            title.setFixedHeight(40)
            title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            title.setAlignment(Qt.AlignCenter)
        
        base_col_layout.addWidget(self.base_path_title)
        base_col_layout.addWidget(self.base_path_line)
        
        paths_layout.addWidget(self.template_path_column)
        paths_layout.addStretch()
        paths_layout.addWidget(self.base_path_column)
        

        frame_layout_output = QVBoxLayout()
        frame_layout_output.setContentsMargins(5,5,5,5)
        frame_layout_output.setSpacing(5)
        frame_layout_output.addLayout(paths_layout)

################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################
################################################################################################################################################################################################################################################################################################################################################################################################

        # # # # # # # # # # # # # # # # # # # # # # # Ouput Folder Creator # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # NO
        self.tree_frame = QFrame()
        self.tree_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_frame.setMinimumHeight(0)
        self.tree_frame.setFrameShape(QFrame.StyledPanel)
        
        
        tree_layout = QVBoxLayout()
        tree_layout.setContentsMargins(5,5,5,5)
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
                "Files can either be drag drop loaded in here."
                "Or created/loaded using the buttons above."
                "(accepts .json, .txt, .md files).\n"

                "User templates using the save button are saved as .json, md or.txt."
                "A copy of them will be saved to:\n"
                "C:/Users/yourusername/AppData/Local/FolderCreator/.\n"
                "To access this easily, right click the dropdown arrow on 'User Templates'.\n"
                "Drag-and-dropped templates are also saved there automatically.\n\n"

                "Folder trees can be copy pasted in here using Ctrl + V as plain text."
                "Entire trees from your desktop can be dragged onto here.\n"
                "Files will be ignored and only the folder structure will be shown.\n\n"

                "Hotkeys:\n"
                "Ctrl + N → Add Folder."
                "Ctrl + Shift + N → Add Subfolder."
                "Ctrl + S → Save Template."
                "Ctrl + O → Load Template.\n"
                "F2 → Rename."
                "Delete → Remove selected folder.\n\n"

                "Template tip:\n"
                "Templates can be saved as .json, .txt, or .md using the save dialog.\n\n"

                "Tips:\n"
                "• Drag folders to change hierarchy."
                "• Drag below → new parent-level folder."
                "• Drag onto → make subfolder."
                "• Auto-numbering only applies when using Add Folder/Subfolder buttons.\n"
                "• Auto-numbering is disabled for default templates."
                "• Drag-and-drop only changes structure."
            ),
            bold=True
        )

        # IMPORTANT: put the tree inside the frame
        tree_layout.addWidget(self.tree)
        
        # add the frame instead of the tree
        self.smart_layout.addWidget(self.tree_frame)
        
        # ==========================================================
        # FRAME 6 NO tree controls Expand find etc
        # ==========================================================

        tree_controls_layout = QHBoxLayout()
        tree_controls_layout.setContentsMargins(5,5,5,5)
        tree_controls_layout.setSpacing(5)

        # Buttons
        self.expand_tree_btn = QPushButton("EXPAND TREE")
        self.expand_folders_collapse_btn = QPushButton("EXPAND FOLDERS")
        self.sort_btn = QPushButton("SORT A/Z")
        self.find_btn = QPushButton("FIND")
        self.find_output_line = QLineEdit()
        self.find_output_line.setPlaceholderText("INPUT FOR FINDING FOLDERS.")
        self.find_output_line.setStyleSheet("font: 15px solid #FFFFFF;")
        self.find_output_line.setEnabled(True)
        self.find_output_line.setFixedSize(230,40)

        for btn in [
            self.expand_tree_btn
        ]:
            btn.setFixedSize(120,40)

        self.expand_folders_collapse_btn.setFixedSize(140,40)

        for btns in [
            self.find_btn,
            self.sort_btn,
        ]:
            btns.setFixedSize(100,40)
            
        tree_controls_layout.addWidget(self.expand_tree_btn)
        tree_controls_layout.addWidget(self.expand_folders_collapse_btn)
        tree_controls_layout.addStretch()
        tree_controls_layout.addWidget(self.sort_btn)
        tree_controls_layout.addWidget(self.find_btn)
        tree_controls_layout.addWidget(self.find_output_line)
        
        self.expand_folders_collapse_btn.setEnabled(False)
        self.find_btn.setEnabled(False)
        self.sort_btn.setEnabled(False)

        # Add frame BELOW the tree
        self.smart_layout.addLayout(tree_controls_layout)
        
        self.tree.setAlternatingRowColors(True)

        # ==========================================================
        # FRAME 5 NO
        # ==========================================================
        self.build_buttons_frame = QFrame()
        self.build_buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.build_buttons_frame.setFixedWidth(145)
        
    

        build_layout = QVBoxLayout()
        build_layout.setContentsMargins(5,5,5,5)
        build_layout.setSpacing(5)
        self.build_buttons_frame.setLayout(build_layout)

        self.default_to_desktop_btn = QPushButton("Default To Desk")
        self.output_location_btn = QPushButton("Output Dir")
        self.build_folders_btn = QPushButton("Build 📁")

        for btns in [
            self.load_template_btn,
            self.save_template_btn,
        ]:
            btns.setFixedSize(145,40)

        for btn in [
            self.default_to_desktop_btn,
            self.output_location_btn,
            self.build_folders_btn
        ]:
            btn.setFixedHeight(40)
            btn.setFixedWidth(125)
            
        build_layout.addWidget(self.default_to_desktop_btn)
        build_layout.addWidget(self.output_location_btn)
        build_layout.addWidget(self.build_folders_btn)
        build_layout.setAlignment(Qt.AlignTop)

        self.post_build_frame = QFrame()
        self.post_build_frame.setFrameShape(QFrame.StyledPanel)
        self.post_build_frame.setFixedWidth(140)

        self.open_folder_build_toggle = QPushButton("OPEN FOLDER\nLOCATION AFTER\n BUILD")
        self.minimize_after_build_toggle = QPushButton("MINIMIZE APP\nAFTER BUILD")

        for btn in [
            self.open_folder_build_toggle,
            self.minimize_after_build_toggle,

        ]:
            btn.setFixedWidth(120)
            btn.setMinimumHeight(60)
            btn.setCheckable(True)
    
        self.post_build_layout = QVBoxLayout()
        self.post_build_layout.setContentsMargins(5,5,5,5)
        self.post_build_layout.setSpacing(5)
        self.post_build_layout.setAlignment(Qt.AlignTop)

        self.post_build_frame.setLayout(self.post_build_layout)
        self.post_build_layout.addWidget(self.open_folder_build_toggle)
        self.post_build_layout.addWidget(self.minimize_after_build_toggle)
                
        min_after = state.get("minimize_after_build", False)
        self.minimize_after_build_toggle.setChecked(min_after)

        self.nested_ui = NestedUIController(self)
        self.nested_ui.connect_signals()

        for frames in [
            self.build_buttons_frame,
            self.date_controls_frame,
            self.folder_buttons_frame,
            self.post_build_frame,
            self.template_controls_frame,


        ]:
            frames.setFixedHeight(230)

        widgets = [
            self.folder_buttons_frame,
            self.date_controls_frame,
            self.post_build_frame,
            self.template_controls_frame,
            self.build_buttons_frame
        ]

        for dropdowns in [
            self.load_user_template_dropdown,
            self.load_default_template_dropdown,

        ]:
            dropdowns.setFixedSize(145,40)

        for col, widget in enumerate(widgets):
            main_controls_layout.addWidget(widget, 0, col)

        for i in range(5):  # first 5 frames only
            main_controls_layout.setColumnStretch(i, 1)

        # ---- Nested Status Panel ---- 
        self.smart_status_frame = QFrame()
        self.smart_status_frame.setObjectName("statusFrame")
        self.smart_status_frame.setFixedHeight(50)
        
        smart_status_layout = QHBoxLayout()
        smart_status_layout.setContentsMargins(5,5,5,5)
        smart_status_layout.setSpacing(5)

        self.smart_status_frame.setLayout(smart_status_layout)
        self.smart_status_frame.setStyleSheet("border: 5px solid 4D4D4DFF;")
        self.smart_status_frame.setFixedWidth(850)

        self.smart_status_icon = QLabel(">")
        self.smart_status_text = QLabel("")
        self.smart_status_text.setMaximumWidth(600)
        
        smart_status_layout.addWidget(self.smart_status_icon)
        smart_status_layout.addWidget(self.smart_status_text)
        smart_status_layout.addStretch()

        for frames in [
            self.date_controls_frame,
            self.folder_buttons_frame,
            self.template_controls_frame,
            self.build_buttons_frame,
            self.post_build_frame,

        ]:
            frames.setStyleSheet("border: 5px solid #000000")

        frame_layout_output.addWidget(self.smart_status_frame,alignment=Qt.AlignHCenter) 
        self.smart_layout.addLayout(frame_layout_output)
        frame_layout_output.setContentsMargins(0,0,0,0)
        frame_layout_output.setSpacing(0)
        main_layout.addWidget(self.smart_folder_creator_frame, alignment=Qt.AlignHCenter)

        self.ui_state = UIStateController(self)
    
        connections = [
            (self.date_time_toggle.clicked,self.desktop_on_date_stamp_toggled),
            (self.folder_to_desktop.clicked, self.create_desktop_folder),
            (self.enumerate_toggle.clicked, self.on_enumerate_toggle),
            (self.date_time_config.currentIndexChanged, self.desktop_on_date_mode_changed),
            (self.expand_folders_collapse_btn.clicked, self.toggle_tree_expand),
            (self.tree.itemExpanded, self.update_expand_button_text),
            (self.tree.itemExpanded, self.ui_state.update_build_button_state),
            (self.tree.itemCollapsed, self.ui_state.update_build_button_state),
            (self.tree.itemCollapsed, self.update_expand_button_text),
            (self.tree.addFolderShortcut, self.add_folder_btn.click),
            (self.tree.addSubfolderShortcut, self.add_subfolder_btn.click),
            (self.tree.saveTemplateShortcut, self.save_template_btn.click),
            (self.sort_btn.clicked, self.service.nested_manager.sort_tree),
            (self.desktop_folder_line.returnPressed, self.folder_to_desktop.click),
            (self.tree.itemChanged, self.ui_state.update_build_button_state),
            (self.load_template_btn.clicked, self.nested_ui.load_template),
            (self.expand_tree_btn.clicked,self.tree_gui_stretch),
            (self.tree.itemChanged, self.enforce_tree_name_limit),
            (self.tree.itemChanged, self.ui_state.update_nested_build_state)
        ]

        for signal, handler in connections:
            signal.connect(handler)
        
        self.load_user_template_dropdown.enterEvent = lambda e: (
            self.status.set(
                "Right-click to open user templates folder."
                "Can delete folders here if you wish.",
                target="nested",
                status_type="info"
            ),
            QComboBox.enterEvent(self.load_user_template_dropdown, e)
        )

        self.load_user_template_dropdown.leaveEvent = lambda e: (self.status.reset("nested"),QComboBox.leaveEvent(self.load_user_template_dropdown, e))
        self.load_user_template_dropdown.setContextMenuPolicy(Qt.CustomContextMenu)
        self.load_user_template_dropdown.customContextMenuRequested.connect(lambda pos: os.startfile(str(self.service.template_paths.user_dir)))
        self.load_user_template_dropdown.currentIndexChanged.connect(self.nested_ui.load_user_template_from_dropdown)
        self.open_folder_build_toggle.toggled.connect(lambda v: self.service.state_manager.update("open_folder_after_build", v))
        self.nested_ui.refresh_user_templates_dropdown()
            
        self.desktop_folder_number_enumerator.valueChanged.connect(lambda v: self.service.set_state("desktop_enumeration_count", v))
        self.add_folder_btn.clicked.connect(lambda: (self.service.nested_manager.add_root_folder(), self.ui_state.update_build_button_state()))
        self.add_subfolder_btn.clicked.connect(lambda: (self.service.nested_manager.add_subfolder(), self.ui_state.update_build_button_state()))
        self.remove_btn.clicked.connect(lambda: (self.service.nested_manager.remove_selected_folders(),self.ui_state.update_build_button_state(),QTimer.singleShot(0, self.ui_state.update_nested_build_state)))
        self.tree.itemSelectionChanged.connect(self.ui_state.update_build_button_state)
        self.remove_all_btn.clicked.connect(
            lambda: (
                self.service.nested_manager.remove_all_folders(),
                self.load_user_template_dropdown.setCurrentIndex(0),
                self.load_default_template_dropdown.setCurrentIndex(0),
                setattr(self.nested_ui, "_current_loaded_template", None),
                self.ui_state.update_build_button_state(),
                QTimer.singleShot(0, self.ui_state.update_nested_build_state)
            )
        )

        self.file_dropdown.currentIndexChanged.connect(
            lambda i: (
                None if i in (0, 1, 6, 10, 14) else (
                    self.service.nested_manager.add_file(
                        {
                            2: "main.py",
                            3: "script.js",
                            4: "index.html",
                            5: "styles.css",

                            7: "notes.txt",
                            8: "README.md",
                            9: "README.md",

                            11: "data.json",
                            12: "config.yaml",
                            13: ".env",

                            15: "run.bat",
                            16: "script.ps1"
                        }.get(i, "new_file.txt")
                    ),
                    self.file_dropdown.setCurrentIndex(0),
                    self.ui_state.update_build_button_state()
                )
            )
        )

        state = self.service.state
        self.state = state
        theme_index = state.get("theme_index", -2)

        if theme_index not in (-2, -1):
            theme_index = -2

        self.service.theme_controller.select_theme(theme_index, self.service,self)

        for i, btn in enumerate(self.theme_buttons):

            is_active = (
                (theme_index == -2 and i == 0) or
                (theme_index == -1 and i == 1)
            )

            btn.setChecked(is_active)
            btn.setCheckable(not is_active)

        for icon in [
            self.desktop_status_icon,
            self.smart_status_icon
        ]:
            icon.setStyleSheet(f"font-weight: 700; color: ;")

        self.current_mode = state.get("ui_mode", "desktop")

        for attr, target in [
            ("desktop_status_timer", "desktop"),
            ("smart_status_timer", "nested"),
        ]:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda t=target: self.status.reset(t))
            setattr(self, attr, timer)

        # ---------------------------------------------------------
        # Initial UI mode
        # ---------------------------------------------------------
        if self.current_mode == "nested":
            self.desktop_section_title.setText("Nested Folder Creator\n(click to switch)")
            self.desktop_folder_frame.hide()
            self.smart_folder_creator_frame.show()
            self.setFixedSize(self.nested_mode_width, self.nested_mode_height)
        else:
            self.desktop_section_title.setText("Desktop Folder Creator\n(click to switch)")
            self.smart_folder_creator_frame.hide()
            self.desktop_folder_frame.show()
            self.setFixedSize(635, self.desktop_mode_height)
            
        # ---------------------------------------------------------
        # Restore Last Base Directory
        # ---------------------------------------------------------
        last_base = state.get("last_base_dir", "")
        self.base_path_line.setText(last_base)

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
        self.base_path_line.textChanged.connect(self.ui_state.update_build_button_state)

        self.update_desktop_build_state()
        self.ui_state.update_build_button_state()
        
    def enforce_tree_name_limit(self, item, column):
        name = item.text(0)

        if len(name) > MAX_NESTED_FOLDER_NAME_LENGTH:
            trimmed = name[:MAX_NESTED_FOLDER_NAME_LENGTH]
            item.setText(0, trimmed)

            self.smart_status_icon.setText("⚠")
            self.smart_status_text.setText(f"Folder names limited to {MAX_NESTED_FOLDER_NAME_LENGTH} characters.")
            
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
        line.setFixedWidth(6)  # thickness
        line.setStyleSheet("border: 6px solid 4D4D4DFF;")
        return line
        
    def toggle_tree_expand(self):
        if self.ui_state.tree_has_collapsed_nodes():
            self.tree.expandAll()
        else:
            self.tree.collapseAll()

        self.update_expand_button_text()
        
    def update_desktop_build_state(self):
        text = self.desktop_folder_line.text().strip()
        if not text:
            self.folder_to_desktop.setEnabled(False)
            self.desktop_status_icon.setText(">")
            self.desktop_status_text.clear()
            return

        has_invalid = any(c in text for c in INVALID_FOLDER_CHARS)
        self.folder_to_desktop.setEnabled(not has_invalid)

        # ---- validation priority ----
        if has_invalid:
            self.desktop_status_icon.setText("⚠")
            self.desktop_status_text.setText("Invalid characters detected. Remove <>:\"/\\|?* from folder name.")

        elif len(text) >= MAX_NESTED_FOLDER_NAME_LENGTH:
            self.desktop_status_icon.setText("⚠")
            self.desktop_status_text.setText(f"Folder name limit is {MAX_NESTED_FOLDER_NAME_LENGTH} characters.")

        else:
            self.desktop_status_icon.setText(">")
            self.desktop_status_text.clear()

    def tree_gui_stretch(self):
        is_visible = self.smart_status_frame.isVisible()

        targets = [
            self.template_path_column,
            self.base_path_column,
            self.smart_status_frame
        ]

        if is_visible:
            for w in targets:
                w.hide()
            self.expand_tree_btn.setText("COLLAPSE TREE")

        else:
            for w in targets:
                w.show()
            self.expand_tree_btn.setText("EXPAND TREE")

        QTimer.singleShot(0, self.ui_state.update_build_button_state)
        self.tree.setVisible(True)
    
    def toggle_mode(self):
        if self.current_mode == "desktop":
            self.current_mode = "nested"
            self.service.set_state("ui_mode", self.current_mode)
            self.desktop_section_title.setText("Nested Folder Creator\n(click to switch)")

            self.smart_folder_creator_frame.show()
            self.desktop_folder_frame.hide()
            self.setFixedSize(self.nested_mode_width, self.nested_mode_height)

        else:
            self.current_mode = "desktop"
            self.service.set_state("ui_mode", self.current_mode)

            self.desktop_section_title.setText("Desktop Folder Creator\n(click to switch)")
            self.desktop_folder_frame.show()
            self.smart_folder_creator_frame.hide()
            self.setFixedSize(635, self.desktop_mode_height)

    
    ####################### Desktop Folder Creator methods #################################
    
    def update_expand_button_text(self):
        if self.ui_state.tree_has_collapsed_nodes():
            self.expand_folders_collapse_btn.setText("EXPAND FOLDERS")
        else:
            self.expand_folders_collapse_btn.setText("COLLAPSE FOLDERS")
            
    def update_expand_tree(self):
        if self.tree_gui_stretch():
            self.expand_tree_btn.setText("EXPAND TREE")
        else:
            self.expand_tree_btn.setText("COLLAPSE TREE")

    def desktop_on_date_stamp_toggled(self, checked):
        self.date_time_config.setEnabled(checked)

        self.service.set_state("desktop_date_stamp_enabled",checked)
        
    def on_enumerate_toggle(self, checked: bool):
        self.desktop_folder_number_enumerator.setEnabled(checked)

        if checked and self.desktop_folder_number_enumerator.value() == 1:
            self.desktop_folder_number_enumerator.setValue(2)

        self.service.set_state("desktop_enumeration_enabled",checked)
        
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

        self.service.set_state("desktop_date_stamp_mode",mode)
                    
    def create_desktop_folder(self):
        raw_name = self.desktop_folder_line.text().strip()
        base_name = self.desktop_folder_line.text().strip()

        if not base_name:
            self.status.set(
                "No folder name entered.",
                target="desktop",
                status_type="error"
            )
            return
        # push cleaned name back into the UI
        if base_name != raw_name:
            self.desktop_folder_line.setText(base_name)

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
            self.status.set(
                f'Folder "{base_name}" created on Desktop.',
                target="desktop",
                status_type="success"
            )

        elif created > 1:
            self.status.set(
                f"{created} folders created on Desktop.",
                target="desktop",
                status_type="success"
            )

        else:
            self.status.set(
                "Folders already exist or could not be created.",
                target="desktop",
                status_type="error"
            )

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
