# -*- coding: utf-8 -*-
LATEX_PREAMBLE = r"""\documentclass[11pt,journal,onecolumn]{IEEEtran}
% Lưu ý: Có thể chuyển đổi sang chuẩn IEEE Conference 2 cột bằng cách đổi thành:
% \documentclass[conference]{IEEEtran}

\usepackage[utf8]{inputenc}
\usepackage[vietnamese,english]{babel}
\usepackage[T5,T1]{fontenc}

\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{algorithmic}
\usepackage{algorithm}
\usepackage{array}
\usepackage{booktabs}
\usepackage{cite}
\usepackage{graphicx}
\usepackage{listings}
\usepackage{multirow}
\usepackage{makecell}
\usepackage{url}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{longtable}
\usepackage[a4paper,left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm]{geometry}
\usepackage{setspace}
\setstretch{1.25} % Giãn dòng 1.25 chuẩn báo cáo / luận văn học thuật (~40 trang A4)

\usepackage[colorlinks=true,linkcolor=blue!80!black,citecolor=blue!80!black,urlcolor=blue!80!black]{hyperref}

% Định dạng cho khối mã nguồn
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.97,0.98,0.99}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen}\itshape,
    keywordstyle=\color{blue}\bfseries,
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize,
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
    frame=single,
    rulecolor=\color{gray!30}
}
\lstset{style=mystyle}

% Thiết lập Header và Footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{Báo cáo Đề tài RedLamp - UIT/VNU-HCM}}
\fancyhead[R]{\small\textit{Phát hiện bất thường chuỗi thời gian không giám sát}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\begin{document}
\selectlanguage{vietnamese}



% =========================================================================
"""

