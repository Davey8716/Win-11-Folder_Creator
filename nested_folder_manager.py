
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTreeWidgetItemIterator
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

Node = Dict[str, Any]

class NestedFolderManager:
    def __init__(self, tree_widget):
        self.tree = tree_widget
        self.auto_number_enabled = False

    def serialize_tree(self):
        data = []
        for i in range(self.tree.topLevelItemCount()):
            data.append(self._serialize_item(self.tree.topLevelItem(i)))
        return data
    
    def deserialize_tree(self, data):
        self.tree.clear()
        if isinstance(data, dict):
            self._deserialize_item(data, None)
        else:
            for item in data:
                self._deserialize_item(item, None)
                
        # ---- Auto expand all nodes after loading ----
        self.expand_all_animated()

    def _serialize_item(self, item):
        return {
            "name": item.text(0),
            "children": [
                self._serialize_item(item.child(i))
                for i in range(item.childCount())
            ]
        }

    def _deserialize_item(self, data, parent):
        item = QTreeWidgetItem([data.get("name", "Unnamed")])
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        if parent:
            parent.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        for child in data.get("children", []):
            self._deserialize_item(child, item)

    def expand_all_animated(self, step_ms: int = 25, max_items: int = 2000):
        """
        Expands the tree progressively so Qt's animation is actually visible.
        step_ms: delay between expanding each item
        max_items: safety cap for huge trees
        """
        it = QTreeWidgetItemIterator(self.tree)
        items = []
        n = 0
        while it.value() and n < max_items:
            items.append(it.value())
            it += 1
            n += 1

        # Expand roots first for best visual effect
        items.sort(key=lambda i: 0 if i.parent() is None else 1)

        def tick():
            if not items:
                return

            item = items.pop(0)

            try:
                if item and item.treeWidget():
                    item.setExpanded(True)
            except RuntimeError:
                pass

            QTimer.singleShot(step_ms, tick)

        QTimer.singleShot(0, tick)

    def _count_leading_ws(self,line: str) -> Tuple[int, str]:
        """
        Returns (indent_count, stripped_line) where indent_count is the number of
        leading whitespace chars (tabs count as 1 here; we normalize later).
        """
        m = re.match(r"^([ \t]*)(.*)$", line)
        ws = m.group(1)
        text = m.group(2)
        return len(ws), text

    def parse_indented_text(self,text: str) -> List[Node]:
        """
        Parses an indented outline into a tree structure:
        - Each non-empty line is a folder name.
        - Indentation defines parent/child.
        - Supports tabs or spaces (or even mixed, but prefer consistent).
        Returns a list of root nodes (same format as your JSON templates).
        """
        # Preprocess lines: keep original indentation; drop empty/comment lines
        raw_lines = []
        for raw in text.splitlines():
            if not raw.strip():
                continue
            # optional: allow comments
            if raw.lstrip().startswith("#"):
                continue
            raw_lines.append(raw.rstrip("\n\r"))

        if not raw_lines:
            return []

        # Determine indentation unit (best-effort):
        # Find the smallest positive indent across lines (after normalization).
        # We'll treat a tab as 4 spaces for indent-unit detection only.
        indents = []
        for line in raw_lines:
            ws_len, stripped = self._count_leading_ws(line)
            if not stripped.strip():
                continue
            # normalize tabs for indent detection
            ws = line[:ws_len].replace("\t", " " * 4)
            n = len(ws)
            if n > 0:
                indents.append(n)

        indent_unit = min(indents) if indents else 4  # if everything is root-level

        roots: List[Node] = []
        stack: List[Tuple[int, Node]] = []  # (depth, node)

        for line in raw_lines:
            ws_len, name = self._count_leading_ws(line)
            name = name.strip()

            # normalize indent: tabs -> 4 spaces for depth computation
            ws_norm = line[:ws_len].replace("\t", " " * 4)
            indent_len = len(ws_norm)

            # Depth as "indent steps"
            depth = indent_len // indent_unit if indent_unit > 0 else 0

            node: Node = {"name": name, "children": []}

            if not stack:
                roots.append(node)
                stack.append((depth, node))
                continue

            # If depth is greater than last, it's a child of last
            last_depth, last_node = stack[-1]
            if depth > last_depth:
                last_node["children"].append(node)
                stack.append((depth, node))
                continue

            # Otherwise pop until we find parent depth < current depth
            while stack and stack[-1][0] >= depth:
                stack.pop()

            if not stack:
                roots.append(node)
                stack.append((depth, node))
            else:
                stack[-1][1]["children"].append(node)
                stack.append((depth, node))

        return roots
    
    def build_folders(self, base_path, timestamp_mode=None):
        base_dir = QDir(base_path)

        if self.tree.topLevelItemCount() == 0:
            return "empty", "Tree is empty."

        try:
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)

                name = item.text(0).strip()

                if timestamp_mode:
                    from desktop_folder_manager import DesktopFolderManager
                    stamp = DesktopFolderManager().build_timestamp(timestamp_mode)
                    name = f"{name}_{stamp}"

                full_path = base_dir.filePath(name)

                if QDir(full_path).exists():
                    return "exists", "Folder structure already exists."

                base_dir.mkpath(name)

                child_dir = QDir(full_path)

                for j in range(item.childCount()):
                    self._mk_dirs(child_dir, item.child(j))

            return "success", "Folder structure created successfully."

        except Exception:
            return "error", "Error creating folder structure."
                        
    def _mk_dirs(self, parent_dir, item):
        name = item.text(0).strip()
        if not name:
            return

        parent_dir.mkpath(name)
        child_dir = QDir(parent_dir.filePath(name))

        for i in range(item.childCount()):
            self._mk_dirs(child_dir, item.child(i))
            
    def add_root_folder(self):
        default_base = "New Folder"
        
        # ---- If auto numbering OFF → just create base name ----
        if not self.auto_number_enabled:
            item = QTreeWidgetItem([default_base])
            item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

            self.tree.addTopLevelItem(item)
            self.tree.setCurrentItem(item)   
            self.tree.editItem(item, 0)
            return

        count = self.tree.topLevelItemCount()

        if count == 0:
            base_name = default_base
        else:
            first_name = self.tree.topLevelItem(0).text(0).strip()
            base_name = first_name if first_name else default_base

        existing_names = [
            self.tree.topLevelItem(i).text(0)
            for i in range(count)
        ]

        n = 0
        name = base_name
        while name in existing_names:
            n += 1
            name = f"{base_name} {n}"

        item = QTreeWidgetItem([name])
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        self.tree.addTopLevelItem(item)
        self.tree.setCurrentItem(item)
        self.tree.editItem(item, 0)


    def add_subfolder(self):
        selected = self.tree.currentItem()
        if not selected:
            return

        default_base = "New Subfolder"
        
        # ---- If auto numbering OFF ----
        if not self.auto_number_enabled:
            child = QTreeWidgetItem([default_base])
            child.setFlags(child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

            selected.addChild(child)
            selected.setExpanded(True)
            self.tree.setCurrentItem(child) 
            self.tree.editItem(child, 0)
            return

        count = selected.childCount()

        if count == 0:
            base_name = default_base
        else:
            first_name = selected.child(0).text(0).strip()
            base_name = first_name if first_name else default_base

        existing_names = [
            selected.child(i).text(0)
            for i in range(count)
        ]

        n = 0
        name = base_name
        while name in existing_names:
            n += 1
            name = f"{base_name} {n}"

        child = QTreeWidgetItem([name])
        child.setFlags(child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        selected.addChild(child)
        selected.setExpanded(True)
        self.tree.editItem(child, 0)
        
    

    def remove_all_folders(self):
        self.tree.clear()

    def remove_selected_folders(self):
        selected = self.tree.currentItem()
        if not selected:
            return

        parent = selected.parent()
        if parent:
            parent.removeChild(selected)
        else:
            index = self.tree.indexOfTopLevelItem(selected)
            self.tree.takeTopLevelItem(index)
            

    # ---------------------------------------------------------
    # Import folder tree from filesystem
    # ---------------------------------------------------------
    def import_folder_tree(self, folder_path: str):
        """
        Reads a real folder structure from disk and recreates it in the tree.
        Files are ignored.
        """

        root = Path(folder_path)

        if not root.exists() or not root.is_dir():
            return

        def walk(path: Path):
            node = {
                "name": path.name,
                "children": []
            }

            for child in sorted(path.iterdir()):
                if child.is_dir():
                    node["children"].append(walk(child))

            return node

        data = walk(root)

        self.deserialize_tree([data])
        
    def sort_tree(self):
        """
        Alphabetically sorts the entire tree recursively.
        """

        def sort_item(parent):
            children = []
            for i in range(parent.childCount()):
                children.append(parent.takeChild(0))

            children.sort(key=lambda x: x.text(0).lower())

            for child in children:
                parent.addChild(child)
                sort_item(child)
                
        

        # ---- Sort top level items ----
        roots = []
        for i in range(self.tree.topLevelItemCount()):
            roots.append(self.tree.takeTopLevelItem(0))

        roots.sort(key=lambda x: x.text(0).lower())

        for root in roots:
            self.tree.addTopLevelItem(root)
            sort_item(root)
            
        self.expand_all_animated()
        
        # ensure something is selected
        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

        # refresh UI state
        window = self.tree.window()
        if hasattr(window, "update_build_button_state"):
            window.update_build_button_state()
        

        
        
