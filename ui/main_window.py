from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from ui.tab_extractor import SubtitleExtractorTab
from ui.tab_converter import SubtitleConverterTab
from ui.tab_align import SubtitleAlignTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中日双语字幕小工具集")
        self.setGeometry(100, 100, 900, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 添加三个标签页
        self.extractor_tab = SubtitleExtractorTab()
        self.converter_tab = SubtitleConverterTab()
        self.align_tab = SubtitleAlignTab() 
        
        self.tab_widget.addTab(self.extractor_tab, "MKV/ASS双语字幕提取为中/日文")
        self.tab_widget.addTab(self.converter_tab, "SRT转ASS转换器")
        self.tab_widget.addTab(self.align_tab, "SRT字幕对齐")