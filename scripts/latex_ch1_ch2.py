# -*- coding: utf-8 -*-
CHAPTER_1_LATEX = r"""
% CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ TÍNH CẤP THIẾT
% =========================================================================
\section{TỔNG QUAN ĐỀ TÀI VÀ TÍNH CẤP THIẾT}
\label{sec:chapter1}

\subsection{Bối cảnh phát hiện bất thường trong dữ liệu chuỗi thời gian}
Trong kỷ nguyên Chuyển đổi số và Công nghiệp 4.0, sự bùng nổ của hạ tầng điện toán đám mây quy mô siêu lớn (\textit{Hyperscale Cloud}), mạng lưới thiết bị Internet vạn vật công nghiệp (\textit{Industrial IoT} -- IIoT), các hệ thống giám sát vệ tinh không gian (\textit{Spacecraft Telemetry}) và các nền tảng giao dịch tài chính tần suất cao (\textit{High-Frequency Trading}) đã sản sinh ra một khối lượng khổng lồ dữ liệu chuỗi thời gian (\textit{Time-Series Data}). Chuỗi thời gian là tập hợp các quan sát số học được ghi nhận liên tục theo trình tự thời gian, phản ánh trạng thái động lực học, hành vi hoạt động và sức khỏe vật lý của các thực thể phần cứng lẫn phần mềm. Trong các môi trường vận hành khắt khe này, một sự cố gián đoạn dịch vụ, một lỗi quá tải phần cứng máy chủ, hay một hư hỏng cảm biến cơ khí nhỏ nếu không được nhận diện kịp thời đều có thể dẫn đến thiệt hại hàng triệu đô la, thậm chí đe dọa nghiêm trọng đến an toàn tính mạng con người và an ninh quốc gia.

Do đó, bài toán Phát hiện bất thường trong chuỗi thời gian (\textit{Time-Series Anomaly Detection} -- TSAD) trở thành một trong những lĩnh vực nghiên cứu nền tảng và có giá trị ứng dụng thực tiễn cao nhất của Trí tuệ Nhân tạo và Khoa học Dữ liệu hiện đại. Mục tiêu tối thượng của TSAD là tự động phân tích dòng dữ liệu liên tục để chỉ ra chính xác thời điểm, khoảng thời gian và mức độ nghiêm trọng của các hành vi dị biệt (\textit{anomalies / outliers}) khác biệt rõ rệt so với quy luật vận hành danh định (\textit{nominal behavior}).

\subsection{Những thách thức cốt lõi trong thực tế}
Mặc dù đã trải qua hàng thập kỷ phát triển từ các phương pháp thống kê cổ điển đến các mạng nơ-ron học sâu phức tạp, bài toán TSAD trong thực tiễn vẫn phải đối mặt với ba rào cản kỹ thuật đặc biệt nan giải:

\begin{enumerate}
    \item \textbf{Sự khan hiếm nghiêm trọng của nhãn dữ liệu chuẩn (\textit{Ground-Truth Labels}):} 
    Trong hầu hết các hệ thống thực tế, các sự cố bất thường xảy ra với tần suất vô cùng thấp (thường chiếm dưới $1\%$ đến $5\%$ tổng thời lượng quan sát). Việc thu thập và gắn nhãn thủ công các sự cố này đòi hỏi chi phí khổng lồ, cần đến sự can thiệp của các chuyên gia miền chuyên sâu (\textit{Domain Experts}) và tiềm ẩn nguy cơ sai lệch chủ quan. Hơn thế nữa, các dạng lỗi mới phát sinh trong tương lai thường không hề xuất hiện trong lịch sử quá khứ. Vì vậy, các giải pháp học có giám sát truyền thống hoàn toàn bị tê liệt hoặc suy giảm độ chính xác nghiêm trọng khi đối mặt với dữ liệu thế giới thực không có nhãn.
    
    \item \textbf{Nghịch lý ``Tổng quát hóa thái quá'' (\textit{Over-Generalization}) của các mô hình học sâu tái tạo:} 
    Để vượt qua bài toán thiếu nhãn, hướng tiếp cận không giám sát dựa trên mô hình tự mã hóa (\textit{Autoencoder} -- AE) hoặc tự mã hóa biến phân (\textit{VAE}) đã trở thành tiêu chuẩn chủ đạo. Cơ chế hoạt động của AE là học cách nén chuỗi thời gian đầu vào thành một vector tiềm ẩn (\textit{latent vector}) rồi tái tạo lại chính chuỗi đó, dựa trên giả định rằng mô hình chỉ được huấn luyện trên dữ liệu bình thường nên sẽ không thể tái tạo được các bất thường, từ đó sinh ra sai số tái tạo (\textit{Reconstruction Error}) cao tại các vị trí lỗi. Tuy nhiên, các nghiên cứu gần đây đã chỉ ra một hạn chế chí mạng: do khả năng xấp xỉ hàm phi tuyến mạnh mẽ của mạng nơ-ron sâu, các mô hình AE thông thường rất dễ rơi vào hiện tượng ``tổng quát hóa thái quá''. Khi gặp một đoạn bất thường có biên độ hoặc tần số lạ, bộ giải mã vẫn có thể vô tình tái tạo lại chính xác đoạn lỗi đó với sai số cực nhỏ. Hậu quả là mô hình bỏ sót các sự cố nguy hiểm (tăng tỉ lệ \textit{False Negatives}).
    
    \item \textbf{Tính phức tạp đa chiều và sự tương quan chéo giữa các cảm biến (\textit{Multivariate Inter-dependencies}):} 
    Các hệ thống hiện đại như cụm máy chủ phân tán (SMD với 38 chỉ số đo lường) hay hệ thống tàu thăm dò không gian của NASA (MSL với 55 thuộc tính) có sự liên kết phi tuyến cực kỳ phức tạp giữa các kênh đo. Một sự cố có thể không biểu hiện rõ rệt ở từng kênh riêng lẻ (biên độ vẫn nằm trong ngưỡng an toàn) mà chỉ bộc lộ qua sự phá vỡ mối tương quan giữa các kênh đồng thời. Việc phát hiện các bất thường phụ thuộc ngữ cảnh (\textit{Contextual Anomalies}) đòi hỏi kiến trúc nơ-ron phải có khả năng đồng thời trích xuất đặc trưng thời gian (\textit{Temporal Dynamics}) và đặc trưng không gian đa kênh (\textit{Spatial Correlations}) một cách hiệu quả mà không làm bùng nổ chi phí tính toán.
\end{enumerate}

\subsection{Mục tiêu nghiên cứu và Phạm vi đề tài}
Xuất phát từ các thách thức thực tiễn nêu trên, đề tài tập trung nghiên cứu, cải tiến và xây dựng hoàn chỉnh hệ thống phát hiện bất thường chuỗi thời gian không giám sát \textbf{RedLamp} (\textit{Robust and Explainable Detector of Time Series Anomaly via Augmenting Multiclass Pseudo-Anomalies}).

Mục tiêu cụ thể của đề tài bao gồm:
\begin{enumerate}
    \item Nghiên cứu sâu sắc cơ chế học tự giám sát (\textit{Self-Supervised Learning}) kết hợp giữa mô hình tái tạo có mặt nạ (\textit{Masked Reconstruction}) và phân loại hình thái bất thường nhân tạo đa lớp (\textit{Multi-class Pseudo-Anomaly Classification}).
    \item Tối ưu hóa kiến trúc mạng nơ-ron tích chập 1 chiều \textbf{ConvAEC} (\textit{Convolutional Autoencoder with Classifier}), loại bỏ hoàn toàn các lớp hồi quy tuần tự (RNN/LSTM) để đạt tốc độ xử lý song song vượt trội trên GPU/CPU, đồng thời duy trì độ chính xác cao trên các chuỗi thời gian đa chiều.
    \item Xây dựng bộ sinh 12 hình thái biến dạng bất thường giả lập phong phú, kết hợp kỹ thuật làm mượt nhãn bất đối xứng (\textit{Asymmetric Label Smoothing with Normal Prior}) và cơ chế tính điểm hai giai đoạn (\textit{Two-Stage Composite Anomaly Scoring}) để triệt tiêu hiện tượng báo động giả và khắc phục triệt để hiện tượng over-generalization.
    \item Triển khai thực nghiệm nghiêm ngặt, đối sánh toàn diện RedLamp với các mô hình cơ sở (\textit{Isolation Forest, XGBoost, LSTM-VAE}) và các mô hình SOTA quốc tế trên 6 bộ benchmark tiêu chuẩn (SMD, IOPS, SMAP, MSL, Stock, UCR Anomaly Archive) theo các thang đo phạm vi hiện đại (VUS-ROC, VUS-PR, Range-F1).
    \item Thiết kế và phát triển hoàn chỉnh ứng dụng Web Demo tương tác (Python FastAPI backend + HTML5 Canvas offline frontend), cho phép người dùng kiểm thử trực tiếp trên 159 thực thể benchmark, đồng thời cung cấp khả năng giải thích trực quan (\textit{Explainable AI}) từng tầng nơ-ron của mô hình thông qua cơ chế PyTorch forward hooks.
\end{enumerate}

\subsection{Các đóng góp khoa học và thực tiễn nổi bật của đề tài}
\label{subsec:contributions}
Công trình nghiên cứu mang lại 5 đóng góp học thuật và kỹ thuật nổi bật sau:

\begin{itemize}
    \item \textbf{Đóng góp 1 (Khung tự giám sát không giám sát đột phá):} Đề tài loại bỏ hoàn toàn sự lệ thuộc vào nhãn sự cố của con người, đề xuất cơ chế tự giám sát dựa trên việc tiêm các hình thái dị biệt giả lập vào chuỗi sạch, biến bài toán không giám sát truyền thống thành bài toán tối ưu hóa đa nhiệm (\textit{Multi-task Learning}) có định hướng rõ ràng.
    
    \item \textbf{Đóng góp 2 (Hệ thống phân loại 12 hình thái biến dạng tín hiệu):} Xây dựng bộ phân loại bao quát 11 hình thái bất thường nhân tạo đặc trưng (chia thành hai nhóm: bất thường điểm biến dị cục bộ như Spike, Noise, Cutoff; và bất thường cấu trúc biến dạng hình thái như Flip, Speedup, Average, Scale, Wander, Contextual, UpsideDown, Mixture) cùng với trạng thái Normal danh định.
    
    \item \textbf{Đóng góp 3 (Cơ chế làm mượt nhãn bất đối xứng với tiên nghiệm Normal):} Đề xuất công thức làm mượt nhãn mềm chuyên biệt gán trọng số ưu tiên $\alpha = 0.1$ cho lớp Normal và phân bổ đều $\beta = 0.01$ cho các lớp còn lại. Cơ chế này ngăn chặn mạng nơ-ron tự tin thái quá (\textit{over-confidence}) vào các tạo tác nhân tạo, tạo ra vùng đệm dung sai hoàn hảo khi tiếp xúc với các dị biệt thực tế ngoài tự nhiên.
    
    \item \textbf{Đóng góp 4 (Quy trình tính điểm kết hợp hai giai đoạn có lọc nền động):} Đề xuất công thức hợp nhất điểm số cuối cùng $\text{Score}(t) = 0.5 \cdot [\text{Score}_{\text{MSE}}(t) + \text{Score}_{\text{CE}}(t)]$, trong đó nhánh phân loại $\text{Score}_{\text{CE}}$ được trang bị cơ chế tự động loại bỏ các lớp nền có xác suất trung bình toàn chuỗi vượt ngưỡng $0.05$ ($\theta_{\text{bg}} = 0.05$), triệt tiêu các cảnh báo giả do biến động nhiễu môi trường.
    
    \item \textbf{Đóng góp 5 (Hệ thống Web Demo Explainable AI hoàn chỉnh chạy Offline):} Xây dựng thành công ứng dụng demo trực quan với kiến trúc phi phụ thuộc Internet ($100\%$ offline), tích hợp đầy đủ 159 thực thể của 5 bộ dữ liệu quốc tế, cho phép can thiệp tham số, tiêm điểm dữ liệu tùy biến và bóc tách trực quan từng lớp kích hoạt nơ-ron (\textit{Feature Heatmap, Latent Vector, Reconstructed Curves}).
\end{itemize}

\subsection{Bố cục của báo cáo}
Báo cáo khóa luận được cấu trúc thành 7 chương chính như sau:
\begin{itemize}
    \item \textbf{Chương 1:} Tổng quan đề tài và Tính cấp thiết.
    \item \textbf{Chương 2:} Cơ sở lý thuyết và Các công trình liên quan.
    \item \textbf{Chương 3:} Kiến trúc mô hình RedLamp và Giải thuật cốt lõi.
    \item \textbf{Chương 4:} Dữ liệu thực nghiệm, Môi trường phần cứng và Thiết lập huấn luyện.
    \item \textbf{Chương 5:} Kết quả thực nghiệm và Phân tích đối sánh chuyên sâu.
    \item \textbf{Chương 6:} Thiết kế và Hiện thực Hệ thống Web Demo Tương tác \& Khả năng Giải thích (Explainable AI).
    \item \textbf{Chương 7:} Kết luận và Hướng phát triển tương lai.
    \item \textbf{Tài liệu tham khảo \& Phụ lục kỹ thuật:} Liệt kê 20 tài liệu chuẩn quốc tế và các mã nguồn, bảng tra cứu chi tiết.
\end{itemize}



% =========================================================================
"""

