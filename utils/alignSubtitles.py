import os
import subprocess
from pathlib import Path

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

# def main():
#     """主函数"""
#     jp_dir = input("请输入日文字幕文件夹路径: ")
#     cn_dir = input("请输入中文字幕文件夹路径: ")
#     jp_ext = input("请输入日文字幕文件后缀(如.srt或.jp.srt): ")
#     cn_ext = input("请输入中文字幕文件后缀(如.ass或.sc.ass或.srt): ")
#     output_dir = input("请输入输出文件夹路径: ")
    
#     os.makedirs(output_dir, exist_ok=True)
#     pairs = find_matching_pairs(jp_dir, cn_dir, jp_ext, cn_ext)
#     failed_files = []
    
#     for jp_file, cn_file in pairs:
#         jp_path = os.path.join(jp_dir, jp_file)
#         cn_path = os.path.join(cn_dir, cn_file)
#         output_path = os.path.join(output_dir, jp_file)
        
#         # 如果中文是ASS格式，先转换为SRT临时文件
#         if cn_file.endswith('.ass'):
#             temp_srt = Path(cn_path).with_suffix('.temp.srt')
#             convert_ass_to_srt(cn_path, temp_srt)
#             cn_ref_path = temp_srt
#         else:
#             cn_ref_path = cn_path
        
#         try:
#             align_subtitles(jp_path, cn_ref_path, output_path)
#             print(f"成功对齐: {jp_file} 和 {cn_file}")
#         except subprocess.CalledProcessError as e:
#             print(f"对齐失败: {jp_file} 和 {cn_file}, 错误: {e}")
#             failed_files.append(jp_file)
#         finally:
#             # 删除临时SRT文件
#             if cn_file.endswith('.ass') and os.path.exists(temp_srt):
#                 os.remove(temp_srt)
    
#     if failed_files:
#         print("\n以下文件对齐失败:")
#         for file in failed_files:
#             print(f"- {file}")

# if __name__ == "__main__":
#     main()