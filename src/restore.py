import os
import zipfile
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
from utils import get_file_size, format_size

class RestoreThread(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    restore_completed = pyqtSignal()
    restore_failed = pyqtSignal(str)

    def __init__(self, backup_file, restore_dir):
        super().__init__()
        self.backup_file = backup_file
        self.restore_dir = restore_dir

    def run(self):
        try:
            if self.backup_file.lower().endswith('.zip'):
                self.restore_from_zip()
            else:
                self.restore_uncompressed()
            self.restore_completed.emit()
        except Exception as e:
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
            self.restore_failed.emit(f"Failed to restore from zip: {str(e)}")

    def restore_uncompressed(self):
        try:
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
            self.restore_failed.emit(f"Failed to restore uncompressed: {str(e)}")
