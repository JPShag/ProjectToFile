from PyQt5.QtWidgets import QApplication
import sys
from gui import BackupRestoreApp

def main():
    app = QApplication(sys.argv)
    window = BackupRestoreApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
