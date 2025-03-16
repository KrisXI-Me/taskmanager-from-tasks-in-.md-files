/*************  ✨ Codeium Command 🌟  *************/
import os
import sys

# Check if PySide6 is installed
if not hasattr(sys, 'pyside_version'):
    print("PySide6 is not installed. Install it with `pip install pyside6`.")
    sys.exit()
/******  3c324834-fd32-4585-a90a-ea5b37b82a3e  *******/
import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QMessageBox, QComboBox, QInputDialog, QMenu
)
from PySide6.QtCore import Qt, QSettings
from utils.file_utils import find_markdown_files
from utils.task_utils import parse_tasks
from utils.config_utils import save_column_config, load_column_config
from widgets.custom_table import CustomTableWidget
from models.column_types import TextColumn, DropdownColumn, CheckboxColumn

class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Task Manager")
        self.setGeometry(100, 100, 1000, 800)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Directory selection
        self.dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Workspace Directory:")
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select a directory...")
        self.dir_button = QPushButton("Browse")
        self.dir_button.clicked.connect(self.select_directory)
        self.dir_layout.addWidget(self.dir_label)
        self.dir_layout.addWidget(self.dir_input)
        self.dir_layout.addWidget(self.dir_button)
        self.layout.addLayout(self.dir_layout)

        # Filter options
        self.filter_layout = QHBoxLayout()
        self.filter_label = QLabel("Filter by Tag:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("e.g., @work")
        self.filter_button = QPushButton("Apply Filter")
        self.filter_button.clicked.connect(self.load_tasks)
        self.filter_layout.addWidget(self.filter_label)
        self.filter_layout.addWidget(self.filter_input)
        self.filter_layout.addWidget(self.filter_button)
        self.layout.addLayout(self.filter_layout)

        # Task tree
        self.task_tree = CustomTableWidget()
        self.task_tree.setHeaderLabels(["Status", "Description", "Tag", "File"])
        self.task_tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.task_tree.itemDoubleClicked.connect(self.edit_task_inline)
        self.task_tree.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_tree.header().customContextMenuRequested.connect(self.show_header_context_menu)
        self.task_tree.itemChanged.connect(self.save_changes)
        self.layout.addWidget(self.task_tree)

        # Set column types
        self.task_tree.set_column_type(0, DropdownColumn(["Pending", "Completed"]))  # Status column
        self.task_tree.set_column_type(1, TextColumn())  # Description column
        self.task_tree.set_column_type(2, TextColumn())  # Tag column
        self.task_tree.set_column_type(3, TextColumn())  # File column

        # Load tasks button
        self.load_button = QPushButton("Load Tasks")
        self.load_button.clicked.connect(self.load_tasks)
        self.layout.addWidget(self.load_button)

        # Save changes button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_all_changes)
        self.layout.addWidget(self.save_button)

        # Store the original task data
        self.original_tasks = []

        # Store dropdown columns and their options
        self.dropdown_columns = {
            "Status": ["Pending", "Completed"]
        }

        # Load column configuration
        self.settings = QSettings("MyCompany", "TaskManager")
        load_column_config(self.task_tree, self.settings)

    def select_directory(self):
        """Open a dialog to select the workspace directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Workspace Directory")
        if directory:
            self.dir_input.setText(directory)

    def load_tasks(self):
        """Load and display tasks and subtasks in a tree structure."""
        directory = self.dir_input.text()
        if not directory:
            QMessageBox.warning(self, "Error", "Please select a workspace directory.")
            return

        # Clear the tree
        self.task_tree.clear()

        # Find and parse tasks
        markdown_files = find_markdown_files(directory)
        if not markdown_files:
            QMessageBox.information(self, "Info", "No Markdown files found.")
            return

        self.original_tasks = []
        all_tasks = []
        for file in markdown_files:
            tasks = parse_tasks(file)
            all_tasks.extend(tasks)
            self.original_tasks.extend(tasks)

        # Apply tag filter
        filter_tag = self.filter_input.text().strip()
        if filter_tag:
            all_tasks = [task for task in all_tasks if filter_tag.lower() in task[3].lower()]

        # Build the task tree
        task_tree = {}
        for task in all_tasks:
            indent, status, description, tag, file_path, _ = task
            item = QTreeWidgetItem([status, description, tag, file_path])
            item.setFlags(item.flags() | Qt.ItemIsEditable)  # Make cells editable
            if indent == 0:
                # Top-level task
                self.task_tree.addTopLevelItem(item)
                task_tree[item] = indent
            else:
                # Find the parent task based on indentation
                for parent_item, parent_indent in reversed(list(task_tree.items())):
                    if parent_indent < indent:
                        parent_item.addChild(item)
                        task_tree[item] = indent
                        break

            # Add dropdown for Status column
            if self.task_tree.headerItem().text(0) == "Status":
                combo = QComboBox()
                combo.addItems(self.dropdown_columns["Status"])
                combo.setCurrentText(status)
                combo.currentTextChanged.connect(lambda text, item=item: self.update_status(item, text))
                self.task_tree.setItemWidget(item, 0, combo)

        # Disable the itemChanged signal temporarily to avoid premature triggering
        self.task_tree.itemChanged.disconnect(self.save_changes)
        self.task_tree.itemChanged.connect(self.save_changes)

    def update_status(self, item, status):
        """Update the status of a task."""
        item.setText(0, status)

    def save_changes(self, item, column):
        """Save changes made to a task."""
        status = item.text(0)
        description = item.text(1)
        tag = item.text(2)
        file_path = item.text(3)

        # Update the original task data
        row = self.task_tree.indexOfTopLevelItem(item)
        if row == -1:
            # Handle child items if needed
            pass
        else:
            self.original_tasks[row] = (status, description, tag, file_path, None)

    def save_all_changes(self):
        """Save all changes back to the Markdown files."""
        if not self.original_tasks:
            QMessageBox.warning(self, "Error", "No tasks loaded.")
            return

        # Group tasks by file
        file_tasks = {}
        for task in self.original_tasks:
            status, description, tag, file_path, _ = task
            if file_path not in file_tasks:
                file_tasks[file_path] = []
            file_tasks[file_path].append((status, description, tag))

        # Save changes to each file
        for file_path, tasks in file_tasks.items():
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            with open(file_path, 'w', encoding='utf-8') as file:
                for line in lines:
                    match = re.match(r'-\s*\[(.)\]\s*(.*)', line)
                    if match:
                        # Replace the line with the updated task
                        for status, description, tag in tasks:
                            if tag in line:
                                new_line = f"- [{'x' if status == 'Completed' else ' '}] {description}\n"
                                file.write(new_line)
                                break
                        else:
                            file.write(line)
                    else:
                        file.write(line)

        QMessageBox.information(self, "Success", "All changes saved.")

    def edit_task_inline(self, item, column):
        """Enable inline editing for the task."""
        self.task_tree.edit_item(item, column)

    def show_header_context_menu(self, position):
        """Show a context menu for managing columns when right-clicking on the header."""
        menu = QMenu(self)
        add_column_action = menu.addAction("Add Column")
        remove_column_action = menu.addAction("Remove Column")
        edit_column_action = menu.addAction("Edit Column")
        add_dropdown_action = menu.addAction("Add Dropdown to Column")
        action = menu.exec_(self.task_tree.header().mapToGlobal(position))

        if action == add_column_action:
            self.add_column()
        elif action == remove_column_action:
            self.remove_column()
        elif action == edit_column_action:
            self.edit_column()
        elif action == add_dropdown_action:
            self.add_dropdown_to_column()

    def add_column(self):
        """Add a new column to the table with a selected column type."""
        column_name, ok = QInputDialog.getText(self, "Add Column", "Enter column name:")
        if ok and column_name:
            # Ask the user to select a column type
            column_types = ["Text", "Dropdown", "Checkbox"]
            column_type, ok = QInputDialog.getItem(
                self, "Select Column Type", "Choose a column type:", column_types, 0, False
            )
            if ok:
                # Add the column
                self.task_tree.setColumnCount(self.task_tree.columnCount() + 1)
                self.task_tree.headerItem().setText(self.task_tree.columnCount() - 1, column_name)

                # Set the column type
                if column_type == "Text":
                    self.task_tree.set_column_type(self.task_tree.columnCount() - 1, TextColumn())
                elif column_type == "Dropdown":
                    options, ok = QInputDialog.getText(
                        self, "Dropdown Options", "Enter options (comma-separated):"
                    )
                    if ok and options:
                        options = [opt.strip() for opt in options.split(",")]
                        self.task_tree.set_column_type(
                            self.task_tree.columnCount() - 1, DropdownColumn(options)
                        )
                elif column_type == "Checkbox":
                    self.task_tree.set_column_type(self.task_tree.columnCount() - 1, CheckboxColumn())

                # Save the column configuration
                save_column_config(self.task_tree, self.settings)

    def remove_column(self):
        """Remove the selected column from the table."""
        column = self.task_tree.currentColumn()
        if column != -1:
            self.task_tree.setColumnCount(self.task_tree.columnCount() - 1)
            save_column_config(self.task_tree, self.settings)

    def edit_column(self):
        """Edit the name and type of the selected column."""
        column = self.task_tree.currentColumn()
        if column != -1:
            # Get the current column name
            current_name = self.task_tree.headerItem().text(column)

            # Ask the user for a new column name
            new_name, ok = QInputDialog.getText(
                self, "Edit Column", "Enter new column name:", text=current_name
            )
            if ok and new_name:
                # Update the column name
                self.task_tree.headerItem().setText(column, new_name)

                # Ask the user to select a new column type
                column_types = ["Text", "Dropdown", "Checkbox"]
                column_type, ok = QInputDialog.getItem(
                    self, "Select Column Type", "Choose a column type:", column_types, 0, False
                )
                if ok:
                    # Set the new column type
                    if column_type == "Text":
                        self.task_tree.set_column_type(column, TextColumn())
                    elif column_type == "Dropdown":
                        options, ok = QInputDialog.getText(
                            self, "Dropdown Options", "Enter options (comma-separated):"
                        )
                        if ok and options:
                            options = [opt.strip() for opt in options.split(",")]
                            self.task_tree.set_column_type(column, DropdownColumn(options))
                    elif column_type == "Checkbox":
                        self.task_tree.set_column_type(column, CheckboxColumn())

                # Save the column configuration
                save_column_config(self.task_tree, self.settings)

    def add_dropdown_to_column(self):
        """Add a dropdown to the selected column."""
        column = self.task_tree.currentColumn()
        if column != -1:
            column_name = self.task_tree.headerItem().text(column)
            options, ok = QInputDialog.getText(self, "Add Dropdown", f"Enter options for {column_name} (comma-separated):")
            if ok and options:
                options = [opt.strip() for opt in options.split(",")]
                self.dropdown_columns[column_name] = options
                self.load_tasks()  # Reload tasks to apply dropdowns