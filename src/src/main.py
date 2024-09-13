from PyQt5.QtWidgets import QApplication
import sys
import logging
from gui import BackupRestoreApp

def main():
    logging.basicConfig(level=logging.INFO, filename='app.log', 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        app = QApplication(sys.argv)
        window = BackupRestoreApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
