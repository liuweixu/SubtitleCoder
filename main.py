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
    # 加载默认样式
    style_file = str(Path(__file__).parent / "qss" / "MacOS.qss")
    style_sheet = QSSLoader.read_qss_file(style_file)
    window.setStyleSheet(style_sheet)
    
    # 连接样式切换信号
    def on_style_changed(qss_file):
        style_sheet = QSSLoader.read_qss_file(qss_file)
        window.setStyleSheet(style_sheet)
    
    window.style_changed.connect(on_style_changed)
    
    window.show()
    sys.exit(app.exec())