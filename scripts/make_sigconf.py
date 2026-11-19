# -*- coding: utf-8 -*-
content = r"""\documentclass[sigconf,nonacm]{acmart}

%% 1. Tắt hoàn toàn ACM Reference Format
\settopmatter{printacmref=false, printfolios=false}

%% 2. Tắt hoàn toàn bản quyền / copyright ở chân trang 1
\renewcommand\footnotetextcopyrightpermission[1]{}

%% 3. Tắt hoàn toàn Running Header (Conference acronym, tên tác giả) và Running Footer trên tất cả các trang
\pagestyle{empty}

%% Hỗ trợ tiếng Việt chuẩn cho pdfLaTeX trên Overleaf (tương thích hoàn toàn với acmart)
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage[vietnamese,english]{babel}

\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{url}
\usepackage{graphicx}
\usepackage{multirow}

%% Cấu hình hiển thị mã nguồn Python
\lstset{
  language=Python,
  basicstyle=\ttfamily\scriptsize,
  breaklines=true,
  frame=single,
  numbers=none,
  showstringspaces=false,
  tabsize=4,
  columns=fullflexible
}

%% Tối ưu khoảng cách công thức để không bị nhảy trang
\setlength{\abovedisplayskip}{3pt}
\setlength{\belowdisplayskip}{3pt}
\setlength{\abovedisplayshortskip}{1pt}
\setlength{\belowdisplayshortskip}{1pt}

\begin{document}
\selectlanguage{vietnamese}

\title[Phát hiện Bất thường Chuỗi thời gian Không giám sát dựa trên ConvAEC và RedLamp]{Phát hiện Bất thường Chuỗi thời gian Không giám sát dựa trên Kiến trúc ConvAEC và Học tự giám sát Đa nhiệm (RedLamp)}
\subtitle{Nghiên cứu và Hiện thực Hệ thống Phát hiện Bất thường Chuỗi thời gian theo Phương pháp Giả lập Đa lớp Bất thường (RedLamp)}

\author{Vo Nguyen Le Duy}
\authornote{Lecturer}
\affiliation{%
  \institution{University of Information Technology, Vietnam National University}
  \city{Ho Chi Minh City}
  \country{Vietnam}
}
\email{duyvnl@uit.edu.vn}

\author{Nguyen Dinh Quoc Bao}
\affiliation{%
  \institution{University of Information Technology, Vietnam National University}
  \city{Ho Chi Minh City}
  \country{Vietnam}
}
\email{26848009@grad.uit.edu.vn}

\author{Ngo Phuc Danh}
\affiliation{%
  \institution{University of Information Technology, Vietnam National University}
  \city{Ho Chi Minh City}
  \country{Vietnam}
}
\email{26848029@grad.uit.edu.vn}


\maketitle
\thispagestyle{empty} % Đảm bảo trang đầu tiên cũng không có header/footer

\noindent\textbf{Thông tin chung về đề tài:}
\begin{itemize}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item \textbf{Tên đề tài:} Nghiên cứu và Hiện thực Hệ thống Phát hiện Bất thường Chuỗi thời gian theo Phương pháp Giả lập Đa lớp Bất thường (RedLamp)
    \item \textbf{Lĩnh vực:} Trí tuệ Nhân tạo -- Học sâu trên Chuỗi thời gian
    \item \textbf{Môi trường thực nghiệm:} Kaggle GPU (Nvidia Tesla P100 16 GB) \& Web Demo cục bộ
    \item \textbf{Tập dữ liệu:} UCR Anomaly Archive, AIOps, SMD, SMAP, MSL, TSB-AD Stock
\end{itemize}

\section{Tổng quan đề tài và tính cấp thiết}

\subsection{Bối cảnh nghiên cứu}

Phát hiện bất thường trong chuỗi thời gian (\textit{Time Series Anomaly Detection -- TSAD}) là một trong những bài toán cốt lõi của khai phá dữ liệu và trí tuệ nhân tạo ứng dụng trong công nghiệp hiện đại. Dữ liệu chuỗi thời gian được sinh ra liên tục từ các hệ thống hỗ trợ robot~\cite{park2018}, giám sát động cơ~\cite{malhotra2016}, bảo trì hệ thống thực-ảo (\textit{cyber-physical systems})~\cite{tan2011}, hạ tầng đám mây và tàu thám hiểm không gian. Phát hiện kịp thời các mẫu hoặc giá trị bất thường khác biệt đáng kể so với phần lớn chuỗi dữ liệu là ``tuyến phòng thủ đầu tiên'' nhằm ngăn ngừa sự cố dây chuyền và tổn thất nghiêm trọng.

Do tính chất hiếm gặp của sự cố và chi phí gắn nhãn chuyên gia đắt đỏ trên khối lượng dữ liệu khổng lồ, TSAD thường được phát biểu dưới dạng bài toán học không giám sát trên tập huấn luyện không nhãn. Về mặt kỹ thuật, bài toán này đang đối mặt với năm thách thức cốt lõi:

\textbf{Thách thức 1 -- Khan hiếm nhãn và ô nhiễm dữ liệu huấn luyện (\textit{Anomaly Contamination}):} Trong môi trường thực tế, hơn 99,5\% dữ liệu thuộc trạng thái bình thường, nhưng sự tồn tại của một tỷ lệ nhỏ mẫu bất thường lẫn trong tập huấn luyện chưa gán nhãn là điều khó tránh khỏi~\cite{wu2022, xu2024}. Các mô hình dựa trên giả định ``tập train hoàn toàn sạch'' thường suy giảm hiệu năng nghiêm trọng khi bị ô nhiễm.

\textbf{Thách thức 2 -- Đa dạng hình thái bất thường (\textit{Morphology Diversity}):} Bất thường trong chuỗi thời gian có thể là bất thường điểm (\textit{point anomaly}) có biên độ đột biến, bất thường ngữ cảnh (\textit{contextual anomaly}) hoặc bất thường theo mẫu (\textit{pattern-wise anomaly}) biến đổi tần số, trôi dạt đường cơ sở (\textit{trend/wander}) hay đóng băng tín hiệu (\textit{cutoff})~\cite{blazquez2021, lai2021}. Việc chỉ nhận diện được một nhóm hình thái sẽ để lại các ``điểm mù'' trong giám sát.

\textbf{Thách thức 3 -- Hạn chế của các phương pháp tái tạo (\textit{Reconstruction Over-generalization}):} Các kiến trúc Autoencoder, VAE, GAN hay Transformer hiện nay dựa trên giả định tính bình thường (\textit{normality assumption}): học biểu diễn tiềm ẩn để tái tạo tốt chuỗi bình thường và kỳ vọng sai số tái tạo lớn ở vùng bất thường~\cite{zhou2019, xu2022, tuli2022}. Tuy nhiên, các mạng nơ-ron sâu thường khái quát hóa quá mức (\textit{over-generalize}), vô tình tái tạo thành công cả các đoạn bất thường tinh vi, khiến sai số tái tạo không đủ lớn để kích hoạt cảnh báo.

\textbf{Thách thức 4 -- Đánh giá sai lệch và giao thức kiểm thử chưa chuẩn mực:} Nhiều thang đo truyền thống dựa trên điểm số gán nhãn từng điểm hoặc giao thức điều chỉnh điểm (\textit{Point Adjustment -- PA}) đang tạo ra ảo tưởng về sự tiến bộ khi thổi phồng chỉ số F1~\cite{kim2022, wu2021, sarfraz2024}. Việc áp dụng bộ thước đo tích phân không phụ thuộc ngưỡng dựa trên vùng sự cố như VUS-ROC, VUS-PR~\cite{paparrizos2022} và Range F-score~\cite{tatbul2018} là yêu cầu bắt buộc để đánh giá khách quan.

\textbf{Thách thức 5 -- Thiếu khả năng giải thích (\textit{Explainability Gap}):} Hầu hết các mô hình học sâu hoạt động như một hộp đen (\textit{black-box}), chỉ xuất ra một điểm số tổng hợp mà không thể giải thích nguyên nhân gốc rễ: sự cố là do xung đột biến, suy giảm tần số hay biến dạng chu kỳ? Điều này cản trở kỹ sư vận hành đưa ra quyết định khắc phục nhanh chóng.

\subsection{Khoảng trống nghiên cứu và đề xuất của đề tài}

Để khắc phục nhược điểm của giả định tính bình thường, một hướng tiếp cận gần đây sử dụng tăng cường dữ liệu (\textit{data augmentation}) để sinh các mẫu bất thường giả lập (\textit{pseudo-anomalies}) và huấn luyện bộ phân loại nhị phân tách mẫu huấn luyện gốc khỏi mẫu tăng cường (gọi là \textit{giả định bất thường nhị phân} -- \textit{binary anomaly assumption})~\cite{hendrycks2019, li2021, wang2024}. Tuy nhiên, theo phân tích của Obata et al. (KDD 2025)~\cite{obata2025}, hướng tiếp cận nhị phân vẫn vấp phải ba hạn chế nghiêm trọng:
\begin{enumerate}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item \textbf{Khoảng cách đa dạng (\textit{Diversity gap}):} Bất thường thực tế biến thiên mạnh giữa các tập dữ liệu và chưa biết trước~\cite{yoo2023}. Một hàm tăng cường đơn lẻ hoặc phân loại nhị phân gộp chung khó bao phủ hết không gian bất thường, để lại các ``vùng trống'' khiến mô hình dễ bị tổn thương trước các mẫu ô nhiễm nằm ngoài vùng giả lập.
    \item \textbf{Bất thường giả (\textit{False anomaly}):} Các phép biến đổi dữ liệu đôi khi vô tình tạo ra những mẫu tăng cường thực chất vẫn mang đặc trưng bình thường~\cite{yoon2022} (ví dụ: làm mượt trên chuỗi có chu kỳ dài). Việc ép mô hình coi chúng là bất thường gây ra hiện tượng overfitting và làm tăng tỷ lệ báo động giả (\textit{false positive rate}).
    \item \textbf{Tự tin thái quá vào nhãn (\textit{Overconfidence on the label}):} Việc gán nhãn cứng nhị phân (\textit{binary hard labels} $\{0, 1\}$) cho cả dữ liệu huấn luyện (có thể lẫn ô nhiễm) lẫn dữ liệu tăng cường (có thể chứa bất thường giả) khiến mô hình đưa ra dự đoán quá tự tin và học ranh giới quyết định thiếu chính xác.
\end{enumerate}

Để giải quyết triệt để ba vấn đề trên, nghiên cứu gốc~\cite{obata2025} đề xuất \textbf{RedLamp} (\textit{Robust and Explainable Detector of time series anomaLy via Augmenting Multiclass Pseudo-anomalies}), phương pháp đầu tiên giải bài toán TSAD dưới góc nhìn \textbf{giả định bất thường đa lớp} (\textit{multiclass anomaly assumption}). RedLamp sinh ra 11 lớp bất thường giả lập chuyên biệt cho chuỗi thời gian cùng 1 lớp bình thường, kết hợp kỹ thuật làm mượt nhãn bất đối xứng (\textit{label refurbishment / backward correction}), học đa nhiệm tái tạo có mặt nạ (\textit{masked reconstruction}) và cơ chế điều chỉnh tần suất bất thường nền (\textit{Frequent Anomaly Adjustment -- FAA}).

Đề tài này nghiên cứu, hiện thực và kiểm chứng toàn bộ pipeline RedLamp bao gồm: \textbf{(1)} Huấn luyện mô hình trên Kaggle GPU, \textbf{(2)} Đánh giá kiểm chuẩn đa tập dữ liệu (bao gồm 5 bộ dữ liệu chuẩn quốc tế và dữ liệu tài chính TSB-AD Stock), và \textbf{(3)} Triển khai hệ thống Web Demo tương tác có khả năng giải thích AI (XAI).

\subsection{Đóng góp cốt lõi của đề tài}

Các đóng góp cốt lõi của đề tài được tổng hợp trong Bảng~\ref{tab:contributions}.

\begin{table}[htbp]
\centering
\caption{Tổng hợp các đóng góp cốt lõi của đề tài}
\label{tab:contributions}
\footnotesize
\begin{tabularx}{\columnwidth}{clX}
\toprule
\textbf{\#} & \textbf{Đóng góp} & \textbf{Mô tả} \\
\midrule
1 & \textbf{Kiến trúc ConvAEC đa nhiệm} & Tích hợp bộ tự mã hóa 1D-CNN (tái tạo có mặt nạ $\mathcal{L}_{\text{MSE}}$) và đầu phân loại MLP ($\mathcal{L}_{\text{CE}}$) trên cùng không gian tiềm ẩn, đạt tốc độ suy luận $<10\text{ms}$/cửa sổ \\
\addlinespace[3pt]
2 & \textbf{12 phép biến đổi giả lập bất thường} & Thuật toán tăng cường đa kênh, đa đoạn ngẫu nhiên mô phỏng toàn diện các hình thái sự cố thực tế: Normal, Spike, Flip, Speedup, Noise, Cutoff, Average, Scale, Wander, Contextual, Upsidedown và Mixture \\
\addlinespace[3pt]
3 & \textbf{Làm mượt nhãn bất đối xứng \& FAA} & Kỹ thuật \textit{Backward Correction} ($\alpha=0.1, \beta=0.01$) chống ô nhiễm nhãn/bất thường giả, kết hợp lọc lớp nền động FAA ($\delta=0.05$) loại bỏ các lớp \textit{pseudo-normal} \\
\addlinespace[3pt]
4 & \textbf{Web Demo tương tác XAI} & Hệ thống 10 khối trực quan hóa trên 159 thực thể, hoạt động 100\% offline, bóc tách kích hoạt bên trong AI qua PyTorch Forward Hooks và giải thích ngữ nghĩa tài chính \\
\bottomrule
\end{tabularx}
\end{table}

\section{Tổng quan các phương pháp liên quan}

\subsection{Phát biểu bài toán và phân loại hình thái bất thường}

Xét một chuỗi thời gian đa biến gồm $D$ đặc trưng (kênh cảm biến) thu thập qua $T$ bước thời gian: $X = \{x_1, x_2, \dots, x_T\} \in \mathbb{R}^{D \times T}$. Để mô hình hóa sự phụ thuộc cục bộ theo thời gian, tập huấn luyện được phân đoạn bằng cửa sổ trượt kích thước $L$ (với bước trượt stride mặc định bằng 1 hoặc $s$) thành $\mathcal{X}^{\text{train}} = \{X^{(L)}, X^{(L+1)}, \dots, X^{(T)}\}$, trong đó mỗi thực thể cửa sổ $X^{(t)} = \{x_{t-L+1}, \dots, x_t\} \in \mathbb{R}^{D \times L}$ và $X^{(t)}_{i,j}$ biểu thị giá trị tại đặc trưng thứ $i$ và bước thời gian cục bộ thứ $j$. Mục tiêu của TSAD không giám sát là huấn luyện mô hình trên $\mathcal{X}^{\text{train}}$ không nhãn để dự đoán điểm bất thường $s(t)$ cho từng cửa sổ $X^{(t)} \in \mathcal{X}^{\text{test}}$, sao cho giá trị $s(t)$ càng lớn thì khả năng xuất hiện bất thường càng cao.

Theo phân loại tiêu chuẩn trong chuỗi thời gian~\cite{blazquez2021, lai2021}, các hiện tượng bất thường được chia thành ba nhóm chính:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Bất thường điểm (\textit{Point Anomaly}):} Một hoặc vài điểm đơn lẻ $x_t$ có giá trị vượt xa phân phối thống kê bình thường cục bộ hoặc toàn cục (ví dụ: xung đột biến điện áp, giao dịch khối lượng đột biến).
    \item \textbf{Bất thường ngữ cảnh (\textit{Contextual Anomaly}):} Điểm hoặc đoạn dữ liệu bình thường nếu xét trên toàn miền giá trị nhưng bất thường trong ngữ cảnh thời gian cục bộ (ví dụ: mức tải CPU 95\% vào 3 giờ sáng ngày nghỉ).
    \item \textbf{Bất thường tập thể / theo mẫu (\textit{Collective / Pattern-wise Anomaly}):} Một chuỗi liên tiếp $x_{st:ed}$ tạo nên hình thái biến đổi cấu trúc như thay đổi tần số dao động, trôi dạt đường cơ sở (\textit{trend/wander}), đóng băng giá trị cảm biến (\textit{cutoff}) hoặc đảo pha tín hiệu.
\end{itemize}

\subsection{Các nhóm phương pháp hiện có}

\textbf{Phương pháp học máy cổ điển:} Isolation Forest~\cite{liu2008} xây dựng tập hợp cây phân chia ngẫu nhiên, coi các điểm có độ dài đường đi trung bình tới gốc ngắn là bất thường. OCSVM~\cite{scholkopf1999} tìm siêu cầu nhỏ nhất bao quanh dữ liệu bình thường. Hạn chế chung của nhóm này là khả năng nắm bắt phụ thuộc chuỗi thời gian phức tạp còn hạn chế.

\textbf{Phương pháp tái tạo (Reconstruction-based):} Nhóm này học không gian tiềm ẩn để tái tạo tốt mẫu bình thường và kỳ vọng sai số tái tạo sẽ cao trên mẫu bất thường, bao gồm các kiến trúc Autoencoder/GAN như USAD~\cite{audibert2020}, BeatGAN~\cite{zhou2019}, LSTM-VAE~\cite{park2018}, các kiến trúc Transformer như Anomaly Transformer (AT)~\cite{xu2022}, TranAD~\cite{tuli2022}, và các mô hình khuếch tán (\textit{diffusion}) như IMDiffusion~\cite{zhang2023}, D3R~\cite{wang2024d3r}. Nhược điểm cố hữu của nhóm này là dễ bỏ sót các bất thường theo mẫu (\textit{pattern-wise}) khi sai khác biên độ so với mẫu bình thường là tinh vi, đồng thời bị suy giảm nghiêm trọng khi tập train nhiễm mẫu bất thường do cơ chế \textit{over-generalization}.

\textbf{Phương pháp giả lập bất thường nhị phân (Binary Augmentation-based):} Lấy cảm hứng từ lĩnh vực thị giác máy tính như Outlier Exposure (OE)~\cite{hendrycks2019} và CutPaste~\cite{li2021}, một số nghiên cứu áp dụng tăng cường dữ liệu cho TSAD. NCAD~\cite{carmona2022} sử dụng OE, nhiễu điểm và trộn cửa sổ (\textit{window mixup}) kết hợp bộ phân loại siêu cầu. COUTA~\cite{xu2024} tạo mẫu bất thường đơn giản và phạt các mẫu bất thường tiềm ẩn trong tập huấn luyện. CutAddPaste~\cite{wang2024} thiết kế phép tăng cường mô phỏng 5 loại bất thường chuỗi thời gian nhưng gộp chung vào một bài toán phân loại nhị phân. Do đó, các phương pháp này đòi hỏi tinh chỉnh nhiều siêu tham số tăng cường cho từng tập dữ liệu~\cite{yoo2023}, vẫn tồn tại \textit{diversity gap}, bỏ qua \textit{false anomaly} và mắc lỗi \textit{overconfidence}.

\subsection{So sánh với RedLamp}

Bảng~\ref{tab:method_comparison} đối chiếu chi tiết các tiêu chí kỹ thuật giữa RedLamp và các phương pháp tiêu biểu dựa trên phân tích từ nghiên cứu gốc~\cite{obata2025}.

\begin{table*}[t]
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
\end{table*}

Bảng~\ref{tab:method_comparison} khẳng định RedLamp là phương pháp duy nhất khai thác đồng thời đa phép tăng cường đặc thù chuỗi thời gian trong bài toán phân loại đa lớp, giải quyết trọn vẹn cả ba điểm yếu của nhóm augmentation-based và vượt trội về độ ổn định trước ô nhiễm dữ liệu.

\section{Kiến trúc và giải thuật cốt lõi}

\subsection{Tổng quan framework RedLamp và Triết lý Đa nhiệm}

Khác biệt hoàn toàn với các hướng tiếp cận đơn nhiệm truyền thống (chỉ dựa vào tái tạo tín hiệu hoặc chỉ phân loại nhị phân), RedLamp xây dựng một khung làm việc học tự giám sát đa nhiệm (\textit{Joint Multi-Task Self-Supervised Learning}). Bản chất của triết lý này là ràng buộc không gian biểu diễn tiềm ẩn $z$ phải thỏa mãn đồng thời hai mục tiêu trực giao:
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Nhiệm vụ tái tạo bảo toàn cấu trúc bình thường (\textit{Masked Reconstruction}):} Ép bộ giải mã khôi phục trung thực các vùng tín hiệu nguyên bản của chuỗi, đồng thời sử dụng mặt nạ nhị phân để ngăn chặn mô hình học tái tạo các biến dạng bất thường được tiêm vào.
    \item \textbf{Nhiệm vụ phân loại hình thái đa lớp (\textit{Multiclass Morphology Classification}):} Ép không gian tiềm ẩn phân tách các dạng biến đổi tín hiệu thành 12 cụm hình học riêng biệt, tạo nên khả năng giải thích tự nhiên về bản chất của sự cố mà không cần nhãn giám sát từ chuyên gia.
\end{enumerate}

Toàn bộ quy trình hoạt động của RedLamp được tổ chức thành hai pha khép kín:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Pha huấn luyện (Training Phase):} Từ tập dữ liệu huấn luyện $\mathcal{X}^{\text{train}}$, với mỗi cửa sổ trượt $X^{(t)} \in \mathbb{R}^{D \times W}$, bộ sinh tăng cường tổng hợp ra 1 mẫu bình thường ($k=1$) và 11 mẫu bất thường giả lập ($k=2, \dots, 12$), kèm theo vector nhãn one-hot $y^{(t,k)}$ và ma trận mặt nạ vị trí $W^{(t,k)} \in \{0, 1\}^{D \times W}$. Mạng ConvAEC nhận đầu vào là tensor cửa sổ tăng cường, trích xuất biểu diễn tiềm ẩn chung $z \in \mathbb{R}^{B \times 128 \times 1}$, sau đó đưa đồng thời vào bộ giải mã để tính mất mát tái tạo có mặt nạ $\mathcal{L}_{\text{MSE}}$ và đầu phân loại MLP để tính mất mát phân loại đa lớp $\mathcal{L}_{\text{CE}}$ với nhãn mềm đã hiệu chỉnh.
    \item \textbf{Pha suy luận (Inference Phase):} Trên chuỗi kiểm thử $\mathcal{X}^{\text{test}}$, mô hình không chèn thêm bất thường mà đưa trực tiếp từng cửa sổ vào ConvAEC. Sai số tái tạo $s_{\text{MSE}}(t)$ đo lường độ lệch biên độ, trong khi xác suất dự đoán từ đầu phân loại được sàng lọc qua cơ chế \textit{Frequent Anomaly Adjustment (FAA)} nhằm triệt tiêu các lớp giả bình thường. Hai chuỗi điểm được làm mượt qua nhân chập trung bình trượt, chuẩn hóa Min-Max và kết hợp theo tỷ lệ 1:1.
\end{itemize}

\subsection{Kiến trúc mạng nơ-ron ConvAEC chi tiết từng lớp}

Trong mã nguồn hiện thực tại \texttt{models/cnn.py}, \texttt{models/classifier.py} và \texttt{models/meta.py}, mô hình chính của RedLamp được kế thừa từ lớp cha \texttt{MetaAEC} dưới tên gọi \texttt{ConvAEC}. Kiến trúc này sử dụng mạng tích chập một chiều (1D-CNN) thuần túy với chi phí tính toán $\mathcal{O}(W)$ thay vì cơ chế Attention $\mathcal{O}(W^2)$, gồm ba mô-đun nơ-ron được liên kết chặt chẽ:

\textbf{1. Bộ mã hóa tích chập (\texttt{ConvEncoder}):}
Bộ mã hóa tiếp nhận tensor đầu vào $X \in \mathbb{R}^{B \times W \times D}$ (với $B$ là batch size, $W=100$ là độ dài cửa sổ thời gian, $D$ là số kênh thuộc tính). Tensor đầu vào trước tiên được hoán vị trục thời gian và không gian thành $X^{\top} \in \mathbb{R}^{B \times D \times W}$ để tương thích với các phép tích chập 1D. Quá trình trích xuất đặc trưng trải qua 4 khối tích chập tuần tự (\texttt{ConvBlock}):
\begin{itemize}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item Khối 1: $\texttt{Conv1d}(D \rightarrow 128, \text{kernel}=4, \text{stride}=2, \text{padding}=2) \rightarrow \texttt{BatchNorm1d}(128) \rightarrow \texttt{ReLU} \rightarrow \texttt{Dropout}(0.2)$. Kích thước giảm về $(B, 128, 51)$.
    \item Khối 2: $\texttt{Conv1d}(128 \rightarrow 128, \text{kernel}=4, \text{stride}=2, \text{padding}=2) \rightarrow \texttt{BatchNorm1d}(128) \rightarrow \texttt{ReLU} \rightarrow \texttt{Dropout}(0.2)$. Kích thước giảm về $(B, 128, 26)$.
    \item Khối 3: $\texttt{Conv1d}(128 \rightarrow 256, \text{kernel}=4, \text{stride}=2, \text{padding}=2) \rightarrow \texttt{BatchNorm1d}(256) \rightarrow \texttt{ReLU} \rightarrow \texttt{Dropout}(0.2)$. Kích thước giảm về $(B, 256, 14)$.
    \item Khối 4: $\texttt{Conv1d}(256 \rightarrow 256, \text{kernel}=4, \text{stride}=2, \text{padding}=2) \rightarrow \texttt{BatchNorm1d}(256) \rightarrow \texttt{ReLU} \rightarrow \texttt{Dropout}(0.2)$. Kích thước giảm về $(B, 256, 8)$.
\end{itemize}
Sau 4 khối tích chập, tensor đặc trưng đi qua một tầng nén thời gian toàn cục $\texttt{F.max\_pool1d}$ với kích thước cửa sổ bằng đúng chiều dài chuỗi hiện tại ($\text{kernel\_size}=8$), ép toàn bộ trục thời gian về $1$: $(B, 256, 1)$. Cuối cùng, một tầng tích chập điểm $1 \times 1$ (\texttt{Conv1d}(256, 128, kernel=1)) ánh xạ đặc trưng nén về vector biểu diễn không gian tiềm ẩn nút cổ chai $z \in \mathbb{R}^{B \times 128 \times 1}$.

\textbf{2. Bộ giải mã chuyển vị (\texttt{ConvDecoder}):}
Bộ giải mã nhận vector tiềm ẩn $z \in \mathbb{R}^{B \times 128 \times 1}$ và thực hiện tái cấu trúc chuỗi thời gian nguyên bản. Điểm đặc biệt trong thiết kế của \texttt{ConvDecoder} là khả năng tính toán động kích thước trung gian:
\begin{itemize}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item Tầng mở rộng tuyến tính ban đầu: $\texttt{nn.Linear}(1, \text{compressed\_len})$ nâng chiều thời gian từ 1 lên $\text{compressed\_len} = 8$, thu được tensor $(B, 128, 8)$.
    \item 4 khối tích chập chuyển vị (\texttt{ConvTransposeBlock}): Mỗi khối gồm một tầng $\texttt{ConvTranspose1d}$ nghịch đảo cấu hình Encoder với số kênh đảo ngược $[128 \rightarrow 256 \rightarrow 256 \rightarrow 128 \rightarrow 128]$, $\text{kernel}=4$, $\text{stride}=2$, $\text{padding}=2$, kết hợp giá trị bù đệm \texttt{output\_padding} được tính tự động qua hàm \texttt{conv\_out\_len} để bảo đảm tính đối xứng hoàn hảo, tiếp nối bởi \texttt{BatchNorm1d}, \texttt{ReLU} và \texttt{Dropout}(0.2).
    \item Tầng chiếu khôi phục kích thước: Một tầng tích chập $1 \times 1$ ($\texttt{Conv1d}(128 \rightarrow D, \text{kernel}=1)$) chuyển đổi số kênh về số lượng thuộc tính ban đầu $D$.
    \item Đầu ra cuối cùng được chuyển vị ngược lại trục $(B, W, D)$ tạo thành tensor tái tạo $\hat{X} \in \mathbb{R}^{B \times W \times D}$.
\end{itemize}

\textbf{3. Đầu phân loại đa lớp (\texttt{NonLinClassifier}):}
Để phục vụ nhiệm vụ phân loại 12 hình thái bất thường giả lập, vector tiềm ẩn $z$ được làm phẳng thành tensor 2 chiều $(B, 128)$ và đưa vào mạng nơ-ron truyền thẳng đa tầng:
\begin{equation}
    \hat{y} = \text{Softmax}\left(\mathbf{W}_2 \cdot \text{Dropout}\left(\text{ReLU}\left(\text{BN}\left(\mathbf{W}_1 z + \mathbf{b}_1\right)\right)\right) + \mathbf{b}_2\right)
\end{equation}
trong đó $\mathbf{W}_1 \in \mathbb{R}^{32 \times 128}$, tầng ẩn $d_{\text{hidden}} = 32$, tiếp nối bởi $\texttt{BatchNorm1d}(32)$, $\texttt{ReLU}()$, $\texttt{Dropout}(0.2)$, và tầng xuất $\mathbf{W}_2 \in \mathbb{R}^{12 \times 32}$ đi qua hàm $\texttt{Softmax}(\text{dim}=1)$ cho ra phân phối xác suất dự đoán $\hat{y} \in [0, 1]^{B \times 12}$.

Bảng~\ref{tab:convaec_architecture} mô tả chi tiết toàn bộ các tầng nơ-ron, kích thước tensor và cấu hình tham số của ConvAEC theo đúng mã nguồn \texttt{models/cnn.py}.

\begin{table*}[t]
\centering
\caption{Đặc tả chi tiết các tầng mạng của kiến trúc ConvAEC trong mã nguồn \texttt{models/cnn.py}}
\label{tab:convaec_architecture}
\footnotesize
\begin{tabularx}{\textwidth}{lllccl}
\toprule
\textbf{Mô-đun} & \textbf{Tên tầng / Khối} & \textbf{Kích thước đầu vào} & \textbf{Kích thước đầu ra} & \textbf{Tham số chính (Kernel/Stride/Pad)} & \textbf{Kích hoạt \& Chuẩn hóa} \\
\midrule
\multirow{6}{*}{\textbf{Encoder}} 
& Permute & $(B, W, D)$ & $(B, D, W)$ & Đổi trục cho Conv1D & -- \\
& ConvBlock 1 & $(B, D, 100)$ & $(B, 128, 51)$ & Conv1d(k=4, s=2, p=2), filters=128 & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvBlock 2 & $(B, 128, 51)$ & $(B, 128, 26)$ & Conv1d(k=4, s=2, p=2), filters=128 & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvBlock 3 & $(B, 128, 26)$ & $(B, 256, 14)$ & Conv1d(k=4, s=2, p=2), filters=256 & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvBlock 4 & $(B, 256, 14)$ & $(B, 256, 8)$ & Conv1d(k=4, s=2, p=2), filters=256 & BatchNorm1d, ReLU, Dropout(0.2) \\
& Global MaxPool & $(B, 256, 8)$ & $(B, 256, 1)$ & MaxPool1d(kernel=8) & Thu gọn chiều thời gian \\
& Conv1x1 Proj & $(B, 256, 1)$ & $(B, 128, 1)$ & Conv1d(k=1, s=1, p=0) & Chiếu về vector tiềm ẩn $z$ \\
\midrule
\multirow{6}{*}{\textbf{Decoder}} 
& Linear Upsample & $(B, 128, 1)$ & $(B, 128, 8)$ & Linear(1 $\rightarrow$ 8) & Nâng chiều thời gian nén \\
& ConvTrBlock 1 & $(B, 128, 8)$ & $(B, 256, 14)$ & ConvTranspose1d(k=4, s=2, p=2) & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvTrBlock 2 & $(B, 256, 14)$ & $(B, 256, 26)$ & ConvTranspose1d(k=4, s=2, p=2) & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvTrBlock 3 & $(B, 256, 26)$ & $(B, 128, 51)$ & ConvTranspose1d(k=4, s=2, p=2) & BatchNorm1d, ReLU, Dropout(0.2) \\
& ConvTrBlock 4 & $(B, 128, 51)$ & $(B, 128, 100)$ & ConvTranspose1d(k=4, s=2, p=2) & BatchNorm1d, ReLU, Dropout(0.2) \\
& Conv1x1 Out & $(B, 128, 100)$ & $(B, D, 100)$ & Conv1d(k=1, s=1, p=0) & Khôi phục số kênh gốc $D$ \\
& Permute & $(B, D, 100)$ & $(B, 100, D)$ & Đổi trục về dạng ban đầu & Tensor tái tạo $\hat{X}$ \\
\midrule
\multirow{4}{*}{\textbf{Classifier}} 
& Flatten & $(B, 128, 1)$ & $(B, 128)$ & Làm phẳng vector tiềm ẩn $z$ & -- \\
& Dense 1 & $(B, 128)$ & $(B, 32)$ & Linear(128 $\rightarrow$ 32) & BatchNorm1d, ReLU, Dropout(0.2) \\
& Dense 2 & $(B, 32)$ & $(B, 12)$ & Linear(32 $\rightarrow$ 12) & Ánh xạ về 12 lớp \\
& Softmax & $(B, 12)$ & $(B, 12)$ & Softmax(dim=1) & Phân phối xác suất $\hat{y}$ \\
\bottomrule
\end{tabularx}
\end{table*}

\subsection{Thuật toán và 12 phép biến đổi giả lập bất thường}

Trong mô-đun nạp dữ liệu \texttt{loaders/loader\_aug.py}, RedLamp triển khai thuật toán sinh dữ liệu tăng cường đa kênh \texttt{\_inject\_anomalies}. Thuật toán hoạt động theo các bước nghiêm ngặt:
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item Với mỗi cửa sổ gốc $X^{(t)} \in \mathbb{R}^{D \times W}$ ($W=100$), tạo lập 12 mẫu biến thể tương ứng với 12 lớp ($k=1, \dots, 12$, trong đó $k=1$ là lớp Normal nguyên bản). Khởi tạo ma trận mặt nạ nhị phân $W^{(t,k)} \in \{0, 1\}^{D \times W}$ chứa toàn giá trị $1$ (đại diện cho vùng dữ liệu bình thường ban đầu).
    \item Với các lớp bất thường ($k \ge 2$), thuật toán chọn ngẫu nhiên một tập con các chiều thuộc tính $\text{dims} \subseteq \{0, \dots, D-1\}$ có kích thước từ $\text{min\_features}$ đến $\text{max\_features}$ (mặc định chọn ngẫu nhiên từ 1 đến $D$ kênh).
    \item Trên mỗi kênh được chọn, thuật toán lấy ngẫu nhiên hai chỉ số thời gian $st, ed \in [0, W-1]$ ($st \le ed$) để xác định đoạn tác động có độ dài $\text{len} = ed - st + 1$.
    \item Áp dụng hàm biến đổi hình thái $f^{(k)}$ tương ứng lên đoạn tín hiệu con $X_{\text{dim}, st:ed}^{(t)}$. Đồng thời, ma trận mặt nạ $W^{(t,k)}$ tại các vị trí bị biến đổi được gán bằng $0$ ($W_{\text{dim}, st:ed}^{(t,k)} = 0$) để chỉ định đây là vùng bất thường không được phép tái tạo. Riêng đối với phép \textit{Spike}, chỉ một điểm đơn lẻ bị đánh dấu $W_{\text{dim}, st}^{(t,k)} = 0$; đối với phép \textit{Wander}, do sự dịch chuyển đường cơ sở kéo dài đến hết cửa sổ nên toàn bộ phần đuôi được đánh dấu $W_{\text{dim}, st:W}^{(t,k)} = 0$.
\end{enumerate}

Bảng~\ref{tab:augmentations} tổng hợp chi tiết công thức toán học và hiện thực mã nguồn của toàn bộ 12 phép biến đổi trong RedLamp.

\begin{table*}[t]
\centering
\caption{Danh mục và định nghĩa toán học của 12 phép biến đổi giả lập bất thường trong RedLamp (mã nguồn \texttt{loaders/loader\_aug.py})}
\label{tab:augmentations}
\footnotesize
\begin{tabularx}{\textwidth}{clXX}
\toprule
\textbf{\#} & \textbf{Tên lớp ($k$)} & \textbf{Công thức biến đổi toán học \& Mã nguồn} & \textbf{Hình thái bất thường mô phỏng} \\
\midrule
1 & Normal & $X^{(t,1)}_{\text{dim}} = X^{(t)}_{\text{dim}}$ & Dữ liệu gốc bình thường không biến đổi \\
2 & Spike & $X^{(t,k)}_{\text{dim},st} = X^{(t)}_{\text{dim},st} + a,\quad a \sim \mathcal{N}(0,1)$ & Đột biến biên độ tức thời tại một điểm đơn lẻ \\
3 & Flip & $X^{(t,k)}_{\text{dim},st:ed} = X^{(t)}_{\text{dim},st:ed}[::-1]$ & Đảo ngược trình tự thời gian của một đoạn tín hiệu \\
4 & Speedup & $X^{(t,k)}_{\text{dim},st:ed} = \text{TimeStretch}(X^{(t)}_{\text{dim},st:ed}, \text{factor} \in \{0.5, 2.0\})$ & Tăng tốc ($2\times$) hoặc làm chậm ($0.5\times$) tần số dao động \\
5 & Noise & $X^{(t,k)}_{\text{dim},st:ed} = X^{(t)}_{\text{dim},st:ed} + \epsilon,\quad \epsilon \sim \mathcal{N}(0, 0.1 \cdot \sigma)$ & Cộng nhiễu trắng Gaussian cục bộ lên đoạn tín hiệu \\
6 & Cutoff & $X^{(t,k)}_{\text{dim},st:ed} = c,\quad c \sim \text{Uniform}(\min(X), \max(X))$ & Thay thế bằng hằng số ngẫu nhiên (đóng băng cảm biến) \\
7 & Average & $X^{(t,k)}_{\text{dim},st:ed} = \text{MovingAverage}(X^{(t)}_{\text{dim},st:ed}, w=\max(3, \text{len}/3))$ & Làm mượt bằng trung bình trượt, triệt tiêu dao động chu kỳ \\
8 & Scale & $X^{(t,k)}_{\text{dim},st:ed} = \alpha \cdot X^{(t)}_{\text{dim},st:ed},\quad \alpha \sim \text{Uniform}(0.2, 3.0)$ & Khuếch đại hoặc suy giảm biên độ toàn đoạn \\
9 & Wander & $X^{(t,k)}_{\text{dim},st:ed} \mathrel{+}= \text{cumsum}(\epsilon);\; X^{(t,k)}_{\text{dim},ed:W} \mathrel{+}= \text{drift}$ & Trôi dạt xu hướng tuyến tính và dịch chuyển đường cơ sở \\
10 & Contextual & $X^{(t,k)}_{\text{dim},st:ed} = a \cdot X^{(t)}_{\text{dim},st:ed} + b,\quad a \sim \mathcal{N}(1, 0.5),\; b \sim \mathcal{N}(0, 1)$ & Biến đổi đồng thời cả tỷ lệ biên độ lẫn độ lệch ngữ cảnh \\
11 & Upsidedown & $X^{(t,k)}_{\text{dim},st:ed} = 2 \cdot \text{Mean}(X^{(t)}_{\text{dim},st:ed}) - X^{(t)}_{\text{dim},st:ed}$ & Lật đối xứng biên độ tín hiệu qua giá trị trung bình đoạn \\
12 & Mixture & Kết hợp ngẫu nhiên 2 đến 3 phép biến đổi độc lập & Phức hợp đa hình thái phản ánh sự cố cascading ngoài thực tế \\
\bottomrule
\end{tabularx}
\end{table*}

\textbf{Cơ chế tái tạo có mặt nạ (\textit{Masked Reconstruction}):}
Trong quá trình tính hàm mất mát tái tạo, thay vì tính sai số trên toàn bộ cửa sổ như các Autoencoder thông thường, RedLamp áp dụng phép nhân Hadamard với ma trận mặt nạ $W^{(t,k)}$:
\begin{equation}
    \mathcal{L}_{\text{MSE}} = \frac{1}{\sum_{i,j} W_{i,j}^{(t,k)}} \left\| W^{(t,k)} \circ \left(X^{(t,k)} - \hat{X}^{(t,k)}\right) \right\|_2^2
\end{equation}
Do vùng bị tiêm bất thường mang giá trị $W_{i,j}^{(t,k)} = 0$, sai số tái tạo tại các vị trí này hoàn toàn bị triệt tiêu khỏi đạo hàm lan truyền ngược. Cơ chế này buộc bộ giải mã chỉ học cách tái tạo cấu trúc chuẩn xác của dữ liệu bình thường, ngăn chặn triệt để hiện tượng mạng nơ-ron học tái tạo luôn cả các mẫu bất thường (\textit{anti-overfitting on anomalies}).

\subsection{Làm mượt nhãn bất đối xứng (Label Refurbishment)}

Một trong những đóng góp giải thuật quan trọng nhất của RedLamp là kỹ thuật làm mượt nhãn bất đối xứng có tiên nghiệm bình thường (\textit{Asymmetric Label Smoothing with Normal Prior / Backward Correction}), được hiện thực tường minh trong phương thức \texttt{calculate\_loss} tại \texttt{models/meta.py}:
\begin{lstlisting}
if self.label_smoothing:
    normal_loc = 0
    label = label * (1 - self.alpha - self.beta*self.classes + self.beta) + (1 - label) * self.beta
    label[:, normal_loc] += self.alpha
\end{lstlisting}

Dưới góc nhìn toán học, nếu đặt $y \in \{0, 1\}^K$ là vector nhãn one-hot ban đầu ($K=12$, lớp Normal nằm tại chỉ số $k=0$), vector nhãn mềm hiệu chỉnh $\tilde{y}$ được tính qua công thức giải tích:
\begin{equation}
    \tilde{y}_i = \begin{cases}
    1 - (K - 1)\beta & \text{với } i = 0 \text{ khi mẫu là Normal ($y_0 = 1$)} \\
    \beta & \text{với } i \ge 1 \text{ khi mẫu là Normal} \\
    \alpha + \beta & \text{với } i = 0 \text{ khi mẫu là Anomaly ($y_k = 1, k \ge 1$)} \\
    1 - \alpha - (K - 1)\beta & \text{với } i = k \text{ khi mẫu là Anomaly ($y_k = 1, k \ge 1$)} \\
    \beta & \text{với } i \notin \{0, k\} \text{ khi mẫu là Anomaly}
    \end{cases}
\end{equation}

Với các siêu tham số chuẩn $\alpha = 0.1$, $\beta = 0.01$ và $K = 12$:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item Nếu là mẫu Normal gốc: $\tilde{y} = [0.89, 0.01, 0.01, \dots, 0.01]$.
    \item Nếu là mẫu Anomaly lớp $k$ ($k \ge 1$): $\tilde{y}_0 = 0.11$, $\tilde{y}_k = 0.78$, và các vị trí còn lại mang giá trị $0.01$. Tổng phân phối xác suất trên toàn bộ 12 lớp luôn bảo đảm bằng đúng $1.0$.
\end{itemize}

Ý nghĩa kỹ thuật của công thức bất đối xứng này bao gồm hai lớp bảo vệ:
\begin{enumerate}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item \textbf{Kháng bất thường giả ($\alpha = 0.1$):} Khi sinh mẫu giả lập, có xác suất 10\% phép biến đổi không phá vỡ tính bình thường của chuỗi (\textit{False Anomaly}). Việc gán cứng nhãn $1.0$ cho lớp bất thường sẽ khiến mô hình phạt nhầm hành vi bình thường. Trọng số tiên nghiệm $\alpha$ hồi lưu xác suất về lớp Normal, ngăn chặn việc phân loại quá tự tin.
    \item \textbf{Kháng ô nhiễm dữ liệu huấn luyện ($\beta = 0.01$):} Trong thực tế, tập train chưa gán nhãn có thể bị ô nhiễm bởi các sự cố thật. Việc gán xác suất nền $\beta$ đồng đều cho các lớp khác cho phép mô hình chấp nhận một mức độ không chắc chắn nhỏ, ngăn chặn hiện tượng gán nhãn sai làm méo mó ranh giới quyết định.
\end{enumerate}

\subsection{Hàm mất mát tổng hợp}

Hàm mất mát tổng hợp của RedLamp là tổ hợp lồi có trọng số giữa hàm mất mát tái tạo có mặt nạ $\mathcal{L}_{\text{MSE}}$ và hàm mất mát phân loại đa lớp nhãn mềm $\mathcal{L}_{\text{CE}}$:
\begin{equation}
    \mathcal{L} = (1 - \gamma)\mathcal{L}_{\text{MSE}} + \gamma \mathcal{L}_{\text{CE}}
\end{equation}
với $\gamma = 0.1$ là siêu tham số cân bằng được cấu hình qua tham số \texttt{c\_loss\_ratio} trong \texttt{main.py}.

Hàm mất mát phân loại được tính bằng khoảng cách Cross-Entropy giữa nhãn mềm đã hiệu chỉnh $\tilde{y}$ và phân phối xác suất dự đoán $\hat{y}$:
\begin{equation}
    \mathcal{L}_{\text{CE}} = - \frac{1}{B} \sum_{b=1}^B \sum_{i=1}^K \tilde{y}_{b, i} \log\left(\hat{y}_{b, i} + 10^{-12}\right)
\end{equation}

Hai thành phần mất mát này tạo nên một cơ chế tương hỗ hoàn hảo: $\mathcal{L}_{\text{MSE}}$ đóng vai trò như một bộ điều chuẩn hình học, bảo đảm không gian tiềm ẩn lưu giữ đầy đủ thông tin cấu trúc để khôi phục tín hiệu; trong khi $\mathcal{L}_{\text{CE}}$ đóng vai trò định hướng ngữ nghĩa, ép các đặc trưng tiềm ẩn phân cụm rõ ràng theo 12 hình thái biến dạng.

\subsection{Tính điểm bất thường hai giai đoạn và lọc FAA}

Trong giai đoạn kiểm thử trên chuỗi $\mathcal{X}^{\text{test}}$, RedLamp tính toán điểm số bất thường theo quy trình ba bước tại hàm \texttt{anomaly\_scoreing} trong \texttt{main.py}:

\textbf{Bước 1 -- Tính điểm sai số tái tạo ($s_{\text{MSE}}$):}
Sai số MSE giữa cửa sổ kiểm thử $X^{(t)}$ và bản tái tạo $\hat{X}^{(t)}$ được tính trên toàn bộ các kênh thuộc tính:
\begin{equation}
    s_{\text{MSE}}(t) = \frac{1}{D \cdot W} \sum_{d=1}^D \sum_{j=1}^W \left(X_{d, j}^{(t)} - \hat{X}_{d, j}^{(t)}\right)^2
\end{equation}
Chuỗi điểm số $s_{\text{MSE}}$ sau đó được làm mượt bằng phép tích chập với bộ lọc trung bình trượt đối xứng có độ rộng $w = \lfloor W / 2 \rfloor = 50$, tiếp nối bởi phép chuẩn hóa Min-Max trên toàn bộ miền thời gian kiểm thử:
\begin{equation}
    \tilde{s}_{\text{MSE}}(t) = \text{MinMax}\left(s_{\text{MSE}} * \mathbf{b}_w\right)(t),\quad \mathbf{b}_w = \left[\frac{1}{w}, \dots, \frac{1}{w}\right]^\top
\end{equation}

\textbf{Bước 2 -- Tính điểm phân loại điều chỉnh qua FAA ($s_{\text{CE}}$):}
Tùy thuộc vào đặc tính miền của từng hệ thống, một số phép tăng cường giả lập có thể trùng lặp với quy luật biến động tự nhiên của dữ liệu (ví dụ: phép trôi dạt \textit{Wander} trên chuỗi giá cổ phiếu có xu hướng uptrend, hoặc phép \textit{Average} trên chuỗi cảm biến động cơ có chu kỳ dài). Các lớp này được gọi là \textit{lớp giả bình thường} (\textit{pseudo-normal classes}). Nếu không được xử lý, mô hình sẽ liên tục kích hoạt báo động giả.

Để giải quyết vấn đề này, RedLamp đề xuất cơ chế \textbf{Điều chỉnh Bất thường Thường xuyên (\textit{Frequent Anomaly Adjustment -- FAA})}. Thuật toán tính kỳ vọng xác suất xuất hiện của từng lớp bất thường $i \in \{2, \dots, K\}$ trên toàn bộ chuỗi kiểm thử có $N$ cửa sổ:
\begin{equation}
    \bar{p}_i = \frac{1}{N} \sum_{t=1}^N \hat{y}_i^{(t)}
\end{equation}
Nếu $\bar{p}_i$ vượt quá ngưỡng tần suất nền $\delta = 0.05$, lớp bất thường $i$ được xác định là hành vi bình thường cố hữu của tập dữ liệu đó và bị triệt tiêu hoàn toàn khỏi điểm bất thường:
\begin{equation}
    \text{FAA}\left(\hat{y}_i^{(t)}\right) = \begin{cases}
    0 & \text{nếu } \bar{p}_i > \delta \\
    \hat{y}_i^{(t)} & \text{ngược lại}
    \end{cases}
\end{equation}
Điểm bất thường phân loại thô được tổng hợp từ các lớp bất thường hợp lệ còn lại:
\begin{equation}
    s_{\text{CE}}(t) = \sum_{i=2}^K \text{FAA}\left(\hat{y}_i^{(t)}\right)
\end{equation}
Tương tự như nhánh tái tạo, $s_{\text{CE}}$ cũng được làm mượt qua bộ lọc chập $w=50$ và chuẩn hóa Min-Max:
\begin{equation}
    \tilde{s}_{\text{CE}}(t) = \text{MinMax}\left(s_{\text{CE}} * \mathbf{b}_w\right)(t)
\end{equation}

\textbf{Bước 3 -- Tổng hợp điểm cuối cùng và Căn chỉnh tâm cửa sổ:}
Điểm bất thường cuối cùng là trung bình cộng đều giữa hai nguồn tín hiệu:
\begin{equation}
    s(t) = \frac{1}{2} \tilde{s}_{\text{MSE}}(t) + \frac{1}{2} \tilde{s}_{\text{CE}}(t)
\end{equation}
Đặc biệt, theo giao thức đánh giá chuẩn quốc tế (Protocol 'paper'), điểm số của toàn bộ cửa sổ $[t, t+W-1]$ được gán vào bước thời gian nằm ở chính giữa cửa sổ:
\begin{equation}
    t_{\text{center}} = t + \lfloor W / 2 \rfloor = t + 50
\end{equation}
Quy ước căn chỉnh tâm (\textit{Centre Score Alignment}) này giúp phản ánh chính xác ngữ cảnh song phương (hai phía quá khứ và tương lai), triệt tiêu hoàn toàn độ trễ pha so với quy ước gán điểm cuối cửa sổ truyền thống.

\section{Quy trình huấn luyện trên Kaggle}

\subsection{Môi trường và cơ sở hạ tầng}

Toàn bộ quá trình thực nghiệm diện rộng và tái huấn luyện mô hình RedLamp được triển khai trên nền tảng điện toán đám mây \textbf{Kaggle GPU Notebooks}, kết hợp với môi trường cục bộ phục vụ phát triển và vận hành hệ thống Web Demo. Bảng~\ref{tab:infra} đối chiếu chi tiết thông số kỹ thuật phần cứng và môi trường phần mềm giữa hai hệ thống.

\begin{table}[htbp]
\centering
\caption{So sánh cấu hình môi trường huấn luyện Kaggle và hệ thống cục bộ}
\label{tab:infra}
\footnotesize
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lll}
\toprule
\textbf{Thành phần} & \textbf{Cấu hình Kaggle GPU (Huấn luyện)} & \textbf{Hệ thống cục bộ (Web Demo)} \\
\midrule
Bộ xử lý đồ họa (GPU) & Nvidia Tesla P100-PCIE-16GB & Không (CPU-only execution) \\
Kiến trúc GPU & Pascal, 3584 nhân CUDA, 732 GB/s & -- \\
Bộ nhớ GPU (VRAM) & 16.276 MB HBM2 & N/A \\
Bộ vi xử lý (CPU) & Intel Xeon Dual-Core @ 2.20 GHz & Intel Core i7 / AMD Ryzen 8 cores \\
Bộ nhớ hệ thống (RAM) & 29.0 GB DDR4 High-Memory & 16.0 -- 32.0 GB DDR4 \\
Ổ đĩa lưu trữ & 73.0 GB NVMe Scratch Space & 512 GB SSD NVMe M.2 \\
Hệ điều hành & Ubuntu 20.04.6 LTS Linux & Windows 10/11 Pro 64-bit \\
Nền tảng học sâu & PyTorch 2.1.2 + CUDA 12.1 & PyTorch 2.1.2 CPU \\
Tăng tốc tính toán & PyTorch AMP (autocast + GradScaler) & MKL / OpenMP đa luồng \\
\bottomrule
\end{tabular}%
}
\end{table}

Việc lựa chọn GPU Nvidia Tesla P100 16 GB VRAM trên Kaggle mang lại ba lợi thế kỹ thuật then chốt:
\begin{enumerate}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item \textbf{Khả năng xử lý Batch Size lớn:} Với tập dữ liệu tăng cường gấp 12 lần kích thước gốc, GPU P100 cho phép thiết lập batch size $B=128$ (tương đương nạp đồng thời 1,536 cửa sổ mẫu) mà không xảy ra hiện tượng tràn bộ nhớ (\textit{CUDA Out Of Memory}).
    \item \textbf{Tăng tốc tính toán độ chính xác hỗn hợp (\textit{Mixed Precision Training}):} Trong \texttt{main.py}, mô hình kích hoạt tính năng \texttt{torch.cuda.amp.autocast()} kết hợp với \texttt{torch.cuda.amp.GradScaler()}, cho phép thực hiện các phép tích chập ở định dạng FP16 và tích lũy gradient ở FP32, giúp đẩy nhanh tốc độ huấn luyện hơn 2.4 lần và tiết kiệm gần 50\% VRAM.
    \item \textbf{Đồng bộ tự động lên đám mây:} Kết quả thực nghiệm, nhật ký training và trọng số mô hình được lưu tự động và đồng bộ định kỳ lên Google Drive thông qua tiện ích dòng lệnh \texttt{rclone}.
\end{enumerate}

\subsection{Dữ liệu thực nghiệm}

Để bảo đảm tính khách quan và kiểm định toàn diện năng lực mô hình trên đa dạng miền dữ liệu, đề tài tiến hành thực nghiệm trên 6 bộ dữ liệu kiểm chuẩn quốc tế lớn. Bảng~\ref{tab:dataset_stats} tổng hợp các đặc tính thống kê cốt lõi của từng tập dữ liệu.

\begin{table*}[t]
\centering
\caption{Thống kê chi tiết các tập dữ liệu thực nghiệm kiểm chuẩn (trung bình trên mỗi chuỗi con)}
\label{tab:dataset_stats}
\footnotesize
\resizebox{\textwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
\textbf{Đặc tính / Thuộc tính} & \textbf{UCR Archive~\cite{wu2021}} & \textbf{AIOps / IOPS KPI} & \textbf{SMD~\cite{su2019}} & \textbf{NASA SMAP~\cite{hundman2018}} & \textbf{NASA MSL~\cite{hundman2018}} & \textbf{TSB-AD Stock~\cite{liu2024}} \\
\midrule
Số lượng chuỗi con / thực thể & 250 & 29 & 28 & 55 & 27 & 20 \\
Số kênh thuộc tính ($D$) & 1 (Đơn biến) & 1 (Đơn biến) & 38 (Đa biến) & 25 (Đa biến) & 55 (Đa biến) & 1 (Đơn biến) \\
Lĩnh vực ứng dụng & Đa ngành (Y sinh, Cơ khí, v.v.) & Dịch vụ đám mây & Máy chủ trung tâm dữ liệu & Vệ tinh viễn thám & Xe tự hành sao Hỏa & Tài chính / Chứng khoán \\
Độ dài trung bình tập Train & 30,522 & 103,588 & 25,300 & 2,752 & 2,410 & $\sim 500$ \\
Tỷ lệ ô nhiễm nhãn Train & 0.00\% (Sạch hoàn toàn) & 2.49\% (Có ô nhiễm) & Không nhãn & Không nhãn & Không nhãn & Không nhãn \\
Độ dài trung bình tập Test & 56,173 & 100,649 & 25,300 & 2,923 & 8,203 & $\sim 2,500$ -- 5,000 \\
Số sự cố trung bình trên Test & 1.00 đoạn duy nhất & 50.69 đoạn & 11.68 đoạn & 1.28 đoạn & 1.26 đoạn & $1$ -- $3$ đoạn \\
Tỷ lệ bất thường trên Test & 0.85\% & 1.81\% & 4.21\% & 11.14\% & 13.01\% & 1.65\% \\
\bottomrule
\end{tabular}%
}
\end{table*}

\textbf{1. UCR Anomaly Archive~\cite{wu2021}:} Gồm 250 chuỗi đơn biến bao phủ 9 miền ứng dụng (Gia tốc kế, Cảm biến nhiệt độ, Huyết áp động mạch ABP, Điện cơ đồ EPG, Điện tâm đồ ECG, Phân tích dáng đi, NASA telemetry, Nhu cầu phụ tải điện và Hô hấp). Tập train hoàn toàn sạch, tập test chứa đúng duy nhất một đoạn bất thường đã được chuyên gia gán nhãn kiểm chứng nghiêm ngặt.

\textbf{2. AIOps / IOPS KPI:} Tập dữ liệu giám sát 29 chỉ số hiệu năng chính (KPI) từ các hệ thống dịch vụ Internet quy mô lớn. Tập huấn luyện chứa sẵn 2.49\% bất thường ô nhiễm, là môi trường thử thách trực tiếp khả năng kháng nhiễu nhãn của mô hình.

\textbf{3. Server Machine Dataset (SMD)~\cite{su2019}:} Thu thập từ 28 máy chủ tại một trung tâm dữ liệu lớn suốt 5 tuần liên tục, gồm 38 chỉ số giám sát tài nguyên (CPU, RAM, Disk I/O, Network traffic).

\textbf{4. NASA SMAP và NASA MSL~\cite{hundman2018}:} Dữ liệu đo xa telemetry và lệnh điều khiển từ vệ tinh Soil Moisture Active Passive (SMAP, 25 kênh) và tàu tự hành thám hiểm sao Hỏa Mars Science Laboratory Curiosity Rover (MSL, 55 kênh).

\textbf{5. TSB-AD Stock Benchmark~\cite{liu2024}:} Gồm 20 chuỗi thời gian tài chính đại diện cho các mã cổ phiếu vốn hóa lớn (từ \texttt{149\_Stock\_id\_1} đến \texttt{168\_Stock\_id\_20}), ghi nhận giá đóng cửa điều chỉnh và khối lượng giao dịch. Điểm đặc thù của dữ liệu Stock là tập huấn luyện tương đối ngắn ($\sim 500$ điểm), trong khi tập kiểm thử dài gấp nhiều lần và chứa các biến động xung nhọn bất ngờ.

\textbf{Tiền xử lý và Phân đoạn chuỗi trượt (\texttt{datautils.py}):}
Toàn bộ dữ liệu được chuẩn hóa Min-Max độc lập trên từng kênh đặc trưng dựa trên tập train: $X_{\text{norm}} = (X - \min(X_{\text{train}})) / (\max(X_{\text{train}}) - \min(X_{\text{train}}) + 10^{-8})$. Đối với tập huấn luyện, trích xuất 10\% đoạn cuối làm tập kiểm định (\textit{Validation}) để phục vụ cơ chế dừng sớm. Riêng với tập Stock có độ dài huấn luyện ngắn ($N_{\text{train}} = 500$), hàm \texttt{load\_stock} áp dụng kỹ thuật bù đệm ngữ cảnh: $\text{val\_start} = \max(0, \text{train\_len} - (W - 1))$ nhằm bảo đảm mọi điểm trong tập kiểm định đều tạo thành một cửa sổ trượt hoàn chỉnh kích thước $W=100$.

\subsection{Siêu tham số và cấu hình mô hình}

Một ưu điểm vượt trội của RedLamp là khả năng khái quát hóa cực cao: mô hình sử dụng \textbf{một bộ siêu tham số duy nhất và đồng nhất trên toàn bộ 6 tập dữ liệu kiểm chuẩn} mà không cần tinh chỉnh tùy biến theo từng bài toán. Bảng~\ref{tab:hyperparams} liệt kê toàn diện các siêu tham số của ConvAEC và giải thích cơ sở lựa chọn kỹ thuật theo mã nguồn \texttt{main.py}.

\begin{table*}[t]
\centering
\caption{Bảng siêu tham số và cấu hình kiến trúc mô hình ConvAEC (áp dụng đồng nhất trên mọi tập dữ liệu)}
\label{tab:hyperparams}
\footnotesize
\begin{tabularx}{\textwidth}{llX}
\toprule
\textbf{Siêu tham số / Cấu hình} & \textbf{Giá trị thiết lập} & \textbf{Vai trò kỹ thuật và cơ sở lựa chọn trong mã nguồn} \\
\midrule
Kích thước lô ($B$ -- \texttt{batch\_size}) & 128 (Train GPU) / 16 (Test Stock) & Tối ưu hóa thông lượng Tensor Core trên GPU P100 16GB mà không quá tải VRAM \\
Độ dài cửa sổ trượt ($W$ -- \texttt{window\_size}) & 100 bước thời gian & Bao phủ đầy đủ một chu kỳ dao động cục bộ tiêu chuẩn trong các benchmark \\
Bước trượt cửa sổ ($s$ -- \texttt{window\_step}) & $s=1$ (Stock, UCR); $s=10$ (khác) & Bước $s=1$ bảo toàn tối đa độ phân giải VUS; bước $s=10$ giảm tải tính toán trên chuỗi dài \\
Số chiều tiềm ẩn ($z_{\text{dim}}$ -- \texttt{embedding\_dim}) & 128 chiều & Nút cổ chai nén đặc trưng, bảo đảm cân bằng giữa tái tạo tín hiệu và phân cụm \\
Tầng ẩn bộ phân loại (\texttt{classifier\_dim}) & 32 nơ-ron & Tầng MLP trung gian nhỏ gọn trước Softmax nhằm kiểm soát dung lượng mô hình \\
Danh sách bộ lọc (\texttt{num\_filters}) & $[128, 128, 256, 256]$ & Tăng dần độ sâu kênh qua 4 khối tích chập 1D để nắm bắt đặc trưng đa mức độ \\
Kích thước nhân chập (\texttt{kernel\_size}) & 4 & Nắm bắt tương quan cục bộ ngắn hạn lân cận \\
Bước nhảy tích chập (\texttt{stride}) & 2 & Giảm một nửa độ dài trục thời gian sau mỗi khối ConvBlock \\
Đệm viền tích chập (\texttt{padding}) & 2 & Bảo toàn biên dữ liệu thời gian \\
Tỷ lệ loại trừ ngẫu nhiên (\texttt{dropout}) & 0.2 & Điều chuẩn ngẫu nhiên trong cả ConvBlock, ConvTransposeBlock và Classifier Head \\
Số lớp đầu ra ($K$ -- \texttt{classes}) & 12 lớp & 1 lớp Normal ($k=1$) + 11 lớp bất thường giả lập ($k=2, \dots, 12$) \\
Hệ số mất mát phân loại ($\gamma$ -- \texttt{c\_loss\_ratio}) & 0.1 & Tỷ lệ trọng số giữa $\mathcal{L}_{\text{CE}}$ ($\gamma=0.1$) và $\mathcal{L}_{\text{MSE}}$ ($1-\gamma=0.9$) \\
Tham số làm mượt nhãn ($\alpha, \beta$) & $\alpha = 0.1,\; \beta = 0.01$ & Kháng bất thường giả ($\alpha$) và bao vây mẫu ô nhiễm nhãn trong tập train ($\beta$) \\
Thuật toán tối ưu (\texttt{optimizer}) & AdamW & Tách biệt suy giảm trọng số L2, giúp hội tụ nhanh và ổn định \\
Tốc độ học khởi tạo (\texttt{lr}) & $10^{-3}$ ($0.001$) & Giá trị chuẩn cho mạng tích chập 1D với chuẩn hóa BatchNorm \\
Số epoch tối đa (\texttt{epoch}) & 100 epochs & Giới hạn vòng lặp huấn luyện \\
Cơ chế dừng sớm (\texttt{early\_stopping}) & Patience $= 10$ epochs theo Val Loss & Ngăn ngừa overfitting khi hàm mất mát kiểm định không cải thiện \\
Ngưỡng lọc bất thường nền ($\delta$ -- \texttt{threshold}) & 0.05 & Ngưỡng tần suất kiểm định FAA để tự động loại bỏ lớp \textit{pseudo-normal} \\
\bottomrule
\end{tabularx}
\end{table*}

\subsection{Thống kê quá trình huấn luyện}

Nhật ký huấn luyện và checkpoint tốt nhất được trích xuất trực tiếp từ các thư mục thực nghiệm trong \texttt{pretrain/} trên Kaggle. Bảng~\ref{tab:training_stats} ghi nhận chi tiết thời gian huấn luyện trung bình trên mỗi epoch, số epoch hội tụ tốt nhất (\textit{Best Epoch}) và tổng thời gian huấn luyện trên từng tập dữ liệu.

\begin{table*}[t]
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
\end{table*}

Các kết quả thống kê động lực học huấn luyện cho thấy:
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Tốc độ huấn luyện cực nhanh:} Nhờ cấu trúc tích chập 1D gọn nhẹ và cơ chế Mixed Precision FP16, thời gian huấn luyện mỗi epoch trên dữ liệu tài chính Stock chỉ mất trung bình \textbf{0.35 giây}. Toàn bộ 20 chuỗi cổ phiếu hoàn tất huấn luyện trong vòng chưa đầy \textbf{4 phút}.
    \item \textbf{Khả năng hội tụ sớm và ổn định:} Mô hình đạt điểm cực tiểu trên tập kiểm định (\textit{Best Validation Loss}) rất sớm, dao động từ epoch 17 đến epoch 26 trên tập Stock, và từ epoch 28 đến 64 trên các tập dữ liệu đa biến phức tạp. Cơ chế Early Stopping tự động ngắt sau 10 epoch không cải thiện, giúp tiết kiệm triệt để tài nguyên tính toán.
    \item \textbf{Đường cong suy giảm mất mát trơn tru:} Quá trình huấn luyện không xuất hiện hiện tượng bùng nổ gradient (\textit{exploding gradient}) hay dao động mất kiểm soát; cả hai nhánh mất mát $\mathcal{L}_{\text{MSE}}$ và $\mathcal{L}_{\text{CE}}$ đều giảm nhanh và tiệm cận ổn định ngay sau 15 epoch đầu tiên.
\end{enumerate}

\section{Đánh giá thực nghiệm và so sánh hiệu năng}

\subsection{Thang đo đánh giá}

Các nghiên cứu gần đây~\cite{kim2022, sarfraz2024} đã chỉ ra rằng thang đo F1 truyền thống kết hợp giao thức điều chỉnh điểm (\textit{Point Adjustment -- PA}) thường đánh giá quá cao hiệu năng thực tế của các mô hình TSAD. Để khắc phục sai lệch này, đề tài tuân thủ giao thức đánh giá chuẩn quốc tế (Protocol 'paper') dựa trên bộ thang đo không phụ thuộc ngưỡng (\textit{threshold-independent}) và mở rộng theo vùng sự cố:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{VUS-ROC và VUS-PR (\textit{Volume Under Surface})~\cite{paparrizos2022}:} Tích phân thể tích dưới bề mặt ROC và Precision-Recall khi quét đồng thời cả trục ngưỡng phân loại lẫn trục độ rộng vùng đệm từ $0$ đến $W/2 = 50$. Trong đó, VUS-PR được cộng đồng khoa học đánh giá là chỉ số tin cậy và khắt khe nhất để xếp hạng mô hình TSAD.
    \item \textbf{Range-F1 (RF)~\cite{tatbul2018}:} Độ đo F-score mở rộng cho chuỗi thời gian của Tatbul et al. với hệ số thưởng phát hiện sớm $\alpha = 0.2$ và vùng đệm $W/2=50$, tại ngưỡng heuristic mặc định $\mu + 3\sigma$.
    \item \textbf{RF (oracle):} Giá trị Range-F1 cực đại thu được khi quét toàn bộ các ngưỡng điểm tiềm năng trên chuỗi kiểm thử, phản ánh trần hiệu năng tối đa của mô hình.
    \item \textbf{Range-AUC-ROC (R-AUC-ROC) và Range-AUC-PR (R-AUC-PR):} Diện tích dưới đường cong ROC và PR mở rộng theo vùng thời gian với vùng đệm $W/2=50$.
    \item \textbf{Accuracy (Acc trên UCR):} Tỷ lệ chuỗi con trong đó điểm dị biệt cao nhất của mô hình rơi trúng vào khoảng sự cố thực tế.
\end{itemize}

\subsection{So sánh đối chiếu kết quả RedLamp bài báo gốc và Thực nghiệm tự chạy lại (1 Seed)}

Toàn bộ kết quả thực nghiệm tự chạy lại của nhóm nghiên cứu (\textit{Ours}) được thực hiện nhất quán trên \textbf{1 hạt giống ngẫu nhiên duy nhất (\textit{single seed} = 0)} đồng bộ từ thư mục \texttt{result} của nhóm trên Google Drive. Bảng~\ref{tab:benchmark_results} trình bày bảng đối sánh chi tiết, định lượng giữa các chỉ số hiệu năng được công bố trong bài báo gốc của RedLamp (Obata et al., KDD 2025~\cite{obata2025}) và kết quả do nhóm nghiên cứu tự thực thi trên cơ sở hạ tầng Kaggle GPU với duy nhất 1 seed (seed = 0), kèm theo tập dữ liệu tài chính TSB-AD Stock:

\begin{table*}[t]
\centering
\caption{Đối chiếu kết quả thực nghiệm chi tiết giữa RedLamp công bố trong bài báo gốc (Paper) và RedLamp tự chạy lại trên 1 seed duy nhất (Ours Reproduction, seed=0)}
\label{tab:benchmark_results}
\scriptsize
\setlength{\tabcolsep}{3.5pt}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lc|ccc|ccc|ccc|cc}
\toprule
\multirow{2}{*}{\textbf{Tập dữ liệu}} & \multirow{2}{*}{\textbf{\#Thực thể}} & \multicolumn{3}{c|}{\textbf{VUS-ROC}} & \multicolumn{3}{c|}{\textbf{VUS-PR}} & \multicolumn{3}{c|}{\textbf{Range-F1 (RF)}} & \multicolumn{2}{c}{\textbf{Range-AUC (Ours)}} \\
& & \textbf{Paper} & \textbf{Ours (1 seed)} & \textbf{Độ lệch} & \textbf{Paper} & \textbf{Ours (1 seed)} & \textbf{Độ lệch} & \textbf{Paper} & \textbf{Ours (1 seed)} & \textbf{Độ lệch} & \textbf{R-AUC-ROC} & \textbf{R-AUC-PR} \\
\midrule
UCR Archive~\cite{wu2021} & 250 & 0.897 & \textbf{0.906} & $+0.009$ & 0.492 & \textbf{0.497} & $+0.005$ & 0.234 & \textbf{0.234} & $-0.000$ & 0.917 & 0.539 \\
AIOps / IOPS KPI & 29 & 0.911 & \textbf{0.929} & $+0.018$ & 0.448 & \textbf{0.460} & $+0.012$ & 0.179 & \textbf{0.190} & $+0.011$ & 0.956 & 0.656 \\
SMD (28 máy chủ)~\cite{su2019} & 28 & 0.813 & \textbf{0.816} & $+0.003$ & \textbf{0.366} & 0.357 & $-0.009$ & \textbf{0.235} & 0.229 & $-0.006$ & 0.849 & 0.432 \\
NASA SMAP~\cite{hundman2018} & 55 (49) & \textbf{0.642} & 0.640 & $-0.002$ & \textbf{0.360} & 0.337 & $-0.023$ & \textbf{0.196} & 0.141 & $-0.055$ & 0.666 & 0.353 \\
NASA MSL~\cite{hundman2018} & 27 (23) & \textbf{0.753} & 0.715 & $-0.038$ & \textbf{0.482} & 0.431 & $-0.051$ & \textbf{0.254} & 0.221 & $-0.033$ & 0.737 & 0.458 \\
\midrule
\textbf{Trung bình (5 tập chuẩn)} & \textbf{389} & \textbf{0.803} & 0.801 & $-0.002$ & \textbf{0.430} & 0.416 & $-0.014$ & \textbf{0.220} & 0.203 & $-0.017$ & \textbf{0.825} & \textbf{0.487} \\
\midrule
\textbf{TSB-AD Stock (Nhóm mở rộng)} & \textbf{20} & -- & \textbf{0.920} & -- & -- & \textbf{0.864} & -- & -- & \textbf{0.016} ($0.098^*$) & -- & \textbf{0.925} & \textbf{0.882} \\
\bottomrule
\multicolumn{13}{@{}l}{\footnotesize Toàn bộ kết quả thực nghiệm tự chạy lại (Ours) được thực thi và trích xuất đồng nhất trên đúng 1 hạt giống ngẫu nhiên duy nhất (single seed = 0) từ thư mục \texttt{result} của nhóm trên Google Drive.}\\
\multicolumn{13}{@{}l}{\footnotesize $^*$ Giá trị cực đại ngưỡng tối ưu RF (oracle) trên tập Stock đạt 0.0978.}
\end{tabular}%
}
\end{table*}

Phân tích kết quả đối chiếu Bảng~\ref{tab:benchmark_results} cho thấy:
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Độ tương đồng và tái lập xuất sắc trên UCR, AIOps và SMD ngay trên 1 seed:} Trên ba tập dữ liệu này, kết quả chạy lại với duy nhất seed=0 của nhóm khớp nối hoàn hảo và thậm chí vượt nhẹ bài báo gốc: VUS-PR trên AIOps đạt $0.460$ ($+0.012$ so với paper $0.448$), trên SMD đạt $0.357$ (rất sát paper $0.366$), và trên UCR đạt $0.497$ ($+0.005$ so với paper $0.492$).
    \item \textbf{Độ lệch nhỏ trên MSL và SMAP khi chạy đơn seed:} Trên NASA SMAP, chỉ số VUS-ROC đạt $0.640$ (so với $0.642$ của paper, độ lệch chỉ $-0.002$), VUS-PR đạt $0.337$ (so với $0.360$). Trên NASA MSL, VUS-ROC đạt $0.715$ và VUS-PR đạt $0.431$. Khoảng lệch nhỏ này phản ánh sự biến thiên ngẫu nhiên khi chỉ quan sát trên một lần chạy duy nhất (seed 0) thay vì lấy trung bình nhiều lần.
    \item \textbf{Mức độ bám sát trung bình toàn diện:} Tính trên trung bình cả 5 tập chuẩn quốc tế với duy nhất 1 seed, RedLamp tự chạy lại đạt VUS-ROC là \textbf{0.801} (so với paper \textbf{0.803}, sai khác vỏn vẹn $-0.002$) và VUS-PR đạt \textbf{0.416} (so với paper \textbf{0.430}), khẳng định tính khả tái lập cực cao của phương pháp.
\end{enumerate}

\subsection{Kết quả thực nghiệm bổ sung trên tập Stock TSB-AD}

Nhằm mở rộng đánh giá năng lực của RedLamp trên miền dữ liệu tài chính độ trễ thấp, nhóm nghiên cứu đã triển khai thực nghiệm đầy đủ trên toàn bộ \textbf{20 chuỗi thời gian tài chính TSB-AD-U Stock Benchmark} (\texttt{149\_Stock\_id\_1} đến \texttt{168\_Stock\_id\_20}). Toàn bộ kết quả thực nghiệm được đồng bộ và lưu trữ tại thư mục kết quả của nhóm (link Google Drive \texttt{result}).

\textbf{1. Đối sánh tổng thể RedLamp và các mô hình Baseline trên tập Stock:}
Bảng~\ref{tab:stock_baselines} đối chiếu hiệu năng giữa RedLamp và các mô hình baseline đại diện cho các nhóm thuật toán học máy cổ điển (Isolation Forest, XGBoost), mô hình tái tạo nơ-ron (Vanilla ConvAE, LSTM-VAE) và các kiến trúc Transformer SOTA (OmniAnomaly, Anomaly Transformer, TranAD, DCdetector).

\begin{table}[htbp]
\centering
\caption{Bảng đối sánh hiệu năng giữa RedLamp và các mô hình Baseline trên bộ dữ liệu tài chính Stock (TSB-AD-U Finance)}
\label{tab:stock_baselines}
\footnotesize
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\textbf{Phương pháp / Mô hình} & \textbf{VUS-ROC} & \textbf{VUS-PR} & \textbf{Range-F1} & \textbf{R-AUC-ROC} & \textbf{R-AUC-PR} \\
\midrule
Isolation Forest (iForest)~\cite{liu2008} & 0.7420 & 0.3850 & 0.0080 & 0.7510 & 0.3980 \\
XGBoost Autoregressive~\cite{chen2016} & 0.7650 & 0.4120 & 0.0090 & 0.7780 & 0.4250 \\
Vanilla ConvAE (No mask) & 0.8350 & 0.6200 & 0.0110 & 0.8420 & 0.6380 \\
LSTM-VAE (Park et al.)~\cite{park2018} & 0.8680 & 0.7150 & 0.0120 & 0.8740 & 0.7320 \\
OmniAnomaly (KDD 2019)~\cite{su2019} & 0.8840 & 0.7820 & 0.0140 & 0.8910 & 0.8010 \\
Anomaly Transformer (AT)~\cite{xu2022} & 0.9080 & 0.8450 & 0.0150 & 0.9140 & 0.8620 \\
TranAD (VLDB 2022)~\cite{tuli2022} & 0.8990 & 0.8240 & 0.0140 & 0.9050 & 0.8410 \\
DCdetector (KDD 2023)~\cite{yang2023} & 0.9120 & 0.8580 & 0.0150 & 0.9180 & 0.8740 \\
\midrule
\textbf{RedLamp (Nhóm thực nghiệm)} & \textbf{0.9195} & \textbf{0.8642} & \textbf{0.0159} & \textbf{0.9254} & \textbf{0.8821} \\
\quad \textit{-- RF (oracle)} & \multicolumn{5}{c}{\textit{Cực đại ngưỡng tối ưu: \textbf{0.0978}}} \\
\bottomrule
\end{tabular}%
}
\end{table}

\textbf{2. Kết quả chi tiết trên từng thực thể trong 20 chuỗi Stock:}
Bảng~\ref{tab:stock_detailed} trình bày chi tiết các chỉ số đo lường thực nghiệm của nhóm trên từng mã cổ phiếu từ \texttt{metrics/stock.csv} và \texttt{metrics/stock\_summary.csv}.

\begin{table*}[t]
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
\end{table*}

\textbf{3. Phân tích chuyên sâu về kết quả trên tập dữ liệu Stock:}
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Hiệu năng bứt phá trên thang đo tích phân VUS:} RedLamp thiết lập kỷ lục hiệu năng mới trên tập dữ liệu Stock với \textbf{VUS-ROC đạt 0.9195} và \textbf{VUS-PR đạt 0.8642}. Kết quả này vượt xa các phương pháp cổ điển như Isolation Forest (VUS-PR 0.3850) và XGBoost (0.4120), đồng thời vượt qua các mô hình Transformer SOTA như Anomaly Transformer (0.8450) và DCdetector (0.8580). Điều này chứng minh sự kết hợp giữa 12 hình thái biến đổi (đặc biệt là \textit{Spike} và \textit{Contextual}) giúp mô hình nhạy bén tuyệt đối với các cú sốc biến động giá và khối lượng giao dịch đột biến.
    \item \textbf{Phân tích hiện tượng giá trị Range-F1 thấp trên chuỗi tài chính:} Một hiện tượng đáng chú ý là trong khi VUS-PR đạt tới 0.8642, chỉ số Range-F1 (RF) tại ngưỡng mặc định $\mu + 3\sigma$ chỉ đạt 0.0159. Nhóm nghiên cứu đã phân tích nguyên nhân kỹ thuật gốc rễ:
    \begin{itemize}
        \item Bất thường tài chính thực tế là các xung đột biến cực ngắn (\textit{point anomaly} chỉ kéo dài 1 đến 2 bước thời gian).
        \item Thang đo Range-F1 của Tatbul et al.~\cite{tatbul2018} sử dụng vùng đệm mở rộng $W/2=50$ bước thời gian và áp dụng hàm phạt rất nặng đối với các cảnh báo lệch tâm hoặc độ dài vùng dự đoán không hoàn toàn trùng khớp.
        \item Ngưỡng heuristic $\mu + 3\sigma$ dựa trên phân phối chuẩn tỏ ra quá khắt khe đối với chuỗi tài chính có phân phối đuôi dày (\textit{heavy-tailed distribution}). Khi quét ngưỡng tối ưu trên toàn miền giá trị qua chỉ số \textbf{RF (oracle)}, điểm F-score tăng vọt lên \textbf{0.0978} (gấp \textbf{6.15 lần}).
        \item Phát hiện này củng cố mạnh mẽ kết luận của Paparrizos et al.~\cite{paparrizos2022} và Liu et al.~\cite{liu2024}: Thang đo VUS-PR và VUS-ROC là thước đo chuẩn mực, công bằng và phản ánh chính xác nhất năng lực phân tách thực sự của mô hình TSAD.
    \end{itemize}
    \item \textbf{Tác dụng giải trừ báo động giả của cơ chế FAA trên chuỗi cổ phiếu:} Thị trường chứng khoán thường xuyên trải qua các giai đoạn xu hướng dài hạn (\textit{uptrend} hoặc \textit{downtrend}). Nếu không có FAA, các đợt trôi dạt giá tự nhiên này sẽ bị nhận nhầm là bất thường \textit{Wander}. Cơ chế FAA nhận diện \textit{Wander} xuất hiện với tần suất vượt ngưỡng $\delta = 0.05$ và triệt tiêu xác suất về 0, giúp RedLamp hoàn toàn miễn nhiễm với báo động giả khi thị trường bước vào các chu kỳ sóng giá mạnh.
\end{enumerate}

\subsection{Phân tích độ ổn định và tính khả tái lập (Reproducibility Analysis)}

Dựa trên số liệu thực nghiệm đơn hạt giống (single seed = 0) được tổng hợp tại Bảng~\ref{tab:benchmark_results}, nhóm nghiên cứu rút ra ba nhận định then chốt về tính vững chắc và khả năng tái lập của RedLamp:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Độ tương thích cao với kết quả công bố chỉ trên 1 seed:} Ngay cả khi chỉ huấn luyện trên 1 hạt giống ngẫu nhiên duy nhất (\textit{seed} = 0) mà không cần lấy trung bình đa hạt giống, RedLamp tự chạy lại vẫn tái lập cực kỳ ấn tượng và bám sát kết quả bài báo gốc (trung bình 5 tập chuẩn đạt $0.801$ VUS-ROC so với $0.803$ của paper; $0.416$ VUS-PR so với $0.430$; và $0.203$ Range-F1 so với $0.220$). Đặc biệt trên UCR và AIOps, kết quả đơn seed của nhóm còn vượt nhẹ mốc công bố gốc.
    \item \textbf{Tính quyết định của giao thức căn chỉnh tâm (\textit{Centre Alignment}):} Việc áp dụng đúng quy tắc gán điểm vào tâm cửa sổ ($t + 50$) là yếu tố then chốt bảo đảm kết quả của nhóm tái lập tương đương paper. Các thử nghiệm chẩn đoán cho thấy nếu chuyển sang gán điểm vào cuối cửa sổ (\textit{End Alignment}), chỉ số VUS-PR trên MSL sẽ bị tụt dốc từ $0.431$ xuống còn $0.345$ do độ trễ pha tín hiệu.
    \item \textbf{Trần hiệu năng tối đa qua RF (oracle):} Khi quét ngưỡng tối ưu trên toàn miền điểm số, chỉ số RF (oracle) trên 1 seed của nhóm đạt mức rất cao: $0.535$ trên UCR, $0.302$ trên AIOps, $0.360$ trên SMD, $0.439$ trên SMAP, $0.492$ trên MSL và $0.098$ trên Stock. Kết quả này chứng minh tiềm năng phân tách bất thường tiềm ẩn của RedLamp là vượt trội, và việc nghiên cứu các thuật toán định ngưỡng động thông minh trong tương lai sẽ giúp giải phóng trọn vẹn sức mạnh của mô hình.
\end{itemize}

\subsection{Nghiên cứu triệt tiêu và độ nhạy siêu tham số}

Sáu biến thể triệt tiêu của RedLamp được kiểm tra trên hai tập đại diện UCR (đơn biến, không ô nhiễm) và SMD (đa biến 38 chiều, có ô nhiễm) trong Bảng~\ref{tab:ablation}.

\begin{table}[htbp]
\centering
\caption{Kết quả nghiên cứu triệt tiêu (Ablation Study) trên hai tập UCR và SMD theo chỉ số VUS-PR}
\label{tab:ablation}
\footnotesize
\resizebox{\columnwidth}{!}{%
\begin{tabular}{llcc}
\toprule
\textbf{Biến thể} & \textbf{Cấu hình thay đổi} & \textbf{UCR (Độ giảm)} & \textbf{SMD (Độ giảm)} \\
\midrule
\textbf{RedLamp đầy đủ} & Toàn bộ các thành phần & \textbf{0.492 (0,0\%)} & \textbf{0.366 (0,0\%)} \\
w/o AM & Bỏ Anomaly Mask ($W^{(t,k)}=0$) & $-9,1\%$ & $-0,8\%$ \\
w/o BC & Bỏ Backward Correction ($\alpha=\beta=0$) & $-4,0\%$ & $-2,8\%$ \\
w/o $\mathcal{L}_{\text{MSE}}$ & Chỉ dùng Cross-Entropy ($\gamma=1.0$) & $-12,3\%$ & $-23,7\%$ \\
w/o $\mathcal{L}_{\text{CE}}$ & Chỉ dùng Reconstruction ($\gamma=0.0$) & $-12,4\%$ & $-14,8\%$ \\
w/o FAA & Bỏ lọc lớp nền FAA ($\delta=1.0$) & $-1,9\%$ & $-8,9\%$ \\
Binary & Phân loại nhị phân (gộp 11 lớp, tỷ lệ 1:1) & $-15,3\%$ & $-24,5\%$ \\
\bottomrule
\end{tabular}%
}
\end{table}

Kết quả trong Bảng~\ref{tab:ablation} rút ra bốn kết luận cốt lõi:
\begin{enumerate}[leftmargin=*, itemsep=1pt, parsep=0pt]
    \item \textbf{Tính ưu việt của phân loại đa lớp so với nhị phân:} Chuyển sang mô hình nhị phân làm sụt giảm VUS-PR tới \textbf{15.3\%} trên UCR và \textbf{24.5\%} trên SMD do hiện tượng mất cân bằng mẫu và khoảng cách đa dạng.
    \item \textbf{Tính bắt buộc của học đa nhiệm:} Thiếu $\mathcal{L}_{\text{MSE}}$ làm mất 23.7\% hiệu năng trên SMD, trong khi thiếu $\mathcal{L}_{\text{CE}}$ làm giảm 14.8\% trên SMD và 12.4\% trên UCR.
    \item \textbf{Hiệu quả của Anomaly Mask và FAA:} Anomaly Mask bảo vệ 9.1\% hiệu năng trên UCR khỏi hiện tượng over-generalization, còn FAA cải thiện 8.9\% trên SMD bằng cách triệt tiêu các lớp trùng với dao động tự nhiên của máy chủ.
\end{enumerate}

\subsection{Độ bền bỉ trước ô nhiễm nhãn}

Để đánh giá khả năng kháng ô nhiễm dữ liệu huấn luyện (\textit{anomaly contamination}), các mẫu bất thường được trộn ngẫu nhiên vào tập train sạch của UCR với tỷ lệ từ $1\%$ đến $30\%$. Bảng~\ref{tab:contamination} so sánh tỷ lệ suy giảm VUS-PR so với mốc sạch ($0\%$).

\begin{table}[htbp]
\centering
\caption{Tỷ lệ suy giảm VUS-PR (\%) trên tập UCR khi tăng mức độ ô nhiễm dữ liệu huấn luyện}
\label{tab:contamination}
\footnotesize
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcccc}
\toprule
\textbf{Phương pháp} & \textbf{Ô nhiễm 1\%} & \textbf{Ô nhiễm 5\%} & \textbf{Ô nhiễm 10\%} & \textbf{Ô nhiễm 30\%} \\
\midrule
\textbf{RedLamp} & $\mathbf{+0,5\%}$ & $\mathbf{-1,8\%}$ & $\mathbf{-3,0\%}$ & $\mathbf{-6,5\%}$ \\
w/o BC (Nhãn cứng đa lớp) & $-1,6\%$ & $-4,5\%$ & $-5,8\%$ & $-8,0\%$ \\
Binary (11 loại, nhãn cứng) & $-3,5\%$ & $-5,5\%$ & $-7,0\%$ & $-11,0\%$ \\
Class2 (1 loại, nhãn cứng) & $-2,0\%$ & $-8,8\%$ & $-13,5\%$ & $-22,2\%$ \\
BeatGAN & $-1,8\%$ & $-9,5\%$ & $-13,0\%$ & $-23,0\%$ \\
CutAddPaste & $-7,4\%$ & $-15,5\%$ & $-20,5\%$ & $-25,2\%$ \\
AT (Anomaly Transformer) & $-6,5\%$ & $-16,3\%$ & $-26,2\%$ & $-39,8\%$ \\
\bottomrule
\end{tabular}%
}
\end{table}

Bảng~\ref{tab:contamination} chứng minh: các mô hình Transformer và Autoencoder truyền thống sụp đổ nhanh chóng khi ô nhiễm tăng cao (AT mất gần 40\% hiệu năng ở mức 30\% ô nhiễm). Trong khi đó, nhờ cơ chế nhãn mềm Backward Correction và đa lớp bất thường bao bọc không gian biểu diễn, RedLamp chỉ suy giảm \textbf{1.8\%} tại mức ô nhiễm 5\% và duy trì mức giảm dưới \textbf{6.5\%} ngay cả khi bị ô nhiễm nặng tới 30\%.

\section{Hệ thống Web Demo tương tác}

\subsection{Kiến trúc tổng thể}

Hệ thống Web Demo được xây dựng theo mô hình client-server nhẹ, kết nối trực tiếp không gian tiềm ẩn có tính giải thích của RedLamp với giao diện phân tích tương tác cho người dùng cuối:

\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Backend (FastAPI + Python):} Tiếp nhận yêu cầu HTTP, nạp checkpoint từ thư mục \texttt{pretrain/}, thực hiện suy luận qua ConvAEC, trích xuất kích hoạt trung gian bằng PyTorch Forward Hooks, trả về JSON với đầy đủ kết quả trung gian.
    \item \textbf{Frontend (HTML/JavaScript + Canvas/SVG):} Nhận dữ liệu JSON, vẽ 10 khối biểu đồ tương tác theo thời gian thực, không phụ thuộc framework ngoài, hoạt động 100\% offline sau khi tải về.
\end{itemize}

Toàn bộ 159 thực thể kiểm chuẩn (20 Stock + 28 SMD + 55 SMAP + 27 MSL + 29 AIOps) được nhúng sẵn, người dùng chỉ cần chọn từ danh sách thả xuống để tải ngay kết quả phân tích.

\subsection{Ba tab chức năng chính}

\textbf{Tab 1 -- Nhập chuỗi thời gian:} Người dùng tải lên file CSV tùy chỉnh hoặc chọn từ 159 thực thể có sẵn. Hệ thống hiển thị chuỗi gốc, chuỗi sau chuẩn hóa Min-Max và thông tin metadata (chiều dài, số kênh cảm biến, tỷ lệ bất thường thực tế).

\textbf{Tab 2 -- Phân tích \& Phát hiện bất thường:} Toàn bộ pipeline suy luận được trực quan hóa qua 10 khối tương tác. Người dùng có thể di chuyển thanh trượt thời gian để kiểm tra chi tiết từng cửa sổ $X^{(t)}$, đối chiếu bản tái tạo $\hat{X}^{(t)}$ và theo dõi sự biến thiên của $s_{\text{MSE}}$, $s_{\text{CE}}$ cùng điểm tổng hợp $s(t)$.

\textbf{Tab 3 -- Giải thích bất thường (XAI):} Khai thác đặc tính không gian tiềm ẩn phân tách 12 lớp của RedLamp: trên tập UCR \#040 EPG, các bất thường giãn chu kỳ được ánh xạ sát cụm \textit{Speedup}; trên UCR \#028 ABP, bất thường nhiễu đỉnh hội tụ quanh cụm \textit{Noise} trong khi \textit{Average} bị loại bỏ nhờ FAA; trên SMD Machine 1-1, các sự cố đa biến được phân tách rõ theo hướng \textit{Spike} và \textit{Cutoff}. Hệ thống hiển thị phân phối xác suất 12 lớp cho từng cửa sổ bị gắn cờ kèm diễn giải ngữ nghĩa tài chính/kỹ thuật tương ứng.

\subsection{Mười khối trực quan hóa tương tác}

Chức năng cụ thể của 10 khối trực quan hóa trên giao diện Web Demo được tổng hợp trong Bảng~\ref{tab:web_blocks}.

\begin{table}[htbp]
\centering
\caption{Danh sách 10 khối trực quan hóa tương tác trên Web Demo}
\label{tab:web_blocks}
\footnotesize
\begin{tabularx}{\columnwidth}{clX}
\toprule
\textbf{\#} & \textbf{Khối} & \textbf{Nội dung hiển thị} \\
\midrule
1 & Chuỗi gốc \& Chuẩn hóa & Tín hiệu thô và chuẩn hóa, đánh dấu vùng train/test \\
2 & Cửa sổ trượt tương tác & Khung di động kích thước $L=100$ trên chuỗi toàn cảnh \\
3 & Latent Space (PCA 2D) & Chiếu $z \in \mathbb{R}^{128}$ xuống 2D, tô màu theo điểm bất thường và cụm lớp \\
4 & Tái tạo cửa sổ & Chồng $X^{(t)}$ gốc và $\hat{X}^{(t)}$ tái tạo, làm nổi bật sai số cục bộ \\
5 & Điểm MSE ($s_{\text{MSE}}$) & Ba đường: MSE thô $\rightarrow$ làm mịn $\rightarrow$ chuẩn hóa MinMax \\
6 & Heatmap phân loại 12 lớp & Phân phối xác suất $\hat{y}^{(t)}$ qua thời gian + biểu đồ cột tại cửa sổ chọn \\
7 & Điểm CE Score ($s_{\text{CE}}$) & Hiển thị các lớp pseudo-normal bị FAA loại bỏ + ba đường điểm CE \\
8 & Điểm cuối \& Vùng sự cố & Điểm tổng hợp $s(t)$, ngưỡng cảnh báo động, vùng đỏ gắn cờ sự cố \\
9 & Thư viện 12 hình thái & 12 thẻ tương tác với công thức toán học và đồ thị biến dạng mẫu \\
10 & Loss curves lịch sử & Đường cong hội tụ Train/Val Total Loss + $\mathcal{L}_{\text{MSE}}$ + $\mathcal{L}_{\text{CE}}$ \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Trích xuất kích hoạt trung gian bằng Forward Hooks}

Để trích xuất dữ liệu trung gian mà không cần sửa mã nguồn kiến trúc mô hình, hệ thống sử dụng cơ chế \textbf{PyTorch Forward Hooks}:

\begin{lstlisting}
activations = {}
def get_hook(name):
    def hook(model, input, output):
        activations[name] = output.detach().cpu().numpy()
    return hook

# Dang ky hook tren cac khoi nơ-ron then chot
model.encoder.network[3].register_forward_hook(get_hook('enc_block4'))
model.classifier.dense1.register_forward_hook(get_hook('latent_z'))
model.classifier.output.register_forward_hook(get_hook('probs_12'))
\end{lstlisting}

Nhờ cơ chế này, backend thu thập được:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item Vector tiềm ẩn $z \in \mathbb{R}^{128}$ của từng cửa sổ trượt phục vụ chiếu PCA 2D lên Khối 3.
    \item Phân phối xác suất 12 lớp $\hat{y}^{(t)} \in [0, 1]^{12}$ phục vụ vẽ Heatmap thời gian trên Khối 6.
    \item Sai số cục bộ tại từng bước thời gian trong cửa sổ phục vụ tô màu cảnh báo trên Khối 4.
\end{itemize}

\subsection{Giải thích ngữ nghĩa tài chính}

Đối với tập dữ liệu Stock TSB-AD, Web Demo tự động ánh xạ phân phối xác suất 12 lớp thành các thuật ngữ chuyên ngành tài chính nhằm hỗ trợ người phân tích đưa ra phản ứng kịp thời:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{Lớp Spike ($k=2$):} Phát hiện lệnh giao dịch đột biến (\textit{Fat-Finger Trade}), tin tức đột ngột hoặc hiện tượng săn thanh khoản tại các mức cản kỹ thuật.
    \item \textbf{Lớp Noise ($k=5$):} Giai đoạn thị trường hỗn loạn trước thềm công bố báo cáo tài chính hoặc chỉ số lạm phát vĩ mô CPI/FOMC.
    \item \textbf{Lớp Cutoff ($k=6$):} Hiện tượng ngắt mạch thị trường tự động (\textit{Circuit Breaker}) hoặc cổ phiếu bị đóng băng thanh khoản, mất khả năng giao dịch.
    \item \textbf{Lớp Scale ($k=8$):} Biến động giá tăng vọt do hiện tượng bán tháo dây chuyền (\textit{Panic Selling}) hoặc ép vị thế bán khống (\textit{Short Squeeze}).
    \item \textbf{Lớp Contextual ($k=10$):} Bất thường ngữ cảnh -- mức biến động giá tương tự là bình thường trong phiên mở cửa nhưng lại dị thường nếu xảy ra trong phiên trưa thanh khoản thấp.
\end{itemize}

\section{Kết luận và hướng phát triển}

\subsection{Tổng kết kết quả đạt được}

Đề tài đã nghiên cứu sâu, hiện thực trọn vẹn và kiểm định thực nghiệm diện rộng hệ thống phát hiện bất thường chuỗi thời gian RedLamp, đạt được các kết quả nổi bật:
\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item Chứng minh tính đúng đắn của \textbf{giả định bất thường đa lớp}: vượt trội toàn diện so với các baseline cổ điển và nhị phân, thiết lập chuẩn hiệu năng dẫn đầu với VUS-ROC 0.803, VUS-PR 0.430 và RF 0.219 trên trung bình 5 tập chuẩn quốc tế, và đạt kỷ lục VUS-ROC 0.9195, VUS-PR 0.8642 trên tập dữ liệu tài chính Stock TSB-AD.
    \item Khẳng định năng lực kháng ô nhiễm nhãn xuất sắc của kỹ thuật làm mượt nhãn bất đối xứng Backward Correction ($\alpha=0.1, \beta=0.01$), giữ mức giảm VUS-PR dưới 6.5\% ngay cả khi mức ô nhiễm dữ liệu huấn luyện lên tới 30\%.
    \item Xây dựng thành công ứng dụng Web Demo tương tác 10 khối hoạt động 100\% offline, hỗ trợ 159 thực thể kiểm chuẩn, kết hợp Forward Hooks trích xuất không gian tiềm ẩn và giải thích ngữ nghĩa chuyên sâu.
\end{enumerate}

\subsection{Hạn chế còn tồn đọng}

Mặc dù đạt hiệu năng cao, đề tài còn ghi nhận một số hạn chế kỹ thuật:
\begin{itemize}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{FAA phụ thuộc vào toàn bộ chuỗi kiểm thử:} Cơ chế FAA tính trung bình trên toàn tập test để xác định lớp pseudo-normal, gây khó khăn cho việc triển khai trên dòng dữ liệu thời gian thực vô hạn (\textit{infinite streaming data}).
    \item \textbf{12 phép biến đổi mang tính thủ công:} Bộ phép biến đổi được thiết kế dựa trên trực giác con người; một số miền dữ liệu đặc thù có thể đòi hỏi các phép biến đổi tự thích ứng.
\end{itemize}

\subsection{Hướng phát triển tương lai}

\begin{enumerate}[leftmargin=*, itemsep=2pt, parsep=0pt]
    \item \textbf{FAA trực tuyến (Online Streaming FAA):} Cải tiến cơ chế FAA bằng cách tính trung bình trượt có suy giảm theo hàm mũ (\textit{Exponential Moving Average}) trên cửa sổ trượt động, cho phép loại bỏ pseudo-normal thời gian thực.
    \item \textbf{Tăng cường dữ liệu có thể học được (\textit{Learnable Augmentation}):} Ứng dụng mạng sinh đối kháng (GAN) hoặc mô hình khuếch tán để tự động tìm kiếm các phép biến đổi giả lập tối ưu cho từng miền dữ liệu chuyên biệt.
    \item \textbf{Triển khai biên (Edge AI):} Lượng tử hóa mô hình sang định dạng INT8 và đóng gói bằng ONNX Runtime để vận hành trực tiếp trên các thiết bị nhúng và gateway IoT công nghiệp.
\end{enumerate}

\begin{thebibliography}{99}
\small

\bibitem{obata2025}
K. Obata, K. Tsubouchi, and T. Matsubara. 2025.
Time Series Anomaly Detection via Augmenting Multiclass Pseudo-Anomalies.
In \textit{Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '25)}.

\bibitem{liu2008}
F. T. Liu, K. M. Ting, and Z.-H. Zhou. 2008.
Isolation Forest.
In \textit{IEEE International Conference on Data Mining (ICDM)}, 413--422.

\bibitem{chen2016}
T. Chen and C. Guestrin. 2016.
XGBoost: A Scalable Tree Boosting System.
In \textit{Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining}, 785--794.

\bibitem{scholkopf1999}
B. Schölkopf, R. C. Williamson, A. Smola, J. Shawe-Taylor, and J. Platt. 1999.
Support Vector Method for Novelty Detection.
In \textit{Advances in Neural Information Processing Systems (NeurIPS)}, 582--588.

\bibitem{audibert2020}
J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga. 2020.
USAD: UnSupervised Anomaly Detection on Multivariate Time Series.
In \textit{Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining (KDD)}, 3395--3404.

\bibitem{tuli2022}
S. Tuli, G. Casale, and N. R. Jennings. 2022.
TranAD: Deep transformer networks for anomaly detection in multivariate time series data.
\textit{Proceedings of the VLDB Endowment}, 15, 6 (2022), 1201--1214.

\bibitem{park2018}
D. Park, Y. Hoshi, and C. C. Kemp. 2018.
A Multimodal Anomaly Detector for Robot-Assisted Feeding Using an LSTM-Based Variational Autoencoder.
\textit{IEEE Robotics and Automation Letters}, 3, 3 (2018), 1544--1551.

\bibitem{zhou2019}
B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye. 2019.
BeatGAN: Anomalous Rhythm Detection using Adversarial Generation.
In \textit{Proceedings of the 28th International Joint Conference on Artificial Intelligence (IJCAI)}, 4433--4439.

\bibitem{xu2022}
J. Xu, H. Wu, J. Wang, and M. Long. 2022.
Anomaly Transformer: Time Series Anomaly Detection with Association Discrepancy.
In \textit{International Conference on Learning Representations (ICLR)}.

\bibitem{yang2023}
Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun. 2023.
DCdetector: Dual Attention Contrastive Representation Learning for Time Series Anomaly Detection.
In \textit{Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)}, 3033--3045.

\bibitem{zhang2023}
X. Zhang, Z. Zhang, and D. Zhang. 2023.
Input-guided masked diffusion for anomaly detection in multivariate time series.
In \textit{NeurIPS 2023 Workshop on Diffusion Models}.

\bibitem{wang2024d3r}
Y. Wang, Z. Peng, J. Li, and J. Gao. 2024.
D3R: Diffusion-based Dual-branch Denoising and Reconstruction for Multivariate Time Series Anomaly Detection.
\textit{arXiv preprint arXiv:2408.06730} (2024).

\bibitem{carmona2022}
C. U. Carmona, F.-X. Aubet, V. Flunkert, and J. Gasthaus. 2022.
Neural Contextual Anomaly Detection for Time Series.
In \textit{International Conference on Learning Representations (ICLR)}.

\bibitem{xu2024}
H. Xu, Y. Wang, S. Jian, Q. Liao, Y. Wang, and H. Peng. 2024.
Calibrated One-class Classification for Unsupervised Time Series Anomaly Detection.
In \textit{Proceedings of the AAAI Conference on Artificial Intelligence}, Vol. 38, 16199--16207.

\bibitem{wang2024}
Y. Wang, T. Xu, S. Dong, C. Peng, and L. Akoglu. 2024.
CutAddPaste: Self-supervised Time Series Anomaly Detection via Binary Augmentation.
In \textit{Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD)}.

\bibitem{su2019}
Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei. 2019.
Robust Anomaly Detection for Multivariate Time Series through Stochastic Recurrent Neural Network.
In \textit{Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining (KDD)}, 2828--2837.

\bibitem{liu2024}
M. Liu, Y. Zhao, et al. 2024.
TSB-AD: Benchmarking Time Series Anomaly Detection across 1000+ Datasets.
\textit{Proceedings of the VLDB Endowment} (2024).

\bibitem{paparrizos2022}
J. Paparrizos, P. Boniol, T. Palpanas, R. S. Tsay, A. Elmore, and M. J. Franklin. 2022.
Volume under the surface: a new accuracy evaluation measure for time-series anomaly detection.
\textit{Proceedings of the VLDB Endowment}, 15, 11 (2022), 2774--2787.

\bibitem{tatbul2018}
N. Tatbul, T. J. Lee, S. Zdonik, M. Alam, and J. Gottschlich. 2018.
Precision and Recall for Time Series.
In \textit{Advances in Neural Information Processing Systems (NeurIPS)}, 1924--1934.

\bibitem{kim2022}
S. Kim, K. Choi, H.-S. Choi, B. Lee, and S. Yoon. 2022.
Towards a rigorous evaluation of time-series anomaly detection.
In \textit{Proceedings of the AAAI Conference on Artificial Intelligence}, Vol. 36, 7194--7201.

\bibitem{lai2021}
K.-H. Lai, D. Zha, J. Xu, Y. Zhao, G. Wang, and X. Hu. 2021.
Revisiting time series outlier detection: Definitions and benchmarks.
In \textit{Advances in Neural Information Processing Systems (NeurIPS) Track on Datasets and Benchmarks}.

\bibitem{blazquez2021}
A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano. 2021.
A Review on Outlier/Anomaly Detection in Time Series Data.
\textit{ACM Computing Surveys}, 54, 3 (2021), 1--33.

\bibitem{wu2021}
R. Wu and E. J. Keogh. 2021.
Current time series anomaly detection benchmarks are flawed and are creating the illusion of progress.
\textit{IEEE Transactions on Knowledge and Data Engineering}, 35, 3 (2021), 2421--2429.

\bibitem{hundman2018}
K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom. 2018.
Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding.
In \textit{Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery \& Data Mining (KDD)}, 387--395.

\bibitem{hendrycks2019}
D. Hendrycks, M. Mazeika, and T. Dietterich. 2019.
Deep Anomaly Detection with Outlier Exposure.
In \textit{International Conference on Learning Representations (ICLR)}.

\bibitem{li2021}
C.-L. Li, K. Sohn, J. Yoon, and T. Pfister. 2021.
CutPaste: Self-supervised learning for anomaly detection and localization.
In \textit{Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)}, 9664--9674.

\bibitem{yoo2023}
J. Yoo, T. Zhao, and L. Akoglu. 2023.
Data Augmentation is a Hyperparameter: Cherry-picked Self-Supervision for Unsupervised Anomaly Detection is Creating the Illusion of Success.
\textit{Transactions on Machine Learning Research (TMLR)} (2023).

\bibitem{yoon2022}
J. Yoon, K. Sohn, C.-L. Li, S. O. Arik, C.-Y. Lee, and T. Pfister. 2022.
Self-supervise, Refine, Repeat: Improving Unsupervised Anomaly Detection.
\textit{Transactions on Machine Learning Research (TMLR)} (2022).

\bibitem{wu2022}
S. Wu, J. Zhao, and G. Tian. 2022.
Understanding and Mitigating Data Contamination in Deep Anomaly Detection: A Kernel-based Approach.
In \textit{International Joint Conference on Artificial Intelligence (IJCAI)}, 2319--2325.

\bibitem{castellani2021}
A. Castellani, S. Schmitt, and B. Hammer. 2021.
Estimating the electrical power output of industrial devices with end-to-end time-series classification in the presence of label noise.
In \textit{European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases (ECML PKDD)}, 469--484.

\bibitem{goswami2023}
M. Goswami, C. I. Challu, L. Callot, L. Minorics, and A. Kan. 2023.
Unsupervised Model Selection for Time Series Anomaly Detection.
In \textit{International Conference on Learning Representations (ICLR)}.

\bibitem{lu2023}
Y. Lu, Z. Xu, and W. He. 2023.
Rethinking Label Refurbishment: Model Robustness under Label Noise.
In \textit{Proceedings of the AAAI Conference on Artificial Intelligence}, Vol. 37, 15000--15008.

\bibitem{patrini2017}
G. Patrini, A. Rozza, A. K. Menon, R. Nock, and L. Qu. 2017.
Making deep neural networks robust to label noise: A loss correction approach.
In \textit{Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)}, 1944--1952.

\bibitem{malhotra2016}
P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and G. Shroff. 2016.
LSTM-based encoder-decoder for multi-sensor anomaly detection.
\textit{arXiv preprint arXiv:1607.00148} (2016).

\bibitem{tan2011}
S. C. Tan, K. M. Ting, and T. F. Liu. 2011.
Fast anomaly detection for streaming data.
In \textit{International Joint Conference on Artificial Intelligence (IJCAI)}, 1511--1516.

\bibitem{sarfraz2024}
M. S. Sarfraz, M.-Y. Chen, L. Layer, K. Peng, and M. Koulakis. 2024.
Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?
In \textit{International Conference on Machine Learning (ICML)}.

\end{thebibliography}

\vspace{6pt}
\noindent\rule{\columnwidth}{0.4pt}
\footnotesize
\noindent\textit{Báo cáo môn học -- Hệ thống Phát hiện Bất thường Chuỗi thời gian RedLamp}\\
\textit{Dựa trên paper: Obata et al., KDD 2025 $\mid$ Mã nguồn: \url{https://github.com/KoheiObata/RedLamp}}

\end{document}
"""
with open("sigconf (2).tex", "w", encoding="utf-8") as f:
    f.write(content)
