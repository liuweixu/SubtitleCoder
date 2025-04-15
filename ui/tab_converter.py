import os
import re
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                              QPushButton, QTextEdit, QFileDialog, QMessageBox,
                              QGroupBox, QSpinBox, QColorDialog, QFontComboBox, 
                              QScrollArea, QButtonGroup, QCheckBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QFontDatabase
from utils.styles import DEFAULT_STYLE
from utils.resolution import ResolutionExtractor

class SubtitleConverterTab(QWidget):
    def __init__(self):
        super().__init__()
        self.overwrite_mode = None
        self.current_play_res_x = 1920
        self.current_play_res_y = 1080
        self.current_font_size = 70
        self.resolution_extractor = ResolutionExtractor()
        self.suffix_checkboxes = []  # 存储后缀选择复选框
        self.suffix_button_group = QButtonGroup(self)  # 用于管理复选框组
        self.suffix_button_group.setExclusive(False)  # 允许多选
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout(self)

        # 输入输出目录
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        input_btn = QPushButton("浏览...")
        input_btn.clicked.connect(lambda: self.select_directory(self.input_edit))
        input_layout.addWidget(QLabel("输入目录:"))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_btn)
        
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(lambda: self.select_directory(self.output_edit))
        output_layout.addWidget(QLabel("输出目录:"))
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        
        # 分辨率设置
        resolution_group = QGroupBox("分辨率设置 (PlayResX/Y)")
        resolution_layout = QHBoxLayout()
        
        resolution_layout.addWidget(QLabel("PlayResX:"))
        self.res_x_spin = QSpinBox()
        self.res_x_spin.setRange(1, 9999)
        self.res_x_spin.setValue(1920)
        resolution_layout.addWidget(self.res_x_spin)
        
        resolution_layout.addWidget(QLabel("PlayResY:"))
        self.res_y_spin = QSpinBox()
        self.res_y_spin.setRange(1, 9999)
        self.res_y_spin.setValue(1080)
        resolution_layout.addWidget(self.res_y_spin)
        
        # 从ASS提取分辨率按钮
        extract_res_btn = QPushButton("从ASS提取")
        extract_res_btn.clicked.connect(self.extract_resolution_from_ass)
        resolution_layout.addWidget(extract_res_btn)
        
        resolution_group.setLayout(resolution_layout)
        
        # 样式编辑
        style_group = QGroupBox("ASS样式定义")
        style_layout = QVBoxLayout()
        
        self.style_edit = QTextEdit()
        self.style_edit.setPlainText(DEFAULT_STYLE)
        
        # 样式参数编辑
        self.style_params_group = QGroupBox("样式参数")
        params_layout = QVBoxLayout()

        # 添加样式名称编辑框
        style_name_layout = QHBoxLayout()
        style_name_layout.addWidget(QLabel("样式名称:"))
        self.style_name_edit = QLineEdit("Dial_JP")
        style_name_layout.addWidget(self.style_name_edit)
        params_layout.addLayout(style_name_layout)
        
        # 字体名称 - 使用下拉框
        font_name_layout = QHBoxLayout()
        font_name_layout.addWidget(QLabel("字体名称:"))
        self.font_combo = QFontComboBox()
        # 设置默认字体
        font_db = QFontDatabase()
        default_font = "FOT-Humming ProN E"  # 默认字体
        if "Humming" in font_db.families():
            default_font = "FOT-Humming ProN E"
        elif "Microsoft YaHei" in font_db.families():
            default_font = "Microsoft YaHei"
        self.font_combo.setCurrentText(default_font)
        font_name_layout.addWidget(self.font_combo)
        params_layout.addLayout(font_name_layout)
        
        # 字体大小
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字体大小:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 200)
        self.font_size_spin.setValue(70)
        font_size_layout.addWidget(self.font_size_spin)
        
        calc_font_btn = QPushButton("计算大小")
        calc_font_btn.clicked.connect(self.calculate_font_size)
        font_size_layout.addWidget(calc_font_btn)
        params_layout.addLayout(font_size_layout)
        
        # 颜色设置 &H00FFFFFF,&H000000FF,&H00705E5B,&H00000000
        colors = [
            ("PrimaryColour:", "&H00FFFFFF", self.show_color_dialog),  
            ("SecondaryColour:", "&H000000FF", self.show_color_dialog),
            ("OutlineColour:", "&H00705E5B", self.show_color_dialog),
            ("BackColour:", "&H00000000", self.show_color_dialog)
        ]
        
        self.color_btns = []
        for label, default, callback in colors:
            color_layout = QHBoxLayout()
            color_layout.addWidget(QLabel(label))
            
            color_btn = QPushButton(default)
            color_btn.clicked.connect(callback)
            self.color_btns.append(color_btn)
            color_layout.addWidget(color_btn)
            
            params_layout.addLayout(color_layout)
        
        # 更新样式按钮
        update_style_btn = QPushButton("更新样式定义")
        update_style_btn.clicked.connect(self.update_style_from_params)
        params_layout.addWidget(update_style_btn)
        
        self.style_params_group.setLayout(params_layout)
        
        style_layout.addWidget(self.style_edit)
        style_layout.addWidget(self.style_params_group)
        style_group.setLayout(style_layout)
        
        # 控制按钮布局
        button_layout = QHBoxLayout()
        
        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.convert_btn)
        
        # 清空日志按钮
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_log_btn)
        
        # 日志显示
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("转换日志将显示在这里...")


        # 在原有控制按钮布局前添加后缀选择区域
        self.suffix_group = QGroupBox("选择要转换的后缀")
        suffix_layout = QVBoxLayout()
        
        # 添加一个滚动区域，以防后缀太多
        scroll_area = QScrollArea()

        scroll_area.setMinimumHeight(150)  # 设置最小高度为150像素
        scroll_area.setMaximumHeight(250)  # 设置最大高度为250像素
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 这里会在扫描目录时动态添加复选框
        self.suffix_container = QWidget()
        self.suffix_container_layout = QVBoxLayout(self.suffix_container)
        scroll_layout.addWidget(self.suffix_container)
        
        # 全选/取消全选按钮
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_suffixes)
        btn_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all_suffixes)
        btn_layout.addWidget(deselect_all_btn)
        
        scan_suffixes_btn = QPushButton("扫描后缀")
        scan_suffixes_btn.clicked.connect(self.scan_suffixes)
        btn_layout.addWidget(scan_suffixes_btn)
        
        scroll_layout.addLayout(btn_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        suffix_layout.addWidget(scroll_area)
        self.suffix_group.setLayout(suffix_layout)

        # 布局组装
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.suffix_group)
        layout.addWidget(resolution_group)
        layout.addWidget(style_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_area)
        
        # 连接信号
        self.res_x_spin.valueChanged.connect(self.update_resolution_values)
        self.res_y_spin.valueChanged.connect(self.update_resolution_values)
        self.resolution_extractor.resolution_extracted.connect(self.update_resolution_ui)
        
        # 初始更新
        self.update_resolution_values()
        self.update_style_params()

        # 重置
        reset_style_btn = QPushButton("重置为默认样式")
        reset_style_btn.clicked.connect(self.reset_style_to_default)
        params_layout.addWidget(reset_style_btn)

    # 在类中添加新的方法
    def reset_style_to_default(self):
        """将样式参数重置为默认值"""
        # 重置字体选择
        font_db = QFontDatabase()
        if "FOT-Humming ProN E" in font_db.families():
            self.font_combo.setCurrentText("FOT-Humming ProN E")
        elif "Microsoft YaHei" in font_db.families():
            self.font_combo.setCurrentText("Microsoft YaHei")
        else:
            self.font_combo.setCurrentIndex(0)
        
        # 重置字体大小
        self.font_size_spin.setValue(70)
        
        # 重置颜色按钮  
        default_colors = [
            "&H00FFFFFF",  # PrimaryColour
            "&H000000FF",  # SecondaryColour
            "&H00705E5B",  # OutlineColour
            "&H00000000"   # BackColour
        ]
        for btn, color in zip(self.color_btns, default_colors):
            btn.setText(color)
        
        # 重置样式定义文本
        self.style_edit.setPlainText(DEFAULT_STYLE)
        
        self.log("样式参数已重置为默认值")

    def clear_log(self):
        """清空日志区域"""
        self.log_area.clear()
        self.log("日志已清空")

    def calculate_font_size(self):
        """根据分辨率计算字体大小"""
        play_res_x = self.res_x_spin.value()
        play_res_y = self.res_y_spin.value()
        
        font_size = 69 * play_res_x / 1920
        if play_res_x == 1280:
            font_size -= 5
        if play_res_x == 1024:
            font_size -= 1
        
        calculated_size = round(font_size)
        self.font_size_spin.setValue(calculated_size)
        self.log(f"计算字体大小: {calculated_size} (基于分辨率 {play_res_x}x{play_res_y})")
        return calculated_size

    def update_resolution_values(self):
        """更新分辨率值"""
        self.current_play_res_x = self.res_x_spin.value()
        self.current_play_res_y = self.res_y_spin.value()
        self.calculate_font_size()

    def update_resolution_ui(self, filename, res_x, res_y):
        """更新分辨率UI显示"""
        self.res_x_spin.setValue(int(res_x))
        self.res_y_spin.setValue(int(res_y))
        self.log(f"从 {filename} 提取分辨率: {res_x}x{res_y}")

    def extract_resolution_from_ass(self):
        """从ASS文件提取分辨率"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择ASS文件", "", "ASS Files (*.ass)"
        )
        if filepath:
            self.resolution_extractor.extract_from_ass(filepath)

    def update_style_params(self):
        """从样式定义更新参数"""
        style = self.style_edit.toPlainText().strip()
        if not style.startswith("Style: "):
            return
        
        parts = style.split(",")
        if len(parts) < 5:
            return
        
        # 设置样式名称
        style_name = parts[0][7:].strip()  # 提取"Style: "之后的部分
        self.style_name_edit.setText(style_name)

        # 设置字体名称
        font_name = parts[1].strip()
        font_db = QFontDatabase()
        fonts = font_db.families()
        
        if font_name in fonts:
            self.font_combo.setCurrentText(font_name)
        else:
            # 如果字体不存在，尝试设置最接近的
            similar_fonts = [f for f in fonts if font_name.lower() in f.lower()]
            if similar_fonts:
                self.font_combo.setCurrentText(similar_fonts[0])
            else:
                self.font_combo.setCurrentIndex(0)
        
        # 设置其他参数
        self.font_size_spin.setValue(int(parts[2].strip()))
        
        color_indices = [3, 4, 5, 6]
        for i, idx in enumerate(color_indices):
            if idx < len(parts):
                self.color_btns[i].setText(parts[idx].strip())

    def update_style_from_params(self):
        """从参数更新样式定义，只更新字体名称、大小和颜色参数，保持其他参数不变"""
        # 获取当前样式文本
        current_style = self.style_edit.toPlainText().strip()
        
        # 如果当前不是有效的样式定义，则使用默认样式
        if not current_style.startswith("Style: "):
            current_style = DEFAULT_STYLE.strip()
        
        # 分割样式参数
        parts = current_style.split(",")
        
        # 确保有足够的参数部分
        if len(parts) < 18:  # ASS样式通常有18个参数
            parts = DEFAULT_STYLE.strip().split(",")
            if len(parts) < 18:
                parts = ["Style: Dial_JP"] + [""]*17  # 作为最后的回退
        
        # 获取用户当前选择的参数
        style_name = self.style_name_edit.text().strip() or "Dial_JP"
        font_name = self.font_combo.currentText()
        font_size = str(self.font_size_spin.value())
        colors = [btn.text() for btn in self.color_btns]
        
        # 只更新指定的6个参数，其他参数保持不变
        new_parts = [
            f"Style: {style_name}",  # 使用自定义样式名称
            font_name,  # 更新字体名称
            font_size,  # 更新字体大小
            *colors,    # 更新4个颜色参数
            *parts[7:]  # 保持其他参数不变
        ]
        
        # 重新组合为样式字符串
        new_style = ",".join(new_parts)
        self.style_edit.setPlainText(new_style)
        self.log(f"样式定义已更新")

    def show_color_dialog(self):
        """显示颜色选择对话框"""
        sender = self.sender()
        current_color = sender.text()
        
        if current_color.startswith("&H"):
            hex_str = current_color[2:]
            a = int(hex_str[0:2], 16)
            b = int(hex_str[2:4], 16)
            g = int(hex_str[4:6], 16)
            r = int(hex_str[6:8], 16)
            color = QColor(r, g, b, a)
        else:
            color = QColor(current_color)
        
        new_color = QColorDialog.getColor(color, self, "选择颜色")
        if new_color.isValid():
            a = new_color.alpha()
            b = new_color.blue()
            g = new_color.green()
            r = new_color.red()
            ass_color = f"&H{a:02X}{b:02X}{g:02X}{r:02X}"
            sender.setText(ass_color)

    def select_directory(self, target_edit):
        """选择目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        if dir_path:
            target_edit.setText(dir_path)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")

    def validate_paths(self):
        """验证路径"""
        if not os.path.isdir(self.input_edit.text()):
            QMessageBox.critical(self, "错误", "输入目录无效或不存在")
            return False
        if not self.output_edit.text():
            QMessageBox.critical(self, "错误", "请指定输出目录")
            return False
        return True

    def convert_srt_to_ass(self, srt_path, ass_path):
        """执行转换"""
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        play_res_x = self.res_x_spin.value()
        play_res_y = self.res_y_spin.value()
        style = self.style_edit.toPlainText().strip() or DEFAULT_STYLE
        
        # 从样式定义中提取样式名称
        style_name = "Dial_JP"  # 默认值
        if style.startswith("Style: "):
            parts = style.split(",")
            style_name = parts[0][7:].strip()  # 提取"Style: "之后的部分
        
        if play_res_x == 1920:
            scaledBorderAndShadowFlag = "yes"
        else:
            scaledBorderAndShadowFlag = "no"
            
        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "WrapStyle: 2",
            "ScaledBorderAndShadow: " + scaledBorderAndShadowFlag,
            f"PlayResX: {play_res_x}",
            f"PlayResY: {play_res_y}",
            "YCbCr Matrix: TV.709",
            # f"LayoutResX: 1920",
            # f"LayoutResY: 1080",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            style,
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        time_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")
        blocks = re.split(r"\n{2,}", srt_content.strip())
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) < 3:
                continue
            
            match = time_pattern.match(lines[1])
            if not match:
                continue
            
            start = datetime.strptime(match[1], "%H:%M:%S,%f").strftime("%H:%M:%S.%f")[:-4]
            end = datetime.strptime(match[2], "%H:%M:%S,%f").strftime("%H:%M:%S.%f")[:-4]
            text = r"\N".join(lines[2:]).strip()
            
            # ass_content.append(f"Dialogue: 0,{start},{end},Dial_JP,,0,0,0,,{text}")
            ass_content.append(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{text}")
        
        with open(ass_path, 'w', encoding='utf_8_sig') as f:
            f.write('\n'.join(ass_content))

    def start_conversion(self):
        """开始转换（修改后的版本，支持后缀筛选）"""
        if not self.validate_paths():
            return
        
        # 扫描后缀（如果尚未扫描）
        if not self.suffix_checkboxes:
            self.scan_suffixes()
            # 如果没有找到带后缀的文件，转换所有文件
            if any(not isinstance(cb, QCheckBox) for cb in self.suffix_checkboxes):
                if QMessageBox.question(self, "确认", 
                                    "未找到带后缀的SRT文件，是否转换所有SRT文件？",
                                    QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                    return
                # 设置标志表示转换所有文件
                convert_all = True
            else:
                convert_all = False
        else:
            # 已经有复选框，检查是否选择了任何后缀
            selected_suffixes = self.get_selected_suffixes()
            if selected_suffixes:
                convert_all = False
                suffix_info = f"选中的后缀: {', '.join(selected_suffixes)}"
            else:
                # 用户明确取消了所有选择，不转换任何文件
                QMessageBox.information(self, "信息", "没有选择任何后缀，将不转换任何文件")
                return
        
        self.overwrite_mode = None
        input_dir = self.input_edit.text()
        output_dir = self.output_edit.text()
        
        if convert_all:
            suffix_info = "将转换所有SRT文件"
        elif selected_suffixes:
            suffix_info = f"选中的后缀: {', '.join(selected_suffixes)}"
        
        self.log("=== 开始转换 ===")
        self.log(f"输入目录: {input_dir}")
        self.log(f"输出目录: {output_dir}")
        self.log(suffix_info)
        self.log(f"分辨率: {self.res_x_spin.value()}x{self.res_y_spin.value()}")
        self.log(f"使用字体: {self.font_combo.currentText()}")
        
        success = failed = skipped = 0
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for filename in os.listdir(input_dir):
                if not filename.lower().endswith(".srt"):
                    continue
                
                # 检查后缀筛选（除非convert_all为True）
                if not convert_all:
                    parts = filename.split('.')
                    if len(parts) >= 3:  # xx.AA.srt格式
                        current_suffix = parts[-2]
                        if current_suffix not in selected_suffixes:
                            continue
                    else:  # 不符合xx.AA.srt格式的文件
                        continue
                
                srt_path = os.path.join(input_dir, filename)
                ass_filename = f"{os.path.splitext(filename)[0]}.ass"
                ass_path = os.path.join(output_dir, ass_filename)
                
                if os.path.exists(ass_path):
                    try:
                        overwrite = self.handle_existing_file(ass_filename)
                    except InterruptedError:
                        self.log("用户取消转换")
                        return
                    
                    if not overwrite:
                        self.log(f"已跳过: {filename}")
                        skipped += 1
                        continue
                
                try:
                    self.convert_srt_to_ass(srt_path, ass_path)
                    self.log(f"转换成功: {filename}")
                    success += 1
                except Exception as e:
                    self.log(f"转换失败 [{filename}]: {str(e)}")
                    failed += 1
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生未预期的错误: {str(e)}")
        finally:
            self.log(f"=== 转换完成 ===")
            self.log(f"成功: {success}  失败: {failed}  跳过: {skipped}\n")

    def handle_existing_file(self, filename):
        """处理已存在文件"""
        if self.overwrite_mode == "all":
            return True
        if self.overwrite_mode == "none":
            return False
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("文件已存在")
        dialog.setText(f"文件 {filename} 已存在！")
        dialog.setInformativeText("请选择操作：")
        
        btn_overwrite = dialog.addButton("覆盖", QMessageBox.YesRole)
        btn_overwrite_all = dialog.addButton("覆盖所有", QMessageBox.YesRole)
        btn_skip = dialog.addButton("跳过", QMessageBox.NoRole)
        btn_skip_all = dialog.addButton("跳过所有", QMessageBox.NoRole)
        btn_cancel = dialog.addButton("取消", QMessageBox.RejectRole)
        
        dialog.exec()
        
        clicked = dialog.clickedButton()
        if clicked == btn_overwrite_all:
            self.overwrite_mode = "all"
            return True
        if clicked == btn_skip_all:
            self.overwrite_mode = "none"
            return False
        if clicked == btn_overwrite:
            return True
        if clicked == btn_skip:
            return False
        if clicked == btn_cancel:
            raise InterruptedError("用户取消操作")


    def scan_suffixes(self):
        """扫描输入目录中的SRT文件后缀（取.分隔的倒数第二部分）"""
        input_dir = self.input_edit.text()
        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, "警告", "请输入有效的输入目录")
            return
        
        # 清空现有复选框
        for checkbox in self.suffix_checkboxes:
            checkbox.deleteLater()
        self.suffix_checkboxes = []
        
        # 查找所有SRT文件并提取后缀
        suffixes = set()
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.srt'):
                # 按点分割文件名，取倒数第二部分作为后缀
                parts = filename.split('.')
                if len(parts) >= 3:  # 至少有两个点（如 xx.AA.srt）
                    suffix = parts[-2]  # 取倒数第二部分
                    suffixes.add(suffix)  # 保持原始大小写
        
        if not suffixes:
            # 如果没有找到带后缀的文件，显示一个提示
            label = QLabel("未找到符合格式的SRT文件（格式应为*.AA.srt）")
            self.suffix_container_layout.addWidget(label)
            self.suffix_checkboxes.append(label)
            return
        
        # 按字母顺序排序后缀（保持大小写）
        sorted_suffixes = sorted(suffixes, key=lambda x: x.lower())
        
        # 为每个后缀创建复选框
        for suffix in sorted_suffixes:
            checkbox = QCheckBox(suffix)
            checkbox.setChecked(True)  # 默认选中
            self.suffix_container_layout.addWidget(checkbox)
            self.suffix_checkboxes.append(checkbox)
        
        self.log(f"扫描到 {len(sorted_suffixes)} 个后缀: {', '.join(sorted_suffixes)}")

    def select_all_suffixes(self):
        """选中所有后缀复选框"""
        for checkbox in self.suffix_checkboxes:
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(True)

    def deselect_all_suffixes(self):
        """取消选中所有后缀复选框"""
        for checkbox in self.suffix_checkboxes:
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(False)

    def get_selected_suffixes(self):
        """获取用户选择的后缀列表"""
        selected = []
        for checkbox in self.suffix_checkboxes:
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected.append(checkbox.text())
        return selected