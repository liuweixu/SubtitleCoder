from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QTextEdit, QFileDialog, QGroupBox)
from utils.alignSubtitles import *
from datetime import datetime
from utils.alignWorker import AlignWorker

class SubtitleAlignTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowTitle("字幕对齐工具")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 输入输出目录选择
        input_output_group = QGroupBox("输入输出目录选择")
        input_output_layout = QVBoxLayout()
        input_layout1 = QHBoxLayout()
        self.input_edit1 = QLineEdit()
        input_btn1 = QPushButton("浏览...")
        input_btn1.clicked.connect(lambda: self.select_directory(self.input_edit1))
        input_layout1.addWidget(QLabel("输入日语SRT文件所在的目录 "))
        input_layout1.addWidget(self.input_edit1)
        input_layout1.addWidget(input_btn1)
        input_output_layout.addLayout(input_layout1) 

        input_layout2 = QHBoxLayout()
        self.input_edit2 = QLineEdit()
        input_btn2 = QPushButton("浏览...")
        input_btn2.clicked.connect(lambda: self.select_directory(self.input_edit2))
        input_layout2.addWidget(QLabel("输入中文ASS文件所在的目录 "))
        input_layout2.addWidget(self.input_edit2)
        input_layout2.addWidget(input_btn2)
        input_output_layout.addLayout(input_layout2)

        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(lambda: self.select_directory(self.output_edit))
        output_layout.addWidget(QLabel("对齐后的日语SRT字幕的输出目录 "))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        input_output_layout.addLayout(output_layout)
        input_output_group.setLayout(input_output_layout)

        # 字幕后缀输入框
        suffix_group = QGroupBox("字幕后缀选择")
        suffix_srt_layout = QHBoxLayout()
        suffix_srt_layout.addWidget(QLabel("日语SRT字幕后缀（默认：.srt）"))
        self.suffix_srt_edit = QLineEdit()
        self.suffix_srt_edit.setPlaceholderText("例如：.srt")
        suffix_srt_layout.addWidget(self.suffix_srt_edit)

        suffix_ass_layout = QHBoxLayout()
        suffix_ass_layout.addWidget(QLabel("中文ASS后缀（默认：.ass）"))
        self.suffix_ass_edit = QLineEdit()
        self.suffix_ass_edit.setPlaceholderText("例如：.ass")
        suffix_ass_layout.addWidget(self.suffix_ass_edit)

        container_layout = QHBoxLayout()
        container_layout.addLayout(suffix_srt_layout)
        container_layout.addLayout(suffix_ass_layout)
        suffix_group.setLayout(container_layout)

        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.start_alignment)  # 连接按钮点击事件到槽函数，用于启动对齐操作（涉及到异步通信）
        
        # 日志显示
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("日志将显示在这里")   

        # 清空日志按钮
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)

        # 布局组装
        layout.addWidget(input_output_group)
        layout.addWidget(suffix_group)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.log_area)
        layout.addWidget(self.clear_log_btn)
    
    def select_directory(self, target_edit):
        """选择目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            target_edit.setText(dir_path)
    
    def start_alignment(self):
        self.confirm_btn.setEnabled(False)
        self.worker = AlignWorker(
            self.input_edit1.text(),
            self.input_edit2.text(),
            self.output_edit.text(),
            self.suffix_srt_edit.text() or '.srt',
            self.suffix_ass_edit.text() or '.ass'
        )
        """
        连接信号和槽函数，用于处理日志和完成信号。
        当 worker 的 log_signal 信号被触发时 (即接收信号)，会调用 self.log 方法，将日志信息显示在文本框中。
        主线程的 log() 方法会自动收到字符串参数，并显示到日志区域中。
        当 worker 的 finished 信号被触发时，会调用 lambda 函数，将确认按钮的状态设置为可启用。
        这样，当 worker 完成任务时，确认按钮就会重新启用，用户可以再次开始新的任务。
        """
        # 连接日志信号到槽函数，是观察者模式的一种实现方式，也可以理解接收信号，而self.log是接收信号时调用的处理方法（槽函数）
        self.worker.log_signal.connect(self.log) 
        self.worker.finished.connect(lambda: self.confirm_btn.setEnabled(True))
        self.worker.start()

    def clear_log(self):
        """清空日志区域"""
        self.log_area.clear()
        self.log("日志已清空")

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")