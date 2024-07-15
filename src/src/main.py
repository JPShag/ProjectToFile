from PyQt5.QtWidgets import QApplication
import sys
from gui import BackupRestoreApp

def main():
    try:
        app = QApplication(sys.argv)
        window = BackupRestoreApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
