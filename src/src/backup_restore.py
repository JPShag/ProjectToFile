import os
import logging
import zipfile
from datetime import datetime
from cryptography.fernet import Fernet
from PyQt5.QtCore import QThread, pyqtSignal
from utils import format_size

class BackupRestoreHandler(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    backup_completed = pyqtSignal(str)
    backup_failed = pyqtSignal(str)
    restore_completed = pyqtSignal()
    restore_failed = pyqtSignal(str)

    def __init__(self, action, files=None, backup_path=None, restore_dir=None, compress=False, include_subdirs=False, backup_file=None, encryption_key=None):
        super().__init__()
        self.action = action
        self.files = files
        self.backup_path = backup_path
        self.restore_dir = restore_dir
        self.compress = compress
        self.include_subdirs = include_subdirs
        self.backup_file = backup_file
        self.encryption_key = encryption_key
        logging.basicConfig(level=logging.INFO, filename='backup_restore.log', format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self):
        if self.action == 'backup':
            self._backup()
        elif self.action == 'restore':
            self._restore()

    def _backup(self):
        try:
            if self.encryption_key:
                with open(self.backup_path, 'wb') as f:
                    self._write_backup(f, encrypted=True)
            else:
                with open(self.backup_path, 'w', encoding='utf-8') as f:
                    self._write_backup(f, encrypted=False)
            logging.info(f"Backup completed successfully at {self.backup_path}")
            self.backup_completed.emit(self.backup_path)
        except Exception as e:
            logging.error(f"Backup failed: {e}", exc_info=True)
            self.backup_failed.emit(str(e))

    def _write_backup(self, f, encrypted):
        timestamp = datetime.now().isoformat()
        total_size = self.get_total_size()
        processed_size = 0

        try:
            if encrypted:
                fernet = Fernet(self.encryption_key)
                f.write(fernet.encrypt(f"Backup created on {timestamp}\n\n".encode('utf-8')))
            else:
                f.write(f"Backup created on {timestamp}\n\n")

            for item in self.files:
                if os.path.isdir(item):
                    for root, _, files in os.walk(item):
                        if not self.include_subdirs and root != item:
                            continue
                        for file in files:
                            file_path = os.path.join(root, file)
                            self._write_file(f, file_path, encrypted)
                            file_size = os.path.getsize(file_path)
                            processed_size += file_size
                            self.progress_updated.emit(int(processed_size / total_size * 100))
                            self.file_processed.emit(f"{file_path} ({format_size(file_size)})")
                elif os.path.isfile(item):
                    self._write_file(f, item, encrypted)
                    file_size = os.path.getsize(item)
                    processed_size += file_size
                    self.progress_updated.emit(int(processed_size / total_size * 100))
                    self.file_processed.emit(f"{item} ({format_size(file_size)})")
        except Exception as e:
            logging.error(f"Error during backup: {e}", exc_info=True)

    def _write_file(self, f, file_path, encrypted):
        header = f"--- {file_path} ---\n".encode('utf-8')
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                if encrypted:
                    fernet = Fernet(self.encryption_key)
                    f.write(fernet.encrypt(header))
                    f.write(fernet.encrypt(content))
                else:
                    f.write(header.decode('utf-8'))
                    f.write(content.decode('utf-8', errors='ignore'))
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}\n".encode('utf-8')
            logging.error(f"Error reading file {file_path}: {e}", exc_info=True)
            if encrypted:
                fernet = Fernet(self.encryption_key)
                f.write(fernet.encrypt(error_msg))
            else:
                f.write(error_msg.decode('utf-8'))

    def get_total_size(self):
        total_size = 0
        for item in self.files:
            if os.path.isdir(item):
                for root, _, files in os.walk(item):
                    if not self.include_subdirs and root != item:
                        continue
                    total_size += sum(os.path.getsize(os.path.join(root, file)) for file in files)
            elif os.path.isfile(item):
                total_size += os.path.getsize(item)
        return total_size

    def _restore(self):
        try:
            if self.backup_file.lower().endswith('.zip'):
                self.restore_from_zip()
            else:
                self.restore_uncompressed()
            self.restore_completed.emit()
        except Exception as e:
            logging.error(f"Restore failed: {e}", exc_info=True)
            self.restore_failed.emit(str(e))

    def restore_from_zip(self):
        try:
            with zipfile.ZipFile(self.backup_file, 'r') as zf:
                total_size = sum(info.file_size for info in zf.infolist())
                processed_size = 0
                for info in zf.infolist():
                    zf.extract(info, self.restore_dir)
                    processed_size += info.file_size
                    self.progress_updated.emit(int(processed_size / total_size * 100))
                    self.file_processed.emit(f"{os.path.join(self.restore_dir, info.filename)} ({format_size(info.file_size)})")
        except Exception as e:
            logging.error(f"Failed to restore from zip: {e}", exc_info=True)
            self.restore_failed.emit(f"Failed to restore from zip: {str(e)}")

    def restore_uncompressed(self):
        try:
            if self.encryption_key:
                with open(self.backup_file, 'rb') as f:
                    content = f.read()
                fernet = Fernet(self.encryption_key)
                content = fernet.decrypt(content).decode('utf-8')
            else:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            files = content.split('\n\n')
            total_size = sum(len(file) for file in files)
            processed_size = 0

            for file in files:
                if file.strip():
                    header, data = file.split('\n', 1)
                    file_path = header.strip("--- ").strip()
                    restore_path = os.path.join(self.restore_dir, os.path.relpath(file_path))
                    os.makedirs(os.path.dirname(restore_path), exist_ok=True)
                    with open(restore_path, 'w', encoding='utf-8') as out_file:
                        out_file.write(data)
                    file_size = len(data)
                    processed_size += file_size
                    self.progress_updated.emit(int(processed_size / total_size * 100))
                    self.file_processed.emit(f"{restore_path} ({format_size(file_size)})")
        except Exception as e:
            logging.error(f"Failed to restore uncompressed: {e}", exc_info=True)
            self.restore_failed.emit(f"Failed to restore uncompressed: {str(e)}")
