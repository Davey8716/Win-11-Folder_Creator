import json
from typing import Any
from PySide6.QtWidgets import QFileDialog

class TemplateService:
    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save_json(self, file_path: str, data: Any) -> tuple[str, str]:
        """
        Returns (status, message)
        """

        if not file_path:
            return "cancelled", ""

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return "success", "Template saved successfully"

        except Exception:
            return "error", "Error saving template"
        
    def load_template(self, file_path: str, text_parser):
        """
        Loads either JSON template or indented text template.
        Returns deserialized tree data.
        """

        if file_path.lower().endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        elif file_path.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return text_parser(text)

        else:
            raise ValueError("Unsupported file type")

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    def load_into_tree(self, parent, tree_manager):
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Load Template",
            "",
            "Templates (*.json *.txt);;JSON Files (*.json);;Text Outline (*.txt)"
        )

        if not file_path:
            return "cancelled", ""

        try:
            data = self.load_template(
                file_path,
                tree_manager.parse_indented_text
            )

            tree_manager.deserialize_tree(data)
            return "success", "Template loaded"

        except Exception:
            return "error", "Error loading template"

    def save_from_tree(self, parent, tree_manager):
        if tree_manager.tree.topLevelItemCount() == 0:
            return "empty", "Tree is empty."

        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save Template",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return "cancelled", ""

        data = tree_manager.serialize_tree()
        return self.save_json(file_path, data)