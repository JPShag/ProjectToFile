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
        with zipfile.ZipFile(self.backup_file, 'r') as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            processed_size = 0
            for info in zf.infolist():
                zf.extract(info, self.restore_dir)
                processed_size += info.file_size
                self.progress_updated.emit(int(processed_size / total_size * 100))
                self.file_processed.emit(f"{os.path.join(self.restore_dir, info.filename)} ({format_size(info.file_size)})")

    def restore_uncompressed(self):
        total_size = sum(get_file_size(os.path.join(root, file))
                         for root, _, files in os.walk(self.backup_file)
                         for file in files)
        processed_size = 0
        for root, dirs, files in os.walk(self.backup_file):
            for file in files:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(self.restore_dir, os.path.relpath(src_path, self.backup_file))
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                file_size = get_file_size(src_path)
                processed_size += file_size
                self.progress_updated.emit(int(processed_size / total_size * 100))
                self.file_processed.emit(f"{dst_path} ({format_size(file_size)})")