import os
import zipfile
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
from utils import get_file_size, format_size

class BackupThread(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    backup_completed = pyqtSignal(str)
    backup_failed = pyqtSignal(str)

    def __init__(self, files, backup_path, compress, include_subdirs):
        super().__init__()
        self.files = files
        self.backup_path = backup_path
        self.compress = compress
        self.include_subdirs = include_subdirs

    def run(self):
        try:
            if self.compress:
                self.backup_compressed()
            else:
                self.backup_uncompressed()
            self.backup_completed.emit(self.backup_path)
        except Exception as e:
            self.backup_failed.emit(str(e))

    def backup_compressed(self):
        try:
            with zipfile.ZipFile(self.backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                total_size = self.get_total_size()
                processed_size = 0
                for item in self.files:
                    if os.path.isdir(item):
                        for root, _, files in os.walk(item):
                            if not self.include_subdirs and root != item:
                                continue
                            for file in files:
                                file_path = os.path.join(root, file)
                                zf.write(file_path, os.path.relpath(file_path, os.path.dirname(item)))
                                file_size = get_file_size(file_path)
                                processed_size += file_size
                                self.progress_updated.emit(int(processed_size / total_size * 100))
                                self.file_processed.emit(f"{file_path} ({format_size(file_size)})")
                    elif os.path.isfile(item):
                        zf.write(item, os.path.basename(item))
                        file_size = get_file_size(item)
                        processed_size += file_size
                        self.progress_updated.emit(int(processed_size / total_size * 100))
                        self.file_processed.emit(f"{item} ({format_size(file_size)})")
        except Exception as e:
            self.backup_failed.emit(f"Failed to create compressed backup: {str(e)}")

    def backup_uncompressed(self):
        try:
            total_size = self.get_total_size()
            processed_size = 0
            for item in self.files:
                if os.path.isdir(item):
                    for root, _, files in os.walk(item):
                        if not self.include_subdirs and root != item:
                            continue
                        for file in files:
                            src_path = os.path.join(root, file)
                            dst_path = os.path.join(self.backup_path, os.path.relpath(src_path, os.path.dirname(item)))
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                            shutil.copy2(src_path, dst_path)
                            file_size = get_file_size(src_path)
                            processed_size += file_size
                            self.progress_updated.emit(int(processed_size / total_size * 100))
                            self.file_processed.emit(f"{src_path} ({format_size(file_size)})")
                elif os.path.isfile(item):
                    dst_path = os.path.join(self.backup_path, os.path.basename(item))
                    shutil.copy2(item, dst_path)
                    file_size = get_file_size(item)
                    processed_size += file_size
                    self.progress_updated.emit(int(processed_size / total_size * 100))
                    self.file_processed.emit(f"{item} ({format_size(file_size)})")
        except Exception as e:
            self.backup_failed.emit(f"Failed to create uncompressed backup: {str(e)}")

    def get_total_size(self):
        total_size = 0
        for item in self.files:
            if os.path.isdir(item):
                for root, _, files in os.walk(item):
                    if not self.include_subdirs and root != item:
                        continue
                    total_size += sum(get_file_size(os.path.join(root, file)) for file in files)
            elif os.path.isfile(item):
                total_size += get_file_size(item)
        return total_size
