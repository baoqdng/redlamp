# -*- coding: utf-8 -*-
"""
Script to format all tables in sigconf (2).tex:
- Long/wide tables with lots of content span across the entire page (table*) with \textwidth,
  reducing font size (\footnotesize or \scriptsize) to fit layout perfectly.
- Small/compact tables fit within a single column (table) with \columnwidth (\footnotesize).
"""

with open("sigconf (2).tex", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Table 1: tab:contributions (Small -> Fit in column)
old_t1 = r"""\begin{table}[h]
\centering
\caption{Tổng hợp các đóng góp cốt lõi của đề tài}
\label{tab:contributions}
\small
\begin{tabularx}{\columnwidth}{clX}"""

new_t1 = r"""\begin{table}[htbp]
\centering
\caption{Tổng hợp các đóng góp cốt lõi của đề tài}
\label{tab:contributions}
\footnotesize
\begin{tabularx}{\columnwidth}{clX}"""

assert old_t1 in text, "old_t1 not found!"
text = text.replace(old_t1, new_t1)

# 2. Table 2: tab:method_comparison (Wide, 6 columns with long text -> Span across page table* with resizebox textwidth)
old_t2 = r"""\begin{table*}[t]
\centering
\caption{So sánh tổng quan giữa RedLamp và các phương pháp phát hiện bất thường tiêu biểu}
\label{tab:method_comparison}
\small
\begin{tabular}{lccccc}
\toprule
\textbf{Tiêu chí} & \textbf{Isolation Forest} & \textbf{LSTM-VAE / AT} & \textbf{NCAD / COUTA} & \textbf{CutAddPaste} & \textbf{RedLamp} \\
\midrule
Giả định nền tảng & Phân tách cây & Tính bình thường & Bất thường nhị phân & Bất thường nhị phân & \textbf{Bất thường đa lớp} \\
Khai thác tương quan thời gian & Kém & Rất tốt & Tốt & Tốt & \textbf{Rất tốt (1D-CNN)} \\
Đa dạng bất thường giả lập & Không & Không & Thấp & Trung bình (gộp nhị phân) & \textbf{Cao (11 lớp tách biệt)} \\
Giải quyết Diversity gap & N/A & N/A & Không & Một phần & \textbf{Giải quyết triệt để} \\
Xử lý False anomaly (FAA) & N/A & N/A & Không & Không & \textbf{Có (Lọc lớp nền FAA)} \\
Chống Overconfidence & N/A & N/A & Không & Không & \textbf{Có (Soft Labels BC)} \\
Tính giải thích không gian ẩn & Thấp & Thấp & Thấp & Thấp (nhị phân) & \textbf{Cao (Phân cụm 12 lớp)} \\
Tốc độ suy luận & Nhanh & Chậm ($\mathcal{O}(L^2)$ với AT) & Trung bình & Trung bình & \textbf{Nhanh ($<10\text{ms}$/cửa sổ)} \\
Độ giảm VUS-PR (ô nhiễm 5\%) & Kém & Giảm mạnh ($\sim 16\%$) & Kém & Giảm 15,5\% & \textbf{Giảm chỉ 1,8\%} \\
\bottomrule
\end{tabular}
\end{table*}"""

new_t2 = r"""\begin{table*}[t]
\centering
\caption{So sánh tổng quan giữa RedLamp và các phương pháp phát hiện bất thường tiêu biểu}
\label{tab:method_comparison}
\footnotesize
\resizebox{\textwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\textbf{Tiêu chí} & \textbf{Isolation Forest} & \textbf{LSTM-VAE / AT} & \textbf{NCAD / COUTA} & \textbf{CutAddPaste} & \textbf{RedLamp} \\
\midrule
Giả định nền tảng & Phân tách cây & Tính bình thường & Bất thường nhị phân & Bất thường nhị phân & \textbf{Bất thường đa lớp} \\
Khai thác tương quan thời gian & Kém & Rất tốt & Tốt & Tốt & \textbf{Rất tốt (1D-CNN)} \\
Đa dạng bất thường giả lập & Không & Không & Thấp & Trung bình (gộp nhị phân) & \textbf{Cao (11 lớp tách biệt)} \\
Giải quyết Diversity gap & N/A & N/A & Không & Một phần & \textbf{Giải quyết triệt để} \\
Xử lý False anomaly (FAA) & N/A & N/A & Không & Không & \textbf{Có (Lọc lớp nền FAA)} \\
Chống Overconfidence & N/A & N/A & Không & Không & \textbf{Có (Soft Labels BC)} \\
Tính giải thích không gian ẩn & Thấp & Thấp & Thấp & Thấp (nhị phân) & \textbf{Cao (Phân cụm 12 lớp)} \\
Tốc độ suy luận & Nhanh & Chậm ($\mathcal{O}(L^2)$ với AT) & Trung bình & Trung bình & \textbf{Nhanh ($<10\text{ms}$/cửa sổ)} \\
Độ giảm VUS-PR (ô nhiễm 5\%) & Kém & Giảm mạnh ($\sim 16\%$) & Kém & Giảm 15,5\% & \textbf{Giảm chỉ 1,8\%} \\
\bottomrule
\end{tabular}%
}
\end{table*}"""

assert old_t2 in text, "old_t2 not found!"
text = text.replace(old_t2, new_t2)

# 3. Table 3: tab:convaec_architecture (Detailed 18 rows -> Span across page table* with \footnotesize)
old_t3_header = r"""\begin{table*}[t]
\centering
\caption{Đặc tả chi tiết các tầng mạng của kiến trúc ConvAEC trong mã nguồn \texttt{models/cnn.py}}
\label{tab:convaec_architecture}
\small
\begin{tabularx}{\textwidth}{lllccl}"""

new_t3_header = r"""\begin{table*}[t]
\centering
\caption{Đặc tả chi tiết các tầng mạng của kiến trúc ConvAEC trong mã nguồn \texttt{models/cnn.py}}
\label{tab:convaec_architecture}
\footnotesize
\begin{tabularx}{\textwidth}{lllccl}"""

assert old_t3_header in text, "old_t3_header not found!"
text = text.replace(old_t3_header, new_t3_header)

# 4. Table 4: tab:augmentations (12 rows of math -> Span across page table* with \footnotesize)
old_t4_header = r"""\begin{table*}[t]
\centering
\caption{Danh mục và định nghĩa toán học của 12 phép biến đổi giả lập bất thường trong RedLamp (mã nguồn \texttt{loaders/loader\_aug.py})}
\label{tab:augmentations}
\small
\begin{tabularx}{\textwidth}{clXX}"""

new_t4_header = r"""\begin{table*}[t]
\centering
\caption{Danh mục và định nghĩa toán học của 12 phép biến đổi giả lập bất thường trong RedLamp (mã nguồn \texttt{loaders/loader\_aug.py})}
\label{tab:augmentations}
\footnotesize
\begin{tabularx}{\textwidth}{clXX}"""

assert old_t4_header in text, "old_t4_header not found!"
text = text.replace(old_t4_header, new_t4_header)

# 5. Table 5: tab:infra (Small -> Fit in column table[htbp] with \footnotesize)
old_t5 = r"""\begin{table}[h]
\centering
\caption{So sánh cấu hình môi trường huấn luyện Kaggle và hệ thống cục bộ}
\label{tab:infra}
\small
\resizebox{\columnwidth}{!}{%"""

new_t5 = r"""\begin{table}[htbp]
\centering
\caption{So sánh cấu hình môi trường huấn luyện Kaggle và hệ thống cục bộ}
\label{tab:infra}
\footnotesize
\resizebox{\columnwidth}{!}{%"""

assert old_t5 in text, "old_t5 not found!"
text = text.replace(old_t5, new_t5)

# 6. Table 6: tab:dataset_stats (7 columns wide -> Span across page table* with \footnotesize)
old_t6 = r"""\begin{table*}[t]
\centering
\caption{Thống kê chi tiết các tập dữ liệu thực nghiệm kiểm chuẩn (trung bình trên mỗi chuỗi con)}
\label{tab:dataset_stats}
\small
\resizebox{\textwidth}{!}{%"""

new_t6 = r"""\begin{table*}[t]
\centering
\caption{Thống kê chi tiết các tập dữ liệu thực nghiệm kiểm chuẩn (trung bình trên mỗi chuỗi con)}
\label{tab:dataset_stats}
\footnotesize
\resizebox{\textwidth}{!}{%"""

assert old_t6 in text, "old_t6 not found!"
text = text.replace(old_t6, new_t6)

# 7. Table 7: tab:hyperparams (18 rows explanations -> Span across page table* with \footnotesize)
old_t7_header = r"""\begin{table*}[t]
\centering
\caption{Bảng siêu tham số và cấu hình kiến trúc mô hình ConvAEC (áp dụng đồng nhất trên mọi tập dữ liệu)}
\label{tab:hyperparams}
\small
\begin{tabularx}{\textwidth}{llX}"""

new_t7_header = r"""\begin{table*}[t]
\centering
\caption{Bảng siêu tham số và cấu hình kiến trúc mô hình ConvAEC (áp dụng đồng nhất trên mọi tập dữ liệu)}
\label{tab:hyperparams}
\footnotesize
\begin{tabularx}{\textwidth}{llX}"""

assert old_t7_header in text, "old_t7_header not found!"
text = text.replace(old_t7_header, new_t7_header)

# 8. Table 8: tab:training_stats (7 columns wide -> Span across page table* with \footnotesize and \resizebox{\textwidth}{!})
old_t8 = r"""\begin{table*}[t]
\centering
\caption{Thống kê thời gian huấn luyện, số epoch hội tụ và tài nguyên tính toán trên Kaggle GPU Nvidia Tesla P100}
\label{tab:training_stats}
\small
\begin{tabular}{lcccccc}
\toprule
\textbf{Tập dữ liệu} & \textbf{Số kênh ($D$)} & \textbf{Số mẫu Train gốc} & \textbf{Thời gian / 1 Epoch} & \textbf{Epoch hội tụ (Best Val)} & \textbf{Epoch dừng sớm} & \textbf{Tổng thời gian} \\
\midrule
TSB-AD Stock (149\_Stock\_id\_1) & 1 & 500 & \textbf{0.36 giây} & \textbf{Epoch 26} & Epoch 36 & \textbf{12.83 giây} \\
TSB-AD Stock (150\_Stock\_id\_2) & 1 & 500 & \textbf{0.34 giây} & \textbf{Epoch 17} & Epoch 27 & \textbf{9.06 giây} \\
TSB-AD Stock (Trung bình 20 chuỗi) & 1 & $\sim 500$ & \textbf{0.35 giây} & \textbf{Epoch 22} & Epoch 32 & \textbf{11.20 giây} \\
UCR Archive (Trung bình 1 chuỗi) & 1 & $\le 10,000$ & 2.10 giây & Epoch 38 & Epoch 48 & $\sim 1.5$ phút \\
AIOps / IOPS KPI & 1 & $\sim 10,358$ & 8.50 giây & Epoch 28 & Epoch 38 & $\sim 5.4$ phút \\
SMD (machine-1-1) & 38 & 12,500 & 2.94 giây & Epoch 45 & Epoch 55 & $\sim 2.7$ phút \\
NASA SMAP & 25 & 13,760 & 1.20 giây & Epoch 52 & Epoch 62 & $\sim 1.3$ phút \\
NASA MSL & 55 & 5,543 & 0.80 giây & Epoch 64 & Epoch 74 & $\sim 1.0$ phút \\
\bottomrule
\end{tabular}
\end{table*}"""

new_t8 = r"""\begin{table*}[t]
\centering
\caption{Thống kê thời gian huấn luyện, số epoch hội tụ và tài nguyên tính toán trên Kaggle GPU Nvidia Tesla P100}
\label{tab:training_stats}
\footnotesize
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
\textbf{Tập dữ liệu} & \textbf{Số kênh ($D$)} & \textbf{Số mẫu Train gốc} & \textbf{Thời gian / 1 Epoch} & \textbf{Epoch hội tụ (Best Val)} & \textbf{Epoch dừng sớm} & \textbf{Tổng thời gian} \\
\midrule
TSB-AD Stock (149\_Stock\_id\_1) & 1 & 500 & \textbf{0.36 giây} & \textbf{Epoch 26} & Epoch 36 & \textbf{12.83 giây} \\
TSB-AD Stock (150\_Stock\_id\_2) & 1 & 500 & \textbf{0.34 giây} & \textbf{Epoch 17} & Epoch 27 & \textbf{9.06 giây} \\
TSB-AD Stock (Trung bình 20 chuỗi) & 1 & $\sim 500$ & \textbf{0.35 giây} & \textbf{Epoch 22} & Epoch 32 & \textbf{11.20 giây} \\
UCR Archive (Trung bình 1 chuỗi) & 1 & $\le 10,000$ & 2.10 giây & Epoch 38 & Epoch 48 & $\sim 1.5$ phút \\
AIOps / IOPS KPI & 1 & $\sim 10,358$ & 8.50 giây & Epoch 28 & Epoch 38 & $\sim 5.4$ phút \\
SMD (machine-1-1) & 38 & 12,500 & 2.94 giây & Epoch 45 & Epoch 55 & $\sim 2.7$ phút \\
NASA SMAP & 25 & 13,760 & 1.20 giây & Epoch 52 & Epoch 62 & $\sim 1.3$ phút \\
NASA MSL & 55 & 5,543 & 0.80 giây & Epoch 64 & Epoch 74 & $\sim 1.0$ phút \\
\bottomrule
\end{tabular}%
}
\end{table*}"""

assert old_t8 in text, "old_t8 not found!"
text = text.replace(old_t8, new_t8)

# 9. Table 9: tab:benchmark_results (13 columns wide -> Span across page table* with \scriptsize and \setlength{\tabcolsep}{3pt})
old_t9_top = r"""\begin{table*}[t]
\centering
\caption{Đối chiếu kết quả thực nghiệm chi tiết giữa RedLamp công bố trong bài báo gốc (Paper) và RedLamp tự chạy lại trên 1 seed duy nhất (Ours Reproduction, seed=0)}
\label{tab:benchmark_results}
\small
\resizebox{\textwidth}{!}{%"""

new_t9_top = r"""\begin{table*}[t]
\centering
\caption{Đối chiếu kết quả thực nghiệm chi tiết giữa RedLamp công bố trong bài báo gốc (Paper) và RedLamp tự chạy lại trên 1 seed duy nhất (Ours Reproduction, seed=0)}
\label{tab:benchmark_results}
\scriptsize
\setlength{\tabcolsep}{3.5pt}
\resizebox{\textwidth}{!}{%"""

assert old_t9_top in text, "old_t9_top not found!"
text = text.replace(old_t9_top, new_t9_top)

# 10. Table 10: tab:stock_baselines (Small -> Fit in column table[htbp] with \footnotesize)
old_t10 = r"""\begin{table}[h]
\centering
\caption{Bảng đối sánh hiệu năng giữa RedLamp và các mô hình Baseline trên bộ dữ liệu tài chính Stock (TSB-AD-U Finance)}
\label{tab:stock_baselines}
\small
\resizebox{\columnwidth}{!}{%"""

new_t10 = r"""\begin{table}[htbp]
\centering
\caption{Bảng đối sánh hiệu năng giữa RedLamp và các mô hình Baseline trên bộ dữ liệu tài chính Stock (TSB-AD-U Finance)}
\label{tab:stock_baselines}
\footnotesize
\resizebox{\columnwidth}{!}{%"""

assert old_t10 in text, "old_t10 not found!"
text = text.replace(old_t10, new_t10)

# 11. Table 11: tab:stock_detailed (22 rows x 7 cols -> Span across page table* with \footnotesize and \resizebox{\textwidth}{!})
old_t11 = r"""\begin{table*}[t]
\centering
\caption{Kết quả thực nghiệm chi tiết của nhóm trên 20 chuỗi tài chính Stock (TSB-AD-U Finance) trích xuất từ \texttt{metrics/stock.csv}}
\label{tab:stock_detailed}
\small
\begin{tabular}{lcccccc}
\toprule
\textbf{Thực thể (Entity)} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{Range-F1 (RF)} & \textbf{RF (oracle)} & \textbf{R-AUC-ROC} & \textbf{R-AUC-PR} \\
\midrule
149\_Stock\_id\_1 & 0.8962 & 0.8071 & 0.0167 & 0.0837 & 0.9021 & 0.8245 \\
150\_Stock\_id\_2 & 0.9507 & 0.9299 & 0.0138 & 0.1121 & 0.9568 & 0.9382 \\
151\_Stock\_id\_3 & 0.8873 & 0.8148 & 0.0311 & 0.0954 & 0.9284 & 0.8912 \\
152\_Stock\_id\_4 & 0.9516 & 0.9302 & 0.0247 & 0.0892 & 0.9145 & 0.8654 \\
153\_Stock\_id\_5 & 0.8769 & 0.7861 & 0.0181 & 0.1045 & 0.9392 & 0.9021 \\
154\_Stock\_id\_6 & 0.8928 & 0.8020 & 0.0236 & 0.0921 & 0.9214 & 0.8754 \\
155\_Stock\_id\_7 & 0.8986 & 0.8083 & 0.0156 & 0.0789 & 0.8954 & 0.8251 \\
156\_Stock\_id\_8 & 0.8865 & 0.8029 & 0.0000 & 0.1184 & 0.9485 & 0.9214 \\
157\_Stock\_id\_9 & 0.9508 & 0.9293 & 0.0097 & 0.0998 & 0.9312 & 0.8945 \\
158\_Stock\_id\_10 & 0.8900 & 0.7959 & 0.0131 & 0.0874 & 0.9174 & 0.8687 \\
159\_Stock\_id\_11 & 0.9503 & 0.9273 & 0.0236 & 0.1092 & 0.9442 & 0.9142 \\
160\_Stock\_id\_12 & 0.8931 & 0.7947 & 0.0086 & 0.0815 & 0.9102 & 0.8542 \\
161\_Stock\_id\_13 & 0.8814 & 0.7969 & 0.0229 & 0.1021 & 0.9354 & 0.9012 \\
162\_Stock\_id\_14 & 0.9473 & 0.9246 & 0.0153 & 0.0945 & 0.9241 & 0.8821 \\
163\_Stock\_id\_15 & 0.9491 & 0.9272 & 0.0077 & 0.1215 & 0.9512 & 0.9284 \\
164\_Stock\_id\_16 & 0.9501 & 0.9281 & 0.0258 & 0.0845 & 0.9042 & 0.8354 \\
165\_Stock\_id\_17 & 0.9507 & 0.9286 & 0.0146 & 0.1054 & 0.9374 & 0.9054 \\
166\_Stock\_id\_18 & 0.9494 & 0.9240 & 0.0161 & 0.0912 & 0.9201 & 0.8742 \\
167\_Stock\_id\_19 & 0.8859 & 0.7947 & 0.0000 & 0.0974 & 0.9285 & 0.8895 \\
168\_Stock\_id\_20 & 0.9507 & 0.9319 & 0.0168 & 0.1084 & 0.9421 & 0.9112 \\
\midrule
\textbf{Trung bình (Mean)} & \textbf{0.9195} & \textbf{0.8642} & \textbf{0.0159} & \textbf{0.0978} & \textbf{0.9254} & \textbf{0.8821} \\
\bottomrule
\end{tabular}
\end{table*}"""

new_t11 = r"""\begin{table*}[t]
\centering
\caption{Kết quả thực nghiệm chi tiết của nhóm trên 20 chuỗi tài chính Stock (TSB-AD-U Finance) trích xuất từ \texttt{metrics/stock.csv}}
\label{tab:stock_detailed}
\footnotesize
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
\textbf{Thực thể (Entity)} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{Range-F1 (RF)} & \textbf{RF (oracle)} & \textbf{R-AUC-ROC} & \textbf{R-AUC-PR} \\
\midrule
149\_Stock\_id\_1 & 0.8962 & 0.8071 & 0.0167 & 0.0837 & 0.9021 & 0.8245 \\
150\_Stock\_id\_2 & 0.9507 & 0.9299 & 0.0138 & 0.1121 & 0.9568 & 0.9382 \\
151\_Stock\_id\_3 & 0.8873 & 0.8148 & 0.0311 & 0.0954 & 0.9284 & 0.8912 \\
152\_Stock\_id\_4 & 0.9516 & 0.9302 & 0.0247 & 0.0892 & 0.9145 & 0.8654 \\
153\_Stock\_id\_5 & 0.8769 & 0.7861 & 0.0181 & 0.1045 & 0.9392 & 0.9021 \\
154\_Stock\_id\_6 & 0.8928 & 0.8020 & 0.0236 & 0.0921 & 0.9214 & 0.8754 \\
155\_Stock\_id\_7 & 0.8986 & 0.8083 & 0.0156 & 0.0789 & 0.8954 & 0.8251 \\
156\_Stock\_id\_8 & 0.8865 & 0.8029 & 0.0000 & 0.1184 & 0.9485 & 0.9214 \\
157\_Stock\_id\_9 & 0.9508 & 0.9293 & 0.0097 & 0.0998 & 0.9312 & 0.8945 \\
158\_Stock\_id\_10 & 0.8900 & 0.7959 & 0.0131 & 0.0874 & 0.9174 & 0.8687 \\
159\_Stock\_id\_11 & 0.9503 & 0.9273 & 0.0236 & 0.1092 & 0.9442 & 0.9142 \\
160\_Stock\_id\_12 & 0.8931 & 0.7947 & 0.0086 & 0.0815 & 0.9102 & 0.8542 \\
161\_Stock\_id\_13 & 0.8814 & 0.7969 & 0.0229 & 0.1021 & 0.9354 & 0.9012 \\
162\_Stock\_id\_14 & 0.9473 & 0.9246 & 0.0153 & 0.0945 & 0.9241 & 0.8821 \\
163\_Stock\_id\_15 & 0.9491 & 0.9272 & 0.0077 & 0.1215 & 0.9512 & 0.9284 \\
164\_Stock\_id\_16 & 0.9501 & 0.9281 & 0.0258 & 0.0845 & 0.9042 & 0.8354 \\
165\_Stock\_id\_17 & 0.9507 & 0.9286 & 0.0146 & 0.1054 & 0.9374 & 0.9054 \\
166\_Stock\_id\_18 & 0.9494 & 0.9240 & 0.0161 & 0.0912 & 0.9201 & 0.8742 \\
167\_Stock\_id\_19 & 0.8859 & 0.7947 & 0.0000 & 0.0974 & 0.9285 & 0.8895 \\
168\_Stock\_id\_20 & 0.9507 & 0.9319 & 0.0168 & 0.1084 & 0.9421 & 0.9112 \\
\midrule
\textbf{Trung bình (Mean)} & \textbf{0.9195} & \textbf{0.8642} & \textbf{0.0159} & \textbf{0.0978} & \textbf{0.9254} & \textbf{0.8821} \\
\bottomrule
\end{tabular}%
}
\end{table*}"""

assert old_t11 in text, "old_t11 not found!"
text = text.replace(old_t11, new_t11)

# 12. Table 12: tab:ablation (Small -> Fit in column table[htbp] with \footnotesize)
old_t12 = r"""\begin{table}[h]
\centering
\caption{Kết quả nghiên cứu triệt tiêu (Ablation Study) trên hai tập UCR và SMD theo chỉ số VUS-PR}
\label{tab:ablation}
\small
\resizebox{\columnwidth}{!}{%"""

new_t12 = r"""\begin{table}[htbp]
\centering
\caption{Kết quả nghiên cứu triệt tiêu (Ablation Study) trên hai tập UCR và SMD theo chỉ số VUS-PR}
\label{tab:ablation}
\footnotesize
\resizebox{\columnwidth}{!}{%"""

assert old_t12 in text, "old_t12 not found!"
text = text.replace(old_t12, new_t12)

# 13. Table 13: tab:contamination (Small -> Fit in column table[htbp] with \footnotesize)
old_t13 = r"""\begin{table}[h]
\centering
\caption{Tỷ lệ suy giảm VUS-PR (\%) trên tập UCR khi tăng mức độ ô nhiễm dữ liệu huấn luyện}
\label{tab:contamination}
\small
\resizebox{\columnwidth}{!}{%"""

new_t13 = r"""\begin{table}[htbp]
\centering
\caption{Tỷ lệ suy giảm VUS-PR (\%) trên tập UCR khi tăng mức độ ô nhiễm dữ liệu huấn luyện}
\label{tab:contamination}
\footnotesize
\resizebox{\columnwidth}{!}{%"""

assert old_t13 in text, "old_t13 not found!"
text = text.replace(old_t13, new_t13)

# 14. Table 14: tab:web_blocks (Small -> Fit in column table[htbp] with \footnotesize)
old_t14 = r"""\begin{table}[h]
\centering
\caption{Danh sách 10 khối trực quan hóa tương tác trên Web Demo}
\label{tab:web_blocks}
\small
\begin{tabularx}{\columnwidth}{clX}"""

new_t14 = r"""\begin{table}[htbp]
\centering
\caption{Danh sách 10 khối trực quan hóa tương tác trên Web Demo}
\label{tab:web_blocks}
\footnotesize
\begin{tabularx}{\columnwidth}{clX}"""

assert old_t14 in text, "old_t14 not found!"
text = text.replace(old_t14, new_t14)

with open("sigconf (2).tex", "w", encoding="utf-8") as f:
    f.write(text)

with open("scripts/make_sigconf.py", "w", encoding="utf-8") as f:
    f.write(f'# -*- coding: utf-8 -*-\ncontent = r"""{text}"""\nwith open("sigconf (2).tex", "w", encoding="utf-8") as f:\n    f.write(content)\n')

print("All 14 tables formatted and saved successfully!")
