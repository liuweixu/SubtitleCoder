import os
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QFileDialog, QMessageBox, QTextEdit)
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt
from utils.resolution import ResolutionExtractor

class ResolutionModifierTab(QWidget):
    def __init__(self):
        super().__init__()
        self.resolution_extractor = ResolutionExtractor()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # 主布局
        layout = QVBoxLayout(self)
        
        # 文件夹选择部分
        folder_group = QWidget()
        folder_layout = QHBoxLayout(folder_group)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        
        self.folder_label = QLabel("目标文件夹:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("点击浏览选择文件夹或直接输入路径")
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_button)
        
        # 分辨率设置部分
        resolution_group = QWidget()
        resolution_layout = QHBoxLayout(resolution_group)
        resolution_layout.setContentsMargins(0, 0, 0, 0)
        
        # self.resolution_label = QLabel("PlayRes")
        self.x_label = QLabel("PlayResX:")
        self.x_input = QLineEdit("1920")
        self.x_input.setValidator(QIntValidator(1, 99999))
        self.y_label = QLabel("PlayResY:")
        self.y_input = QLineEdit("1080")
        self.y_input.setValidator(QIntValidator(1, 99999))
        
        # 新增：从ASS提取分辨率按钮
        self.extract_res_btn = QPushButton("从ASS提取")
        self.extract_res_btn.setToolTip("从指定的ASS文件中提取分辨率设置")
        
        # resolution_layout.addWidget(self.resolution_label)
        resolution_layout.addWidget(self.x_label)
        resolution_layout.addWidget(self.x_input)
        resolution_layout.addWidget(self.y_label)
        resolution_layout.addWidget(self.y_input)
        resolution_layout.addWidget(self.extract_res_btn)
        
        # 操作按钮部分
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.process_button = QPushButton("处理文件")
        self.clear_button = QPushButton("清空")
        
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        
        # 日志输出部分
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("操作日志将显示在这里...")
        self.log_output.setMinimumHeight(200)
        
        # 将所有部件添加到主布局
        layout.addWidget(folder_group)
        layout.addWidget(resolution_group)
        layout.addWidget(button_group)
        layout.addWidget(self.log_output)
        
        # 设置边距和间距
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

    def connect_signals(self):
        """连接所有信号与槽"""
        self.process_button.clicked.connect(self.process_files)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.extract_res_btn.clicked.connect(self.extract_resolution_from_ass)
        self.resolution_extractor.resolution_extracted.connect(self.update_resolution_ui)

    def browse_folder(self):
        """打开文件夹选择对话框"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_input.setText(folder)
            self.log(f"已选择文件夹: {folder}")

    def extract_resolution_from_ass(self):
        """从ASS文件提取分辨率设置"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择ASS文件", "", "ASS Files (*.ass)"
        )
        if filepath:
            self.resolution_extractor.extract_from_ass(filepath)

    def update_resolution_ui(self, filename, res_x, res_y):
        """更新分辨率UI显示"""
        if res_x != "N/A" and res_y != "N/A":
            self.x_input.setText(res_x)
            self.y_input.setText(res_y)
            self.log(f"从 {os.path.basename(filename)} 提取分辨率: {res_x}x{res_y}")
        else:
            self.log(f"文件 {os.path.basename(filename)} 中未找到分辨率设置")

    def process_files(self):
        """处理选中的文件夹中的所有ASS文件"""
        folder_path = self.folder_input.text().strip()
        x_text = self.x_input.text().strip()
        y_text = self.y_input.text().strip()
        
        # 验证输入
        if not folder_path:
            QMessageBox.warning(self, "警告", "请选择目标文件夹！")
            return
            
        if not os.path.exists(folder_path):
            QMessageBox.warning(self, "警告", "指定的路径不存在！")
            return
            
        try:
            res_x = int(x_text) if x_text else 1920
            res_y = int(y_text) if y_text else 1080
        except ValueError:
            QMessageBox.warning(self, "警告", "分辨率必须是正整数！")
            return
            
        if res_x <= 0 or res_y <= 0:
            QMessageBox.warning(self, "警告", "分辨率必须是正整数！")
            return
            
        # 开始处理文件
        self.log_output.append(f"开始处理文件夹: {folder_path}")
        self.log_output.append(f"设置分辨率为: {res_x}x{res_y}")
        
        try:
            count = self.modify_ass_resolution(folder_path, res_x, res_y)
            self.log_output.append(f"\n处理完成！共修改了 {count} 个文件。")
            QMessageBox.information(self, "完成", f"所有.ass文件分辨率参数已更新为{res_x}x{res_y}！")
        except Exception as e:
            self.log_output.append(f"\n处理过程中出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"处理过程中出错:\n{str(e)}")

    def modify_ass_resolution(self, folder_path, res_x, res_y):
        """修改ASS文件的分辨率设置"""
        count = 0
        for filename in os.listdir(folder_path):
            if not filename.lower().endswith('.ass'):
                continue
                
            filepath = os.path.join(folder_path, filename)
            
            try:
                # 读取文件内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用正则表达式替换分辨率设置
                modified_content = re.sub(
                    r'(PlayResX\s*:\s*)(\d+)', 
                    fr'\g<1>{res_x}', 
                    content,
                    flags=re.IGNORECASE
                )
                modified_content = re.sub(
                    r'(PlayResY\s*:\s*)(\d+)', 
                    fr'\g<1>{res_y}', 
                    modified_content,
                    flags=re.IGNORECASE
                )
                
                # 写入修改后的内容
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.log(f'已成功处理文件: {filename}')
                count += 1
            except UnicodeDecodeError:
                self.log(f'文件 {filename} 编码错误，跳过处理')
                continue
            except Exception as e:
                self.log(f'处理文件 {filename} 时出错: {str(e)}')
                continue
                
        return count

    def clear_inputs(self):
        """清空所有输入"""
        self.folder_input.clear()
        self.x_input.setText("1920")
        self.y_input.setText("1080")
        self.log_output.clear()
        self.log("已重置所有输入")

    def log(self, message):
        """记录日志信息"""
        self.log_output.append(message)
        # 自动滚动到底部
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )