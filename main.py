import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyInstaller.config import CONF
CONF['has_console'] = False
from pathlib import Path

class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    style_file = str(Path(__file__).parent / "qss" / "MacOS.qss")
    style_sheet = QSSLoader.read_qss_file(style_file)
    window.setStyleSheet(style_sheet)
    window.show()
    sys.exit(app.exec())