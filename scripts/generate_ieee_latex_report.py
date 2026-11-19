# -*- coding: utf-8 -*-
"""
Kịch bản tự động lắp ráp và sinh Báo cáo Đề tài RedLamp quy chuẩn học thuật IEEE (~40 trang A4)
viết hoàn toàn bằng TIẾNG VIỆT, tên giảng viên và học viên để trống theo yêu cầu.
Đồng bộ ghi vào cả hai tệp:
1. D:\\repo\\redlamp\\conference_101719.tex
2. D:\\repo\\redlamp\\Bao_Cao_De_Tai_RedLamp_IEEE_40Trang.tex
và sao lưu vào Artifact directory.
"""

import os
import sys

# Đảm bảo import được các module từ thư mục scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from latex_generator_parts import LATEX_PREAMBLE, FRONTMATTER_LATEX
from latex_ch1_ch2 import CHAPTER_1_LATEX, CHAPTER_2_LATEX
from latex_ch3_ch4 import CHAPTER_3_LATEX, CHAPTER_4_LATEX
from latex_ch5_ch6_ch7 import CHAPTER_5_LATEX, CHAPTER_6_LATEX, CHAPTER_7_AND_BACKMATTER_LATEX

def assemble_latex():
    sections = [
        LATEX_PREAMBLE,
        FRONTMATTER_LATEX,
        CHAPTER_1_LATEX,
        CHAPTER_2_LATEX,
        CHAPTER_3_LATEX,
        CHAPTER_4_LATEX,
        CHAPTER_5_LATEX,
        CHAPTER_6_LATEX,
        CHAPTER_7_AND_BACKMATTER_LATEX
    ]
    return "\n\n".join(sections)

def main():
    print("=========================================================================")
    print("   SINH BÁO CÁO HỌC THUẬT REDLAMP TIẾNG VIỆT (~40 TRANG) CHUẨN IEEE      ")
    print("   TÊN GIẢNG VIÊN VÀ HỌC VIÊN BỎ TRỐNG THEO YÊU CẦU                      ")
    print("=========================================================================")
    
    latex_content = assemble_latex()
    
    targets = [
        r"D:\repo\redlamp\conference_101719.tex",
        r"D:\repo\redlamp\Bao_Cao_De_Tai_RedLamp_IEEE_40Trang.tex",
        r"C:\Users\Admin\.gemini\antigravity\brain\d03213b0-b0d2-4eb1-97e0-8bfec6404e33\conference_101719.tex",
        r"C:\Users\Admin\.gemini\antigravity\brain\d03213b0-b0d2-4eb1-97e0-8bfec6404e33\Bao_Cao_De_Tai_RedLamp_IEEE_40Trang.tex"
    ]
    
    for path in targets:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            print(f"[THÀNH CÔNG] Đã ghi tệp tại: {path}")
        except Exception as e:
            print(f"[CẢNH BÁO] Không thể ghi {path}: {e}")
        
    lines = latex_content.splitlines()
    words = latex_content.split()
    chars = len(latex_content)
    
    print("-------------------------------------------------------------------------")
    print(f"Tổng số dòng LaTeX  : {len(lines):,} dòng")
    print(f"Tổng số từ văn bản : {len(words):,} từ")
    print(f"Tổng số ký tự       : {chars:,} ký tự")
    print(f"Ước tính số trang PDF (One-column, 11pt, 1.25 spacing, Math/Tables): ~{len(words)/380:.1f} - {len(words)/340:.1f} trang A4")
    print("=========================================================================")

if __name__ == '__main__':
    main()
