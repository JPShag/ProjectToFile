import os
import shutil
import zipfile
import json
from PyQt5.QtCore import QThread, pyqtSignal

class FileProcessor(QThread):
    progress_updated = pyqtSignal(int)
    file_processed = pyqtSignal(str)
    processing_completed = pyqtSignal()
    processing_failed = pyqtSignal(str)

    def __init__(self, action, source_paths, destination_path, options):
        super().__init__()
        self.action = action
        self.source_paths = source_paths
        self.destination_path = destination_path
        self.options = options

    def run(self):
        try:
            if self.action == 'copy':
                self._copy_files()
            elif self.action == 'move':
                self._move_files()
            elif self.action == 'zip':
                self._zip_files()
            elif self.action == 'unzip':
                self._unzip_files()
            elif self.action == 'delete':
                self._delete_files()
            self.processing_completed.emit()
        except Exception as e:
            self.processing_failed.emit(str(e))

    def _copy_files(self):
        for source in self.source_paths:
            if os.path.isfile(source):
                shutil.copy2(source, self.destination_path)
                self.file_processed.emit(f"Copied: {source}")
            elif os.path.isdir(source):
                dest_dir = os.path.join(self.destination_path, os.path.basename(source))
                shutil.copytree(source, dest_dir)
                self.file_processed.emit(f"Copied directory: {source}")

    def _move_files(self):
        for source in self.source_paths:
            dest = os.path.join(self.destination_path, os.path.basename(source))
            shutil.move(source, dest)
            self.file_processed.emit(f"Moved: {source}")

    def _zip_files(self):
        with zipfile.ZipFile(self.destination_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source in self.source_paths:
                if os.path.isfile(source):
                    zipf.write(source, os.path.basename(source))
                    self.file_processed.emit(f"Added to zip: {source}")
                elif os.path.isdir(source):
                    for root, _, files in os.walk(source):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(source))
                            zipf.write(file_path, arcname)
                            self.file_processed.emit(f"Added to zip: {file_path}")

    def _unzip_files(self):
        with zipfile.ZipFile(self.source_paths[0], 'r') as zipf:
            zipf.extractall(self.destination_path)
            for file in zipf.namelist():
                self.file_processed.emit(f"Extracted: {file}")

    def _delete_files(self):
        for source in self.source_paths:
            if os.path.isfile(source):
                os.remove(source)
                self.file_processed.emit(f"Deleted: {source}")
            elif os.path.isdir(source):
                shutil.rmtree(source)
                self.file_processed.emit(f"Deleted directory: {source}")

def process_files(action, source_paths, destination_path, options=None):
    processor = FileProcessor(action, source_paths, destination_path, options)
    processor.start()
    return processor