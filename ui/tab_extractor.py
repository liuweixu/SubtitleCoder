import os
from shutil import rmtree
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QProgressBar, QTextEdit, QFileDialog,
                              QMessageBox, QGroupBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QThread
from utils.extractorWorker import ExtractorWorker

class SubtitleExtractorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker_thread = None
        self.worker = None

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 文件类型选择
        self.filetype_group = QGroupBox("选择要处理的文件类型")
        filetype_layout = QHBoxLayout()

        # 单选框
        self.filetype_btn_group = QButtonGroup(self)
        self.mkv_radio = QRadioButton("处理MKV文件")
        self.ass_radio = QRadioButton("处理ASS文件")
        # 将单选框添加到按钮组
        self.filetype_btn_group.addButton(self.mkv_radio)
        self.filetype_btn_group.addButton(self.ass_radio)
        # 设置默认选中MKV
        self.mkv_radio.setChecked(True)
        filetype_layout.addWidget(self.mkv_radio)
        filetype_layout.addWidget(self.ass_radio)
        self.filetype_group.setLayout(filetype_layout)

        # 输入目录
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("请选择包含MKV/ASS文件的文件夹")
        input_btn = QPushButton("浏览...")
        input_btn.clicked.connect(self.select_input_dir)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)

        # 输出目录
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("请选择输出文件夹")
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)

        # 轨道ID控件
        track_layout = QHBoxLayout()
        track_layout.addWidget(QLabel("字幕轨道ID:"))
        self.track_id_edit = QLineEdit()
        self.track_id_edit.setPlaceholderText("默认为2")
        self.track_id_edit.setText("2")
        self.track_id_edit.setMaximumWidth(50)
        track_layout.addWidget(self.track_id_edit)
        track_layout.addStretch()

        # 字体调整控件
        fontsize_layout = QHBoxLayout()
        fontsize_layout.addWidget(QLabel("字体大小调整（+/-数值）："))
        self.size_adjust_edit = QLineEdit()
        self.size_adjust_edit.setPlaceholderText("例如：+5 或 -3")
        self.size_adjust_edit.setMaximumWidth(100)
        fontsize_layout.addWidget(self.size_adjust_edit)
        fontsize_layout.addStretch()

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # 控制按钮
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.clear_log_btn = QPushButton("清空日志")  # 新增清空日志按钮
        self.clear_log_btn.clicked.connect(self.clear_log)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.clear_log_btn)  # 将清空按钮添加到布局

        # 日志显示
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("处理日志将显示在这里...")  # 添加placeholder文本
        self.log_area.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")  # 设置日志页面为半透明

        # 语言选择组
        language_group = QGroupBox("选择字幕语言")
        language_layout = QHBoxLayout()
        self.chs_radio = QRadioButton("中文 (CHS)", checked=True)
        self.jp_radio = QRadioButton("日文 (JP)")
        language_layout.addWidget(self.chs_radio)
        language_layout.addWidget(self.jp_radio)
        language_group.setLayout(language_layout)

        # 组合控件
        layout.addWidget(self.filetype_group)
        layout.addWidget(language_group)  
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(track_layout)
        layout.addLayout(fontsize_layout)
        layout.addWidget(QLabel("处理进度:"))
        layout.addWidget(self.progress_bar)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("处理日志:"))
        layout.addWidget(self.log_area)
        

    def clear_log(self):
        """清空日志区域"""
        self.log_area.clear()
        self.log_message("日志已清空")  # 添加一条清空确认日志

    def select_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if dir_path:
            self.input_edit.setText(dir_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if dir_path:
            self.output_edit.setText(dir_path)

    def log_message(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def update_resolution_info(self, filename, res_x, res_y):
        if res_x == "N/A (SRT字幕)":
            info = f"{filename}: SRT"
        else:
            info = f"{filename}: ASS"

    def start_processing(self):
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()

        # 如果选择保存文件，需要验证输出目录
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                QMessageBox.critical(self, "错误", "无法创建输出文件夹！")
                return
            
        try:
            track_id = int(self.track_id_edit.text()) if self.track_id_edit.text() else 2
            if track_id < 0:
                raise ValueError("轨道ID必须大于等于0")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "轨道ID必须是大于等于0的整数！")
            return

        adjust_str = self.size_adjust_edit.text().strip()
        try:
            font_adjust = int(adjust_str) if adjust_str else 0
        except ValueError:
            QMessageBox.warning(self, "输入错误", "字体调整值必须是整数（如+5或-3）")
            return

        # 单选
        process_mkv = self.mkv_radio.isChecked()
        process_ass = self.ass_radio.isChecked()
        if not (process_mkv or process_ass):
            QMessageBox.warning(self, "错误", "请至少选择一种要处理的文件类型！")
            return

        # 获取选择的语言
        language = 'chs' if self.chs_radio.isChecked() else 'jp'

        if not os.path.isdir(input_dir):
            QMessageBox.critical(self, "错误", "输入文件夹不存在！")
            return
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                QMessageBox.critical(self, "错误", "无法创建输出文件夹！")
                return

        media_files = []
        for f in os.listdir(input_dir):
            lower_f = f.lower()
            if process_mkv and lower_f.endswith('.mkv'):
                media_files.append(f)
            if process_ass and lower_f.endswith('.ass'):
                media_files.append(f)
        
        if not media_files:
            QMessageBox.warning(self, "提示", "输入文件夹中没有符合选择的文件类型！")
            return

        self.worker_thread = QThread()
        self.worker = ExtractorWorker(input_dir, output_dir, media_files, font_adjust, track_id, language)
        
        self.worker.moveToThread(self.worker_thread)
        
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_message.connect(self.log_message)
        self.worker.finished.connect(self.on_finished)
        self.worker.resolution_info.connect(self.update_resolution_info)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log_area.clear()
        self.log_message("=== 开始处理 ===")
        self.log_message(f"选择的语言: {'中文' if language == 'chs' else '日文'}")
        self.log_message(f"使用的轨道ID: {track_id}")
        if font_adjust != 0:
            self.log_message(f"字体大小调整量：{font_adjust:+}")

    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.log_message("=== 用户请求停止处理 ===")
            self.stop_btn.setEnabled(False)

    def update_progress(self, current, total, filename):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.log_area.append(f"正在处理 ({current}/{total}): {filename}")

    def on_finished(self):
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_message("=== 处理完成 ===")
        QMessageBox.information(self, "完成", "所有文件处理完成！")