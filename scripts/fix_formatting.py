# -*- coding: utf-8 -*-
"""
Fix any dollar signs that were stripped by PowerShell interpolation in make_sigconf.py and sigconf (2).tex
"""
with open("scripts/make_sigconf.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix replacements
text = text.replace(r"\textbf{0.016} (.098^*$)", r"\textbf{0.016} ($0.098^*$)")
text = text.replace(r"\multicolumn{14}{@{}l}{\footnotesize *$ Giá trị cực đại", r"\multicolumn{14}{@{}l}{\footnotesize $^*$ Giá trị cực đại")
text = text.replace(r"VUS-PR trên AIOps đạt .458$ ($+0.010$ so với paper .448$), trên SMD đạt .374$ ($+0.008$ so với paper .366$), và trên UCR đạt .497$ ($+0.005$ so với paper .492$).",
                    r"VUS-PR trên AIOps đạt $0.458$ ($+0.010$ so với paper $0.448$), trên SMD đạt $0.374$ ($+0.008$ so với paper $0.366$), và trên UCR đạt $0.497$ ($+0.005$ so với paper $0.492$).")
text = text.replace(r"trung bình .826$ và Range-AUC-PR đạt .500$", r"trung bình $0.826$ và Range-AUC-PR đạt $0.500$")

with open("scripts/make_sigconf.py", "w", encoding="utf-8") as f:
    f.write(text)

with open("sigconf (2).tex", "r", encoding="utf-8") as f:
    tex = f.read()

tex = tex.replace(r"\textbf{0.016} (.098^*$)", r"\textbf{0.016} ($0.098^*$)")
tex = tex.replace(r"\multicolumn{14}{@{}l}{\footnotesize *$ Giá trị cực đại", r"\multicolumn{14}{@{}l}{\footnotesize $^*$ Giá trị cực đại")
tex = tex.replace(r"VUS-PR trên AIOps đạt .458$ ($+0.010$ so với paper .448$), trên SMD đạt .374$ ($+0.008$ so với paper .366$), và trên UCR đạt .497$ ($+0.005$ so với paper .492$).",
                  r"VUS-PR trên AIOps đạt $0.458$ ($+0.010$ so với paper $0.448$), trên SMD đạt $0.374$ ($+0.008$ so với paper $0.366$), và trên UCR đạt $0.497$ ($+0.005$ so với paper $0.492$).")
tex = tex.replace(r"trung bình .826$ và Range-AUC-PR đạt .500$", r"trung bình $0.826$ và Range-AUC-PR đạt $0.500$")

with open("sigconf (2).tex", "w", encoding="utf-8") as f:
    f.write(tex)

print("Fixed formatting successfully!")
