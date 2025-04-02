import os
import subprocess
import chardet
from shutil import rmtree
import re
from PySide6.QtCore import QObject, Signal

class ExtractorWorker(QObject):
    """
    字幕提取工作线程类
    用于从MKV/ASS文件中提取字幕
    通过信号机制与主线程通信
    """
    progress_updated = Signal(int, int, str)  # 当前进度, 总数, 文件名
    finished = Signal()                       # 处理完成信号
    error_occurred = Signal(str)              # 错误信息
    log_message = Signal(str)                 # 日志消息
    resolution_info = Signal(str, str, str)    # 文件名, 分辨率X, 分辨率Y

    def __init__(self, input_dir, output_dir, media_files, font_adjust=0, track_id=2, language='chs'):
        """
        初始化工作线程
        :param input_dir: 输入目录路径
        :param output_dir: 输出目录路径
        :param media_files: 要处理的文件列表
        :param font_adjust: 字体大小调整值(可正可负)
        :param track_id: MKV字幕轨道ID(默认为2)
        :param language: 中文或日文单选
        """
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.media_files = media_files
        self.font_adjust = font_adjust
        self.track_id = track_id
        self.language = language.lower()  # 'chs' 或 'jp'
        self._is_running = True  # 线程运行标志
        self._read_only_mode = False  # 新增：只读模式标志

    def stop(self):
        """请求停止处理"""
        self._is_running = False
        self.log_message.emit("正在停止处理...")

    def set_read_only_mode(self, read_only):
        """设置只读模式，仅读取信息不保存文件"""
        self._read_only_mode = read_only

    def run(self):
        """主处理流程"""
        total = len(self.media_files)
        for i, filename in enumerate(self.media_files, 1):
            if not self._is_running:  # 检查停止标志
                break
                
            # 发送进度更新信号
            self.progress_updated.emit(i, total, filename)
            try:
                file_path = os.path.join(self.input_dir, filename)
                if filename.lower().endswith('.mkv'):
                    self.process_mkv_file(file_path)  # 处理MKV文件
                elif filename.lower().endswith('.ass'):
                    self.process_external_ass(file_path)  # 处理外部ASS文件
            except Exception as e:
                self.log_message.emit(f"处理失败: {filename} - {str(e)}")
                self.error_occurred.emit(str(e))
        
        # 处理完成发送信号
        self.finished.emit()

    def detect_encoding(self, file_path):
        """
        检测文件编码
        :param file_path: 文件路径
        :return: 检测到的编码格式
        """
        with open(file_path, 'rb') as f:
            rawdata = f.read(4096)
            # 检查BOM头判断编码
            bom_map = {
                b'\xff\xfe': 'utf-16-le',
                b'\xfe\xff': 'utf-16-be',
                b'\xef\xbb\xbf': 'utf-8-sig'
            }
            for bom, encoding in bom_map.items():
                if rawdata.startswith(bom):
                    return encoding
            # 使用chardet作为后备方案
            result = chardet.detect(rawdata)
            return result['encoding'] if result['confidence'] > 0.9 else 'utf-8'

    def extract_japanese_lines(self, content):
        """
        根据语言选择过滤出目标语言字幕行
        :param content: ASS文件内容列表
        :return: 过滤后的字幕行列表
        """
        target_lines = []
        
        for line in content:
            line = line.strip()
            if line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) < 10:
                    continue
                
                style_name = parts[3].strip()
                # 添加特例：1. 悠哉日常大王第二季繁体版 2. 再见龙生，您好人生猎户压制组版本
                is_japanese = 'JP' in style_name.upper() or 'JA' in style_name.upper() or '少女日常日文' in style_name \
                            or '日文歌詞方案' in style_name or '正 文 日' in style_name
                
                # 根据语言选择决定保留哪些行
                if (self.language == 'chs' and not is_japanese) or (self.language == 'jp' and is_japanese):
                    target_lines.append(line)
            else:
                target_lines.append(line)
        return target_lines

    def get_ass_resolution(self, content):
        """
        从ASS内容中提取分辨率信息
        :param content: ASS文件内容列表
        :return: (PlayResX, PlayResY)
        """
        play_res_x = "N/A"
        play_res_y = "N/A"
        
        for line in content:
            if line.startswith("PlayResX:"):
                play_res_x = line.split(":")[1].strip()
            elif line.startswith("PlayResY:"):
                play_res_y = line.split(":")[1].strip()
        
        return play_res_x, play_res_y

    def process_ass(self, input_file, output_file=None):
        """
        处理ASS字幕文件
        :param input_file: 输入文件路径
        :param output_file: 输出文件路径(可选，None表示仅读取信息)
        :return: 处理是否成功
        """
        try:
            # 检测并读取文件
            encoding = self.detect_encoding(input_file)
            with open(input_file, 'r', encoding=encoding, errors='replace') as f_in:
                content = f_in.readlines()
        except Exception as e:
            self.log_message.emit(f"无法读取文件 {input_file}: {str(e)}")
            return False

        # 获取原始分辨率并发送信号
        play_res_x, play_res_y = self.get_ass_resolution(content)
        self.resolution_info.emit(os.path.basename(input_file), play_res_x, play_res_y)

        # 如果是只读模式，直接返回成功
        if output_file is None or self._read_only_mode:
            return True

        # 过滤日语字幕行
        jp_content = self.extract_japanese_lines(content)
        
        # 应用字体大小调整
        if self.font_adjust != 0:
            adjusted_content = []
            for line in jp_content:
                line = line.strip()
                if line.startswith('Style:'):
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            original_size = int(parts[2])
                            new_size = original_size + self.font_adjust
                            new_size = max(1, new_size)  # 确保不小于1
                            parts[2] = str(new_size)
                            adjusted_line = ','.join(parts)
                            adjusted_content.append(adjusted_line)
                            continue
                        except (ValueError, IndexError):
                            pass
                adjusted_content.append(line)
            jp_content = adjusted_content
        
        # 写入输出文件
        try:
            with open(output_file, 'w', encoding='utf-8-sig') as f_out:
                f_out.write('\n'.join(jp_content))
            return True
        except Exception as e:
            self.log_message.emit(f"无法写入文件 {output_file}: {str(e)}")
            return False

    def detect_subtitle_format(self, file_path):
        """
        检测字幕文件格式
        :param file_path: 文件路径
        :return: 'ass'/'srt'/'unknown'
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline().strip()
                if first_line.startswith('[Script Info]'):
                    return 'ass'
                elif first_line.isdigit():  # SRT格式通常以数字开头
                    return 'srt'
                else:
                    return 'unknown'
        except:
            return 'unknown'

    def process_mkv_file(self, mkv_path):
        """
        处理MKV文件并提取字幕
        :param mkv_path: MKV文件路径
        """
        base_name = os.path.basename(mkv_path)
        base = os.path.splitext(base_name)[0]
        temp_dir = os.path.join(self.output_dir, "temp_extract")
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            temp_sub = os.path.join(temp_dir, f"{base}_temp.sub")
            
            # 使用mkvextract提取字幕轨道
            command = ["mkvextract", "tracks", mkv_path, f"{self.track_id}:{temp_sub}"]
            subprocess.run(command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW) # 不显示控制器
            
            # 检测提取的字幕格式
            sub_format = self.detect_subtitle_format(temp_sub)
            
            if sub_format == 'unknown':
                self.log_message.emit(f"× 失败：{base_name}（无法识别的字幕格式）")
                return
            
            # 根据语言选择设置后缀
            suffix = "CHS" if self.language == 'chs' else "JP"
            
            # 根据格式设置输出文件名
            if sub_format == 'srt':
                final_output = os.path.join(self.output_dir, f"{base}.{suffix}.srt")
                self.resolution_info.emit(base_name, "N/A (SRT字幕)", "N/A (SRT字幕)")
            else:  # ASS格式
                final_output = os.path.join(self.output_dir, f"{base}.{suffix}.ass")

            file_existed = os.path.exists(final_output)
            
            # 处理字幕文件
            if sub_format == 'ass':
                success = self.process_ass(temp_sub, None if self._read_only_mode else final_output)
            else:  # SRT格式处理
                try:
                    if not self._read_only_mode:
                        # 先删除已存在的文件（如果存在）
                        if os.path.exists(final_output):
                            os.remove(final_output)
                        # 然后移动临时文件到目标位置
                        os.rename(temp_sub, final_output)
                    success = True
                except Exception as e:
                    self.log_message.emit(f"SRT文件处理错误: {str(e)}")
                    success = False
            
            if success:
                if self._read_only_mode:
                    self.log_message.emit(f"✓ 已读取分辨率: {base_name}")
                elif file_existed:
                    self.log_message.emit(f"▶ 覆盖：{base_name}（轨道{self.track_id}，{sub_format.upper()}格式）")
                else:
                    self.log_message.emit(f"✓ 成功：{base_name}（轨道{self.track_id}，{sub_format.upper()}格式）")
            else:
                self.log_message.emit(f"× 失败：{base_name}（字幕处理错误）")
                
        except subprocess.CalledProcessError:
            self.log_message.emit(f"× 失败：{base_name}（轨道{self.track_id}不存在或无字幕轨道）")
        except Exception as e:
            self.log_message.emit(f"× 失败：{base_name}（{str(e)}）")
        finally:
            # 清理临时目录
            if os.path.exists(temp_dir):
                rmtree(temp_dir)

    def process_external_ass(self, ass_path):
        """
        处理独立的ASS字幕文件
        :param ass_path: ASS文件路径
        """
        base_name = os.path.basename(ass_path)
        base, ext = os.path.splitext(base_name)
        
        # 获取当前选择的语言后缀
        current_suffix = "CHS" if self.language == 'chs' else "JP"
        
        # 分析文件名中的现有后缀
        parts = base.split('.')
        
        # 检查最后一部分是否是语言后缀
        if len(parts) > 1 and parts[-1].upper() in ['CHS', 'JP']:
            existing_suffix = parts[-1].upper()
            # 如果已有语言后缀与当前选择不同，则替换
            if existing_suffix != current_suffix:
                parts[-1] = current_suffix
                new_base = '.'.join(parts)
                final_name = f"{new_base}{ext}"
            else:
                # 后缀相同，直接使用原文件名
                final_name = base_name
        else:
            # 没有语言后缀，添加新后缀
            final_name = f"{base}.{current_suffix}{ext}"
        
        final_output = None if self._read_only_mode else os.path.join(self.output_dir, final_name)
        
        try:
            file_existed = False if self._read_only_mode else os.path.exists(final_output)
            
            if self.process_ass(ass_path, final_output):
                if self._read_only_mode:
                    self.log_message.emit(f"✓ 已读取分辨率: {base_name}")
                elif file_existed:
                    self.log_message.emit(f"▶ 覆盖：{final_name}")
                else:
                    if final_name != base_name:
                        self.log_message.emit(f"✓ 成功：{base_name} -> {final_name}")
                    else:
                        self.log_message.emit(f"✓ 成功：{base_name}（保持原后缀）")
            else:
                self.log_message.emit(f"× 失败：{base_name}（字幕处理错误）")
                
        except Exception as e:
            self.log_message.emit(f"× 失败：{base_name}（{str(e)}）")
