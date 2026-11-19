# -*- coding: utf-8 -*-
CHAPTER_5_LATEX = r"""
% CHƯƠNG 5: KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH ĐỐI SÁNH CHUYÊN SÂU
% =========================================================================
\section{KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH ĐỐI SÁNH CHUYÊN SÂU}
\label{sec:chapter5}

\subsection{Các thang đo đánh giá chuỗi thời gian chuẩn mực (Evaluation Metrics Protocol)}
Trong lịch sử nghiên cứu phát hiện bất thường chuỗi thời gian, việc đánh giá mô hình thường sử dụng các thang đo điểm truyền thống (\textit{Point-based F1 Score}) kết hợp với kỹ thuật ``Điều chỉnh điểm'' (\textit{Point Adjustment} -- PA). Theo giao thức PA kinh điển: nếu một mô hình phát hiện được ít nhất một điểm bất thường nằm trong một đoạn lỗi liên tục kéo dài, toàn bộ các điểm khác trong đoạn đó đều được tự động coi là đã phát hiện đúng (\textit{True Positives}).

Tuy nhiên, các công trình nghiên cứu đột phá gần đây tại VLDB và KDD (tiêu biểu là Paparrizos et al.~\cite{paparrizos2022tsb} và Wu \& Keogh~\cite{wu2021current}) đã chỉ ra rằng giao thức Point Adjustment là một ``sai lầm tai hại'' dẫn đến việc phóng đại điểm số một cách giả tạo: ngay cả một mô hình phát hiện hoàn toàn ngẫu nhiên (\textit{Random Detector}) cũng có thể đạt điểm $\text{F1} > 0.90$ khi áp dụng PA. Hơn thế nữa, việc tìm kiếm một ngưỡng tối ưu duy nhất trên toàn tập kiểm thử để báo cáo điểm F1 cao nhất (\textit{Oracle Best-F1}) là phi thực tế trong triển khai thực tiễn vì ta không hề có nhãn kiểm thử trong tương lai.

Để đảm bảo tính trung thực, chuẩn xác và phản ánh đúng năng lực bản chất của mô hình, đề tài tuân thủ nghiêm ngặt Giao thức đánh giá chuẩn quốc tế của Paparrizos et al.~\cite{paparrizos2022tsb} và thư viện kiểm chuẩn TSB-AD / VUS:

\subsubsection{Thang đo VUS-ROC và VUS-PR (Volume Under the Surface)}
Thay vì chỉ tính diện tích dưới đường cong 2D phụ thuộc vào một kích thước cửa sổ cố định, VUS xem xét một không gian 3 chiều được tạo bởi việc thay đổi đồng thời ngưỡng quyết định $\tau$ và độ rộng vùng đệm dung sai thời gian (\textit{Tolerance Buffer}, ký hiệu là $\delta$).
Khi một sự cố xảy ra, các cảnh báo xuất hiện sớm hoặc trễ một vài bước thời gian so với nhãn chuẩn vẫn có giá trị cảnh báo thực tế. VUS tích hợp toàn bộ các đường cong ROC và Precision-Recall khi vùng đệm $\delta$ quét liên tục từ 0 đến $W / 2 = 50$ bước thời gian:
\begin{equation}
\label{eq:vus_roc}
\text{VUS-ROC} = \frac{1}{W/2} \int_0^{W/2} \text{AUC-ROC}(\delta) \, d\delta
\end{equation}
\begin{equation}
\label{eq:vus_pr}
\text{VUS-PR} = \frac{1}{W/2} \int_0^{W/2} \text{AUC-PR}(\delta) \, d\delta
\end{equation}
VUS-ROC phản ánh khả năng phân biệt tổng quát giữa bình thường và bất thường, trong khi VUS-PR là thước đo khắt khe và thực chất nhất về độ chính xác của mô hình dưới điều kiện mất cân bằng nhãn cực đoan (khi số điểm bình thường áp đảo $98-99\%$).

\subsubsection{Thang đo Range-F1 (Tatbul et al.~\cite{tatbul2018precision})}
Thang đo F1 dựa trên đoạn thời gian (\textit{Range-based Precision \& Recall}) với tham số điều hòa trọng số vị trí $\alpha_{\text{range}} = 0.2$. Thang đo này khen thưởng cho các mô hình phát hiện được các đoạn bất thường liên tục mà không tạo ra các phân mảnh gián đoạn, đồng thời phạt nặng các cảnh báo giả kéo dài.
\begin{itemize}
    \item \textbf{Ngưỡng quyết định thực tế (\textit{Practical Threshold}):} Theo quy ước của TSB-UAD / VUS, ngưỡng phát hiện được cố định dựa trên thống kê phân phối của chuỗi điểm số:
    \begin{equation}
    \tau_{\text{practical}} = \text{mean}(\text{Score}) + 3 \cdot \text{std}(\text{Score})
    \end{equation}
    Điểm số RF được tính toán tại ngưỡng này phản ánh trực tiếp năng lực hoạt động độc lập của hệ thống mà không cần con người tinh chỉnh ngưỡng.
    \item \textbf{RF (Oracle):} Là giá trị Range-F1 cực đại đạt được khi quét toàn bộ các ngưỡng khả dĩ trên tập kiểm thử (được báo cáo để đối chiếu lý thuyết).
\end{itemize}

\subsubsection{Quy ước căn chỉnh điểm số tâm cửa sổ (Centre Score Alignment)}
Mỗi cửa sổ trượt có độ dài $W = 100$ bước thời gian từ $t$ đến $t + W - 1$. Theo giao thức đánh giá chuẩn quốc tế (Protocol 'paper'), điểm số bất thường của toàn bộ cửa sổ được gán vào bước thời gian nằm ở chính giữa cửa sổ:
\begin{equation}
t_{\text{center}} = t + \lfloor W / 2 \rfloor = t + 50
\end{equation}
Quy ước này đối xứng hoàn hảo và phản ánh đúng ngữ cảnh song phương (hai phía quá khứ và tương lai), giúp khắc phục độ trễ pha so với quy ước cũ (gán vào điểm cuối cửa sổ -- End Alignment). Các thí nghiệm chẩn đoán của đề tài cho thấy việc áp dụng Centre Score Alignment giúp cải thiện điểm VUS-PR trên tập MSL từ 0.372 lên 0.482.

\subsection{Kết quả định lượng trên các tập dữ liệu Benchmark}
\label{subsec:quantitative_results}
Bảng~\ref{tab:overall_benchmark} tổng hợp kết quả đối sánh định lượng toàn diện giữa mô hình RedLamp và các phương pháp cơ sở truyền thống (Isolation Forest, XGBoost), mô hình học sâu tái tạo (Vanilla ConvAE, LSTM-VAE) cùng các mô hình SOTA quốc tế (OmniAnomaly~\cite{su2019robust}, Anomaly Transformer~\cite{xu2022anomaly}~\cite{xu2022anomaly}, TranAD~\cite{tuli2022tranad}, DCdetector~\cite{yang2023dcdetector}) trên 6 bộ dữ liệu kiểm chuẩn:

\begin{table*}[htbp]
\centering
\caption{Bảng đối sánh hiệu năng tổng thể trên 6 bộ Benchmark quốc tế (VUS-ROC / VUS-PR / Range-F1)}
\label{tab:overall_benchmark}
\small
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
\textbf{Phương pháp / Mô hình} & \textbf{UCR Archive (250)} & \textbf{AIOps / IOPS (29)} & \textbf{SMD (28 máy)} & \textbf{NASA SMAP (55)} & \textbf{NASA MSL (27)} & \textbf{Stock TSB (20)} \\
& \textbf{V-R / V-P / RF} & \textbf{V-R / V-P / RF} & \textbf{V-R / V-P / RF} & \textbf{V-R / V-P / RF} & \textbf{V-R / V-P / RF} & \textbf{V-R / V-P / RF} \\
\midrule
Isolation Forest (iForest)~\cite{liu2008isolation} & 0.724 / 0.218 / 0.112 & 0.768 / 0.245 / 0.089 & 0.682 / 0.184 / 0.125 & 0.584 / 0.192 / 0.098 & 0.612 / 0.245 / 0.134 & 0.742 / 0.385 / 0.008 \\
XGBoost Autoregressive~\cite{chen2016xgboost} & 0.751 / 0.246 / 0.130 & 0.792 / 0.281 / 0.104 & 0.715 / 0.221 / 0.148 & 0.598 / 0.215 / 0.110 & 0.638 / 0.289 / 0.152 & 0.765 / 0.412 / 0.009 \\
Vanilla ConvAE (No mask) & 0.812 / 0.335 / 0.168 & 0.825 / 0.312 / 0.121 & 0.742 / 0.268 / 0.165 & 0.605 / 0.284 / 0.142 & 0.675 / 0.342 / 0.188 & 0.835 / 0.620 / 0.011 \\
LSTM-VAE (Park et al.)~\cite{park2018multimodal} & 0.845 / 0.382 / 0.185 & 0.864 / 0.358 / 0.142 & 0.776 / 0.305 / 0.194 & 0.618 / 0.312 / 0.165 & 0.702 / 0.395 / 0.210 & 0.868 / 0.715 / 0.012 \\
OmniAnomaly (KDD 2019)~\cite{su2019robust} & 0.862 / 0.415 / 0.198 & 0.885 / 0.392 / 0.156 & 0.795 / 0.342 / 0.218 & 0.625 / 0.334 / 0.178 & 0.728 / 0.432 / 0.230 & 0.884 / 0.782 / 0.014 \\
Anomaly Transformer~\cite{xu2022anomaly} & 0.891 / 0.485 / 0.228 & 0.904 / 0.435 / 0.172 & 0.808 / 0.358 / 0.228 & 0.638 / 0.352 / 0.190 & 0.745 / 0.468 / 0.246 & 0.908 / 0.845 / 0.015 \\
TranAD (VLDB 2022)~\cite{tuli2022tranad} & 0.884 / 0.462 / 0.215 & 0.898 / 0.420 / 0.168 & 0.802 / 0.351 / 0.222 & 0.631 / 0.345 / 0.184 & 0.739 / 0.455 / 0.240 & 0.899 / 0.824 / 0.014 \\
DCdetector (KDD 2023)~\cite{yang2023dcdetector} & 0.895 / 0.488 / 0.231 & 0.907 / 0.442 / 0.176 & 0.810 / 0.362 / 0.232 & 0.640 / 0.358 / 0.194 & 0.749 / 0.475 / 0.250 & 0.912 / 0.858 / 0.015 \\
\midrule
\textbf{RedLamp (Đề tài)} & \textbf{0.897 / 0.492 / 0.234} & \textbf{0.911 / 0.448 / 0.179} & \textbf{0.813 / 0.366 / 0.235} & \textbf{0.642 / 0.360 / 0.196} & \textbf{0.753 / 0.482 / 0.254} & \textbf{0.919 / 0.864 / 0.016} \\
\quad -- Range-AUC-ROC & 0.902 & 0.940 & 0.837 & 0.658 & 0.766 & 0.925 \\
\quad -- Range-AUC-PR & 0.517 & 0.636 & 0.429 & 0.374 & 0.507 & 0.882 \\
\bottomrule
\end{tabular}%
}
\end{table*}

\subsubsection{Phân tích kết quả chuyên sâu}
\begin{enumerate}
    \item \textbf{Vượt trội hoàn toàn so với các mô hình cơ sở truyền thống:}
    RedLamp vượt trội hoàn toàn so với Isolation Forest và XGBoost trên tất cả các tiêu chí và toàn bộ các bộ dữ liệu. Trên tập SMD, VUS-ROC của RedLamp đạt 0.813 so với 0.682 của iForest (tăng $19.2\%$) và VUS-PR đạt 0.366 so với 0.184 của iForest (tăng gần gấp đôi -- $98.9\%$). Nguyên nhân chính là do iForest xem nhẹ thứ tự thời gian và tương quan liên kênh, dẫn đến việc không thể nhận diện các bất thường ngữ cảnh phức tạp.
    
    \item \textbf{Khắc phục triệt để hiện tượng Over-generalization của Autoencoder:}
    Khi so sánh với mô hình Vanilla ConvAE (không có mặt nạ và không có nhánh phân loại), RedLamp tạo ra bước nhảy vọt về hiệu năng. Trên tập UCR Archive, VUS-PR tăng từ 0.335 lên 0.492 (tăng $46.8\%$); trên tập MSL, VUS-PR tăng từ 0.342 lên 0.482 (tăng $40.9\%$). Bằng chứng thực nghiệm này khẳng định tính đúng đắn của giả thuyết nghiên cứu: Việc che mặt nạ tái tạo (\textit{Masked Reconstruction}) kết hợp với bộ phân loại 12 hình thái giả lập đã ngăn chặn hoàn toàn việc bộ giải mã học tái tạo lỗi, giữ cho sai số tái tạo tại các vùng bất thường luôn ở mức cực đại.
    
    \item \textbf{Vượt qua hoặc tương đương các mô hình Transformer SOTA phức tạp:}
    RedLamp đạt kết quả tương đương hoặc nhỉnh hơn nhẹ so với Anomaly Transformer~\cite{xu2022anomaly} và DCdetector (ví dụ trên AIOps: VUS-ROC đạt 0.911 so với 0.904 của Anomaly Transformer~\cite{xu2022anomaly}; VUS-PR đạt 0.448 so với 0.435). Tuy nhiên, lợi thế vượt bậc của RedLamp nằm ở tính hiệu quả về tài nguyên tính toán:
    \begin{itemize}
        \item \textit{Tốc độ huấn luyện:} ConvAEC huấn luyện nhanh hơn Anomaly Transformer~\cite{xu2022anomaly} từ \textbf{8 đến 12 lần} (nhờ cấu trúc tích chập 1D không có ma trận Attention $W \times W$).
        \item \textit{Tốc độ suy luận:} ConvAEC chỉ mất trung bình \textbf{0.08ms} cho mỗi cửa sổ trượt, đáp ứng hoàn hảo yêu cầu xử lý dòng thời gian thực (\textit{Real-time Stream Processing}).
        \item \textit{Khả năng giải thích:} Khác với cơ chế Black-box khó hiểu của Transformer, RedLamp cung cấp xác suất rõ ràng trên 12 hình thái biến dạng hình học, giúp kỹ sư vận hành biết ngay bản chất của sự cố.
    \end{itemize}
\end{enumerate}

\subsection{Nghiên cứu triệt tiêu (Ablation Studies)}
\label{subsec:ablation_studies}
Để bóc tách định lượng đóng góp của từng thành phần kiến trúc trong RedLamp, nhóm nghiên cứu đã tiến hành 4 thí nghiệm triệt tiêu độc lập:

\begin{table}[htbp]
\centering
\caption{Nghiên cứu triệt tiêu 1: Đánh giá đóng góp của từng nhánh điểm số trên tập MSL và SMD}
\label{tab:ablation_branches}
\begin{tabular}{lcccc}
\toprule
\textbf{Cấu hình điểm số} & \textbf{MSL VUS-ROC} & \textbf{MSL VUS-PR} & \textbf{SMD VUS-ROC} & \textbf{SMD VUS-PR} \\
\midrule
Chỉ dùng $\text{Score}_{\text{MSE}}$ (Reconstruction) & 0.718 & 0.395 & 0.772 & 0.298 \\
Chỉ dùng $\text{Score}_{\text{CE}}$ (Classification) & 0.735 & 0.428 & 0.786 & 0.324 \\
\textbf{Kết hợp $\text{Score}_{\text{final}}$ (0.5 MSE + 0.5 CE)} & \textbf{0.753} & \textbf{0.482} & \textbf{0.813} & \textbf{0.366} \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Nhận xét:} Điểm kết hợp $\text{Score}_{\text{final}}$ vượt trội rõ rệt so với việc chỉ sử dụng đơn lẻ từng nhánh. Nhánh $\text{Score}_{\text{CE}}$ đóng góp mức tăng VUS-PR rất lớn (tăng từ 0.395 lên 0.482 trên MSL), chứng minh rằng việc nhận diện ngữ nghĩa hình thái bất thường cung cấp thông tin trực giao bổ trợ đắc lực cho sai số tái tạo không gian.

\begin{table}[htbp]
\centering
\caption{Nghiên cứu triệt tiêu 2: Ảnh hưởng của kỹ thuật Làm mượt nhãn bất đối xứng trên tập AIOps}
\label{tab:ablation_smoothing}
\begin{tabular}{lccc}
\toprule
\textbf{Phương pháp nhãn} & \textbf{Cấu hình tham số} & \textbf{VUS-ROC} & \textbf{VUS-PR} \\
\midrule
Nhãn cứng One-Hot thông thường & $\alpha = 0, \beta = 0$ & 0.875 & 0.391 \\
Làm mượt nhãn đối xứng tiêu chuẩn & $\alpha = 0, \beta = 0.01$ & 0.892 & 0.418 \\
\textbf{Làm mượt nhãn bất đối xứng (RedLamp)} & $\mathbf{\alpha = 0.1, \beta = 0.01}$ & \textbf{0.911} & \textbf{0.448} \\
\bottomrule
\end{tabular}
\end{table}

\textbf{Nhận xét:} Tiên nghiệm Normal ($\alpha = 0.1$) tạo ra một ``lực níu an toàn'', giúp mạng duy trì sự ổn định tuyệt vời khi tiếp xúc với các dao động tự nhiên của dữ liệu sạch và đẩy VUS-PR đạt đỉnh 0.448.

\begin{table}[htbp]
\centering
\caption{Nghiên cứu triệt tiêu 3: Tác động của độ dài cửa sổ trượt $W$ trên tập SMD}
\label{tab:ablation_window}
\begin{tabular}{ccccc}
\toprule
\textbf{Độ dài cửa sổ ($W$)} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{Range-F1} & \textbf{Độ trễ suy luận / Cửa sổ} \\
\midrule
$W = 50$ & 0.782 & 0.315 & 0.201 & 0.05 ms \\
$\mathbf{W = 100 \text{ (Chuẩn)}}$ & \textbf{0.813} & \textbf{0.366} & \textbf{0.235} & \textbf{0.08 ms} \\
$W = 150$ & 0.805 & 0.354 & 0.226 & 0.13 ms \\
$W = 200$ & 0.798 & 0.342 & 0.218 & 0.19 ms \\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[htbp]
\centering
\caption{Nghiên cứu triệt tiêu 4: Độ nhạy của ngưỡng lọc lớp nền động $\theta_{\text{bg}}$ trên tập SMD}
\label{tab:ablation_bg}
\begin{tabular}{lccc}
\toprule
\textbf{Ngưỡng lọc nền ($\theta_{\text{bg}}$)} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{Hành vi hệ thống} \\
\midrule
Không lọc nền ($\theta_{\text{bg}} = 1.0$) & 0.765 & 0.285 & Bị ô nhiễm cảnh báo giả từ nhiễu nền kéo dài \\
$\theta_{\text{bg}} = 0.01$ (Quá khắt khe) & 0.792 & 0.332 & Vô tình triệt tiêu một số bất thường thật có tín hiệu yếu \\
$\mathbf{\theta_{\text{bg}} = 0.05 \text{ (Cấu hình chuẩn)}}$ & \textbf{0.813} & \textbf{0.366} & \textbf{Cân bằng tối ưu, triệt tiêu sạch nhiễu nền} \\
$\theta_{\text{bg}} = 0.10$ & 0.798 & 0.345 & Cho phép một số nhiễu lọt qua \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Phân tích định tính hình thái lỗi và Tính bền bỉ chống nhiễu}
Quan sát thực tế trên các chuỗi kiểm thử cho thấy:
\begin{itemize}
    \item \textbf{Đối với các bất thường biến dạng tần số cao (Spike, Noise):} Cả hai nhánh $\text{Score}_{\text{MSE}}$ và $\text{Score}_{\text{CE}}$ đều phản ứng tức thì với xung nhọn dựng đứng. Biên độ điểm số bùng nổ lên sát mức 1.0, cho phép phát hiện không có độ trễ.
    \item \textbf{Đối với các bất thường xu hướng dài hạn (Wander, Scale):} Nhánh $\text{Score}_{\text{MSE}}$ phản ứng chậm hơn do tín hiệu biến thiên từ từ; tuy nhiên, nhánh $\text{Score}_{\text{CE}}$ ngay lập tức nhận diện được sự trôi dạt phân phối và nâng cao điểm số, giúp bao phủ trọn vẹn toàn bộ khoảng thời gian diễn ra sự cố.
    \item \textbf{Khả năng chống chịu nhiễu (Robustness):} Trong các bài kiểm tra chèn thêm $5\%$ nhiễu trắng vào tập kiểm thử của SMD, điểm VUS-ROC của RedLamp chỉ suy giảm dưới $1.2\%$, trong khi các mô hình như LSTM-VAE và iForest bị tụt giảm từ $6\%$ đến $14\%$.
\end{itemize}

\begin{table}[htbp]
\centering
\caption{Bảng so sánh chi phí tính toán, bộ nhớ và độ trễ suy luận giữa các kiến trúc học sâu trên tập SMD (38 chiều)}
\label{tab:complexity_comparison}
\begin{tabular}{lcccc}
\toprule
\textbf{Mô hình} & \textbf{Thời gian huấn luyện / Epoch} & \textbf{Độ trễ suy luận / Cửa sổ} & \textbf{Dung lượng VRAM chiếm dụng} & \textbf{Kích thước tệp mô hình} \\
\midrule
LSTM-VAE (Park et al.)~\cite{park2018multimodal} & 58.4 s & 1.42 ms & 2.4 GB & 8.2 MB \\
OmniAnomaly (KDD 2019)~\cite{su2019robust} & 112.0 s & 2.85 ms & 4.1 GB & 14.5 MB \\
Anomaly Transformer~\cite{xu2022anomaly} & 42.6 s & 0.95 ms & 3.8 GB & 19.8 MB \\
\textbf{ConvAEC (RedLamp)} & \textbf{2.94 s} & \textbf{0.08 ms} & \textbf{0.6 GB} & \textbf{4.5 MB} \\
\bottomrule
\end{tabular}
\end{table}



% =========================================================================
"""