FRONTMATTER_LATEX = r"""
% TRANG BÌA CHUẨN ĐẠI HỌC QUỐC GIA TP.HCM - TRƯỜNG ĐH CÔNG NGHỆ THÔNG TIN
% TÊN GIẢNG VIÊN VÀ HỌC VIÊN / SINH VIÊN BỎ TRỐNG THEO YÊU CẦU
% =========================================================================
\begin{titlepage}
\begin{center}
    \large \textbf{ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH}\\
    \large \textbf{TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN}\\
    \large \textbf{KHOA KHOA HỌC MÁY TÍNH}\\
    \large \textit{PHÒNG THÍ NGHIỆM TRÍ TUỆ NHÂN TẠO \& HỆ THỐNG THÔNG MINH}
    
    \vspace{2.0cm}
    \rule{\linewidth}{1.5pt}
    
    \vspace{0.8cm}
    {\Large \textbf{BÁO CÁO TỔNG KẾT ĐỀ TÀI NGHIÊN CỨU KHOA HỌC \& KHÓA LUẬN TỐT NGHIỆP}\par}
    \vspace{0.5cm}
    {\large \textbf{CHUYÊN NGÀNH: KHOA HỌC MÁY TÍNH / TRÍ TUỆ NHÂN TẠO}\par}
    
    \vspace{1.2cm}
    {\LARGE \textbf{NGHIÊN CỨU, CẢI TIẾN VÀ XÂY DỰNG HỆ THỐNG PHÁT HIỆN BẤT THƯỜNG CHUỖI THỜI GIAN KHÔNG GIÁM SÁT DỰA TRÊN TỰ MÃ HÓA TÍCH CHẬP VÀ PHÂN LOẠI HÌNH THÁI BẤT THƯỜNG GIẢ LẬP ĐA LỚP (REDLAMP)}\par}
    
    \vspace{0.4cm}
    {\large \textit{(Robust and Explainable Detector of Time Series Anomaly via Augmenting Multiclass Pseudo-Anomalies - RedLamp)}\par}
    
    \rule{\linewidth}{1.5pt}
    
    \vspace{2.0cm}
    \begin{minipage}[t]{0.48\textwidth}
        \textbf{GIẢNG VIÊN HƯỚNG DẪN:}\\
        \vspace{0.3cm}
        \underline{\hspace{6.0cm}}\\
        \textit{Khoa Khoa học Máy tính}\\
        \textit{Trường ĐH Công nghệ Thông tin, ĐHQG-HCM}
    \end{minipage}
    \hfill
    \begin{minipage}[t]{0.48\textwidth}
        \textbf{NHÓM HỌC VIÊN / SINH VIÊN THỰC HIỆN:}\\
        \vspace{0.2cm}
        1. \underline{\hspace{4.2cm}} (MSHV: \underline{\hspace{1.5cm}})\\
        2. \underline{\hspace{4.2cm}} (MSHV: \underline{\hspace{1.5cm}})\\
        3. \underline{\hspace{4.2cm}} (MSHV: \underline{\hspace{1.5cm}})\\
        4. \underline{\hspace{4.2cm}} (MSHV: \underline{\hspace{1.5cm}})\\
        5. \underline{\hspace{4.2cm}} (MSHV: \underline{\hspace{1.5cm}})
    \end{minipage}
    
    \vfill
    {\large \textbf{TP. HỒ CHÍ MINH, NĂM 2026}\par}
\end{center}
\end{titlepage}

\newpage
\pagenumbering{roman}

% =========================================================================
% LỜI CAM ĐOAN
% =========================================================================
\section*{LỜI CAM ĐOAN}
\addcontentsline{toc}{section}{LỜI CAM ĐOAN}

Chúng tôi xin cam đoan rằng công trình nghiên cứu khoa học và khóa luận tốt nghiệp với đề tài \textbf{``Nghiên cứu, cải tiến và xây dựng hệ thống phát hiện bất thường chuỗi thời gian không giám sát dựa trên tự mã hóa tích chập và phân loại hình thái bất thường giả lập đa lớp (RedLamp)''} là kết quả nghiên cứu độc lập, nghiêm túc và trung thực của tập thể nhóm nghiên cứu dưới sự định hướng và hướng dẫn khoa học trực tiếp của Giảng viên hướng dẫn.

Mọi số liệu thực nghiệm, kết quả mô phỏng, đồ thị huấn luyện, bảng tham số phần cứng và mã nguồn hệ thống được trình bày trong báo cáo này đều được thu thập và thực thi trực tiếp từ các môi trường thí nghiệm thực tế (bao gồm cụm máy chủ đám mây Kaggle GPU Nvidia Tesla P100-PCIE-16GB và máy trạm kiểm thử cục bộ tại đơn vị). Tất cả các tài liệu tham khảo, kết quả nghiên cứu kế thừa từ các công trình khoa học quốc tế uy tín (KDD, VLDB, ICLR, NeurIPS, IEEE TKDE)~\cite{paparrizos2022tsb,su2019robust,xu2022anomaly,tatbul2018precision}~\cite{paparrizos2022tsb,su2019robust,xu2022anomaly,tatbul2018precision} đều được trích dẫn nguồn gốc một cách rõ ràng, minh bạch và chính xác theo đúng quy chuẩn học thuật của Trường Đại học Công nghệ Thông tin - Đại học Quốc gia TP.HCM.

Nhóm tác giả xin hoàn toàn chịu trách nhiệm trước Hội đồng Khoa học và Nhà trường về tính trung thực và tính nguyên bản của công trình nghiên cứu này.

\vspace{1.5cm}
\begin{flushright}
    \textit{Tp. Hồ Chí Minh, ngày 13 tháng 11 năm 2026}\\
    \textbf{Đại diện nhóm nghiên cứu}\\
    \vspace{1.0cm}
    \underline{\hspace{6.0cm}}
\end{flushright}

\newpage

% =========================================================================
% LỜI CẢM ƠN
% =========================================================================
\section*{LỜI CẢM ƠN}
\addcontentsline{toc}{section}{LỜI CẢM ƠN}

Để hoàn thành công trình nghiên cứu và bản báo cáo đề tài tốt nghiệp này, nhóm nghiên cứu đã nhận được sự quan tâm, động viên và hỗ trợ vô cùng to lớn từ các quý Thầy Cô, gia đình, bạn bè và các đồng nghiệp.

Trước hết, nhóm nghiên cứu xin bày tỏ lòng biết ơn sâu sắc và chân thành nhất đến Quý Thầy/Cô Giảng viên hướng dẫn khoa học của đề tài. Thầy/Cô đã dành nhiều thời gian quý báu để định hướng đề tài, truyền đạt phương pháp tư duy nghiên cứu khoa học chuẩn mực, tận tình chỉ dẫn và phản biện sâu sắc từng giải thuật, mô hình thí nghiệm và quy trình đánh giá khắt khe trong suốt quá trình nhóm triển khai nghiên cứu. Những nhận xét thấu đáo và sự khích lệ của Thầy/Cô là động lực to lớn giúp nhóm vượt qua các thách thức kỹ thuật phức tạp trong xử lý chuỗi thời gian đa chiều.

Nhóm xin chân thành cảm ơn Ban Giám hiệu Trường Đại học Công nghệ Thông tin, Ban Chủ nhiệm Khoa Khoa học Máy tính cùng toàn thể quý Thầy Cô giáo đã tận tâm giảng dạy, trang bị cho chúng tôi nền tảng tri thức học thuật vững chắc, tư duy hệ thống và kỹ năng thực nghiệm hiện đại trong suốt những năm học tập và nghiên cứu dưới mái trường Đại học Quốc gia TP.HCM.

Cuối cùng, chúng tôi xin gửi lời tri ân sâu sắc đến gia đình, người thân và các bạn đồng môn đã luôn là chỗ dựa tinh thần vững chắc, luôn sẻ chia, động viên và tạo mọi điều kiện thuận lợi nhất để nhóm nghiên cứu có thể hoàn thành tốt công trình này.

\newpage

% =========================================================================
% TÓM TẮT ĐỀ TÀI (TIẾNG VIỆT)
% =========================================================================
\section*{TÓM TẮT ĐỀ TÀI}
\addcontentsline{toc}{section}{TÓM TẮT ĐỀ TÀI}

Phát hiện bất thường trong dữ liệu chuỗi thời gian (\textit{Time-Series Anomaly Detection} -- TSAD) là bài toán cốt lõi trong giám sát hạ tầng công nghệ thông tin (AIOps), mạng lưới cảm biến công nghiệp (IIoT), thiết bị viễn thông không gian (\textit{Aerospace Telemetry}) và hệ thống tài chính. Thách thức lớn nhất trong môi trường thực tế bắt nguồn từ sự khan hiếm nghiêm trọng của nhãn dữ liệu chuẩn (\textit{ground-truth labels}) và hiện tượng mất cân bằng cực đoan giữa các quan sát bình thường và bất thường. Các phương pháp học sâu không giám sát truyền thống chủ yếu dựa trên mạng tự mã hóa (\textit{Autoencoder} -- AE) hoặc mạng tự mã hóa biến phân (\textit{Variational Autoencoder} -- VAE) gặp phải một nghịch lý cơ bản: hiện tượng ``tổng quát hóa thái quá'' (\textit{Over-generalization}), khi mô hình vô tình tái tạo thành công cả các đoạn chuỗi bị lỗi với sai số nhỏ, dẫn đến suy giảm độ nhạy phát hiện.

Đề tài này tập trung nghiên cứu, tối ưu hóa và hiện thực hóa giải pháp \textbf{RedLamp} (\textit{Robust and Explainable Detector of Time Series Anomaly via Augmenting Multiclass Pseudo-Anomalies}) -- một khung học tự giám sát (\textit{Self-Supervised Learning}) đột phá kết hợp giữa cơ chế tái tạo có mặt nạ (\textit{Masked Autoencoding}) và phân loại hình thái bất thường giả lập đa lớp (\textit{Morphological Pseudo-Anomaly Classification}). Mạng nơ-ron cốt lõi \textbf{ConvAEC} được xây dựng hoàn toàn dựa trên các khối tích chập 1 chiều (1D-CNN) đa tầng song song, loại bỏ hoàn toàn các nút thắt cổ chai tính toán tuần tự của RNN/LSTM. Bằng cách thiết lập bộ sinh 11 hình thái biến dạng bất thường giả lập phong phú (\textit{Spike, Flip, Speedup, Noise, Cutoff, Average, Scale, Wander, Contextual, UpsideDown, Mixture}) cùng với trạng thái bình thường (\textit{Normal}), mô hình được rèn luyện để đồng thời vừa học cách khôi phục lại dữ liệu nguyên bản chưa bị biến dạng thông qua mặt nạ nhị phân, vừa phân biệt chính xác bản chất hình thái hình học của từng loại bất thường thông qua kỹ thuật làm mượt nhãn bất đối xứng (\textit{Asymmetric Label Smoothing with Normal Prior}).

Trong quá trình suy luận, hệ thống áp dụng cơ chế tính điểm hai giai đoạn (\textit{Two-Stage Composite Anomaly Scoring}), kết hợp giữa sai số tái tạo cục bộ ($\text{Score}_{\text{MSE}}$) và điểm xác suất phân loại hình thái ($\text{Score}_{\text{CE}}$) được lọc nhiễu qua bộ loại trừ tần suất nền ngẫu nhiên. Thực nghiệm diện rộng trên 6 bộ dữ liệu tiêu chuẩn quốc tế quy mô lớn gồm Server Machine Dataset (SMD -- 28 máy chủ, 38 chiều), AIOps/IOPS (29 KPI dịch vụ), NASA SMAP (55 kênh, 25 chiều), NASA MSL (27 kênh, 55 chiều), Stock TSB-AD-U~\cite{paparrizos2022tsb} (20 chuỗi tài chính) và UCR Anomaly Archive~\cite{dau2019ucr} (250 chuỗi đa miền) theo giao thức đánh giá chuẩn VUS-ROC, VUS-PR và Range-F1 đã chứng minh tính ưu việt vượt trội của RedLamp so với các phương pháp cơ sở (Isolation Forest, XGBoost, LSTM-VAE) và tương đương hoặc vượt các mô hình SOTA (OmniAnomaly~\cite{su2019robust}, Anomaly Transformer~\cite{xu2022anomaly}~\cite{xu2022anomaly}). Đặc biệt, đề tài đã phát triển hoàn chỉnh ứng dụng Web Demo tương tác (Python FastAPI + HTML5 Canvas offline) hỗ trợ khám phá toàn diện 159 thực thể, cho phép kiểm thử thời gian thực và trực quan hóa giải thích được (\textit{Explainable AI}) cơ chế kích hoạt tầng nơ-ron bên trong của mô hình.

\vspace{0.5cm}
\noindent\textbf{Từ khóa:} Phát hiện bất thường chuỗi thời gian; Tự mã hóa tích chập; Tăng cường hình thái bất thường giả lập; Tự giám sát; Khả năng giải thích AI (XAI); ConvAEC; VUS-ROC; VUS-PR; Range-F1.

\newpage

% =========================================================================
% ABSTRACT (ENGLISH)
% =========================================================================
\selectlanguage{english}
\section*{ABSTRACT}
\addcontentsline{toc}{section}{ABSTRACT}

Time-series anomaly detection (TSAD) is a pivotal task in modern intelligent monitoring, spanning IT infrastructure operations (AIOps), Industrial Internet of Things (IIoT), aerospace telemetry, and quantitative finance. In practical deployment, the scarcity of verified ground-truth labels and severe class imbalance pose formidable challenges. Traditional unsupervised deep learning architectures based purely on reconstruction objectives (such as Autoencoders and Variational Autoencoders) frequently suffer from the ``over-generalization'' paradox: the model inadvertently reconstructs abnormal temporal patterns with minimal residual error, degrading detection precision and recall.

This thesis presents a comprehensive study, optimization, and practical deployment of \textbf{RedLamp} (\textit{Robust and Explainable Detector of Time Series Anomaly via Augmenting Multiclass Pseudo-Anomalies}) -- an innovative self-supervised framework fusing masked autoencoding with multiclass morphological pseudo-anomaly classification. The backbone architecture, \textbf{ConvAEC}, is engineered strictly using hierarchical 1D convolutional residual blocks, entirely eliminating recurrent bottlenecks (LSTM/GRU) and enabling highly parallelized computation. By designing an augmentation engine that injects 11 distinct artificial anomaly morphologies (\textit{Spike, Flip, Speedup, Noise, Cutoff, Average, Scale, Wander, Contextual, UpsideDown, Mixture}) alongside pristine normal sequences, the model is jointly optimized to reconstruct clean context via binary masking and discriminate anomaly geometries through asymmetric label smoothing with a structural normal prior.

At inference time, RedLamp executes a two-stage composite anomaly scoring protocol, harmonizing local reconstruction residual errors ($\text{Score}_{\text{MSE}}$) with classifier confidence scores ($\text{Score}_{\text{CE}}$) filtered dynamically against background false positives. Extensive empirical evaluations across six benchmark suites -- Server Machine Dataset (SMD: 28 entities, 38 dimensions), AIOps/IOPS (29 KPI streams), NASA SMAP (55 channels, 25 dimensions), NASA MSL (27 channels, 55 dimensions), Stock TSB-AD-U (20 financial series), and UCR Anomaly Archive (250 multi-domain series) -- under rigorous range-aware metrics (VUS-ROC, VUS-PR, and Range-F1) substantiate the superior robustness and sensitivity of RedLamp over classical and deep learning baselines (Isolation Forest, XGBoost, LSTM-VAE) and competitive parity with state-of-the-art transformers. Furthermore, a standalone, offline-ready interactive Web Demo system (Python FastAPI backend and lightweight HTML5 Canvas frontend) has been engineered, supporting 159 benchmark entities with real-time inference and Explainable AI (XAI) feature activation visualization.

\vspace{0.5cm}
\noindent\textbf{Keywords:} Time-Series Anomaly Detection; Convolutional Autoencoder; Pseudo-Anomaly Augmentation; Self-Supervised Learning; Explainable AI; ConvAEC; VUS-ROC; VUS-PR; Range-F1.

\selectlanguage{vietnamese}
\newpage

% =========================================================================
% DANH MỤC THUẬT NGỮ VÀ KÝ HIỆU
% =========================================================================
\section*{DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ}
\addcontentsline{toc}{section}{DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ}

\begin{table}[htbp]
\centering
\caption{Danh mục các từ viết tắt được sử dụng trong báo cáo}
\label{tab:abbreviations}
\begin{tabular}{llp{7.5cm}}
\toprule
\textbf{Từ viết tắt} & \textbf{Thuật ngữ tiếng Anh đầy đủ} & \textbf{Ý nghĩa / Diễn giải tiếng Việt} \\
\midrule
TSAD & Time-Series Anomaly Detection & Phát hiện bất thường trong chuỗi thời gian \\
RedLamp & Robust and Explainable Detector... & Hệ thống phát hiện bất thường bền bỉ và giải thích được qua tăng cường giả lập đa lớp \\
ConvAEC & Convolutional Autoencoder with Classifier & Bộ tự mã hóa tích chập tích hợp nhánh phân loại \\
1D-CNN & 1-Dimensional Convolutional Neural Network & Mạng nơ-ron tích chập một chiều \\
RNN & Recurrent Neural Network & Mạng nơ-ron hồi quy tuần tự \\
LSTM & Long Short-Term Memory & Mạng bộ nhớ ngắn-dài hạn \\
VAE & Variational Autoencoder & Bộ tự mã hóa biến phân \\
MLP & Multi-Layer Perceptron & Mạng truyền thẳng đa tầng \\
MSE & Mean Squared Error & Sai số bình phương trung bình \\
CE & Cross-Entropy & Độ mất mát entropy chéo \\
VUS-ROC & Volume Under the Surface of ROC & Thể tích dưới mặt cong ROC tích phân theo vùng đệm trễ \\
VUS-PR & Volume Under the Surface of PR & Thể tích dưới mặt cong Precision-Recall \\
RF / Range-F1 & Range-based F1 Score & Điểm F1 đánh giá theo đoạn thời gian \\
SMD & Server Machine Dataset & Bộ dữ liệu giám sát cụm máy chủ (28 máy, 38 chiều) \\
IOPS & AIOps KPI Challenge Dataset & Bộ dữ liệu chỉ số hiệu năng dịch vụ mạng Internet \\
SMAP & Soil Moisture Active Passive & Dữ liệu viễn thám độ ẩm đất vệ tinh NASA \\
MSL & Mars Science Laboratory & Dữ liệu kỹ thuật xe tự hành Curiosity thám hiểm Sao Hỏa \\
UCR & University of California Riverside & Bộ lưu trữ dữ liệu kiểm chuẩn chuỗi thời gian UCR \\
AMP & Automatic Mixed Precision & Kỹ thuật huấn luyện độ chính xác hỗn hợp tự động \\
XAI & Explainable Artificial Intelligence & Trí tuệ nhân tạo có thể giải thích được \\
\bottomrule
\end{tabular}
\end{table}

\vspace{0.8cm}

\begin{table}[htbp]
\centering
\caption{Danh mục ký hiệu toán học quy chuẩn trong báo cáo}
\label{tab:notations}
\begin{tabular}{cp{12.0cm}}
\toprule
\textbf{Ký hiệu} & \textbf{Ý nghĩa toán học} \\
\midrule
$X \in \mathbb{R}^{T \times D}$ & Ma trận chuỗi thời gian quan sát gồm $T$ bước thời gian và $D$ kênh thuộc tính / cảm biến. \\
$W$ & Độ dài cửa sổ trượt thời gian (mặc định $W = 100$). \\
$s$ & Bước trượt giữa các cửa sổ kế tiếp ($s=1$ trên Stock/UCR, $s=10$ trên SMD/IOPS/SMAP/MSL). \\
$B$ & Kích thước batch huấn luyện (mặc định $B = 128$ mẫu cửa sổ trượt). \\
$M \in \{0, 1\}^{W \times D}$ & Mặt nạ nhị phân tái tạo ($M=0$ tại các điểm bị biến dạng giả lập, $M=1$ tại các điểm sạch). \\
$C$ & Số lượng lớp phân loại hình thái bất thường ($C = 12$, gồm 1 lớp Normal và 11 lớp giả lập). \\
$z \in \mathbb{R}^{B \times 128}$ & Vector đặc trưng tiềm ẩn nén tại cổ chai mạng ConvAEC. \\
$\lambda$ & Hệ số cân bằng giữa hàm mất mát tái tạo và phân loại (mặc định $\lambda = 0.1$). \\
$\alpha, \beta$ & Tham số làm mượt nhãn bất đối xứng ($\alpha = 0.1$ cho Normal, $\beta = 0.01$ cho các lớp còn lại). \\
$\theta_{\text{bg}}$ & Ngưỡng lọc tần suất lớp nền ngẫu nhiên toàn chuỗi (mặc định $\theta_{\text{bg}} = 0.05$). \\
$\text{Score}(t)$ & Điểm bất thường tổng hợp cuối cùng tại bước thời gian $t \in [0, 1]$. \\
\bottomrule
\end{tabular}
\end{table}

\newpage
\tableofcontents
\newpage
\listoftables
\newpage
\listoffigures
\newpage

\pagenumbering{arabic}



% =========================================================================
"""
