from desktop_folder_manager import DesktopFolderManager
from nested_folder_manager import NestedFolderManager
from template_IO_layer import TemplateService
from state_manager import StateManager
from theme_controller import ThemeController


class AppService:

    def __init__(self, tree_widget):
        self.desktop_manager = DesktopFolderManager()
        self.nested_manager = NestedFolderManager(tree_widget)
        self.template_service = TemplateService()
        self.state_manager = StateManager()
        self.theme_controller = ThemeController()

        self.state = self.state_manager.load_state()

    # ---------------------------------------------------------
    # Desktop folder creation
    # ---------------------------------------------------------

    def create_desktop_folder(self, name, timestamp_mode=None):
        return self.desktop_manager.create_folder(name, timestamp_mode)

    # ---------------------------------------------------------
    # Nested tree operations
    # ---------------------------------------------------------

    def add_folder(self):
        self.nested_manager.add_root_folder()

    def add_subfolder(self):
        self.nested_manager.add_subfolder()

    def remove_selected(self):
        self.nested_manager.remove_selected_folders()

    def remove_all(self):
        self.nested_manager.remove_all_folders()

    def build_tree(self, base_path, timestamp_mode=None):
        return self.nested_manager.build_folders(base_path, timestamp_mode)

    # ---------------------------------------------------------
    # Template handling
    # ---------------------------------------------------------

    def save_template(self, parent):
        return self.template_service.save_from_tree(parent, self.nested_manager)

    def load_template_dialog(self, parent):
        return self.template_service.load_into_tree(parent, self.nested_manager)

    def load_template_from_path(self, path):
        data = self.template_service.load_template(
            path,
            self.nested_manager.parse_indented_text
        )

        self.nested_manager.deserialize_tree(data)

    # ---------------------------------------------------------
    # State persistence
    # ---------------------------------------------------------

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value
        self.state_manager.save_state(self.state)

    # ---------------------------------------------------------
    # Theme handling
    # ---------------------------------------------------------

    def theme_count(self):
        return self.theme_controller.theme_count()

    def apply_theme(self, index):
        return self.theme_controller.apply_theme(index)