CHAPTER_2_LATEX = r"""
% CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG TRÌNH LIÊN QUAN
% =========================================================================
\section{CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG TRÌNH LIÊN QUAN}
\label{sec:chapter2}

\subsection{Định nghĩa toán học bài toán phát hiện bất thường chuỗi thời gian}
Chuỗi thời gian đa chiều (\textit{Multivariate Time Series}) được định nghĩa hình thức dưới dạng một ma trận chuỗi:
\begin{equation}
\label{eq:multivariate_ts}
X = [x_1, x_2, \dots, x_T]^T \in \mathbb{R}^{T \times D}
\end{equation}
trong đó $T$ là tổng độ dài thời gian quan sát (số bước thời gian -- \textit{timestamps}) và $D$ là số chiều thuộc tính (số lượng biến số hoặc kênh cảm biến đồng thời, $D \ge 1$). Tại mỗi bước thời gian $t \in \{1, 2, \dots, T\}$, quan sát:
\begin{equation}
x_t = [x_{t,1}, x_{t,2}, \dots, x_{t,D}]^T \in \mathbb{R}^D
\end{equation}
biểu diễn trạng thái tức thời của hệ thống.

Trong bài toán phát hiện bất thường không giám sát (\textit{Unsupervised TSAD}), tập dữ liệu huấn luyện $X_{\text{train}}$ được thu thập từ quá trình vận hành bình thường của hệ thống, nhưng có thể chứa một lượng nhỏ nhiễu ngẫu nhiên không được gắn nhãn. Tập dữ liệu kiểm thử $X_{\text{test}}$ đi kèm với một chuỗi nhãn nhị phân chuẩn $Y \in \{0, 1\}^T$, trong đó $Y_t = 0$ biểu thị trạng thái bình thường (\textit{Nominal}) và $Y_t = 1$ biểu thị trạng thái bất thường (\textit{Anomalous}). 

Mục tiêu của thuật toán TSAD là học một hàm chấm điểm phi tuyến:
\begin{equation}
f: \mathbb{R}^{W \times D} \rightarrow \mathbb{R}^+
\end{equation}
sao cho với mỗi cửa sổ trượt tại thời điểm $t$, hàm $f$ gán một điểm số bất thường $\text{Score}(t) \in [0, 1]$. Một điểm dữ liệu được kết luận là bất thường nếu $\text{Score}(t)$ vượt qua một ngưỡng quyết định $\tau$ (\textit{Threshold}):
\begin{equation}
\hat{Y}_t = 
\begin{cases}
1, & \text{nếu } \text{Score}(t) \ge \tau \\
0, & \text{ngược lại}
\end{cases}
\end{equation}

\subsection{Phân loại hình thái bất thường trong chuỗi thời gian}
Dựa trên đặc tính hình học và phạm vi lan truyền thời gian, các bất thường trong chuỗi thời gian được phân thành 3 nhóm cơ bản:

\begin{enumerate}
    \item \textbf{Bất thường điểm (\textit{Point Anomalies}):} 
    Là các quan sát đơn lẻ có giá trị lệch đột ngột và cực đoan so với toàn bộ phần còn lại của dữ liệu (ví dụ: các xung nhọn tức thời -- \textit{Spikes} do nhiễu điện áp, hoặc sự sụt giảm tức thì về 0 do mất kết nối cảm biến). Điểm bất thường này dễ nhận diện nếu phân tích theo phân phối thống kê biên, nhưng lại dễ bị nhầm lẫn với nhiễu trắng nếu không xét ngữ cảnh lân cận.
    
    \item \textbf{Bất thường ngữ cảnh (\textit{Contextual Anomalies}):} 
    Là các điểm dữ liệu có giá trị biên độ hoàn toàn nằm trong dải hoạt động danh định của hệ thống, nhưng lại trở nên bất thường khi đặt trong bối cảnh thời gian hoặc tương quan giữa các kênh. Ví dụ: nhiệt độ CPU máy chủ đạt $85^\circ\text{C}$ trong giờ cao điểm chạy tác vụ tính toán nặng là bình thường, nhưng nhiệt độ $85^\circ\text{C}$ vào lúc nửa đêm khi CPU chỉ tải $2\%$ là một bất thường ngữ cảnh nghiêm trọng.
    
    \item \textbf{Bất thường tập thể / Bất thường chuỗi (\textit{Collective / Pattern Anomalies}):} 
    Là một chuỗi các điểm dữ liệu liên tiếp mà từng điểm riêng lẻ đều có vẻ bình thường, nhưng toàn bộ hình thái động lực học (\textit{Shapelet / Trajectory}) của đoạn chuỗi đó lại vi phạm chu kỳ hoặc quy luật vận hành của hệ thống (ví dụ: hiện tượng trôi dạt xu hướng -- \textit{Wander}, tín hiệu bị kẹp cứng một mức giá trị không đổi -- \textit{Flatline/Cutoff}, hoặc hiện tượng đảo ngược chu kỳ dao động -- \textit{UpsideDown}).
\end{enumerate}

\subsection{Tổng quan các phương pháp tiếp cận truyền thống}

\subsubsection{Isolation Forest (Rừng cô lập -- iForest)}
Isolation Forest (Liu et al.~\cite{liu2008isolation}) là một trong những giải thuật học máy phi tham số phổ biến nhất trong phát hiện dị biệt. Thuật toán hoạt động dựa trên nguyên lý: các điểm bất thường thường ``ít'' và ``khác biệt'', do đó chúng sẽ bị cô lập nhanh hơn các điểm bình thường trong cấu trúc cây nhị phân phân vùng ngẫu nhiên (\textit{iTree}).
Độ sâu trung bình $h(x)$ của điểm $x$ trên một tập hợp gồm $n_{\text{tree}}$ cây cô lập được sử dụng để tính điểm số bất thường:
\begin{equation}
\label{eq:iforest_score}
\text{Score}_{\text{iForest}}(x) = 2^{-\frac{\mathbb{E}(h(x))}{c(n)}}
\end{equation}
trong đó $c(n)$ là độ sâu trung bình của một cây tìm kiếm nhị phân thất bại xây dựng trên $n$ điểm:
\begin{equation}
c(n) = 2 \ln(n - 1) + 0.5772156649 \text{ (Euler's constant)} - \frac{2(n-1)}{n}
\end{equation}
\textbf{Ưu điểm:} Tốc độ tính toán nhanh, độ phức tạp tuyến tính $\mathcal{O}(n)$, không yêu cầu giả định phân phối chuẩn.
\textbf{Nhược điểm:} iForest xử lý các điểm dữ liệu hoàn toàn độc lập, xem nhẹ mối liên kết thời gian (\textit{Temporal Ordering}). Khi áp dụng vào chuỗi thời gian, ta buộc phải dùng cửa sổ trượt phẳng hóa (\textit{flattened sliding window}), dẫn đến bùng nổ số chiều và mất mát cấu trúc chuỗi liên tục.

\subsubsection{Mô hình dựa trên Gradient Boosting (XGBoost Anomaly Detector)}
XGBoost (Chen \& Guestrin~\cite{chen2016xgboost}) là thuật toán tối ưu hóa cây quyết định tăng cường gradient vượt trội trong các bài toán bảng. Trong bài toán TSAD không giám sát, XGBoost thường được triển khai dưới dạng bộ dự báo tự hồi quy (\textit{Autoregressive Forecaster}): mô hình sử dụng $W-1$ bước thời gian quá khứ $[x_{t-W+1}, \dots, x_{t-1}]$ để dự báo bước thời gian tương lai $x_t$. Sai số tuyệt đối giữa giá trị thực tế và giá trị dự báo $|x_t - \hat{x}_t|$ được chuẩn hóa làm điểm số bất thường.
\textbf{Ưu điểm:} Khả năng học các mối quan hệ phi tuyến phức tạp rất mạnh mẽ, xử lý tốt dữ liệu bảng nhiều thuộc tính.
\textbf{Nhược điểm:} Việc dự báo từng bước thời gian rất nhạy cảm với hiện tượng tích lũy sai số (\textit{Error Accumulation}). Khi tín hiệu có tính ngẫu nhiên cao hoặc biến động phi tuần hoàn, XGBoost sinh ra nhiều cảnh báo giả do sai số dự báo tự nhiên tăng cao.

\subsection{Tổng quan các phương pháp học sâu (Deep Learning Baselines)\nTheo các khảo sát tổng quan hệ thống và nghiên cứu đánh giá toàn diện của Blázquez-García et al.~\cite{blazquez2021review} cũng như Schmidl et al.~\cite{schmidl2022anomaly}, các phương pháp học sâu phát hiện bất thường chuỗi thời gian thường kết hợp mạng tự mã hóa với các mô hình xác suất tiềm ẩn (như DAGMM~\cite{zong2018deep}, USAD~\cite{audibert2020usad}, hay giải mã đa phân giải~\cite{shen2020timeseries}).}

\subsubsection{Mô hình Tự mã hóa Tích chập thuần túy (Vanilla ConvAE)}
Kiến trúc Autoencoder tích chập (ConvAE) nén chuỗi thời gian qua các tầng 1D-CNN thành vector tiềm ẩn và giải mã ngược lại.
Hàm mất mát tối ưu hóa là sai số bình phương trung bình:
\begin{equation}
\mathcal{L}_{\text{AE}} = \frac{1}{W \times D} \sum_{t=1}^W \sum_{d=1}^D (x_{t,d} - \hat{x}_{t,d})^2
\end{equation}
Tuy nhiên, Vanilla ConvAE không có cơ chế ngăn chặn việc học tái tạo các mẫu lỗi, dẫn đến hiện tượng ``tổng quát hóa thái quá'' khi mạng tái tạo thành công cả các dị biệt.

\subsubsection{Mạng Tự mã hóa Biến phân hồi quy (LSTM-VAE)}
LSTM-VAE (Park et al.~\cite{park2018multimodal}) kết hợp khả năng mô hình hóa chuỗi tuần tự của LSTM với tính chất sinh xác suất của VAE. Mô hình ánh xạ chuỗi đầu vào thành các tham số của phân phối chuẩn nhiều chiều trong không gian tiềm ẩn: $\mu_z$ và $\sigma_z$, sau đó sử dụng kỹ thuật tái tham số hóa (\textit{Reparameterization Trick}):
\begin{equation}
z = \mu_z + \sigma_z \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)
\end{equation}
Hàm mục tiêu là cận dưới bằng chứng biến phân (\textit{Evidence Lower Bound} -- ELBO):
\begin{equation}
\mathcal{L}_{\text{ELBO}} = \mathbb{E}_{q(z|X)}[\log p(X|z)] - D_{\text{KL}}(q(z|X) \,\|\, p(z))
\end{equation}
Điểm số bất thường là xác suất tái tạo âm (\textit{Negative Reconstruction Probability}).
\textbf{Hạn chế:} Tốc độ huấn luyện và suy luận của LSTM cực kỳ chậm do tính chất tính toán tuần tự không thể song song hóa triệt để trên GPU; đồng thời mô hình dễ bị suy giảm gradient trên chuỗi dài.

\subsubsection{Các mô hình dựa trên Transformer (Anomaly Transformer~\cite{xu2022anomaly}~\cite{xu2022anomaly}, TranAD~\cite{tuli2022tranad}, DCdetector~\cite{yang2023dcdetector})}
Trong những năm gần đây, các kiến trúc mô hình hóa chuỗi thời gian như Informer~\cite{zhou2021informer}, Autoformer~\cite{wu2021autoformer} đã mở đường cho các biến thể TSAD chuyên biệt. Tiêu biểu là \textit{Anomaly Transformer~\cite{xu2022anomaly}} (Xu et al.~\cite{xu2022anomaly}) đề xuất cơ chế \textit{Association Discrepancy} để so sánh giữa sự chú ý tiên nghiệm (\textit{Prior-Association}) và sự chú ý chuỗi (\textit{Series-Association}). Mô hình \textit{DCdetector} (Yang et al.~\cite{yang2023dcdetector}) sử dụng học tương phản đa tỉ lệ (\textit{Dual Attention Contrastive Learning}).
Mặc dù đạt độ chính xác cao, các mô hình Transformer gặp phải rào cản tính toán: độ phức tạp bộ nhớ và thời gian bậc hai $\mathcal{O}(W^2)$, đòi hỏi hàng chục gigabyte VRAM và thời gian huấn luyện kéo dài gấp 10 lần so với mạng tích chập 1D thuần túy, gây khó khăn lớn khi triển khai trên các thiết bị giám sát thực địa.

\subsection{Khoảng trống nghiên cứu và Sự cần thiết của RedLamp}
Qua việc phân tích toàn diện các công trình nghiên cứu hiện hữu, ta nhận thấy một khoảng trống nghiên cứu rõ rệt:
\begin{itemize}
    \item Các phương pháp AE/VAE truyền thống bị tê liệt trước hiện tượng Over-generalization.
    \item Các mô hình Transformer SOTA có chi phí tính toán quá cao và là ``hộp đen'' hoàn toàn, không cung cấp được lời giải thích trực quan về mặt hình thái học cho kỹ sư vận hành.
\end{itemize}
Do đó, sự ra đời của \textbf{RedLamp} với kiến trúc \textbf{ConvAEC} thuần tích chập, kết hợp tái tạo có mặt nạ và phân loại 12 hình thái bất thường giả lập tự giám sát, là bước đột phá giải quyết đồng thời cả ba tiêu chí: \textbf{Độ chính xác cao -- Tốc độ siêu tốc -- Khả năng giải thích sâu sắc (Explainable AI)}.



% =========================================================================
"""
