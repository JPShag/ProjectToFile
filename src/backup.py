import os
import logging
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class BackupHandler(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    backup_completed = pyqtSignal(str)
    backup_failed = pyqtSignal(str)

    def __init__(self, files, backup_path, compress=False, include_subdirs=False):
        super().__init__()
        self.files = files
        self.backup_path = backup_path
        self.compress = compress
        self.include_subdirs = include_subdirs
        logging.basicConfig(level=logging.INFO, filename='backup.log',
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self):
        try:
            self._backup()
            logging.info(f"Backup completed successfully at {self.backup_path}")
            self.backup_completed.emit(self.backup_path)
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            self.backup_failed.emit(str(e))

    def _backup(self):
        with open(self.backup_path, 'w', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"Backup created on {timestamp}\n\n")
            total_size = self.get_total_size()
            processed_size = 0

            for item in self.files:
                if os.path.isdir(item):
                    for root, _, files in os.walk(item):
                        if not self.include_subdirs and root != item:
                            continue
                        for file in files:
                            file_path = os.path.join(root, file)
                            self._write_file(f, file_path)
                            file_size = os.path.getsize(file_path)
                            processed_size += file_size
                            self.progress_updated.emit(int(processed_size / total_size * 100))
                            self.file_processed.emit(f"{file_path} ({self._format_size(file_size)})")
                elif os.path.isfile(item):
                    self._write_file(f, item)
                    file_size = os.path.getsize(item)
                    processed_size += file_size
                    self.progress_updated.emit(int(processed_size / total_size * 100))
                    self.file_processed.emit(f"{item} ({self._format_size(file_size)})")

    def _write_file(self, f, file_path):
        f.write(f"--- {file_path} ---\n")
        with open(file_path, 'r', encoding='utf-8') as file:
            f.write(file.read())
        f.write("\n\n")

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

    def _format_size(self, size_in_bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} PB"