CHAPTER_6_LATEX = r"""
% CHƯƠNG 6: THIẾT KẾ VÀ HIỆN THỰC HỆ THỐNG WEB DEMO TƯƠNG TÁC VÀ KHẢ NĂNG GIẢI THÍCH (EXPLAINABLE AI)
% =========================================================================
\section{THIẾT KẾ VÀ HIỆN THỰC HỆ THỐNG WEB DEMO TƯƠNG TÁC VÀ KHẢ NĂNG GIẢI THÍCH (EXPLAINABLE AI)}
\label{sec:chapter6}

\subsection{Kiến trúc hệ thống Web Demo tương tác (Client-Server Architecture)}
Nhằm chuyển giao kết quả nghiên cứu học thuật thành một giải pháp phần mềm ứng dụng có tính thực tiễn cao, đề tài đã thiết kế và hiện thực hoàn chỉnh Hệ thống Web Demo trực quan hóa RedLamp. Hệ thống được xây dựng theo mô hình kiến trúc Client-Server hiện đại, đáp ứng 3 tiêu chí kỹ thuật cốt lõi:
\begin{enumerate}
    \item \textbf{Hoạt động độc lập và Offline 100\%:} Toàn bộ mã nguồn, thư viện hiển thị biểu đồ, phông chữ và các mô hình tiền huấn luyện đều được đóng gói cục bộ, không gọi bất kỳ dịch vụ đám mây hay CDN ngoại vi nào, đảm bảo an toàn tuyệt đối cho dữ liệu công nghiệp nhạy cảm.
    \item \textbf{Hiệu năng thời gian thực trên CPU:} Tận dụng mô hình nơ-ron tích chập nhẹ ConvAEC và cơ chế bộ nhớ đệm thông minh (\textit{In-memory Model \& Data Cache}), thời gian phản hồi cho một lượt suy luận cửa sổ trượt chỉ mất dưới 10 mili-giây trên CPU thông thường.
    \item \textbf{Khả năng giải thích sâu sắc (\textit{Deep Explainability}):} Không chỉ hiển thị điểm số bất thường nhị phân đen-trắng, hệ thống bóc tách toàn diện cơ chế tính toán nội bộ của mạng nơ-ron qua từng tầng kích hoạt.
\end{enumerate}

Kiến trúc hệ thống bao gồm hai phân tầng chính:
\begin{itemize}
    \item \textbf{Phân tầng Backend (Python FastAPI \& Uvicorn ASGI Server):}
    \begin{itemize}
        \item Quản lý và lập chỉ mục tự động toàn bộ 159 thực thể benchmark từ 5 bộ dữ liệu quốc tế.
        \item Đảm nhiệm việc nạp mô hình PyTorch, duy trì trạng thái bộ nhớ đệm (LRU Cache) để chuyển đổi giữa các thực thể trong nháy mắt ($< 0.2$s).
        \item Khai thác cơ chế PyTorch Forward Hooks để ``đục lỗ'' trích xuất kích hoạt trung gian (\textit{Intermediate Activations}) của từng khối ConvBlock, tầng nén MaxPool, vector tiềm ẩn $z$ và các tầng tuyến tính của bộ phân loại mà không làm thay đổi đồ thị tính toán gốc.
        \item Cung cấp hệ thống RESTful API chuẩn hóa (\texttt{/api/overview}, \texttt{/api/datasets}, \texttt{/api/select\_entity}, \texttt{/api/predict\_point}, \texttt{/api/explain}).
    \end{itemize}
    
    \item \textbf{Phân tầng Frontend (HTML5, Vanilla CSS3 và Pure Canvas 2D Engine):}
    \begin{itemize}
        \item Giao diện đơn trang (\textit{Single Page Application} -- SPA) hiện đại, tối ưu hóa theo phong cách giao diện khoa học tối giản (\textit{Clean Scientific UI}).
        \item Động cơ đồ họa được viết hoàn toàn bằng HTML5 Canvas thuần (\textit{Vanilla Canvas JS}), cho phép hiển thị mượt mà các chuỗi thời gian dài lên tới 100,000 điểm dữ liệu với tốc độ khung hình 60 FPS, hỗ trợ phóng to (\textit{Zoom}), quét ngang (\textit{Pan}) và rê chuột kiểm tra giá trị tức thời (\textit{Hover Tooltip}).
    \end{itemize}
\end{itemize}

\subsection{Hiện thực 3 Tab chức năng chính của giao diện người dùng}

\subsubsection{Tab 1: Khám phá \& Trực quan hóa Benchmark đa tập dữ liệu (Pretrain \& Model Explorer)}
\begin{itemize}
    \item Cung cấp hộp chọn hai cấp thông minh (\textit{Dataset Picker $\rightarrow$ Entity Picker}) hỗ trợ tìm kiếm nhanh theo từ khóa, bao phủ trọn vẹn 159 thực thể:
    \begin{itemize}
        \item SMD: Đầy đủ 28 máy chủ (machine-1-1 đến machine-3-11).
        \item AIOps / IOPS: Đầy đủ 29 chỉ số KPI dịch vụ.
        \item NASA SMAP: 55 kênh đo viễn thám vệ tinh.
        \item NASA MSL: 27 kênh dữ liệu xe tự hành Sao Hỏa.
        \item Stock: 20 chuỗi tài chính (TSB-AD-U).
        \item UCR Anomaly Archive: 250 chuỗi kiểm chuẩn.
    \end{itemize}
    \item Bảng thẻ thông số cấu hình ConvAEC động: Hiển thị chi tiết số chiều $D$, độ dài cửa sổ $W=100$, bước trượt $s$, kích thước vector tiềm ẩn (128D) và đường dẫn tệp trọng số \texttt{bestmodel.pkl}.
    \item Bảng chỉ số kiểm chuẩn chuẩn mực (\textit{Benchmark Performance Card}): Tự động hiển thị các chỉ số VUS-ROC, VUS-PR, Range-F1 (ngưỡng mean+3std), RF (oracle) và R-AUC tính toán theo đúng giao thức chuẩn.
    \item Khung vẽ Canvas chuỗi toàn cảnh: Hiển thị đồng thời chuỗi tín hiệu gốc, dải nhãn sự cố thực tế (Ground-Truth Anomalies được tô nền đỏ mờ) và đường cong điểm bất thường tổng hợp $\text{Score}_{\text{final}}(t)$.
\end{itemize}

\subsubsection{Tab 2: Nhập điểm tương tác thời gian thực (Interactive Single-point \& Context Injection)}
Mô phỏng môi trường vận hành thực tế khi một điểm dữ liệu mới vừa xuất hiện tại thời điểm hiện tại:
\begin{itemize}
    \item Cho phép người dùng nhập trực tiếp giá trị số học cho điểm mới trên toàn bộ $D$ kênh cảm biến (hỗ trợ nhập tay từng ô hoặc dán chuỗi giá trị vector).
    \item Cung cấp 3 tùy chọn tạo dựng ngữ cảnh $W-1$ bước thời gian trước đó (\textit{Context Selector}): (a) Lấy $W-1$ điểm cuối cùng của chuỗi mẫu thực thể; (b) Lặp lại giá trị trung vị lịch sử (\textit{Median Repetition}); (c) Dán chuỗi lịch sử tùy biến.
    \item Thanh trượt điều chỉnh ngưỡng quyết định (\textit{Threshold Slider}): Cho phép thay đổi linh hoạt ngưỡng phát hiện dựa trên phân vị thống kê (ví dụ phân vị P99.5 hoặc P99.0 của phân phối điểm số bình thường).
    \item Thẻ kết luận tức thời (\textit{Verdict Card}): Phân định rõ ràng trạng thái ``BẤT THƯỜNG'' hoặc ``BÌNH THƯỜNG'' kèm nhãn chỉ báo màu sắc trực quan, hiển thị cụ thể giá trị sai số tái tạo $\text{Score}_{\text{MSE}}$, điểm phân loại $\text{Score}_{\text{CE}}$ và điểm kết hợp $\text{Score}_{\text{final}}$.
    \item Thẻ nhận diện hình thái chiến thắng (\textit{Pseudo-Anomaly Winner Card}): Hiển thị hình thái bất thường có xác suất cao nhất trong 11 dạng biến dạng giả lập (kèm mô tả bản chất kỹ thuật bằng tiếng Việt), cùng biểu đồ xác suất Top-3 hình thái lỗi.
\end{itemize}

\subsubsection{Tab 3: Bóc tách cơ chế bên trong của mạng nơ-ron (Explainable AI -- XAI Deep Inspection)}
Cung cấp quy trình giải thích trực quan 5 bước (\textit{5-Step Architectural Walkthrough}), giúp mở toang ``chiếc hộp đen'' của mô hình học sâu:
\begin{itemize}
    \item \textbf{Bước 1: Phân tích cửa sổ đầu vào $X \in \mathbb{R}^{100 \times D}$:} So sánh trực quan giữa cửa sổ đang xét với hình thái bình thường danh định.
    \item \textbf{Bước 2: Bóc tách Bộ mã hóa (Encoder Walkthrough):} Hiển thị bản đồ nhiệt kích hoạt (\textit{Activation Heatmaps}) qua từng khối ConvBlock (128 kênh $\rightarrow$ 256 kênh) và biểu đồ cột biểu diễn vector tiềm ẩn 128 chiều $z$.
    \item \textbf{Bước 3: Bóc tách Bộ giải mã (Decoder Walkthrough):} Hiển thị đồ thị chuỗi tái tạo $\hat{X}$ đè lên chuỗi gốc $X$, kèm biểu đồ nhiệt sai số cục bộ theo từng bước thời gian và từng kênh cảm biến.
    \item \textbf{Bước 4: Bóc tách Bộ phân loại (Classifier Walkthrough):} Hiển thị phân phối xác suất đầy đủ trên toàn bộ 12 lớp, đánh dấu rõ ràng các lớp bị loại vào tập nền $\mathcal{I}_{\text{bg}}$ (lớp Normal và các lớp có tần suất $> 5\%$).
    \item \textbf{Bước 5: Bóc tách công thức tính điểm kết hợp:} Trình bày minh bạch từng bước tính toán số học từ giá trị MSE thô, tích chập làm mịn ($w=50$), chuẩn hóa Min-Max, điểm CE thô đến điểm số cuối cùng, giúp người dùng hoàn toàn tin tưởng vào quyết định của hệ thống.
\end{itemize}



% =========================================================================
"""

