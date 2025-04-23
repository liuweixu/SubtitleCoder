import os
from PySide6.QtCore import QThread, Signal
from .alignSubtitles import *
from pathlib import Path

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
                """
                emit功能
                - 发射信号：将字符串格式的日志信息 (如对齐成功/失败消息) 推送至Qt事件队列
                - 线程安全: 通过Qt的跨线程通信机制, 实现工作线程与主线程的安全交互
                """
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