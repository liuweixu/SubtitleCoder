import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyInstaller.config import CONF
CONF['has_console'] = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())