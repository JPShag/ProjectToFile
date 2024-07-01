from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QProgressBar,
                             QFileDialog, QMessageBox, QCheckBox, QTabWidget,
                             QTextEdit, QSplitter, QFrame)
from PyQt5.QtCore import Qt
from backup import BackupHandler
from restore import RestoreThread

class BackupRestoreApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Backup and Restore Application")
        self.setGeometry(100, 100, 800, 600)
        self.files = []
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tabs
        self.tabs = QTabWidget()
        self.backup_tab = QWidget()
        self.restore_tab = QWidget()
        self.tabs.addTab(self.backup_tab, "Backup")
        self.tabs.addTab(self.restore_tab, "Restore")
        layout.addWidget(self.tabs)

        # Setup Backup Tab
        self.setup_backup_tab()

        # Setup Restore Tab
        self.setup_restore_tab()

    def setup_backup_tab(self):
        backup_layout = QVBoxLayout(self.backup_tab)

        # File selection area
        file_selection_layout = QVBoxLayout()
        self.file_list = QListWidget()
        file_selection_layout.addWidget(QLabel("Files and folders to backup:"))
        file_selection_layout.addWidget(self.file_list)

        file_btn_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("Add Files")
        self.add_file_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.clear_files)
        file_btn_layout.addWidget(self.add_file_btn)
        file_btn_layout.addWidget(self.add_folder_btn)
        file_btn_layout.addWidget(self.clear_btn)
        file_selection_layout.addLayout(file_btn_layout)

        # Backup options
        self.compress_cb = QCheckBox("Compress backup")
        self.subdirs_cb = QCheckBox("Include subdirectories")
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.compress_cb)
        options_layout.addWidget(self.subdirs_cb)
        
        # Backup control buttons
        control_layout = QVBoxLayout()
        self.backup_btn = QPushButton("Start Backup")
        self.backup_btn.clicked.connect(self.start_backup)
        self.backup_progress = QProgressBar()
        self.backup_progress.setFixedHeight(20)
        control_layout.addWidget(self.backup_btn)
        control_layout.addWidget(self.backup_progress)

        # Backup log
        self.backup_log = QTextEdit()
        self.backup_log.setReadOnly(True)
        backup_log_layout = QVBoxLayout()
        backup_log_layout.addWidget(QLabel("Backup Log:"))
        backup_log_layout.addWidget(self.backup_log)

        # Arrange all layouts
        backup_layout.addLayout(file_selection_layout)
        backup_layout.addLayout(options_layout)
        backup_layout.addLayout(control_layout)
        backup_layout.addLayout(backup_log_layout)

    def setup_restore_tab(self):
        restore_layout = QVBoxLayout(self.restore_tab)

        # Restore control buttons
        control_layout = QVBoxLayout()
        self.restore_btn = QPushButton("Select Backup File and Restore")
        self.restore_btn.clicked.connect(self.start_restore)
        self.restore_progress = QProgressBar()
        self.restore_progress.setFixedHeight(20)
        control_layout.addWidget(self.restore_btn)
        control_layout.addWidget(self.restore_progress)

        # Restore log
        self.restore_log = QTextEdit()
        self.restore_log.setReadOnly(True)
        restore_log_layout = QVBoxLayout()
        restore_log_layout.addWidget(QLabel("Restore Log:"))
        restore_log_layout.addWidget(self.restore_log)

        # Arrange all layouts
        restore_layout.addLayout(control_layout)
        restore_layout.addLayout(restore_log_layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to backup")
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_list.addItem(file)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to backup")
        if folder and folder not in self.files:
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

        self.backup_thread = BackupHandler(self.files, backup_path, 
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
