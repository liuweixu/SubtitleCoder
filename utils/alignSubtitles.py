import os
import subprocess

def get_base_name(filename):
    """获取不带多重后缀的基础文件名"""
    return filename.split('.')[0]

def find_matching_pairs(jp_dir, cn_dir, jp_ext, cn_ext):
    """查找日文和中文匹配的字幕文件对"""
    jp_files = [f for f in os.listdir(jp_dir) if f.endswith(jp_ext)]
    cn_files = [f for f in os.listdir(cn_dir) if f.endswith(cn_ext)]
    
    pairs = []
    for jp_file in jp_files:
        base_jp = get_base_name(jp_file)
        for cn_file in cn_files:
            base_cn = get_base_name(cn_file)
            if base_jp == base_cn:
                pairs.append((jp_file, cn_file))
                break
    return pairs

def convert_ass_to_srt(ass_path, temp_srt_path):
    """使用ffmpeg将ASS转换为SRT临时文件"""
    cmd = f'ffmpeg -i "{ass_path}" "{temp_srt_path}"'
    subprocess.run(cmd, shell=True, check=True)

def align_subtitles(jp_srt_path, cn_ref_path, output_path):
    """使用alass对齐字幕，确保中文ASS作为参考对齐日文SRT"""
    cmd = f'alass "{cn_ref_path}" "{jp_srt_path}" "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)