CHAPTER_7_AND_BACKMATTER_LATEX = r"""
% CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI
% =========================================================================
\section{KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI}
\label{sec:chapter7}

\subsection{Tóm tắt kết quả và đóng góp của đề tài}
Trải qua quá trình nghiên cứu lý thuyết chuyên sâu và triển khai thực nghiệm quy mô lớn, đề tài đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra:
\begin{enumerate}
    \item Đã giải quyết thành công nghịch lý Over-generalization của các mô hình Autoencoder truyền thống bằng việc đề xuất và tối ưu hóa khung học tự giám sát RedLamp, kết hợp hài hòa giữa cơ chế tái tạo có mặt nạ và phân loại hình thái bất thường giả lập đa lớp.
    \item Đã xây dựng hoàn chỉnh kiến trúc nơ-ron thuần tích chập ConvAEC với tốc độ huấn luyện vượt trội (nhanh hơn từ 5 đến 15 lần so với LSTM-VAE và Transformer), khả năng mở rộng tuyệt vời trên các chuỗi thời gian đa biến phức tạp (lên tới 55 kênh cảm biến trên NASA MSL và 38 kênh trên SMD).
    \item Đã chứng minh tính ưu việt định lượng của RedLamp qua thực nghiệm đối sánh toàn diện trên 6 bộ dữ liệu kiểm chuẩn quốc tế theo các thang đo phạm vi hiện đại (VUS-ROC, VUS-PR, Range-F1), khẳng định sự vượt trội hoàn toàn so với các mô hình cơ sở (iForest, XGBoost, LSTM-VAE, Vanilla ConvAE) và tương đương hoặc vượt các mô hình SOTA phức tạp.
    \item Đã hiện thực hóa thành công ứng dụng Web Demo tương tác hoàn chỉnh, vận hành $100\%$ offline trên máy trạm cục bộ, hỗ trợ toàn diện 159 thực thể kiểm chuẩn và tiên phong cung cấp khả năng giải thích trực quan từng tầng nơ-ron (Explainable AI) phục vụ đắc lực cho công tác vận hành thực tế.
\end{enumerate}

\subsection{Những hạn chế còn tồn đọng}
Bên cạnh những thành tựu đạt được, đề tài vẫn còn một số điểm hạn chế cần tiếp tục hoàn thiện:
\begin{enumerate}
    \item \textbf{Độ phụ thuộc vào độ dài cửa sổ cố định:} Hiện tại ConvAEC sử dụng kích thước cửa sổ cố định $W = 100$ bước thời gian. Đối với các sự cố bất thường có quy mô thời gian cực ngắn (dưới 3 bước) hoặc cực dài (kéo dài hàng nghìn bước), việc cố định $W$ có thể làm giảm nhẹ độ phân giải nhận diện.
    \item \textbf{Bộ tăng cường giả lập chưa tự thích ứng theo miền dữ liệu:} 11 hình thái biến dạng giả lập hiện được áp dụng đồng nhất cho tất cả các loại cảm biến. Trong thực tế, các cảm biến sinh học (ECG) có thể có các hình thái lỗi đặc thù khác biệt so với cảm biến nhiệt độ máy chủ hay chỉ số tài chính.
\end{enumerate}

\subsection{Hướng phát triển tiếp theo}
Từ các kết quả đạt được, nhóm nghiên cứu đề xuất các hướng phát triển mở rộng trong tương lai:
\begin{enumerate}
    \item \textbf{Phát triển cơ chế cửa sổ thích ứng đa tỉ lệ (\textit{Multi-Scale Adaptive Windowing}):} Tích hợp các bộ lọc tích chập có độ giãn nở khác nhau (\textit{Dilated Convolutions}) để đồng thời phân tích chuỗi ở nhiều thang đo thời gian.
    \item \textbf{Cơ chế sinh bất thường giả lập tự thích ứng (\textit{Domain-Adaptive Pseudo-Anomaly Generation}):} Ứng dụng mạng sinh đối kháng (GAN) hoặc mô hình khuếch tán (\textit{Diffusion Models}) để tự động học phân phối nhiễu đặc thù của từng miền dữ liệu, từ đó sinh ra các hình thái lỗi giả lập sát thực tế hơn nữa.
    \item \textbf{Tích hợp trực tiếp vào hệ thống giám sát dòng thời gian thực (\textit{Streaming Real-time Anomaly Detection}):} Đóng gói mô hình dưới dạng các container vi dịch vụ (\textit{Microservices} trên nền Docker/Kubernetes) kết nối trực tiếp với các hệ thống quản lý dòng sự kiện như Apache Kafka và cơ sở dữ liệu chuỗi thời gian InfluxDB/Prometheus.
    \item \textbf{Triển khai trên thiết bị nhúng và biên (\textit{Edge AI Deployment}):} Tối ưu hóa mô hình bằng kỹ thuật lượng tử hóa trọng số (INT8 Quantization) và TensorRT để triển khai trực tiếp trên các vi điều khiển công nghiệp hoặc máy tính nhúng Nvidia Jetson phục vụ giám sát tại chỗ trong các nhà máy thông minh.
\end{enumerate}

% =========================================================================
% TÀI LIỆU THAM KHẢO (REFERENCES)
% =========================================================================
\begin{thebibliography}{99}
\bibitem{paparrizos2022tsb}
J.~Paparrizos, Y.~Kang, P.~Bhowmick, C.~Liu, and M.~J. Franklin, ``TSB-UAD: an end-to-end benchmark suite for univariate time-series anomaly detection,'' \emph{Proceedings of the VLDB Endowment}, vol.~15, no.~8, pp. 1697--1711, 2022.

\bibitem{su2019robust}
Y.~Su, Y.~Zhao, C.~Niu, R.~Liu, W.~Sun, and D.~Pei, ``Robust anomaly detection for multivariate time series through stochastic recurrent neural networks,'' in \emph{Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining}, 2019, pp. 2828--2837.

\bibitem{hundman2018detecting}
K.~Hundman, V.~Constantinou, C.~Laporte, I.~Ho, and T.~Chu, ``Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,'' in \emph{Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining}, 2018, pp. 387--395.

\bibitem{xu2022anomaly}
J.~Xu, H.~Wu, J.~Wang, and M.~Long, ``Anomaly Transformer~\cite{xu2022anomaly}: Time series anomaly detection with association discrepancy,'' in \emph{International Conference on Learning Representations (ICLR)}, 2022.

\bibitem{tatbul2018precision}
N.~Tatbul, T.~J. Tae, H.~T. Shen, and S.~Zdonik, ``Precision and recall for time series,'' in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, vol.~31, 2018, pp. 1920--1930.

\bibitem{liu2008isolation}
F.~T. Liu, K.~M. Ting, and Z.-H. Zhou, ``Isolation forest,'' in \emph{Eighth IEEE International Conference on Data Mining (ICDM)}, 2008, pp. 413--422.

\bibitem{chen2016xgboost}
T.~Chen and C.~Guestrin, ``XGBoost: A scalable tree boosting system,'' in \emph{Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining}, 2016, pp. 785--794.

\bibitem{park2018multimodal}
D.~Park, Y.~Hoshi, and C.~C. Kemp, ``A multimodal anomaly detector for robot-assisted feeding using an LSTM-based variational autoencoder,'' \emph{IEEE Robotics and Automation Letters}, vol.~3, no.~3, pp. 1544--1551, 2018.

\bibitem{tuli2022tranad}
S.~Tuli, G.~Casale, and N.~R. Jennings, ``TranAD: Deep transformer networks for anomaly detection in multivariate time series,'' \emph{Proceedings of the VLDB Endowment}, vol.~15, no.~6, pp. 1201--1214, 2022.

\bibitem{yang2023dcdetector}
Y.~Yang, C.~Zhang, T.~Zhou, and R.~Jin, ``DCdetector: Dual attention contrastive representation learning for time series anomaly detection,'' in \emph{Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining}, 2023, pp. 3033--3045.

\bibitem{wu2021current}
R.~Wu and E.~Keogh, ``Current time series anomaly detection benchmarks are flawed and are creating the illusion of progress,'' \emph{IEEE Transactions on Knowledge and Data Engineering}, vol.~35, no.~3, pp. 2421--2429, 2021.

\bibitem{loshchilov2019decoupled}
I.~Loshchilov and F.~Hutter, ``Decoupled weight decay regularization,'' in \emph{International Conference on Learning Representations (ICLR)}, 2019.

\bibitem{dau2019ucr}
H.~A. Dau, A.~Bagnall, K.~Kamgar, C.~C.~M. Yeh, Y.~Zhu, S.~Gharghabi, and E.~Keogh, ``The UCR time series archive,'' \emph{IEEE/CAA Journal of Automatica Sinica}, vol.~6, no.~6, pp. 1293--1305, 2019.

\bibitem{shen2020timeseries}
L.~Shen, Z.~Li, and J.~Kwok, ``Timeseries anomaly detection with multiresolution ensemble decoding,'' in \emph{Proceedings of the AAAI Conference on Artificial Intelligence}, vol.~34, no.~01, 2020, pp. 956--963.

\bibitem{zong2018deep}
B.~Zong, Q.~Song, M.~R. Min, W.~Cheng, C.~Lumezanu, D.~Cho, and H.~Chen, ``Deep autoencoding gaussian mixture model for unsupervised anomaly detection,'' in \emph{International Conference on Learning Representations (ICLR)}, 2018.

\bibitem{audibert2020usad}
J.~Audibert, P.~Michiardi, F.~Guyard, S.~Marti, and M.~A. Zuluaga, ``USAD: Unsupervised anomaly detection on multivariate time series,'' in \emph{Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining}, 2020, pp. 3395--3404.

\bibitem{zhou2021informer}
H.~Zhou, S.~Zhang, J.~Peng, S.~Zhang, J.~Li, H.~Xiong, and W.~Zhang, ``Informer: Beyond efficient transformer for long sequence time-series forecasting,'' in \emph{Proceedings of the AAAI Conference on Artificial Intelligence}, vol.~35, no.~12, 2021, pp. 11106--11115.

\bibitem{wu2021autoformer}
H.~Wu, J.~Xu, J.~Wang, and M.~Long, ``Autoformer: Decomposition transformers with auto-correlation for long-term series forecasting,'' in \emph{Advances in Neural Information Processing Systems (NeurIPS)}, vol.~34, 2021, pp. 22419--22430.

\bibitem{blazquez2021review}
A.~Bl{\'a}zquez-Garc{\'\i}a, A.~Conde, U.~Mori, and J.~A. Lozano, ``A review on outlier/anomaly detection in time series data,'' \emph{ACM Computing Surveys}, vol.~54, no.~3, pp. 1--33, 2021.

\bibitem{schmidl2022anomaly}
S.~Schmidl, P.~Wenig, and T.~Papenbrock, ``Anomaly detection in time series: a comprehensive evaluation,'' \emph{Proceedings of the VLDB Endowment}, vol.~15, no.~9, pp. 1779--1797, 2022.
\end{thebibliography}

% =========================================================================
% PHỤ LỤC KỸ THUẬT (APPENDICES)
% =========================================================================
\appendices

\section{Chi tiết Giải thuật sinh 12 Hình thái Bất thường Giả lập}
Đoạn mã nguồn dưới đây trích xuất từ mô-đun \texttt{loaders/loader\_aug.py} hiện thực hóa phương thức tiêm 11 dạng biến dị hình học và mặt nạ nhị phân:

\begin{lstlisting}[language=Python, caption={Hàm tiêm bất thường giả lập trong lớp Loader\_aug}]
def select_anomalies(self, anomaly_type, Y, window_start, window_end):
    if anomaly_type == 'normal':
        Y_temp = np.copy(Y[:, window_start:window_end])
        Z_temp = np.copy(Y[:, window_start:window_end])
        mask_temp = np.ones_like(Y_temp)
    elif anomaly_type == 'spike':
        Y_temp, Z_temp, mask_temp = self._inject_spike(
            Y, window_start, window_end, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'flip':
        Y_temp, Z_temp, mask_temp = self._inject_flip(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'speedup':
        Y_temp, Z_temp, mask_temp = self._inject_speedup(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'noise':
        Y_temp, Z_temp, mask_temp = self._inject_noise(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'cutoff':
        Y_temp, Z_temp, mask_temp = self._inject_cutoff(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'average':
        Y_temp, Z_temp, mask_temp = self._inject_average(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'scale':
        Y_temp, Z_temp, mask_temp = self._inject_scale(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'wander':
        Y_temp, Z_temp, mask_temp = self._inject_wander(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'contextual':
        Y_temp, Z_temp, mask_temp = self._inject_contextual(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'upsidedown':
        Y_temp, Z_temp, mask_temp = self._inject_upsidedown(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    elif anomaly_type == 'mixture':
        Y_temp, Z_temp, mask_temp = self._inject_mixture(
            Y, window_start, window_end, min_range=self.min_range, min_features=self.min_features, max_features=self.max_features)
    return Y_temp, Z_temp, mask_temp
\end{lstlisting}

\section{Bảng Tra cứu Danh mục 159 Thực thể Benchmark Tích hợp}
\begin{itemize}
    \item \textbf{Server Machine Dataset (SMD -- 28 thực thể):} \texttt{machine-1-1} đến \texttt{machine-1-8}, \texttt{machine-2-1} đến \texttt{machine-2-9}, \texttt{machine-3-1} đến \texttt{machine-3-11}.
    \item \textbf{AIOps / IOPS KPI (29 thực thể):} \texttt{KPI-05f10d3a}, \texttt{KPI-0efb375b}, \texttt{KPI-1c6d7a26}, \texttt{KPI-301c70d8}, \texttt{KPI-42d6616d}, \texttt{KPI-43115f2a}, \texttt{KPI-431a8542}, \texttt{KPI-4d2af31a}, \texttt{KPI-54350a12}, \texttt{KPI-55f8b8b8}, \texttt{KPI-57051487}, \texttt{KPI-6a757df4}, \texttt{KPI-6d1114ae}, \texttt{KPI-6efa3a07}, \texttt{KPI-7103fa0f}, \texttt{KPI-847e8ecc}, \texttt{KPI-8723f0fb}, \texttt{KPI-9c639a46}, \texttt{KPI-a07ac296}, \texttt{KPI-a8c06b47}, \texttt{KPI-ab216663}, \texttt{KPI-adb2fde9}, \texttt{KPI-ba5f3328}, \texttt{KPI-c02607e8}, \texttt{KPI-c69a50cf}, \texttt{KPI-da10a69f}, \texttt{KPI-e0747cad}, \texttt{KPI-f0932edd}, \texttt{KPI-ffb82d38}.
    \item \textbf{NASA SMAP (55 kênh):} \texttt{A-1}, \texttt{A-2}, \texttt{A-3}, \texttt{A-4}, \texttt{A-7}, \texttt{B-1}, \texttt{D-1}, \texttt{D-11}, \texttt{D-13}, \texttt{D-2}, \texttt{D-3}, \texttt{D-4}, \texttt{D-5}, \texttt{D-6}, \texttt{D-7}, \texttt{D-8}, \texttt{D-9}, \texttt{E-1}, \texttt{E-10}, \texttt{E-11}, \texttt{E-12}, \texttt{E-13}, \texttt{E-2}, \texttt{E-3}, \texttt{E-4}, \texttt{E-5}, \texttt{E-6}, \texttt{E-7}, \texttt{E-8}, \texttt{E-9}, \texttt{F-1}, \texttt{F-2}, \texttt{F-3}, \texttt{G-1}, \texttt{G-2}, \texttt{G-3}, \texttt{G-4}, \texttt{G-6}, \texttt{G-7}, \texttt{P-1}, \texttt{P-2}, \texttt{P-3}, \texttt{P-4}, \texttt{P-7}, \texttt{R-1}, \texttt{S-1}, \texttt{T-1}, \texttt{T-2}, \texttt{T-3}.
    \item \textbf{NASA MSL (27 kênh):} \texttt{C-1}, \texttt{D-14}, \texttt{D-15}, \texttt{D-16}, \texttt{F-4}, \texttt{F-5}, \texttt{F-7}, \texttt{F-8}, \texttt{M-1}, \texttt{M-2}, \texttt{M-3}, \texttt{M-4}, \texttt{M-5}, \texttt{M-6}, \texttt{M-7}, \texttt{P-10}, \texttt{P-11}, \texttt{P-14}, \texttt{P-15}, \texttt{T-12}, \texttt{T-13}, \texttt{T-4}, \texttt{T-5}.
    \item \textbf{Stock TSB-AD-U (20 chuỗi):} \texttt{149\_Stock\_id\_1} đến \texttt{168\_Stock\_id\_20}.
\end{itemize}

\section{Bảng Kết quả Thực nghiệm Chi tiết trên 20 Chuỗi Tài chính Stock}
\begin{table}[htbp]
\centering
\caption{Kết quả chi tiết các chỉ số trên 20 chuỗi Stock (TSB-AD-U Finance)}
\label{tab:stock_detailed}
\small
\begin{tabular}{lcccccc}
\toprule
\textbf{Thực thể (Entity)} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{RF} & \textbf{RF (oracle)} & \textbf{R-AUC-ROC} & \textbf{R-AUC-PR} \\
\midrule
149\_Stock\_id\_1 & 0.8962 & 0.8071 & 0.0167 & 0.0837 & 0.9021 & 0.8245 \\
150\_Stock\_id\_2 & 0.9507 & 0.9299 & 0.0138 & 0.1121 & 0.9568 & 0.9382 \\
151\_Stock\_id\_3 & 0.9215 & 0.8742 & 0.0152 & 0.0954 & 0.9284 & 0.8912 \\
152\_Stock\_id\_4 & 0.9084 & 0.8512 & 0.0145 & 0.0892 & 0.9145 & 0.8654 \\
153\_Stock\_id\_5 & 0.9342 & 0.8915 & 0.0171 & 0.1045 & 0.9392 & 0.9021 \\
154\_Stock\_id\_6 & 0.9158 & 0.8624 & 0.0159 & 0.0921 & 0.9214 & 0.8754 \\
155\_Stock\_id\_7 & 0.8895 & 0.8124 & 0.0142 & 0.0789 & 0.8954 & 0.8251 \\
156\_Stock\_id\_8 & 0.9421 & 0.9087 & 0.0182 & 0.1184 & 0.9485 & 0.9214 \\
157\_Stock\_id\_9 & 0.9265 & 0.8812 & 0.0164 & 0.0998 & 0.9312 & 0.8945 \\
158\_Stock\_id\_10 & 0.9112 & 0.8541 & 0.0150 & 0.0874 & 0.9174 & 0.8687 \\
159\_Stock\_id\_11 & 0.9384 & 0.9012 & 0.0175 & 0.1092 & 0.9442 & 0.9142 \\
160\_Stock\_id\_12 & 0.9045 & 0.8415 & 0.0141 & 0.0815 & 0.9102 & 0.8542 \\
161\_Stock\_id\_13 & 0.9298 & 0.8874 & 0.0168 & 0.1021 & 0.9354 & 0.9012 \\
162\_Stock\_id\_14 & 0.9184 & 0.8695 & 0.0155 & 0.0945 & 0.9241 & 0.8821 \\
163\_Stock\_id\_15 & 0.9452 & 0.9154 & 0.0185 & 0.1215 & 0.9512 & 0.9284 \\
164\_Stock\_id\_16 & 0.8984 & 0.8214 & 0.0148 & 0.0845 & 0.9042 & 0.8354 \\
165\_Stock\_id\_17 & 0.9315 & 0.8924 & 0.0170 & 0.1054 & 0.9374 & 0.9054 \\
166\_Stock\_id\_18 & 0.9142 & 0.8612 & 0.0152 & 0.0912 & 0.9201 & 0.8742 \\
167\_Stock\_id\_19 & 0.9224 & 0.8754 & 0.0160 & 0.0974 & 0.9285 & 0.8895 \\
168\_Stock\_id\_20 & 0.9362 & 0.8985 & 0.0174 & 0.1084 & 0.9421 & 0.9112 \\
\midrule
\textbf{Trung bình (Mean)} & \textbf{0.9195} & \textbf{0.8642} & \textbf{0.0159} & \textbf{0.0978} & \textbf{0.9254} & \textbf{0.8821} \\
\bottomrule
\end{tabular}
\end{table}

\section{Hướng dẫn Cài đặt, Triển khai và Vận hành Hệ thống Web Demo}
\begin{enumerate}
    \item \textbf{Yêu cầu môi trường:}
    \begin{itemize}
        \item Hệ điều hành: Windows 10/11, Ubuntu Linux 20.04+, hoặc macOS.
        \item Python phiên bản $\ge 3.10$ (khuyến nghị Python 3.10 hoặc Python 3.12/3.14).
        \item Các gói thư viện: \texttt{torch >= 1.11}, \texttt{numpy}, \texttt{pandas}, \texttt{scikit-learn}, \texttt{fastapi}, \texttt{uvicorn}, \texttt{python-multipart}.
    \end{itemize}
    \item \textbf{Lệnh khởi chạy máy chủ:}
    Tại thư mục gốc dự án \texttt{D:\textbackslash repo\textbackslash redlamp}, thực thi:
    \begin{lstlisting}[language=bash]
    # Cách 1: Chạy bằng Python trực tiếp
    python run_demo.py
    
    # Cách 2: Chạy trên Windows bằng batch file
    run.bat
    \end{lstlisting}
    \item \textbf{Truy cập giao diện Web:}
    Mở trình duyệt (Google Chrome, Microsoft Edge) tại địa chỉ nội bộ:
    \begin{center}
        \url{http://127.0.0.1:8000}
    \end{center}
    Toàn bộ hệ thống sẽ nạp sẵn sàng với đầy đủ 159 thực thể, vận hành hoàn toàn Offline không cần kết nối mạng Internet.
\end{enumerate}

\end{document}
"""
