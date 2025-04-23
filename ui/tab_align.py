import os
from shutil import rmtree
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QProgressBar, QTextEdit, QFileDialog,
                              QMessageBox, QGroupBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QThread, Signal
from utils.alignSubtitles import *
from datetime import datetime

class AlignWorker(QThread):
    log_signal = Signal(str)

    def __init__(self, jp_dir, cn_dir, output_dir, jp_ext, cn_ext):
        super().__init__()
        self.jp_dir = jp_dir
        self.cn_dir = cn_dir
        self.output_dir = output_dir
        self.jp_ext = jp_ext
        self.cn_ext = cn_ext

    def run(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            pairs = find_matching_pairs(self.jp_dir, self.cn_dir, self.jp_ext, self.cn_ext)
            failed_files = []

            for jp_file, cn_file in pairs:
                jp_path = os.path.join(self.jp_dir, jp_file)
                cn_path = os.path.join(self.cn_dir, cn_file)
                output_path = os.path.join(self.output_dir, jp_file)

                # 原有处理逻辑...
                if cn_file.endswith('.ass'):
                    temp_srt = Path(cn_path).with_suffix('.temp.srt')
                    convert_ass_to_srt(cn_path, temp_srt)
                    cn_ref_path = temp_srt
                else:
                    cn_ref_path = cn_path

                try:
                    align_subtitles(jp_path, cn_ref_path, output_path)
                    self.log_signal.emit(f"成功对齐: {jp_file} 和 {cn_file}")
                except Exception as e:
                    self.log_signal.emit(f"对齐失败: {jp_file} 和 {cn_file}, 错误: {e}")
                    failed_files.append(jp_file)
                finally:
                    if cn_file.endswith('.ass') and os.path.exists(temp_srt):
                        os.remove(temp_srt)

            if failed_files:
                self.log_signal.emit("\n以下文件对齐失败:")
                for file in failed_files:
                    self.log_signal.emit(f"- {file}")
        except Exception as e:
            self.log_signal.emit(f"处理过程中发生错误: {str(e)}")

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
        input_layout1.addWidget(QLabel("输入日语Srt文件所在的目录 "))
        input_layout1.addWidget(self.input_edit1)
        input_layout1.addWidget(input_btn1)
        input_output_layout.addLayout(input_layout1) 

        input_layout2 = QHBoxLayout()
        self.input_edit2 = QLineEdit()
        input_btn2 = QPushButton("浏览...")
        input_btn2.clicked.connect(lambda: self.select_directory(self.input_edit2))
        input_layout2.addWidget(QLabel("输入中文Srt文件所在的目录 "))
        input_layout2.addWidget(self.input_edit2)
        input_layout2.addWidget(input_btn2)
        input_output_layout.addLayout(input_layout2)

        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(lambda: self.select_directory(self.output_edit))
        output_layout.addWidget(QLabel("输出目录 "))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        input_output_layout.addLayout(output_layout)
        input_output_group.setLayout(input_output_layout)

        # 字幕后缀输入框
        suffix_group = QGroupBox("字幕后缀选择")
        suffix_srt_layout = QHBoxLayout()
        suffix_srt_layout.addWidget(QLabel("字幕后缀（默认：.srt）"))
        self.suffix_srt_edit = QLineEdit()
        self.suffix_srt_edit.setPlaceholderText("例如：.srt")
        suffix_srt_layout.addWidget(self.suffix_srt_edit)

        suffix_ass_layout = QHBoxLayout()
        suffix_ass_layout.addWidget(QLabel("ASS后缀（默认：.ass）"))
        self.suffix_ass_edit = QLineEdit()
        self.suffix_ass_edit.setPlaceholderText("例如：.ass")
        suffix_ass_layout.addWidget(self.suffix_ass_edit)

        container_layout = QHBoxLayout()
        container_layout.addLayout(suffix_srt_layout)
        container_layout.addLayout(suffix_ass_layout)
        suffix_group.setLayout(container_layout)

        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.start_alignment)  # 连接按钮点击事件到槽函数
        
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
        self.worker.log_signal.connect(self.log)
        self.worker.finished.connect(lambda: self.confirm_btn.setEnabled(True))
        self.worker.start()

    def align_subtitles(self):
        """主函数"""
        jp_dir = self.input_edit1.text()
        cn_dir = self.input_edit2.text()
        output_dir = self.output_edit.text()
        jp_ext = self.suffix_srt_edit.text() or '.srt'
        cn_ext = self.suffix_ass_edit.text() or '.ass'
        
        os.makedirs(output_dir, exist_ok=True)
        pairs = find_matching_pairs(jp_dir, cn_dir, jp_ext, cn_ext)
        failed_files = []
        
        for jp_file, cn_file in pairs:
            jp_path = os.path.join(jp_dir, jp_file)
            cn_path = os.path.join(cn_dir, cn_file)
            output_path = os.path.join(output_dir, jp_file)
            
            # 如果中文是ASS格式，先转换为SRT临时文件
            if cn_file.endswith('.ass'):
                temp_srt = Path(cn_path).with_suffix('.temp.srt')
                convert_ass_to_srt(cn_path, temp_srt)
                cn_ref_path = temp_srt
            else:
                cn_ref_path = cn_path
            
            try:
                align_subtitles(jp_path, cn_ref_path, output_path)
                self.log(f"成功对齐: {jp_file} 和 {cn_file}")
            except subprocess.CalledProcessError as e:
                self.log(f"对齐失败: {jp_file} 和 {cn_file}, 错误: {e}")
                failed_files.append(jp_file)
            finally:
                # 删除临时SRT文件
                if cn_file.endswith('.ass') and os.path.exists(temp_srt):
                    os.remove(temp_srt)
        
        if failed_files:
            self.log("\n以下文件对齐失败:")
            for file in failed_files:
                self.log(f"- {file}")

    def clear_log(self):
        """清空日志区域"""
        self.log_area.clear()
        self.log("日志已清空")

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")