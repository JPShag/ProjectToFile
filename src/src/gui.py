from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QFileDialog,
                             QMessageBox, QCheckBox, QTabWidget, QTextEdit,
                             QTreeWidget, QTreeWidgetItem, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt
import os
import json
from backup_restore import BackupRestoreHandler
from utils import generate_file_tree

SETTINGS_FILE = 'settings.json'

class FileListWidget(QListWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.exists(file_path):
                    self.addItem(file_path)
                    self.main_window.files.append(file_path)

class BackupRestoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Backup and Restore Application")
        self.setGeometry(100, 100, 800, 600)
        self.files = []
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QListWidget, QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: -1px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #cccccc;
                padding: 10px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.backup_tab = QWidget()
        self.restore_tab = QWidget()
        self.file_tree_tab = QWidget()
        self.tabs.addTab(self.backup_tab, "Backup")
        self.tabs.addTab(self.restore_tab, "Restore")
        self.tabs.addTab(self.file_tree_tab, "File Tree")
        layout.addWidget(self.tabs)

        self.setup_backup_tab()
        self.setup_restore_tab()
        self.setup_file_tree_tab()

    def setup_backup_tab(self):
        backup_layout = QVBoxLayout(self.backup_tab)

        file_selection_group = QGroupBox("File Selection")
        file_selection_layout = QVBoxLayout(file_selection_group)
        self.file_list = FileListWidget(self, main_window=self)
        file_selection_layout.addWidget(QLabel("Files and folders to backup:"))
        file_selection_layout.addWidget(self.file_list)

        file_btn_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("Add Files")
        self.add_file_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.clear_files)
        self.restore_backup_settings_btn = QPushButton("Restore Last Backup Settings")
        self.restore_backup_settings_btn.clicked.connect(self.load_backup_settings)
        file_btn_layout.addWidget(self.add_file_btn)
        file_btn_layout.addWidget(self.add_folder_btn)
        file_btn_layout.addWidget(self.clear_btn)
        file_btn_layout.addWidget(self.restore_backup_settings_btn)
        file_selection_layout.addLayout(file_btn_layout)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        self.compress_cb = QCheckBox("Compress backup")
        self.subdirs_cb = QCheckBox("Include subdirectories")
        self.encryption_key_input = QLineEdit()
        self.encryption_key_input.setPlaceholderText("Enter encryption key (optional)")
        options_layout.addWidget(self.compress_cb)
        options_layout.addWidget(self.subdirs_cb)
        options_layout.addWidget(QLabel("Encryption Key:"))
        options_layout.addWidget(self.encryption_key_input)

        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout(control_group)
        self.backup_btn = QPushButton("Start Backup")
        self.backup_btn.clicked.connect(self.start_backup)
        control_layout.addWidget(self.backup_btn)

        log_group = QGroupBox("Backup Log")
        backup_log_layout = QVBoxLayout(log_group)
        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        backup_log_layout.addWidget(self.backup_log)

        backup_layout.addWidget(file_selection_group)
        backup_layout.addWidget(options_group)
        backup_layout.addWidget(control_group)
        backup_layout.addWidget(log_group)

    def setup_restore_tab(self):
        restore_layout = QVBoxLayout(self.restore_tab)

        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout(control_group)
        self.restore_btn = QPushButton("Select Backup File and Restore")
        self.restore_btn.clicked.connect(self.start_restore)
        self.restore_last_btn = QPushButton("Restore Last Settings")
        self.restore_last_btn.clicked.connect(self.load_restore_settings)
        control_layout.addWidget(self.restore_btn)
        control_layout.addWidget(self.restore_last_btn)

        log_group = QGroupBox("Restore Log")
        restore_log_layout = QVBoxLayout(log_group)
        self.restore_log = QTextEdit()
        self.restore_log.setReadOnly(True)
        restore_log_layout.addWidget(self.restore_log)

        restore_layout.addWidget(control_group)
        restore_layout.addWidget(log_group)

    def setup_file_tree_tab(self):
        file_tree_layout = QVBoxLayout(self.file_tree_tab)

        control_group = QGroupBox("Control")
        control_layout = QHBoxLayout(control_group)
        self.file_tree_btn = QPushButton("Select Folder")
        self.file_tree_btn.clicked.connect(self.show_file_tree)
        self.export_tree_btn = QPushButton("Export Tree")
        self.export_tree_btn.clicked.connect(self.export_file_tree)
        self.restore_file_tree_btn = QPushButton("Restore Last File Tree Settings")
        self.restore_file_tree_btn.clicked.connect(self.load_file_tree_settings)
        control_layout.addWidget(self.file_tree_btn)
        control_layout.addWidget(self.export_tree_btn)
        control_layout.addWidget(self.restore_file_tree_btn)

        tree_group = QGroupBox("File Tree")
        tree_layout = QVBoxLayout(tree_group)
        self.file_tree_widget = QTreeWidget()
        self.file_tree_widget.setHeaderLabels(["Name"])
        tree_layout.addWidget(self.file_tree_widget)

        file_tree_layout.addWidget(control_group)
        file_tree_layout.addWidget(tree_group)

    def show_file_tree(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to view tree")
        if not folder:
            return
        
        self.tree = generate_file_tree(folder)
        self.file_tree_widget.clear()
        self.populate_tree_widget(self.file_tree_widget.invisibleRootItem(), self.tree)
        self.save_file_tree_settings(folder)

    def populate_tree_widget(self, parent, tree):
        for key, value in tree.items():
            item = QTreeWidgetItem(parent, [key])
            if isinstance(value, dict):
                self.populate_tree_widget(item, value)

    def export_file_tree(self):
        if not hasattr(self, 'tree'):
            QMessageBox.warning(self, "No Tree", "Please generate the file tree first.")
            return

        export_path, _ = QFileDialog.getSaveFileName(self, "Export File Tree", "", "Text files (*.txt)")
        if not export_path:
            return

        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                self.write_tree_to_file(f, self.tree)
            QMessageBox.information(self, "Export Complete", f"File tree exported to: {export_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export file tree: {str(e)}")

    def write_tree_to_file(self, f, tree, indent=0):
        for key, value in tree.items():
            f.write('  ' * indent + key + '\n')
            if isinstance(value, dict):
                self.write_tree_to_file(f, value, indent + 1)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to backup")
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_list.addItem(file)
        self.save_backup_settings()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to backup")
        if folder and folder not in self.files:
            self.files.append(folder)
            self.file_list.addItem(folder)
        self.save_backup_settings()

    def clear_files(self):
        self.files.clear()
        self.file_list.clear()
        self.save_backup_settings()

    def start_backup(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please add files or folders to backup.")
            return

        file_filter = "ZIP files (*.zip)" if self.compress_cb.isChecked() else "Text files (*.txt)"
        backup_path, _ = QFileDialog.getSaveFileName(self, "Save Backup", "", file_filter)
        if not backup_path:
            return

        encryption_key = self.encryption_key_input.text().encode('utf-8') if self.encryption_key_input.text() else None

        self.backup_thread = BackupRestoreHandler(action='backup', files=self.files, backup_path=backup_path,
                                                  compress=self.compress_cb.isChecked(), include_subdirs=self.subdirs_cb.isChecked(),
                                                  encryption_key=encryption_key)
        self.backup_thread.file_processed.connect(self.log_backup_progress)
        self.backup_thread.backup_completed.connect(self.backup_completed)
        self.backup_thread.backup_failed.connect(self.backup_failed)
        self.backup_thread.start()

        self.backup_btn.setEnabled(False)
        self.backup_log.clear()

    def log_backup_progress(self, file_path):
        self.backup_log.append(f"Backed up: {file_path}")

    def backup_completed(self, backup_path):
        self.backup_btn.setEnabled(True)
        self.backup_log.append(f"\nBackup completed successfully!\nSaved to: {backup_path}")
        QMessageBox.information(self, "Backup Complete", f"Backup saved to: {backup_path}")

    def backup_failed(self, error_message):
        self.backup_btn.setEnabled(True)
        self.backup_log.append(f"\nBackup failed: {error_message}")
        QMessageBox.critical(self, "Backup Failed", f"Error: {error_message}")

    def start_restore(self):
        backup_file, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "Backup files (*.txt *.zip)")
        if not backup_file:
            return

        restore_dir = QFileDialog.getExistingDirectory(self, "Select Restore Directory")
        if not restore_dir:
            return

        encryption_key = self.encryption_key_input.text().encode('utf-8') if self.encryption_key_input.text() else None

        self.restore_thread = BackupRestoreHandler(action='restore', backup_file=backup_file, restore_dir=restore_dir, encryption_key=encryption_key)
        self.restore_thread.file_processed.connect(self.log_restore_progress)
        self.restore_thread.restore_completed.connect(self.restore_completed)
        self.restore_thread.restore_failed.connect(self.restore_failed)
        self.restore_thread.start()

        self.restore_btn.setEnabled(False)
        self.restore_log.clear()

    def log_restore_progress(self, file_path):
        self.restore_log.append(f"Restored: {file_path}")

    def restore_completed(self):
        self.restore_btn.setEnabled(True)
        self.restore_log.append("\nRestore completed successfully!")
        QMessageBox.information(self, "Restore Complete", "Files have been restored successfully.")

    def restore_failed(self, error_message):
        self.restore_btn.setEnabled(True)
        self.restore_log.append(f"\nRestore failed: {error_message}")
        QMessageBox.critical(self, "Restore Failed", f"Error: {error_message}")

    def save_settings(self, settings):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
        else:
            existing_settings = {}

        existing_settings.update(settings)

        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.files = settings.get('files', [])
                self.file_list.addItems(self.files)
                self.compress_cb.setChecked(settings.get('compress', False))
                self.subdirs_cb.setChecked(settings.get('subdirs', False))

    def save_backup_settings(self):
        settings = {
            'files': self.files,
            'compress': self.compress_cb.isChecked(),
            'subdirs': self.subdirs_cb.isChecked()
        }
        self.save_settings(settings)

    def load_backup_settings(self):
        self.load_settings()

    def load_restore_settings(self):
        self.load_settings()

    def save_file_tree_settings(self, folder):
        settings = {'last_tree_folder': folder}
        self.save_settings(settings)

    def load_file_tree_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8'):
                settings = json.load(f)
                last_folder = settings.get('last_tree_folder')
                if last_folder and os.path.exists(last_folder):
                    self.tree = generate_file_tree(last_folder)
                    self.file_tree_widget.clear()
                    self.populate_tree_widget(self.file_tree_widget.invisibleRootItem(), self.tree)
