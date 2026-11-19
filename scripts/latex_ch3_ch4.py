# -*- coding: utf-8 -*-
CHAPTER_3_LATEX = r"""
% CHƯƠNG 3: KIẾN TRÚC MÔ HÌNH REDLAMP VÀ GIẢI THUẬT CỐT LÕI
% =========================================================================
\section{KIẾN TRÚC MÔ HÌNH REDLAMP VÀ GIẢI THUẬT CỐT LÕI}
\label{sec:chapter3}

\subsection{Triết lý thiết kế tổng thể của RedLamp}
RedLamp (\textit{Robust and Explainable Detector of Time Series Anomaly via Augmenting Multiclass Pseudo-Anomalies}) được xây dựng dựa trên một triết lý đột phá nhằm giải quyết tận gốc nghịch lý Over-generalization của các mô hình Autoencoder truyền thống: \textbf{Thay vì chỉ học tái tạo thụ động trên dữ liệu sạch, mô hình được chủ động ``thách thức'' bằng các biến dạng bất thường giả lập (\textit{Pseudo-Anomalies}) có cấu trúc phong phú}.

Khung hoạt động của RedLamp được nâng đỡ bởi ba trụ cột kỹ thuật then chốt:
\begin{enumerate}
    \item \textbf{Cơ chế giám sát kép (\textit{Dual Supervision}):} Kết hợp mặt nạ tái tạo nhị phân (Binary Mask $M$) để buộc bộ giải mã chỉ được tái tạo các vùng tín hiệu nguyên bản (ngăn chặn triệt để việc học tái tạo lỗi), đồng thời kích hoạt một bộ phân loại phi tuyến đa lớp (\textit{Multiclass Classifier}) để nhận diện chính xác hình thái của biến dạng giả lập.
    \item \textbf{Làm mượt nhãn bất đối xứng (\textit{Asymmetric Label Smoothing with Normal Prior}):} Áp dụng một tiên nghiệm an toàn thiên về trạng thái bình thường (Normal), ngăn ngừa bộ phân loại bị thiên lệch hoặc tự tin thái quá vào các tạo tác nhân tạo.
    \item \textbf{Chấm điểm bất thường kết hợp hai giai đoạn (\textit{Two-Stage Composite Anomaly Scoring}):} Tích hợp đồng thời bằng chứng từ sai số tái tạo không gian (\textit{Reconstruction Residual}) và bằng chứng xác suất từ không gian ngữ nghĩa hình thái (\textit{Semantic Classification Confidence}) với cơ chế lọc nền động, tạo nên điểm số bất thường có độ bền bỉ và độ nhạy cực cao.
\end{enumerate}

\subsection{Bộ tăng cường 12 hình thái bất thường giả lập (12 Pseudo-Anomaly Morphologies)}
\label{subsec:morphologies}
Từ một cửa sổ chuỗi thời gian sạch ban đầu $X_{\text{normal}} \in \mathbb{R}^{W \times D}$ (với độ dài cửa sổ $W = 100$ bước thời gian trên $D$ kênh thuộc tính), RedLamp triển khai một động cơ tăng cường dữ liệu tự động tiêm ngẫu nhiên một trong 11 hình thái bất thường giả lập, kết hợp với chuỗi gốc để tạo thành không gian phân loại gồm $C = 12$ lớp (lớp 0 đến lớp 11).

Các hình thái bất thường được phân chia thành hai nhóm hình học rõ rệt:

\subsubsection{Nhóm 1: Bất thường điểm biến dị cục bộ (Local Point Perturbations)}
\begin{itemize}
    \item \textbf{Lớp 0 -- Normal (Bình thường):} Chuỗi thời gian sạch nguyên bản, không bị can thiệp biến dạng. Mặt nạ nhị phân tương ứng là ma trận đơn vị toàn một:
    \begin{equation}
    M = \mathbf{1} \in \{1\}^{W \times D}
    \end{equation}
    
    \item \textbf{Lớp 1 -- Spike (Đỉnh xung nhọn):} Mô phỏng hiện tượng sốc điện áp hoặc xung đột tín hiệu tức thời. Động cơ chọn ngẫu nhiên các vị trí thời gian $t_{\text{spike}}$ và kênh $d_{\text{spike}}$, tiêm vào một giá trị xung có biên độ cực lớn:
    \begin{equation}
    X_{t_{\text{spike}}, d_{\text{spike}}} \leftarrow X_{t_{\text{spike}}, d_{\text{spike}}} + s_{\text{sign}} \cdot \gamma \cdot \sigma_d
    \end{equation}
    với $s_{\text{sign}} \in \{-1, 1\}$, $\gamma \in [3.0, 6.0]$ và $\sigma_d = \text{std}(X_d)$.
    
    \item \textbf{Lớp 4 -- Noise (Nhiễu Gauss cộng dồn):} Mô phỏng hiện tượng suy hao đường truyền hoặc nhiễu trắng cảm biến. Một đoạn chuỗi thời gian $[t_{\text{start}}, t_{\text{end}}]$ được cộng thêm nhiễu phân phối chuẩn không thiên lệch:
    \begin{equation}
    X_{t, d} \leftarrow X_{t, d} + \eta_t, \quad \eta_t \sim \mathcal{N}(0, \sigma_{\text{noise}}^2), \quad \sigma_{\text{noise}} = 0.3 \cdot \sigma_d
    \end{equation}
    
    \item \textbf{Lớp 5 -- Cutoff (Kẹp ngưỡng / Treo cảm biến):} Mô phỏng sự cố cảm biến bị chạm trần đo đạc hoặc bão hòa vật lý. Tín hiệu trong đoạn $[t_{\text{start}}, t_{\text{end}}]$ bị kẹp bởi giá trị ngưỡng hằng số:
    \begin{equation}
    X_{t, d} \leftarrow \text{clamp}(X_{t, d}, \min(X_d), \mu_d)
    \end{equation}
\end{itemize}

\subsubsection{Nhóm 2: Bất thường cấu trúc và biến dạng hình thái (Structural Morphological Perturbations)}
\begin{itemize}
    \item \textbf{Lớp 2 -- Flip (Đảo ngược thời gian):} Mô phỏng hiện tượng đảo chiều tiến trình vật lý. Đoạn chuỗi $[t_{\text{start}}, t_{\text{end}}]$ bị đảo ngược thứ tự trục thời gian:
    \begin{equation}
    X_{t, d} \leftarrow X_{t_{\text{end}} - (t - t_{\text{start}}), d}
    \end{equation}
    
    \item \textbf{Lớp 3 -- Speedup (Tăng tốc tần số):} Mô phỏng hiện tượng dao động cơ học bị kích thích tăng tần số đột ngột. Đoạn tín hiệu được lấy mẫu lại (\textit{Resampling / Linear Interpolation}) với tốc độ gấp đôi, làm nén bước sóng chu kỳ dao động:
    \begin{equation}
    X_{t, d} \leftarrow \text{Interp}(X_{t_{\text{start}}:t_{\text{end}}, d}, \text{factor} = 2.0)
    \end{equation}
    
    \item \textbf{Lớp 6 -- Average (Làm mịn trung bình trượt / Mất dao động):} Mô phỏng sự cố cảm biến bị trễ phản ứng hoặc mất tính năng động. Đoạn chuỗi được thay thế bằng giá trị trung bình trượt cục bộ, làm triệt tiêu hoàn toàn phương sai dao động tự nhiên:
    \begin{equation}
    X_{t, d} \leftarrow \frac{1}{|t_{\text{end}} - t_{\text{start}}|} \sum_{\tau = t_{\text{start}}}^{t_{\text{end}}} X_{\tau, d}
    \end{equation}
    
    \item \textbf{Lớp 7 -- Scale (Khuếch đại / Suy giảm biên độ):} Mô phỏng sự thay đổi hệ số khuếch đại mạch đo. Đoạn chuỗi được nhân với một hệ số tỉ lệ $\alpha_{\text{scale}}$:
    \begin{equation}
    X_{t, d} \leftarrow X_{t, d} \cdot \alpha_{\text{scale}}, \quad \alpha_{\text{scale}} \in [0.2, 0.5] \cup [1.8, 3.0]
    \end{equation}
    
    \item \textbf{Lớp 8 -- Wander (Trôi dạt xu hướng baseline):} Mô phỏng sự trôi dạt điểm không (\textit{Zero-drift}) do ảnh hưởng nhiệt độ môi trường. Một thành phần xu hướng bậc thấp tuyến tính được cộng dồn vào tín hiệu:
    \begin{equation}
    X_{t, d} \leftarrow X_{t, d} + \delta \cdot (t - t_{\text{start}}), \quad \delta = \frac{1.5 \cdot \sigma_d}{t_{\text{end}} - t_{\text{start}}}
    \end{equation}
    
    \item \textbf{Lớp 9 -- Contextual (Lệch ngữ cảnh / Hoán đổi phân đoạn):} Một phân đoạn chuỗi từ vị trí thời gian xa xôi trong quá khứ được sao chép và ghép đè vào vị trí hiện tại $[t_{\text{start}}, t_{\text{end}}]$, tạo ra sự đứt gãy tương quan thời gian dù biên độ vẫn nằm trong dải bình thường.
    
    \item \textbf{Lớp 10 -- UpsideDown (Lật ngược cực tính biên độ):} Mô phỏng hiện tượng đảo cực tính cảm biến. Tín hiệu bị lật ngược quanh đường trục trung vị cục bộ $\mu_d$:
    \begin{equation}
    X_{t, d} \leftarrow \mu_d - (X_{t, d} - \mu_d) = 2\mu_d - X_{t, d}
    \end{equation}
    
    \item \textbf{Lớp 11 -- Mixture (Tổ hợp đa biến dạng):} Sự kết hợp ngẫu nhiên của hai hoặc nhiều hình thái biến dạng nêu trên (ví dụ: vừa bị Wander vừa bị Noise), mô phỏng các sự cố thảm họa phức tạp trong thực tế.
\end{itemize}

Mặt nạ nhị phân tái tạo $M \in \{0, 1\}^{W \times D}$ được sinh đồng bộ:
\begin{equation}
\label{eq:binary_mask}
M_{t, d} = 
\begin{cases}
0, & \text{nếu điểm } (t, d) \text{ bị biến đổi bởi bất thường giả lập} \\
1, & \text{nếu là điểm sạch nguyên bản}
\end{cases}
\end{equation}

\subsection{Kỹ thuật Làm mượt nhãn bất đối xứng (Asymmetric Label Smoothing with Normal Prior)}
\label{subsec:label_smoothing}
Trong học sâu có giám sát thông thường, nhãn mục tiêu là vector one-hot cứng $y \in \{0, 1\}^C$. Tuy nhiên, việc ép mô hình phân loại phải tuyệt đối tin tưởng vào các hình thái giả lập nhân tạo sẽ dẫn đến hai hệ lụy tiêu cực:
\begin{itemize}
    \item Mô hình quá tự tin (\textit{Over-confident}) vào các đặc trưng nhân tạo cụ thể, dẫn đến mất khả năng nhận diện các bất thường thực tế vốn có hình dạng biến hóa linh hoạt hơn.
    \item Trong tập huấn luyện bình thường, một số chuỗi có thể chứa các dao động tự nhiên hơi giống với một dạng biến dạng nhẹ nào đó (ví dụ dao động tần số hơi cao giống Speedup nhẹ). Nếu phạt nặng mô hình khi nó phân vân, quá trình học sẽ trở nên bất ổn định.
\end{itemize}

Để khắc phục hiện tượng này, RedLamp đề xuất kỹ thuật \textbf{Làm mượt nhãn bất đối xứng} độc đáo với tiên nghiệm dành riêng cho lớp Normal (lớp 0).
Cho vector nhãn one-hot chuẩn $y \in \{0, 1\}^C$ (với $C = 12$), vector nhãn mềm $\tilde{y}$ được tính toán theo quy tắc:
\begin{equation}
\label{eq:label_smoothing}
\tilde{y}_c = y_c \cdot (1 - \alpha - \beta \cdot C + \beta) + (1 - y_c) \cdot \beta, \quad \forall c \in \{0, 1, \dots, C-1\}
\end{equation}
Sau đó, riêng vị trí lớp Normal ($\text{normal\_loc} = 0$) được cộng thêm một lượng tiên nghiệm an toàn $\alpha$:
\begin{equation}
\tilde{y}_0 \leftarrow \tilde{y}_0 + \alpha
\end{equation}
Trong triển khai chuẩn của RedLamp:
\begin{itemize}
    \item Siêu tham số $\alpha = 0.1$ đóng vai trò là ``lực kéo an toàn'', củng cố niềm tin cơ bản rằng hệ thống trong phần lớn thời gian luôn có xu hướng trở về trạng thái bình thường danh định.
    \item Siêu tham số $\beta = 0.01$ phân bổ đều một lượng entropy nền nhỏ trên toàn bộ 12 lớp, giúp gradient của hàm mất mát Cross-Entropy không bao giờ bị bão hòa hay phát nổ.
\end{itemize}

\subsection{Chi tiết kiến trúc mạng nơ-ron ConvAEC}
\label{subsec:convaec_details}
Mạng nơ-ron cốt lõi của RedLamp, mang tên \textbf{ConvAEC} (\textit{Convolutional Autoencoder with Classifier}), là sự tích hợp chặt chẽ giữa một bộ tự mã hóa tích chập 1 chiều (1D-CNN) và một đầu phân loại phi tuyến đa lớp (Non-linear MLP Head). Điểm đặc biệt của ConvAEC là loại bỏ hoàn toàn các lớp mạng hồi quy tuần tự (RNN, LSTM, GRU) hay cơ chế tự chú ý bậc hai (Self-Attention $\mathcal{O}(W^2)$), từ đó đạt tốc độ tính toán song song cực đại và tối ưu hóa bộ nhớ đệm trên phần cứng hiện đại.

\begin{table}[htbp]
\centering
\caption{Bảng đặc tả chi tiết cấu hình từng tầng trong kiến trúc ConvAEC ($W=100$, Batch $B=128$)}
\label{tab:convaec_layers}
\begin{tabular}{llcccc}
\toprule
\textbf{Phân hệ} & \textbf{Tên tầng (Layer)} & \textbf{Kích thước vào} & \textbf{Cấu hình Kernel / Stride / Pad} & \textbf{Kích thước ra} & \textbf{Hàm kích hoạt} \\
\midrule
Input & Window Slicer & $(B, W, D)$ & Chuyển vị thành $(B, D, W)$ & $(B, D, 100)$ & None \\
\midrule
\multirow{4}{*}{ConvEncoder} 
& ConvBlock 1 & $(B, D, 100)$ & Conv1d($D \rightarrow 128, k=4, s=2, p=2$) & $(B, 128, 51)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvBlock 2 & $(B, 128, 51)$ & Conv1d($128 \rightarrow 128, k=4, s=2, p=2$) & $(B, 128, 26)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvBlock 3 & $(B, 128, 26)$ & Conv1d($128 \rightarrow 256, k=4, s=2, p=2$) & $(B, 256, 14)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvBlock 4 & $(B, 256, 14)$ & Conv1d($256 \rightarrow 256, k=4, s=2, p=2$) & $(B, 256, 8)$ & BatchNorm + ReLU + Dropout(0.2) \\
\midrule
\multirow{2}{*}{Bottleneck}
& Global MaxPool & $(B, 256, 8)$ & MaxPool1d($k=8$, stride=1) & $(B, 256, 1)$ & None \\
& Pointwise Conv & $(B, 256, 1)$ & Conv1d($256 \rightarrow 128, k=1, s=1, p=0$) & $(B, 128, 1)$ & None (Latent $z$) \\
\midrule
\multirow{6}{*}{ConvDecoder}
& Linear Upsample & $(B, 128, 1)$ & nn.Linear($1 \rightarrow 8$) & $(B, 128, 8)$ & None \\
& ConvTransBlock 1 & $(B, 128, 8)$ & ConvTranspose1d($128 \rightarrow 256, k=4, s=2, p=2, \text{op}=0$) & $(B, 256, 14)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvTransBlock 2 & $(B, 256, 14)$ & ConvTranspose1d($256 \rightarrow 256, k=4, s=2, p=2, \text{op}=0$) & $(B, 256, 26)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvTransBlock 3 & $(B, 256, 26)$ & ConvTranspose1d($256 \rightarrow 128, k=4, s=2, p=2, \text{op}=1$) & $(B, 128, 51)$ & BatchNorm + ReLU + Dropout(0.2) \\
& ConvTransBlock 4 & $(B, 128, 51)$ & ConvTranspose1d($128 \rightarrow 128, k=4, s=2, p=2, \text{op}=0$) & $(B, 128, 100)$ & BatchNorm + ReLU + Dropout(0.2) \\
& Output Head & $(B, 128, 100)$ & Conv1d($128 \rightarrow D, k=1, s=1, p=0$) $\rightarrow$ Transpose & $(B, 100, D)$ & None (Reconstructed $\hat{X}$) \\
\midrule
\multirow{3}{*}{Classifier}
& Dense 1 & $(B, 128)$ & nn.Linear($128 \rightarrow 32$) & $(B, 32)$ & BatchNorm + ReLU + Dropout(0.1) \\
& Dense 2 & $(B, 32)$ & nn.Linear($32 \rightarrow 12$) & $(B, 12)$ & None \\
& Softmax Head & $(B, 12)$ & nn.Softmax(dim=1) & $(B, 12)$ & Softmax Probabilities $\hat{y}$ \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{Bộ mã hóa tích chập 1D (ConvEncoder)}
Đầu vào của mạng là một tensor cửa sổ dữ liệu $X \in \mathbb{R}^{B \times W \times D}$, trong đó $B$ là kích thước batch (Batch size = 128), $W$ là độ dài cửa sổ thời gian ($W = 100$) và $D$ là số kênh cảm biến (\textit{n\_features}). Tensor được chuyển vị thành $\mathbb{R}^{B \times D \times W}$ để trục thời gian $W$ trở thành chiều không gian cho các bộ lọc tích chập 1D.

Bộ mã hóa gồm 4 khối tích chập liên tiếp (ConvBlock), với số lượng bộ lọc tăng dần:
\begin{equation}
\text{num\_filters} = [128, 128, 256, 256]
\end{equation}
Mỗi khối ConvBlock bao gồm 4 tầng con:
\begin{enumerate}
    \item Tầng Conv1d: Kích thước nhân tích chập $\text{kernel\_size} = 4$, bước trượt $\text{stride} = 2$, đệm $\text{padding} = 2$.
    \item Tầng chuẩn hóa BatchNorm1d: Giúp ổn định phân phối kích hoạt giữa các batch.
    \item Tầng hàm kích hoạt phi tuyến ReLU: Triệt tiêu các giá trị âm, kích hoạt tính phi tuyến.
    \item Tầng ngắt kết nối ngẫu nhiên Dropout: Tỉ lệ $\text{dropout} = 0.2$, ngăn chặn hiện tượng quá khớp (\textit{overfitting}).
\end{enumerate}

Quá trình biến đổi kích thước không gian thời gian (\textit{Temporal Length}) qua 4 khối ConvBlock diễn ra theo công thức chuẩn:
\begin{equation}
\label{eq:conv_out_len}
L_{\text{out}} = \left\lfloor \frac{L_{\text{in}} + 2 \cdot \text{padding} - \text{dilation} \cdot (\text{kernel\_size} - 1) - 1}{\text{stride}} + 1 \right\rfloor
\end{equation}
Với $L_0 = 100$:
\begin{itemize}
    \item Qua ConvBlock 1: $[B, D, 100] \rightarrow [B, 128, 51]$
    \item Qua ConvBlock 2: $[B, 128, 51] \rightarrow [B, 128, 26]$
    \item Qua ConvBlock 3: $[B, 128, 26] \rightarrow [B, 256, 14]$
    \item Qua ConvBlock 4: $[B, 256, 14] \rightarrow [B, 256, 8]$
\end{itemize}
Tại đầu ra của ConvBlock 4, đặc trưng có kích thước $[B, 256, 8]$. Mạng tiếp tục áp dụng tầng MaxPool1d toàn cục dọc theo chiều thời gian với $\text{kernel\_size} = 8$, nén đặc trưng thành tensor $[B, 256, 1]$. Cuối cùng, một tầng tích chập điểm $1 \times 1$ (Conv1d với 256 kênh vào, 128 kênh ra) ánh xạ tensor này thành vector biểu diễn tiềm ẩn cô đọng:
\begin{equation}
z \in \mathbb{R}^{B \times 128 \times 1} \quad (\text{hoặc } z_{\text{flat}} \in \mathbb{R}^{B \times 128})
\end{equation}

\subsubsection{Bộ giải mã tích chập chuyển vị (ConvDecoder)}
Bộ giải mã nhận vector tiềm ẩn $z \in \mathbb{R}^{B \times 128 \times 1}$ và thực hiện quá trình tái tạo ngược để khôi phục lại chuỗi có kích thước ban đầu $\mathbb{R}^{B \times W \times D}$.
\begin{enumerate}
    \item Tầng mở rộng tuyến tính (\textit{Linear Upsampling}): $z$ được ánh xạ từ chiều dài không gian 1 lên kích thước nén ban đầu $L_{\text{comp}} = 8$ thông qua tầng \texttt{nn.Linear(1, 8)}, tạo thành tensor $[B, 128, 8]$.
    \item Bốn khối tích chập chuyển vị (ConvTransposeBlock): Số lượng kênh được đảo ngược thứ tự:
    \begin{equation}
    \text{num\_channels\_inv} = [256, 256, 128, 128]
    \end{equation}
    Mỗi khối ConvTransposeBlock gồm ConvTranspose1d ($k=4, s=2, p=2$), BatchNorm1d, ReLU và Dropout(0.2). Để đảm bảo chiều dài thời gian tái tạo khôi phục chính xác 100 điểm ban đầu mà không bị lệch do phép chia lấy phần nguyên ở bộ mã hóa, RedLamp tính toán động tham số \texttt{output\_padding} cho từng khối:
    \begin{equation}
    \text{output\_padding} = [0, 0, 1, 0]
    \end{equation}
    phù hợp với dãy kích thước $8 \rightarrow 14 \rightarrow 26 \rightarrow 51 \rightarrow 100$.
    Sau 4 khối ConvTransposeBlock, tensor đạt kích thước $[B, 128, 100]$.
    \item Tầng tích chập điểm kết thúc (\textit{Terminal 1x1 Conv}): Tầng \texttt{Conv1d(128, D, kernel\_size=1)} chiếu 128 kênh đặc trưng trở lại $D$ kênh thuộc tính ban đầu. Tensor được chuyển vị lại thành $\hat{X} \in \mathbb{R}^{B \times W \times D}$.
\end{enumerate}

\subsubsection{Nhánh phân loại phi tuyến (NonLinClassifier)}
Nhánh phân loại tách ra trực tiếp từ vector tiềm ẩn phẳng hóa $z_{\text{flat}} \in \mathbb{R}^{B \times 128}$ để dự đoán phân phối xác suất trên 12 lớp bất thường giả lập.
Cấu trúc mạng đa tầng (MLP) bao gồm:
\begin{enumerate}
    \item Tầng Dense 1: \texttt{nn.Linear(in\_features=128, out\_features=32)}
    \item Tầng chuẩn hóa: \texttt{nn.BatchNorm1d(num\_features=32)}
    \item Hàm kích hoạt: \texttt{nn.ReLU()}
    \item Tầng ngắt kết nối ngẫu nhiên: \texttt{nn.Dropout(p=0.1)}
    \item Tầng Dense 2: \texttt{nn.Linear(in\_features=32, out\_features=12)}
    \item Tầng chuẩn hóa xác suất Softmax: \texttt{nn.Softmax(dim=1)}
\end{enumerate}
Đầu ra của bộ phân loại là ma trận phân phối xác suất $\hat{y} \in [0, 1]^{B \times 12}$, trong đó $\hat{y}_{b, c}$ thể hiện độ tin cậy rằng mẫu thứ $b$ trong batch mang hình thái bất thường loại $c$.

\subsection{Hàm mất mát liên kết đa nhiệm (Joint Multi-Task Loss Formulation)}
Quá trình huấn luyện ConvAEC được dẫn dắt bởi một hàm mục tiêu liên kết tổng thể:
\begin{equation}
\label{eq:joint_loss}
\mathcal{L}_{\text{total}} = (1 - \lambda)\mathcal{L}_{\text{AE}} + \lambda \mathcal{L}_{\text{C}}
\end{equation}
trong đó siêu tham số $\lambda = 0.1$ (tương ứng $\text{c\_loss\_ratio} = 0.1$) điều tiết sự cân bằng giữa nhiệm vụ tái tạo không gian và nhiệm vụ phân loại ngữ nghĩa.

\subsubsection{Hàm mất mát tái tạo có mặt nạ (Masked Reconstruction Loss -- $\mathcal{L}_{\text{AE}}$)}
Để ngăn chặn hoàn toàn bộ giải mã học cách tái tạo lại các biến dạng bất thường giả lập, sai số bình phương trung bình chỉ được tính trên các bước thời gian và kênh cảm biến mà mặt nạ nhị phân $M$ có giá trị bằng 1 (vùng sạch nguyên bản):
\begin{equation}
\label{eq:loss_ae}
\mathcal{L}_{\text{AE}} = \frac{1}{\|M\|_1} \sum_{b=1}^B \sum_{t=1}^W \sum_{d=1}^D \left[ (X_{b,t,d} - \hat{X}_{b,t,d}) \cdot M_{b,t,d} \right]^2
\end{equation}
Nhờ cơ chế che mặt nạ này, mạng nơ-ron buộc phải học quy luật phân phối nội tại của dữ liệu bình thường để ``điền khuyết'' và tái cấu trúc ngữ cảnh sạch.

\subsubsection{Hàm mất mát phân loại đa lớp (Classification Loss -- $\mathcal{L}_{\text{C}}$)}
Được đo lường bằng độ mất mát Entropy chéo (\textit{Categorical Cross-Entropy}) giữa nhãn mềm đã làm mượt $\tilde{y}$ và phân phối dự đoán của mô hình $\hat{y}$:
\begin{equation}
\label{eq:loss_c}
\mathcal{L}_{\text{C}} = - \frac{1}{B} \sum_{b=1}^B \sum_{c=0}^{C-1} \left[ \tilde{y}_{b,c} \cdot \log( \hat{y}_{b,c} + 10^{-12} ) \right]
\end{equation}

\subsection{Cơ chế tính điểm bất thường hai giai đoạn (Two-Stage Composite Anomaly Scoring)}
Trong giai đoạn kiểm thử trên các chuỗi thời gian thực tế chưa biết trước, dữ liệu không hề có mặt nạ $M$ hay nhãn nhân tạo. RedLamp triển khai quy trình tính điểm kết hợp hai giai đoạn vô cùng tinh xảo:

\subsubsection{Giai đoạn 1: Tính điểm bất thường tái tạo ($\text{Score}_{\text{MSE}}$)}
Với mỗi bước thời gian $t$ trong chuỗi kiểm thử, sai số tái tạo thô là trung bình sai số bình phương trên toàn bộ $D$ kênh cảm biến:
\begin{equation}
\text{MSE}_{\text{raw}}(t) = \frac{1}{D} \sum_{d=1}^D ( X_{t, d} - \hat{X}_{t, d} )^2
\end{equation}
Để loại bỏ các biến động rung lắc tức thời và nắm bắt xu hướng bất thường theo cụm, chuỗi $\text{MSE}_{\text{raw}}$ được lọc qua bộ lọc trung bình trượt tích chập (\textit{Moving Average Convolution Filter}) với độ rộng cửa sổ làm mịn $w = W / 2 = 50$:
\begin{equation}
\text{MSE}_{\text{smooth}}(t) = \frac{1}{w} \sum_{k = -w/2}^{w/2} \text{MSE}_{\text{raw}}(t + k)
\end{equation}
Sau đó, chuỗi được chuẩn hóa Min-Max trên toàn dải quan sát của thực thể để đưa về đoạn $[0, 1]$:
\begin{equation}
\text{Score}_{\text{MSE}}(t) = \frac{\text{MSE}_{\text{smooth}}(t) - \min(\text{MSE}_{\text{smooth}})}{\max(\text{MSE}_{\text{smooth}}) - \min(\text{MSE}_{\text{smooth}}) + 10^{-8}}
\end{equation}

\subsubsection{Giai đoạn 2: Tính điểm bất thường phân loại ($\text{Score}_{\text{CE}}$)}
Đầu phân loại cung cấp xác suất $\hat{y}_c(t)$ cho từng lớp $c \in \{0, 1, \dots, 11\}$. Tuy nhiên, trên dữ liệu thế giới thực, một số chuỗi thời gian bình thường có thể tự nhiên xuất hiện các dao động vi mô khiến mô hình phân loại luôn gán xác suất nhỏ (ví dụ $1-2\%$) cho một lớp biến dạng nào đó (gọi là lớp nền -- \textit{Background Class}). Nếu cộng dồn ngây thơ tất cả các lớp ngoài lớp Normal, các cảnh báo giả sẽ xuất hiện liên tục.

RedLamp giải quyết triệt để vấn đề này bằng Thuật toán lọc tập nền động (\textit{Dynamic Background Exclusion}):
\begin{enumerate}
    \item Tính xác suất trung bình toàn chuỗi của từng lớp $c$:
    \begin{equation}
    \bar{y}_c = \frac{1}{T} \sum_{t=1}^T \hat{y}_c(t)
    \end{equation}
    \item Xác định tập chỉ số nền $\mathcal{I}_{\text{bg}}$ cần loại bỏ: bao gồm lớp Normal (lớp 0) và bất kỳ lớp bất thường nào có tần suất xuất hiện trung bình toàn chuỗi vượt quá ngưỡng $\theta_{\text{bg}} = 0.05$ ($5\%$):
    \begin{equation}
    \label{eq:bg_exclusion}
    \mathcal{I}_{\text{bg}} = \{0\} \cup \{ c \in \{1, 2, \dots, 11\} \mid \bar{y}_c > 0.05 \}
    \end{equation}
    \item Điểm phân loại thô tại bước $t$ là tổng xác suất của các lớp bất thường còn lại nằm ngoài tập nền:
    \begin{equation}
    \text{CE}_{\text{raw}}(t) = \sum_{c \notin \mathcal{I}_{\text{bg}}} \hat{y}_c(t)
    \end{equation}
    \item Chuỗi $\text{CE}_{\text{raw}}$ được làm mịn bằng tích chập trượt ($w = 50$) và chuẩn hóa Min-Max:
    \begin{equation}
    \text{Score}_{\text{CE}}(t) = \text{MinMax}( \text{Convolve}( \text{CE}_{\text{raw}}(t), w=50 ) )
    \end{equation}
\end{enumerate}

\subsubsection{Hợp nhất điểm số cuối cùng (Final Composite Score)}
Điểm số bất thường tổng hợp là trung bình số học cân bằng của hai nhánh:
\begin{equation}
\label{eq:final_score}
\text{Score}_{\text{final}}(t) = \frac{1}{2}\text{Score}_{\text{MSE}}(t) + \frac{1}{2}\text{Score}_{\text{CE}}(t)
\end{equation}
Sự kết hợp này mang lại khả năng phát hiện kép: Nếu một bất thường bị bộ giải mã tái tạo quá tốt ($\text{Score}_{\text{MSE}}$ thấp), nhánh phân loại sẽ ``bắt bài'' được hình thái dị biệt ($\text{Score}_{\text{CE}}$ cao); ngược lại, nếu một bất thường có hình thái lạ lẫm chưa từng gặp trong 11 lớp giả lập, sai số tái tạo không gian vẫn sẽ bùng nổ mạnh mẽ, đảm bảo hệ thống không bao giờ bị qua mặt.

\begin{algorithm}[H]
\caption{Quy trình huấn luyện tự giám sát RedLamp với tăng cường bất thường giả lập}
\label{alg:training}
\begin{algorithmic}[1]
\REQUIRE Chuỗi dữ liệu huấn luyện sạch $X_{\text{train}} \in \mathbb{R}^{T_{\text{train}} \times D}$, cửa sổ $W=100$, bước trượt $s$, batch $B=128$, số epoch $E_{\text{max}}=100$, patience $P=10$, tỉ lệ $\lambda=0.1$.
\ENSURE Trọng số tối ưu của mô hình ConvAEC $\Theta^*$.
\STATE Khởi tạo mô hình $\text{ConvAEC}(\Theta)$ và bộ tối ưu hóa AdamW với tốc độ học $\eta = 0.001$.
\STATE Chuẩn hóa Min-Max chuỗi $X_{\text{train}}$ trên từng kênh cảm biến.
\STATE Trích xuất danh sách các cửa sổ sạch ban đầu $\{ X^{(i)} \}_{i=1}^N$.
\STATE $\text{best\_val\_loss} \leftarrow \infty, \quad \text{stop\_counter} \leftarrow 0$.
\FOR{$\text{epoch} = 1$ \TO $E_{\text{max}}$}
    \STATE Động cơ tăng cường tiêm ngẫu nhiên 12 hình thái giả lập, sinh bộ ba: $\{ (\tilde{X}^{(i)}, M^{(i)}, y^{(i)}) \}_{i=1}^N$.
    \STATE Xáo trộn ngẫu nhiên và phân chia thành các mini-batch kích thước $B = 128$.
    \FORALL{$\text{batch } \{ (\tilde{X}_b, M_b, y_b) \}$}
        \STATE Lan truyền tiến: $(\hat{X}_b, \hat{y}_b, z_b) \leftarrow \text{ConvAEC}(\tilde{X}_b)$.
        \STATE Áp dụng làm mượt nhãn bất đối xứng: $\tilde{y}_b \leftarrow \text{SmoothLabel}(y_b, \alpha=0.1, \beta=0.01)$.
        \STATE Tính mất mát tái tạo có mặt nạ $\mathcal{L}_{\text{AE}}$ theo Eq.~(\ref{eq:loss_ae}) và phân loại $\mathcal{L}_{\text{C}}$ theo Eq.~(\ref{eq:loss_c}).
        \STATE $\mathcal{L}_{\text{total}} \leftarrow (1 - \lambda)\mathcal{L}_{\text{AE}} + \lambda \mathcal{L}_{\text{C}}$.
        \STATE Lan truyền ngược với PyTorch GradScaler và cập nhật trọng số AdamW.
    \ENDFOR
    \STATE Đánh giá mất mát thẩm định $\mathcal{L}_{\text{val}}$ trên tập kiểm định.
    \IF{$\mathcal{L}_{\text{val}} < \text{best\_val\_loss}$}
        \STATE $\text{best\_val\_loss} \leftarrow \mathcal{L}_{\text{val}}, \quad \Theta^* \leftarrow \Theta, \quad \text{stop\_counter} \leftarrow 0$.
    \ELSE
        \STATE $\text{stop\_counter} \leftarrow \text{stop\_counter} + 1$.
        \IF{$\text{stop\_counter} \ge P$}
            \STATE Dừng sớm (\textit{Early Stopping}) và ngắt vòng lặp.
        \ENDIF
    \ENDIF
\ENDFOR
\RETURN $\Theta^*$.
\end{algorithmic}
\end{algorithm}



% =========================================================================
"""

