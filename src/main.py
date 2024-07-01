from PyQt5.QtWidgets import QApplication
import sys
from gui import BackupApp

def main():
    app = QApplication(sys.argv)
    backup_app = BackupApp()
    backup_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
