from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMenuBar, QMenu
from PySide6.QtGui import QPixmap, QPainter, QFont
from PySide6.QtCore import Qt, Signal
from ui.tab_extractor import SubtitleExtractorTab
from ui.tab_converter import SubtitleConverterTab
from ui.tab_align import SubtitleAlignTab
from ui.tab_assprocess import AssProcessTab
from pathlib import Path

class MainWindow(QMainWindow):
    style_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中日双语字幕小工具集")
        self.setGeometry(100, 100, 900, 800)
        
        # 设置背景图片
        self.background = QPixmap(str(Path(__file__).parent.parent / "resources" / "background.jpg"))  # 请替换为您的自定义图片路径
        self.background_opacity = 0.6  # 设置透明度
        
        # 创建菜单栏
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # 添加样式菜单
        style_menu = self.menu_bar.addMenu("样式")
        
        # 获取qss目录下所有样式文件
        qss_dir = Path(__file__).parent.parent / "qss"
        for qss_file in qss_dir.glob("*.qss"):
            action = style_menu.addAction(qss_file.stem)
            action.triggered.connect(lambda checked, f=qss_file: self.change_style(f))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 添加三个标签页
        self.extractor_tab = SubtitleExtractorTab()
        self.converter_tab = SubtitleConverterTab()
        self.align_tab = SubtitleAlignTab() 
        self.assprocess_tab = AssProcessTab()
        
        self.tab_widget.addTab(self.extractor_tab, "MKV/ASS双语字幕提取为中/日文")
        self.tab_widget.addTab(self.converter_tab, "SRT转ASS转换器")
        self.tab_widget.addTab(self.align_tab, "SRT字幕对齐")
        self.tab_widget.addTab(self.assprocess_tab, "ASS文件处理工具")
    

    def paintEvent(self, event):
        """重绘事件，绘制背景图片"""
        painter = QPainter(self)
        painter.setOpacity(self.background_opacity)
        painter.drawPixmap(self.rect(), self.background)
        painter.end() # 停止绘制，防止出现闪烁
        
    def change_style(self, qss_file):
        """切换样式"""
        self.style_changed.emit(str(qss_file))