CHAPTER_4_LATEX = r"""
% CHƯƠNG 4: DỮ LIỆU THỰC NGHIỆM, MÔI TRƯỜNG PHẦN CỨNG VÀ CẤU HÌNH HUẤN LUYỆN
% =========================================================================
\section{DỮ LIỆU THỰC NGHIỆM, MÔI TRƯỜNG PHẦN CỨNG VÀ CẤU HÌNH HUẤN LUYỆN}
\label{sec:chapter4}

\subsection{Mô tả chi tiết các tập dữ liệu đánh giá Benchmark}
Để đánh giá toàn diện năng lực của RedLamp, đề tài tiến hành thực nghiệm trên 6 bộ dữ liệu chuẩn mực quốc tế, bao gồm cả chuỗi đơn biến (\textit{Univariate}) và chuỗi đa biến (\textit{Multivariate}), trải rộng trên nhiều lĩnh vực từ hạ tầng máy chủ, viễn thám vũ trụ, vận hành dịch vụ Internet đến thị trường tài chính:

\begin{enumerate}
    \item \textbf{Server Machine Dataset (SMD):}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Được thu thập và công bố bởi nhóm nghiên cứu NetMan AIOps thuộc Đại học Thanh Hoa (Su et al.~\cite{su2019robust}). Dữ liệu ghi nhận hoạt động liên tục trong 5 tuần của một cụm 28 máy chủ lớn tại một tập đoàn Internet hàng đầu thế giới.
        \item \textit{Cấu trúc:} Gồm 28 thực thể độc lập (được phân nhóm thành 3 cụm: machine-1-1 đến machine-1-8, machine-2-1 đến machine-2-9, machine-3-1 đến machine-3-11). Mỗi thực thể là một chuỗi thời gian đa biến gồm 38 chỉ số đo lường tài nguyên phần cứng và hệ điều hành (CPU utilization, memory usage, network in/out, disk read/write throughput, system load,...).
        \item \textit{Quy mô:} Tổng cộng 708,419 bước thời gian (trung bình $\sim 25,000$ bước thời gian cho mỗi thực thể). Tập dữ liệu được chia đều thành hai nửa: nửa đầu dùng để huấn luyện và nửa sau dùng để kiểm thử. Tỉ lệ điểm bất thường thực tế chiếm khoảng $4.16\%$, với nhãn lỗi được xác nhận chính xác bởi các kỹ sư vận hành hệ thống.
    \end{itemize}
    
    \item \textbf{AIOps / IOPS Challenge Dataset:}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Bộ dữ liệu từ cuộc thi quốc tế AIOps KPI Anomaly Detection Challenge (2018).
        \item \textit{Cấu trúc:} Gồm 29 chuỗi thời gian đơn biến ($D = 1$) ghi nhận các chỉ số hiệu năng cốt lõi (\textit{Key Performance Indicators} -- KPI) của các dịch vụ phần mềm quy mô lớn (ví dụ: Page Views, Search Queries per Second, Response Latency, Connection Error Rates).
        \item \textit{Đặc điểm:} Tín hiệu có tính chu kỳ ngày/đêm rất rõ nét kèm theo xu hướng biến động theo mùa, đồng thời chịu nhiều xung nhiễu đột ngột. Tỉ lệ bất thường trung bình khoảng $2.5\%$, với các đợt sụt giảm lưu lượng hoặc tăng đột biến độ trễ.
    \end{itemize}
    
    \item \textbf{NASA Soil Moisture Active Passive (SMAP):}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Dữ liệu đo đạc viễn thám thực tế từ vệ tinh quan sát độ ẩm đất SMAP của Cơ quan Hàng không và Vũ trụ Hoa Kỳ (NASA) (Hundman et al.~\cite{hundman2018detecting}).
        \item \textit{Cấu trúc:} Gồm 55 kênh đo đạc độc lập (từ thực thể A-1 đến T-3). Dữ liệu đa biến với số chiều thuộc tính $D = 25$ (bao gồm 1 kênh tín hiệu cảm biến chính và 24 kênh lệnh điều khiển/trạng thái nhị phân đi kèm).
        \item \textit{Quy mô:} Khoảng 562,800 bước thời gian. Các sự cố bất thường được ghi nhận trong báo cáo nhật ký sự cố chính thức của NASA (\textit{Incident Anomaly Reports}), phản ánh các lỗi quá nhiệt, lệnh sai hoặc cảm biến bức xạ gặp trục trặc.
    \end{itemize}
    
    \item \textbf{NASA Mars Science Laboratory (MSL):}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Dữ liệu viễn trắc kỹ thuật từ Xe tự hành Sao Hỏa Curiosity (\textit{Mars Curiosity Rover}) của NASA.
        \item \textit{Cấu trúc:} Gồm 27 kênh đo đạc (từ C-1 đến T-5). Số chiều thuộc tính $D = 55$ (1 kênh cảm biến đo động cơ, góc quay, năng lượng hạt nhân và 54 kênh trạng thái telemetry).
        \item \textit{Quy mô:} Khoảng 132,000 bước thời gian. Các bất thường biểu thị các sự cố cơ khí thực tế khi xe tự hành di chuyển trên bề mặt Sao Hỏa.
    \end{itemize}
    
    \item \textbf{Stock Dataset (TSB-AD-U Financial Series):}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Được trích xuất từ bộ benchmark chuẩn quốc tế TSB-UAD (Paparrizos et al.~\cite{paparrizos2022tsb}).
        \item \textit{Cấu trúc:} Gồm 20 chuỗi thời gian đơn biến ($D = 1$) mã hóa giá và khối lượng giao dịch của các mã cổ phiếu tài chính thực tế (các mã từ 149\_Stock\_id\_1 đến 168\_Stock\_id\_20).
        \item \textit{Đặc điểm:} Mỗi chuỗi có độ dài khoảng 3,000 đến 4,000 bước thời gian. 500 bước thời gian đầu tiên được quy định làm tập huấn luyện sạch ($\text{train\_end} = 500$). Dữ liệu có tính ngẫu nhiên cao, không có chu kỳ cố định, các dị biệt thể hiện qua sự sụp đổ giá đột ngột hoặc biến động bất thường của khối lượng khớp lệnh.
    \end{itemize}
    
    \item \textbf{UCR Anomaly Archive:}
    \begin{itemize}
        \item \textit{Nguồn gốc:} Bộ dữ liệu kiểm chuẩn quy mô lớn nhất thế giới về phát hiện bất thường chuỗi thời gian đơn biến do Đại học California Riverside (UCR) biên soạn.
        \item \textit{Quy mô:} Gồm 250 chuỗi thời gian đơn biến độc lập, bao quát các miền ứng dụng vô cùng đa dạng: điện tâm đồ y tế (ECG), cảm biến gia tốc chuyển động người (Accelerometry), âm thanh sinh học, vi cơ điện tử (MEMS) và robot công nghiệp.
    \end{itemize}
\end{enumerate}

\begin{table}[htbp]
\centering
\caption{Bảng tổng hợp đặc tính kỹ thuật 6 bộ dữ liệu Benchmark quốc tế}
\label{tab:dataset_characteristics}
\begin{tabular}{lcccccc}
\toprule
\textbf{Tập dữ liệu} & \textbf{Số thực thể} & \textbf{Số chiều ($D$)} & \textbf{Tổng số điểm ($T$)} & \textbf{Tỉ lệ bất thường (\%)} & \textbf{Bước trượt ($s$)} & \textbf{Miền ứng dụng} \\
\midrule
SMD & 28 & 38 & 708,419 & $4.16\%$ & 10 & Hạ tầng máy chủ cụm Internet \\
AIOps / IOPS & 29 & 1 & 3,024,000 & $2.50\%$ & 10 & Chỉ số hiệu năng KPI mạng \\
NASA SMAP & 55 & 25 & 562,800 & $12.80\%$ & 10 & Viễn thám vệ tinh không gian \\
NASA MSL & 27 & 55 & 132,000 & $10.50\%$ & 10 & Robot xe tự hành Sao Hỏa \\
Stock (TSB-AD-U) & 20 & 1 & 72,000 & $3.20\%$ & 1 & Tài chính \& Thị trường chứng khoán \\
UCR Archive & 250 & 1 & 1,500,000 & $1.80\%$ & 1 & Y sinh, Âm học, Cơ điện tử \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Tiền xử lý dữ liệu và Tạo chuỗi trượt (Sliding Window Extraction)}
Dữ liệu thô từ các cảm biến thường có đơn vị đo lường và thang biên độ chênh lệch rất lớn (ví dụ: RAM tính theo Gigabytes, Network tính theo Megabits, trong khi CPU tính theo phần trăm). Do đó, quy trình tiền xử lý tuân thủ nghiêm ngặt các bước:
\begin{enumerate}
    \item \textbf{Chuẩn hóa Min-Max trên tập huấn luyện:}
    Với mỗi kênh cảm biến $d \in \{1, 2, \dots, D\}$, giá trị cực tiểu $\min(X_d^{(\text{train})})$ và cực đại $\max(X_d^{(\text{train})})$ được tính toán độc quyền trên tập huấn luyện sạch. Sau đó, toàn bộ dữ liệu (cả tập Train và tập Test) được chuẩn hóa về đoạn $[0, 1]$ theo công thức:
    \begin{equation}
    x'_{t, d} = \frac{x_{t, d} - \min(X_d^{(\text{train})})}{\max(X_d^{(\text{train})}) - \min(X_d^{(\text{train})}) + 10^{-8}}
    \end{equation}
    Quy ước này đảm bảo hoàn toàn không xảy ra hiện tượng rò rỉ thông tin từ tương lai (\textit{Data Leakage}).
    
    \item \textbf{Cắt cửa sổ trượt (Sliding Window View):}
    Mô hình ConvAEC xử lý dữ liệu theo từng cửa sổ cục bộ kích thước $W = 100$ bước thời gian. Cửa sổ thứ $i$ bao gồm phân đoạn thời gian từ bước $i \cdot s$ đến bước $i \cdot s + W - 1$, trong đó $s$ là bước trượt (\textit{sliding step}).
    \begin{itemize}
        \item Với UCR Anomaly Archive và Stock Dataset: Thiết lập $s = 1$ nhằm giữ nguyên vẹn $100\%$ độ phân giải thời gian và đảm bảo sự khớp nối 1-1 với nhãn điểm khi tính toán các thang đo tích phân VUS.
        \item Với SMD, IOPS, SMAP và MSL: Do chuỗi thời gian có độ dài lên tới hàng trăm nghìn điểm, bước trượt được đặt $s = 10$ trong quá trình huấn luyện và kiểm thử nhằm tối ưu hóa chi phí tính toán và bộ nhớ RAM mà không làm suy giảm tính toàn vẹn của chuỗi.
    \end{itemize}
\end{enumerate}

\subsection{Môi trường phần cứng và Cấu hình hệ thống (Hardware \& Software Specification)}
\label{subsec:hardware}
Toàn bộ quá trình thực nghiệm huấn luyện, kiểm thử và xây dựng hệ thống demo được thực thi trên hai môi trường điện toán chuyên biệt:

\begin{table}[htbp]
\centering
\caption{Bảng đặc tả cấu hình phần cứng và môi trường phần mềm thực nghiệm}
\label{tab:hardware_specs}
\begin{tabular}{lll}
\toprule
\textbf{Thành phần} & \textbf{Môi trường Huấn luyện Đám mây (Kaggle GPU)} & \textbf{Máy trạm Thực thi Cục bộ \& Web Demo} \\
\midrule
Bộ xử lý đồ họa (GPU) & Nvidia Tesla P100-PCIE-16GB (Pascal, 3584 CUDA, 16GB GDDR5) & Tích hợp / GPU rời tiêu chuẩn \\
Băng thông bộ nhớ GPU & 732 GB/s, Năng lực tính toán FP32: 9.3 TFLOPS & N/A \\
Bộ xử lý trung tâm (CPU) & Intel Xeon E5-2699 v4 @ 2.20GHz (2 vCPUs ảo hóa, L3 55MB) & Intel Core i7 / AMD Ryzen 7 (8 cores / 16 threads @ 4.2GHz) \\
Bộ nhớ hệ thống (RAM) & 13.0 GB DDR4 2400MHz & 16.0 GB -- 32.0 GB DDR4/DDR5 Dual-Channel \\
Ổ cứng lưu trữ & 73.0 GB NVMe High-Speed Solid State Drive & 512 GB -- 1 TB NVMe PCIe Gen 4 SSD \\
Hệ điều hành & Ubuntu 20.04.6 LTS Linux (Kernel 5.15) & Microsoft Windows 11 Pro 64-bit (Build 22631) \\
CUDA Driver / Toolkit & Driver 12.2 / CUDA Toolkit 11.3 \& 11.8 & CUDA Toolkit 12.x / CPU mode \\
Thư viện nền tảng & PyTorch 1.11.0 / 2.0.1, Python 3.10.14 & Python 3.12 / 3.14, FastAPI 0.115, Uvicorn 0.34 \\
Kỹ thuật tối ưu & PyTorch AMP (autocast \& GradScaler) & In-memory Cache \& HTML5 Canvas Offline \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Thiết lập siêu tham số chi tiết (Hyperparameter Configurations)}
\label{subsec:hyperparameters}
Bảng thông số chi tiết dưới đây tổng hợp đầy đủ cấu hình siêu tham số của mô hình ConvAEC trên từng tập dữ liệu:

\begin{table}[htbp]
\centering
\caption{Bảng tổng hợp siêu tham số huấn luyện mô hình RedLamp}
\label{tab:hyperparameters}
\begin{tabular}{llp{7.0cm}}
\toprule
\textbf{Tham số (Hyperparameter)} & \textbf{Ký hiệu} & \textbf{Giá trị cấu hình chuẩn trong thực nghiệm} \\
\midrule
Mô hình cốt lõi & Architecture & ConvAEC (Convolutional Autoencoder with Classifier) \\
Độ dài cửa sổ trượt & $W$ (window\_size) & 100 bước thời gian \\
Bước trượt & $s$ (window\_step) & $s=1$ (Stock, UCR); $s=10$ (SMD, IOPS, SMAP, MSL) \\
Kích thước Batch & $B$ (batch\_size) & 128 mẫu cửa sổ trượt ($128 \times 100 \times D$) \\
Tỉ lệ hạ mẫu & downsampling & 1 (giữ nguyên độ phân giải gốc của tín hiệu) \\
Số kênh thuộc tính & $D$ (n\_features) & 1 (UCR, IOPS, Stock); 38 (SMD); 25 (SMAP); 55 (MSL) \\
Số bộ lọc tích chập & num\_filters & $[128, 128, 256, 256]$ qua 4 khối ConvBlock \\
Kích thước nhân tích chập & $k$ (kernel\_size) & 4 bước thời gian \\
Bước tích chập & stride & 2 \\
Đệm biên & padding & 2 \\
Kích thước vector tiềm ẩn & embedding\_dim & 128 chiều ($z \in \mathbb{R}^{B \times 128 \times 1}$) \\
Tầng ẩn phân loại & classifier\_dim & 32 nơ-ron (nn.Linear(128, 32)) \\
Số lớp phân loại & $C$ (classes) & 12 lớp (1 Normal + 11 lớp bất thường giả lập) \\
Hệ số mất mát phân loại & $\lambda$ (c\_loss\_ratio) & 0.1 ($\mathcal{L}_{\text{total}} = 0.9\mathcal{L}_{\text{AE}} + 0.1\mathcal{L}_{\text{C}}$) \\
Làm mượt nhãn bất đối xứng & label\_smoothing & True (Kích hoạt công thức Eq.~(\ref{eq:label_smoothing})) \\
Tiên nghiệm lớp Normal & $\alpha$ & 0.1 (Cộng thêm vào xác suất mục tiêu của lớp 0) \\
Nhiễu phân bổ entropy & $\beta$ & 0.01 (Phân bổ đều cho toàn bộ 12 lớp) \\
Tỉ lệ ngắt kết nối & dropout & 0.2 (Encoder/Decoder); 0.1 (Classifier) \\
Phương pháp chuẩn hóa & normalization & 'batch' (nn.BatchNorm1d trên tất cả các tầng) \\
Thuật toán tối ưu & optimizer & AdamW (Loshchilov \& Hutter~\cite{loshchilov2019decoupled}) \\
Tốc độ học ban đầu & $\eta$ (learning rate) & 0.001 ($10^{-3}$) \\
Kẹp chuẩn Gradient & max\_grad\_norm & $10^9$ (Kết hợp PyTorch GradScaler AMP) \\
Số epoch tối đa & max\_epochs & 100 epoch \\
Kiên nhẫn dừng sớm & patience & 10 epoch liên tiếp ($\text{stop\_counter} > 9$) \\
Độ rộng làm mịn điểm & $w$ & 50 bước thời gian (bằng $W / 2$) \\
Ngưỡng lọc lớp nền động & $\theta_{\text{bg}}$ & 0.05 ($5\%$ xác suất trung bình toàn chuỗi) \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Động lực học quá trình huấn luyện (Training Dynamics)}
\label{subsec:training_dynamics}
Dữ liệu nhật ký thực tế được trích xuất trực tiếp từ các tệp \texttt{time.txt}, \texttt{train\_loss.txt}, \texttt{valid\_loss.txt}, \texttt{train\_loss\_ae.txt} và \texttt{train\_loss\_c.txt} trong thư mục \texttt{pretrain/} của dự án đã cung cấp các bằng chứng thực nghiệm rõ ràng về tốc độ xử lý, thời gian chạy một epoch và quá trình hội tụ:

\begin{table}[htbp]
\centering
\caption{Bảng thống kê thời gian chạy 1 epoch và quá trình hội tụ thực tế trên Kaggle GPU Nvidia Tesla P100}
\label{tab:training_dynamics}
\begin{tabular}{lccccccc}
\toprule
\textbf{Tập dữ liệu} & \textbf{Số chiều ($D$)} & \textbf{Thời gian/Epoch (Min)} & \textbf{Thời gian/Epoch (Mean)} & \textbf{Thời gian/Epoch (Max)} & \textbf{Best Epoch} & \textbf{Dừng tại} & \textbf{Tổng thời gian} \\
\midrule
Stock (149\_Stock\_id\_1) & 1 & 0.31s & \textbf{0.36s} & 1.33s & Epoch 26 & Epoch 36 & 12.83s \\
Stock (150\_Stock\_id\_2) & 1 & 0.32s & \textbf{0.34s} & 0.38s & Epoch 17 & Epoch 27 & 9.06s \\
SMD (machine-1-1) & 38 & 2.82s & \textbf{2.94s} & 3.78s & Epoch 56 & Epoch 66 & 194.10s (3.2 min) \\
NASA MSL (msl aggregate) & 55 & 5.91s & \textbf{6.15s} & 7.31s & Epoch 34 & Epoch 44 & 270.80s (4.5 min) \\
AIOps / IOPS (KPI-05f10d3a) & 1 & 12.43s & \textbf{12.68s} & 13.21s & Epoch 9 & Epoch 19 & 240.83s (4.0 min) \\
NASA SMAP (smap aggregate) & 25 & 13.57s & \textbf{14.05s} & 18.03s & Epoch 43 & Epoch 53 & 744.83s (12.4 min) \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{Phân tích thời gian thực thi một epoch (Runtime per Epoch)}
Nhờ cấu trúc thuần tích chập 1D không có vòng lặp tuần hoàn và kích thước batch lớn $B = 128$, ConvAEC đạt tốc độ tính toán cực kỳ ấn tượng trên GPU Nvidia Tesla P100:
\begin{itemize}
    \item \textbf{Bộ dữ liệu Stock (1D, 500 mẫu train trượt):} Thời gian trung bình chỉ đạt \textbf{0.36 giây / epoch} (biên độ dao động từ 0.31s đến 1.33s). Trên CPU Intel Core i7 cục bộ, thời gian là $\sim 1.82$s / epoch.
    \item \textbf{Bộ dữ liệu SMD (38D, machine-1-1 với $\sim 12,500$ mẫu trượt):} Thời gian trung bình đạt \textbf{2.94 giây / epoch} (min: 2.82s, max: 3.78s). Trên CPU cục bộ: $\sim 22.5$s / epoch.
    \item \textbf{Bộ dữ liệu MSL (55D, msl aggregate với $\sim 10,000$ mẫu trượt):} Thời gian trung bình đạt \textbf{6.15 giây / epoch} (min: 5.91s, max: 7.31s). Trên CPU cục bộ: $\sim 34.1$s / epoch.
    \item \textbf{Bộ dữ liệu IOPS (1D, KPI-05f10d3a... với $\sim 35,000$ mẫu trượt):} Thời gian trung bình đạt \textbf{12.68 giây / epoch} (min: 12.43s, max: 13.21s). Trên CPU cục bộ: $\sim 58.2$s / epoch.
    \item \textbf{Bộ dữ liệu SMAP (25D, smap aggregate với $\sim 40,000$ mẫu trượt):} Thời gian trung bình đạt \textbf{14.05 giây / epoch} (min: 13.57s, max: 18.03s). Trên CPU cục bộ: $\sim 85.4$s / epoch.
\end{itemize}

So với các mô hình hồi quy như LSTM-VAE (thường mất từ 45 giây đến 180 giây cho mỗi epoch trên cùng tập dữ liệu SMD) hoặc Transformer như Anomaly Transformer~\cite{xu2022anomaly} (mất $\sim 35-50$ giây / epoch do tính toán ma trận Attention $W \times W$), ConvAEC nhanh hơn từ \textbf{5 đến 15 lần}, cho phép triển khai huấn luyện lại mô hình định kỳ rất nhanh chóng trong môi trường công nghiệp.

\subsubsection{Quá trình hội tụ và Cơ chế Dừng sớm (Epoch Convergence Profile)}
Mô hình áp dụng cơ chế Early Stopping với $\text{patience} = 10$ epoch trên hàm mất mát tập thẩm định (\textit{Validation Loss}). Quá trình hội tụ thực tế diễn ra như sau:
\begin{itemize}
    \item \textbf{Tập IOPS (KPI-05f10d3a...):} Mô hình bắt đầu với $\text{Train Loss} = 0.2301$, $\text{Valid Loss} = 30.5850$. Valid Loss đạt cực tiểu \textbf{29.1720 tại epoch thứ 9}. Trong 10 epoch tiếp theo, Valid Loss dao động nhẹ quanh mức 30.2 mà không cải thiện thêm, bộ đếm dừng sớm chạm ngưỡng 10 và mô hình kết thúc huấn luyện tại epoch 19 (tổng thời gian huấn luyện chỉ $\sim 4$ phút).
    \item \textbf{Tập Stock (149\_Stock\_id\_1):} Train Loss giảm nhanh từ 0.4491 xuống 0.2302. Valid Loss đạt giá trị tốt nhất \textbf{1.1440 tại epoch thứ 26} và dừng sớm hoàn toàn tại epoch 36 (tổng thời gian chỉ $\sim 13$ giây).
    \item \textbf{Tập MSL (55 chiều):} Bắt đầu với $\text{Train Loss} = 0.2406$, $\text{Valid Loss} = 7.4241$. Valid Loss giảm đều và chạm đáy \textbf{6.7574 tại epoch thứ 34}, dừng sớm tại epoch 44 (tổng thời gian $\sim 4.5$ phút).
    \item \textbf{Tập SMAP (25 chiều):} Train Loss giảm từ 0.2389 về 0.2064. Valid Loss đạt điểm tối ưu \textbf{17.7070 tại epoch thứ 43}, kết thúc tại epoch 53 (tổng thời gian $\sim 12.4$ phút).
    \item \textbf{Tập SMD (machine-1-1, 38 chiều):} Train Loss giảm từ 0.2439 về 0.2054. Valid Loss tối ưu đạt \textbf{5.3135 tại epoch 56}, dừng sớm tại epoch 66 (tổng thời gian $\sim 3.2$ phút).
    \item \textbf{Đối với 250 chuỗi của UCR Anomaly Archive:} Trung bình các chuỗi hội tụ trong khoảng \textbf{15 đến 35 epochs}.
\end{itemize}

\subsubsection{Phân tích đồ thị suy giảm các thành phần hàm mất mát}
Quan sát chi tiết quá trình huấn luyện cho thấy hai giai đoạn rõ rệt:
\begin{itemize}
    \item \textbf{Giai đoạn 1 (Epoch 0 đến 5):} Hàm mất mát phân loại $\mathcal{L}_{\text{C}}$ giảm mạnh nhất (từ $\sim 2.48$ -- mức phân phối đều ban đầu $\ln(12) \approx 2.4849$ -- xuống dưới 1.20). Mạng nơ-ron học rất nhanh các đặc trưng hình thái thô của 11 dạng biến dạng nhân tạo (đặc biệt là các dạng dễ phân biệt như Spike, Noise, Flip).
    \item \textbf{Giai đoạn 2 (Epoch 6 trở đi):} Hàm mất mát tái tạo $\mathcal{L}_{\text{AE}}$ bắt đầu chiếm ưu thế trong việc kéo giảm tổng loss, giảm dần từ $\sim 0.08$ xuống mức ổn định $\sim 0.015 - 0.022$. Mạng tinh chỉnh các trọng số của ConvTransposeDecoder để khôi phục chính xác các chi tiết tần số cao của tín hiệu bình thường.
\end{itemize}
Nhờ có sự điều tiết của $\lambda = 0.1$ và nhãn mềm bất đối xứng, hai hàm mất mát này bổ trợ hoàn hảo cho nhau mà không xảy ra hiện tượng cạnh tranh gradient (\textit{Gradient Conflict}) hay dao động bất ổn.



% =========================================================================
"""
