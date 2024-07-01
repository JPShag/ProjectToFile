from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QProgressBar, 
                             QFileDialog, QMessageBox, QCheckBox, QTabWidget,
                             QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from backup import BackupThread
from restore import RestoreThread
import os

class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Backup and Restore Application")
        self.setGeometry(100, 100, 800, 600)
        self.files = []
        self.setup_ui()
        self.setup_dark_mode()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Create tabs
        self.tabs = QTabWidget()
        self.backup_tab = QWidget()
        self.restore_tab = QWidget()
        self.tabs.addTab(self.backup_tab, "Backup")
        self.tabs.addTab(self.restore_tab, "Restore")
        layout.addWidget(self.tabs)

        # Backup tab
        backup_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)
        top_widget = QWidget()
        top_layout = QVBoxLayout()

        self.file_list = QListWidget()
        top_layout.addWidget(QLabel("Files to backup:"))
        top_layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Files")
        self.add_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn = QPushButton("Clear Files")
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.clear_btn)
        top_layout.addLayout(btn_layout)

        self.compress_cb = QCheckBox("Compress backup")
        self.compress_cb.setChecked(True)
        top_layout.addWidget(self.compress_cb)

        self.subdirs_cb = QCheckBox("Include subdirectories")
        self.subdirs_cb.setChecked(True)
        top_layout.addWidget(self.subdirs_cb)

        self.backup_btn = QPushButton("Start Backup")
        self.backup_btn.clicked.connect(self.start_backup)
        top_layout.addWidget(self.backup_btn)

        self.backup_progress = QProgressBar()
        self.backup_progress.setFixedHeight(20)  # Fix progress bar size
        top_layout.addWidget(self.backup_progress)

        top_widget.setLayout(top_layout)
        splitter.addWidget(top_widget)

        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        splitter.addWidget(self.backup_log)

        backup_layout.addWidget(splitter)
        self.backup_tab.setLayout(backup_layout)

        # Restore tab
        restore_layout = QVBoxLayout()
        self.restore_btn = QPushButton("Select Backup File and Restore")
        self.restore_btn.clicked.connect(self.start_restore)
        restore_layout.addWidget(self.restore_btn)

        self.restore_progress = QProgressBar()
        self.restore_progress.setFixedHeight(20)  # Fix progress bar size
        restore_layout.addWidget(self.restore_progress)

        self.restore_log = QTextEdit()
        self.restore_log.setReadOnly(True)
        restore_layout.addWidget(self.restore_log)

        self.restore_tab.setLayout(restore_layout)

        central_widget.setLayout(layout)

        # Add dark mode toggle
        self.dark_mode_cb = QCheckBox("Dark Mode")
        self.dark_mode_cb.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_cb)

    def setup_dark_mode(self):
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.BrightText, Qt.red)
        self.dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        self.light_palette = self.style().standardPalette()

    def toggle_dark_mode(self, state):
        if state == Qt.Checked:
            self.setPalette(self.dark_palette)
        else:
            self.setPalette(self.light_palette)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to backup")
        self.files.extend(files)
        self.file_list.addItems(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to backup")
        if folder:
            self.files.append(folder)
            self.file_list.addItem(folder)

    def clear_files(self):
        self.files.clear()
        self.file_list.clear()

    def start_backup(self):
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please add files or folders to backup.")
            return

        file_filter = "ZIP files (*.zip)" if self.compress_cb.isChecked() else "Text files (*.txt)"
        backup_path, _ = QFileDialog.getSaveFileName(self, "Save Backup", "", file_filter)
        if not backup_path:
            return

        self.backup_thread = BackupThread(self.files, backup_path, 
                                          self.compress_cb.isChecked(),
                                          self.subdirs_cb.isChecked())
        self.backup_thread.progress_updated.connect(self.update_backup_progress)
        self.backup_thread.file_processed.connect(self.log_backup_progress)
        self.backup_thread.backup_completed.connect(self.backup_completed)
        self.backup_thread.backup_failed.connect(self.backup_failed)
        self.backup_thread.start()

        self.backup_btn.setEnabled(False)
        self.backup_log.clear()

    def update_backup_progress(self, value):
        self.backup_progress.setValue(value)

    def log_backup_progress(self, file_path):
        self.backup_log.append(f"Backed up: {file_path}")

    def backup_completed(self, backup_path):
        self.backup_progress.setValue(100)
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

        self.restore_thread = RestoreThread(backup_file, restore_dir)
        self.restore_thread.progress_updated.connect(self.update_restore_progress)
        self.restore_thread.file_processed.connect(self.log_restore_progress)
        self.restore_thread.restore_completed.connect(self.restore_completed)
        self.restore_thread.restore_failed.connect(self.restore_failed)
        self.restore_thread.start()

        self.restore_btn.setEnabled(False)
        self.restore_log.clear()

    def update_restore_progress(self, value):
        self.restore_progress.setValue(value)

    def log_restore_progress(self, file_path):
        self.restore_log.append(f"Restored: {file_path}")

    def restore_completed(self):
        self.restore_progress.setValue(100)
        self.restore_btn.setEnabled(True)
        self.restore_log.append("\nRestore completed successfully!")
        QMessageBox.information(self, "Restore Complete", "Files have been restored successfully.")

    def restore_failed(self, error_message):
        self.restore_btn.setEnabled(True)
        self.restore_log.append(f"\nRestore failed: {error_message}")
        QMessageBox.critical(self, "Restore Failed", f"Error: {error_message}")
