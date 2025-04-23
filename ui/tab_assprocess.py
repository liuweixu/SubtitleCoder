from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QTextEdit, QFileDialog, QGroupBox)
from utils.alignSubtitles import *
from datetime import datetime
from utils.alignWorker import AlignWorker
import chardet

class AssProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowTitle("ASS文件处理工具")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. 修改ScaledBorderAndShadow工具
        scaled_border_and_shadow_group = QGroupBox("修改ScaledBorderAndShadow工具")
        scaled_border_and_shadow = QVBoxLayout()
        # 输入目录选择
        input_layout1= QHBoxLayout()
        self.input_edit1 = QLineEdit()
        input_btn1 = QPushButton("浏览...")
        input_btn1.clicked.connect(lambda: self.select_directory(self.input_edit1))
        input_layout1.addWidget(QLabel("请输入包含 ASS 字幕文件的文件夹路径 "))
        input_layout1.addWidget(self.input_edit1)
        input_layout1.addWidget(input_btn1)
        scaled_border_and_shadow.addLayout(input_layout1)
        # 输入后缀选择
        suffix_layout1 = QHBoxLayout()
        suffix_layout1.addWidget(QLabel('请输入要处理的 ASS 文件后缀 '))
        self.suffix_edit1 = QLineEdit()
        self.suffix_edit1.setPlaceholderText('例如: ja.ass')
        suffix_layout1.addWidget(self.suffix_edit1)
        scaled_border_and_shadow.addLayout(suffix_layout1)
        # 修改目标选择
        yes_or_no_layout1 = QHBoxLayout()
        yes_or_no_layout1.addWidget(QLabel('修改目标 '))
        self.yes_or_no_edit1 = QLineEdit()
        self.yes_or_no_edit1.setPlaceholderText('yes or no')
        yes_or_no_layout1.addWidget(self.yes_or_no_edit1)
        scaled_border_and_shadow.addLayout(yes_or_no_layout1)
        scaled_border_and_shadow_group.setLayout(scaled_border_and_shadow)
        # 确认进行按钮
        self.confirm_btn1 = QPushButton("确认进行")
        self.confirm_btn1.clicked.connect(self.process_subtitles1)
        scaled_border_and_shadow.addWidget(self.confirm_btn1)
        scaled_border_and_shadow_group.setLayout(scaled_border_and_shadow)
        
        # 2. 修改ass样式的字体名称
        style_name_modify_group = QGroupBox("修改ass样式的字体名称")
        style_name_modify = QVBoxLayout()
        # 输入目录选择
        input_layout2= QHBoxLayout()
        self.input_edit2 = QLineEdit()
        input_btn2 = QPushButton("浏览...")
        input_btn2.clicked.connect(lambda: self.select_directory(self.input_edit2))
        input_layout2.addWidget(QLabel("请输入包含 ASS 字幕文件的文件夹路径 "))
        input_layout2.addWidget(self.input_edit2)
        input_layout2.addWidget(input_btn2)
        style_name_modify.addLayout(input_layout2)
        # 输入后缀选择
        suffix_layout2 = QHBoxLayout()
        suffix_layout2.addWidget(QLabel('请输入要处理的 ASS 文件后缀 '))
        self.suffix_edit2 = QLineEdit()
        self.suffix_edit2.setPlaceholderText('例如: ja.ass')
        suffix_layout2.addWidget(self.suffix_edit2)
        style_name_modify.addLayout(suffix_layout2)
        # 样式名称选择
        style_name_layout2 = QHBoxLayout()
        style_name_layout2.addWidget(QLabel('请输入要修改的样式名称 '))
        self.style_name_edit2 = QLineEdit()
        self.style_name_edit2.setPlaceholderText('例如: Default')
        style_name_layout2.addWidget(self.style_name_edit2)
        style_name_modify.addLayout(style_name_layout2)
        # 字体名称修改目标选择
        font_name_layout2 = QHBoxLayout()
        font_name_layout2.addWidget(QLabel('请输入要修改的字体名称 '))
        self.font_name_edit2 = QLineEdit()
        self.font_name_edit2.setPlaceholderText('例如: Microsoft YaHei')
        font_name_layout2.addWidget(self.font_name_edit2)
        style_name_modify.addLayout(font_name_layout2)
        # 确认进行按钮
        self.confirm_btn2 = QPushButton("确认进行")
        self.confirm_btn2.clicked.connect(self.process_subtitles2)
        style_name_modify.addWidget(self.confirm_btn2)
        style_name_modify_group.setLayout(style_name_modify)

        # 3. 根据输入样式修改ass样式
        style_information_modify_group = QGroupBox("根据输入样式修改ass样式")
        style_information_modify = QVBoxLayout()
        # 输入目录选择
        input_layout3= QHBoxLayout()
        self.input_edit3 = QLineEdit()
        input_btn3 = QPushButton("浏览...")
        input_btn3.clicked.connect(lambda: self.select_directory(self.input_edit3))
        input_layout3.addWidget(QLabel("请输入包含 ASS 字幕文件的文件夹路径 "))
        input_layout3.addWidget(self.input_edit3)
        input_layout3.addWidget(input_btn3)
        style_information_modify.addLayout(input_layout3)
        # 输入后缀选择
        suffix_layout3 = QHBoxLayout()
        suffix_layout3.addWidget(QLabel('请输入要处理的 ASS 文件后缀 '))
        self.suffix_edit3 = QLineEdit()
        self.suffix_edit3.setPlaceholderText('例如: ja.ass')
        suffix_layout3.addWidget(self.suffix_edit3)
        style_information_modify.addLayout(suffix_layout3)
        # 样式名称选择
        style_name_layout3 = QHBoxLayout()
        style_name_layout3.addWidget(QLabel('请输入要修改的样式名称 '))
        self.style_name_edit3 = QLineEdit()
        self.style_name_edit3.setPlaceholderText('例如: Default')
        style_name_layout3.addWidget(self.style_name_edit3)
        style_information_modify.addLayout(style_name_layout3)
        # 样式信息输入
        style_information_layout3 = QHBoxLayout()
        style_information_layout3.addWidget(QLabel('请输入要修改的样式信息 '))
        self.style_information_edit3 = QLineEdit()
        self.style_information_edit3.setPlaceholderText('例如: FZLanTingYuan-DB-GBK,25.5,&H00FFFFFF,&HF0000000,&H005F5F5F,&H007F7F7F,-1,0,0,0,96,100,0,0,1,0.75,1,2,30,30,7,134')
        style_information_layout3.addWidget(self.style_information_edit3)
        style_information_modify.addLayout(style_information_layout3)
        # 确认进行按钮
        self.confirm_btn3 = QPushButton("确认进行")
        self.confirm_btn3.clicked.connect(self.process_subtitles3)
        style_information_modify.addWidget(self.confirm_btn3)
        style_information_modify_group.setLayout(style_information_modify)

        # 日志显示
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("日志将显示在这里")   

        # 清空日志按钮
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)

        # 布局组装
        layout.addWidget(scaled_border_and_shadow_group)
        layout.addWidget(style_name_modify_group)
        layout.addWidget(style_information_modify_group)
        layout.addWidget(self.log_area)
        layout.addWidget(self.clear_log_btn)

    def select_directory(self, target_edit):
        """选择目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            target_edit.setText(dir_path)
    
    def scaled_border_and_shadow_modify(self):
        """1. 修改ScaledBorderAndShadow函数"""
        if not self.input_edit1.text() or not self.suffix_edit1.text() or not self.yes_or_no_edit1.text():
            self.log("请输入完整")
            return
        if self.yes_or_no_edit1.text().lower() not in ['yes', 'no']:
            self.log("请输入yes或no")
            return
        folder_path = self.input_edit1.text()
        file_suffix = self.suffix_edit1.text()
        yes_or_no = self.yes_or_no_edit1.text()
        if not os.path.isdir(folder_path):
            self.log(f"指定的文件夹路径不存在: {folder_path}")
            return
        filemodify = False # 用于判断是否有需要修改的文件
        for filename in os.listdir(folder_path):
            if filename.endswith(file_suffix):
                filemodify = True
                filepath = os.path.join(folder_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    modified = False
                    in_script_info = False
                    
                    for i, line in enumerate(lines):
                        line_stripped = line.strip()
                        
                        # 检查是否进入 [Script Info] 部分
                        if '[Script Info]' in line_stripped:
                            in_script_info = True
                            continue
                        # 检查是否离开 [Script Info] 部分
                        elif line_stripped.startswith('[') and line_stripped != '[Script Info]':
                            if modified == False:
                                new_line = 'ScaledBorderAndShadow:' + yes_or_no + '\n\n' + line
                                lines[i] = new_line
                                modified = True
                            in_script_info = False
                        
                        # 如果在 [Script Info] 部分且找到目标行
                        if in_script_info and line_stripped.startswith('ScaledBorderAndShadow:'):
                            # 分割键值对
                            parts = line_stripped.split(':', 1)
                            if len(parts) == 2:
                                key, value = parts
                                value = value.strip().lower()
                                if value != yes_or_no:  # 如果不是yes或no
                                    # 替换为 yes或no，保留原始格式
                                    new_line = f"{key}: {yes_or_no}\n"
                                    lines[i] = new_line
                                    modified = True
                    
                    # 如果有修改，则保存文件
                    if modified:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                        self.log(f'已修改文件: {filepath}')
                    else:
                        self.log(f'未找到需要修改的内容: {filepath}')
                
                except Exception as e:
                    self.log(f'处理文件 {filepath} 时出错: {str(e)}')    
        if filemodify == False:
            self.log(f'需要修改的文件不存在')

    def style_font_name_modify(self):
        '''2. 修改ass样式的字体名称函数'''
        if not self.input_edit2.text() or not self.suffix_edit2.text() or not self.style_name_edit2.text() or not self.font_name_edit2.text():
            self.log("请输入完整")
            return
        folder_path = self.input_edit2.text()  # 获取文件夹路径
        file_suffix = self.suffix_edit2.text()  # 获取文件后缀
        style_name = self.style_name_edit2.text()  # 获取样式名称
        font_name = self.font_name_edit2.text()  # 获取字体名称
        if not os.path.isdir(folder_path):
            self.log(f"指定的文件夹路径不存在: {folder_path}")
            return
        filemodify = False # 用于判断是否有需要修改的文件
        for filename in os.listdir(folder_path):
            if len(filename.split('.')) == len(file_suffix.split('.')) and filename.endswith(file_suffix):
                filemodify = True
                filepath = os.path.join(folder_path, filename)
                with open(filepath, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] or 'gbk'  # 默认回退到GBK
                
                stylemodify = False # 用于判断是否有需要修改的样式
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                        in_style_info = False
                        for i, line in enumerate(lines):
                            line_stripped = line.strip()
                            
                            if line_stripped.startswith("LayoutResX: ") or line_stripped.startswith("LayoutResY: "):
                                lines[i] = '\n'

                            # 检查是否进入 [V4+ Styles] 部分
                            if '[V4+ Styles]' in line_stripped:
                                in_style_info = True
                                continue
                            # 检查是否离开 [V4+ Styles] 部分
                            elif line_stripped.startswith('[') and line_stripped != '[V4+ Styles]':
                                in_style_info = False
                            
                            # 如果在 [V4+ Styles] 部分且找到目标行
                            if in_style_info and line_stripped.startswith('Style: ') and line_stripped.split(',')[0].split(':')[1].strip() == style_name:
                                stylemodify = True
                                parts = line_stripped.split(',')
                                parts[1] = font_name
                                new_line = ','.join([parts[0], parts[1]] + parts[2:])
                                lines[i] = new_line + '\n'
                                break
                    #保存修改后的文件
                    if stylemodify == True:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                            self.log(f'已修改文件: {filepath}') 
                    else:
                        self.log(f'未找到需要修改的样式: {filepath}')
            
                except Exception as e:
                    self.log(f'处理文件 {filepath} 时出错: {str(e)}')
        if filemodify == False:
            self.log(f'需要修改的文件不存在')
    
    def style_information_modify(self):
        '''3. 根据输入样式修改ass样式函数'''
        if not self.input_edit3.text() or not self.suffix_edit3.text() or not self.style_name_edit3.text() or not self.style_information_edit3.text():
            self.log("请输入完整")
            return
        folder_path = self.input_edit3.text()  # 获取文件夹路径
        file_suffix = self.suffix_edit3.text()  # 获取文件后缀
        style_name = self.style_name_edit3.text()  # 获取样式名称
        style_information = self.style_information_edit3.text()  # 获取样式信息
        if not os.path.isdir(folder_path):
            self.log(f"指定的文件夹路径不存在: {folder_path}")
            return
        filemodify = False # 用于判断是否有需要修改的文件
        for filename in os.listdir(folder_path):
            filemodify = True
            if len(filename.split('.')) == len(file_suffix.split('.')) and filename.endswith(file_suffix):
                filepath = os.path.join(folder_path, filename)
                with open(filepath, 'rb') as f:
                    raw_data = f.read()
                    encoding = chardet.detect(raw_data)['encoding'] or 'gbk'  # 默认回退到GBK
                stylemodify = False # 用于判断是否有需要修改的样式
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                        in_style_info = False
                        for i, line in enumerate(lines):
                            line_stripped = line.strip()
                            
                            if line_stripped.startswith("LayoutResX: ") or line_stripped.startswith("LayoutResY: "):
                                lines[i] = '\n'

                            # 检查是否进入 [V4+ Styles] 部分
                            if '[V4+ Styles]' in line_stripped:
                                in_style_info = True
                                continue
                            # 检查是否离开 [V4+ Styles] 部分
                            elif line_stripped.startswith('[') and line_stripped != '[V4+ Styles]':
                                in_style_info = False
                            
                            # 如果在 [V4+ Styles] 部分且找到目标行
                            if in_style_info and line_stripped.startswith('Style: ') and line_stripped.split(',')[0].split(':')[1].strip() == style_name:
                                stylemodify = True
                                parts = line_stripped.split(',')
                                new_line = parts[0] + ',' + style_information
                                lines[i] = new_line + '\n'
                                break
                    #保存修改后的文件
                    if stylemodify == True:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                            self.log(f'已修改文件: {filepath}') 
                    else:
                        self.log(f'未找到需要修改的样式: {filepath}')
            
                except Exception as e:
                    self.log(f'处理文件 {filepath} 时出错: {str(e)}')
        if filemodify == False:
            self.log(f'需要修改的文件不存在')

    def process_subtitles1(self):
        self.log("========================================================")
        self.log("1. 修改ScaledBorderAndShadow")
        self.log("========================================================")
        self.log("处理中...")
        self.scaled_border_and_shadow_modify()
    
    def process_subtitles2(self):
        self.log("========================================================")
        self.log("2. 修改ass样式的字体名称")
        self.log("========================================================")
        self.log("处理中...")
        self.style_font_name_modify()
    
    def process_subtitles3(self):
        self.log("========================================================")
        self.log("3. 根据输入样式修改ass样式")
        self.log("========================================================")
        self.log("处理中...")
        self.style_information_modify()

    def clear_log(self):
        """清空日志区域"""
        self.log_area.clear()
        self.log("日志已清空")

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")