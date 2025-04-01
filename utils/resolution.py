import re
import os
from PySide6.QtCore import QObject, Signal

class ResolutionExtractor(QObject):
    resolution_extracted = Signal(str, str, str)

    def extract_from_ass(self, filepath):
        """从ASS文件中提取分辨率信息"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            play_res_x = play_res_y = "N/A"
            
            res_x_match = re.search(r"PlayResX\s*:\s*(\d+)", content)
            res_y_match = re.search(r"PlayResY\s*:\s*(\d+)", content)
            
            if res_x_match:
                play_res_x = res_x_match.group(1)
            if res_y_match:
                play_res_y = res_y_match.group(1)
                
            filename = os.path.basename(filepath)
            self.resolution_extracted.emit(filename, play_res_x, play_res_y)
            return play_res_x, play_res_y
            
        except Exception as e:
            print(f"Error extracting resolution: {str(e)}")
            return "N/A", "N/A"