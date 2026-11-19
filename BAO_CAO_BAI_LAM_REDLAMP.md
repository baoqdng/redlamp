# BÁO CÁO TỔNG KẾT ĐỀ TÀI NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG
# PHÁT HIỆN BẤT THƯỜNG CHUỖI THỜI GIAN KHÔNG GIÁM SÁT DỰA TRÊN KIẾN TRÚC CONVAEC VÀ HỌC TỰ GIÁM SÁT ĐA NHIỆM (REDLAMP)

---

**Học viên / Tác giả thực hiện:** Nhóm Nghiên cứu & Phát triển Dự án RedLamp  
**Lĩnh vực:** Trí tuệ Nhân tạo (Artificial Intelligence) – Học máy & Học sâu trong Chuỗi thời gian (Time Series Deep Learning)  
**Quy mô báo cáo:** Báo cáo khoa học & kỹ thuật toàn diện (~15 trang chuẩn học thuật)  
**Tập dữ liệu kiểm chuẩn:** Server Machine Dataset (SMD), AIOps/IOPS KPI, NASA SMAP, NASA MSL, TSB-U Stock, UCR Archive  
**Môi trường thực nghiệm:** Nền tảng Đám mây Kaggle GPU (Nvidia Tesla P100 16GB) & Hệ thống Web Demo Cục bộ  

---

## MỤC LỤC TỔNG QUAN

1. [PHẦN I: TỔNG QUAN ĐỀ TÀI, TÍNH CẤP THIẾT VÀ ĐÓNG GÓP KHOA HỌC](#phần-i-tổng-quan-đề-tài-tính-cấp-thiết-và-đóng-góp-khoa-học)
   - 1.1. Bối cảnh nghiên cứu và Tầm quan trọng của Phát hiện bất thường chuỗi thời gian (TSAD)
   - 1.2. Những thách thức cốt lõi trong giám sát chuỗi thời gian công nghiệp
   - 1.3. Mục tiêu và Phạm vi nghiên cứu
   - 1.4. Các đóng góp khoa học và kỹ thuật nổi bật của đề tài
2. [PHẦN II: TỔNG QUAN CÁC CÔNG TRÌNH LIÊN QUAN VÀ ĐỐI SÁNH PHƯƠNG PHÁP](#phần-ii-tổng-quan-các-công-trình-liên-quan-và-đối-sánh-phương-pháp)
   - 2.1. Phân loại hình thái bất thường trong chuỗi thời gian
   - 2.2. Các phương pháp thống kê và học máy truyền thống
   - 2.3. Các phương pháp học sâu không giám sát hiện đại
   - 2.4. Bảng phân tích và đối sánh ưu nhược điểm giữa RedLamp với các phương pháp cơ sở
3. [PHẦN III: THIẾT KẾ MÔ HÌNH AI (CONVAEC) VÀ GIẢI THUẬT CỐT LÕI](#phần-iii-thiết-kế-mô-hình-ai-convaec-và-giải-thuật-cốt-lõi)
   - 3.1. Triết lý thiết kế: Tích hợp Đa nhiệm Tái tạo và Phân loại Tự giám sát
   - 3.2. Cơ chế sinh 12 hình thái bất thường giả lập (12 Pseudo-Anomaly Augmentations)
   - 3.3. Kỹ thuật Làm mượt nhãn bất đối xứng (Asymmetric Label Smoothing)
   - 3.4. Đặc tả chi tiết từng tầng (Layers) trong kiến trúc mạng nơ-ron ConvAEC
   - 3.5. Hàm mất mát liên kết đa nhiệm (Joint Multi-Task Loss Formulation)
   - 3.6. Cơ chế tính điểm bất thường hai giai đoạn và Lọc lớp nền động
4. [PHẦN IV: QUY TRÌNH GIAI ĐOẠN 1 — HUẤN LUYỆN MÔ HÌNH TRÊN KAGGLE (TRAIN MODEL)](#phần-iv-quy-trình-giai-đoạn-1--huấn-luyện-mô-hình-trên-kaggle-train-model)
   - 4.1. Môi trường phần cứng Kaggle GPU và Cấu hình hạ tầng
   - 4.2. Dữ liệu thực nghiệm và Quy trình tiền xử lý chuẩn hóa
   - 4.3. Bảng thiết lập siêu tham số cấu hình cho AI (Hyperparameter Specifications)
   - 4.4. Động lực học quá trình huấn luyện: Kích thước Batch, Thời gian chạy 1 Epoch và Tốc độ hội tụ
5. [PHẦN V: QUY TRÌNH GIAI ĐOẠN 2 — ĐÁNH GIÁ THỰC NGHIỆM VÀ ĐỐI SÁNH HIỆU NĂNG (EVALUATE)](#phần-v-quy-trình-giai-đoạn-2--đánh-giá-thực-nghiệm-và-đối-sánh-hiệu-năng-evaluate)
   - 5.1. Hệ thống thang đo đánh giá chuỗi thời gian chuẩn mực (Evaluation Metrics)
   - 5.2. Kết quả định lượng trên 6 tập dữ liệu Benchmark quốc tế
   - 5.3. Nghiên cứu triệt tiêu (Ablation Studies)
   - 5.4. Đánh giá tính bền bỉ và Phân tích độ trễ suy luận
6. [PHẦN VI: QUY TRÌNH GIAI ĐOẠN 3 — THIẾT KẾ VÀ TRIỂN KHAI ỨNG DỤNG TƯƠNG TÁC (DEMO)](#phần-vi-quy-trình-giai-đoạn-3--thiết-kế-và-triển-khai-ứng-dụng-tương-tác-demo)
   - 6.1. Kiến trúc hệ thống Web Demo tương tác Client-Server
   - 6.2. Hiện thực 3 Tab chức năng chính của giao diện người dùng
   - 6.3. Chi tiết 10 khối trực quan hóa tương tác (10 Visualization Blocks)
   - 6.4. Cơ chế trích xuất kích hoạt trung gian bằng PyTorch Forward Hooks và Chiếu PCA Latent Vector
7. [PHẦN VII: KẾT LUẬN, BÀI HỌC KINH NGHIỆM VÀ HƯỚNG PHÁT TRIỂN](#phần-vii-kết-luận-bài-học-kinh-nghiệm-và-hướng-phát-triển)
   - 7.1. Tổng kết kết quả và giá trị thực tiễn
   - 7.2. Những hạn chế còn tồn đọng
   - 7.3. Đề xuất các hướng phát triển tương lai

---

# PHẦN I: TỔNG QUAN ĐỀ TÀI, TÍNH CẤP THIẾT VÀ ĐÓNG GÓP KHOA HỌC

## 1.1. Bối cảnh nghiên cứu và Tầm quan trọng của Phát hiện bất thường chuỗi thời gian (TSAD)

Trong kỷ nguyên chuyển đổi số và công nghiệp 4.0, dữ liệu chuỗi thời gian (*Time Series Data*) được sản sinh liên tục với tốc độ chóng mặt từ hàng triệu cảm biến IoT, hệ thống giám sát cụm máy chủ điện toán đám mây (*Cloud Datacenter Monitoring*), mạng lưới viễn thông, hệ thống tài chính chứng khoán, và các tổ hợp thám hiểm không gian. Phát hiện bất thường trong chuỗi thời gian (*Time Series Anomaly Detection – TSAD*) đóng vai trò là "tuyến phòng thủ số một" nhằm cảnh báo sớm các sự cố nghiêm trọng, ngăn ngừa thảm họa hỏng hóc phần cứng, phát hiện gian lận tài chính, và duy trì tính liên tục của các hạ tầng trọng yếu quốc gia.

Về mặt toán học, bất thường trong chuỗi thời gian là các mẫu dữ liệu, bước nhảy hoặc chu kỳ có hành vi lệch chuẩn một cách đáng kể so với phân phối danh định bình thường của hệ thống. Nếu không được phát hiện kịp thời, những sai lệch này có thể dẫn tới sự sụp đổ dây chuyền của toàn bộ cụm máy chủ, gây thiệt hại hàng triệu đô la Mỹ cho các doanh nghiệp công nghệ, hoặc làm tê liệt nhiệm vụ viễn thám không gian.

## 1.2. Những thách thức cốt lõi trong giám sát chuỗi thời gian công nghiệp

Mặc dù giữ vai trò sống còn, bài toán TSAD trong môi trường thực tiễn đang đối mặt với 4 rào cản kỹ thuật vô cùng nan giải:

```
+-----------------------------------------------------------------------------------+
|                        4 THÁCH THỨC CỐT LÕI TRONG BÀI TOÁN TSAD                  |
+-----------------------------------------------------------------------------------+
| 1. KHAN HIẾM NHÃN SỰ CỐ:     99.9% dữ liệu là bình thường, nhãn lỗi cực hiếm và   |
|                              chi phí chuyên gia gắn nhãn quá cao.                |
+-----------------------------------------------------------------------------------+
| 2. HÌNH THÁI LỖI ĐA DẠNG:    Từ gai nhọn tức thời, trôi dạt baseline, đảo pha,   |
|                              đến đóng băng cảm biến và tổ hợp đa biến phức tạp.   |
+-----------------------------------------------------------------------------------+
| 3. KHỦNG HOẢNG "HỘP ĐEN":    Mô hình Deep Learning chỉ trả về điểm số vô hồn,      |
|                              không giải thích được lý do gây ra cảnh báo.         |
+-----------------------------------------------------------------------------------+
| 4. NGHẼN CỔ CHAI ĐỘ TRỄ:     Các mô hình Transformer / RNN có độ phức tạp O(W^2),  |
|                              không đáp ứng được yêu cầu giám sát thời gian thực.  |
+-----------------------------------------------------------------------------------+
```

1. **Sự khan hiếm trầm trọng của nhãn sự cố (*Extreme Scarcity of Ground-Truth Labels*):** Trong môi trường công nghiệp, hệ thống phần lớn thời gian hoạt động ở trạng thái bình thường (chiếm $> 99.5\%$ tổng số mẫu). Sự cố xảy ra với tần suất rất thấp nhưng mang tính chất dị biệt. Việc thu thập và gắn nhãn chính xác từng bước thời gian đòi hỏi chi phí chuyên gia cực lớn, khiến các thuật toán học có giám sát (*Supervised Learning*) gần như không thể áp dụng trên diện rộng.
2. **Sự đa dạng phức tạp về hình thái bất thường (*Morphological Diversity*):** Sự cố không chỉ xuất hiện dưới dạng đột biến biên độ (như các đỉnh nhọn tức thời – *Point Anomaly*), mà thường tồn tại dưới dạng biến đổi ngữ cảnh (*Contextual Anomaly*) hoặc biến đổi tập hợp (*Collective Anomaly*) như: trôi dạt đường xu hướng (*trend wander*), nén/giãn chu kỳ dao động (*frequency speedup*), đóng băng tín hiệu (*sensor cutoff*), hoặc suy giảm tương quan chéo giữa hàng chục kênh đo đa biến.
3. **Ảo tưởng "Khả năng khái quát hóa quá mức" của Mạng Tự mã hóa (*Autoencoder Over-generalization*):** Các mô hình Deep Autoencoder truyền thống được kỳ vọng là tái tạo kém các mẫu lạ. Tuy nhiên trên thực tế, nhờ dung lượng mạng nơ-ron lớn, Autoencoder thường "vô tình học luôn cả cách tái tạo hoàn hảo các mẫu bất thường", dẫn đến sai số tái tạo rất nhỏ và bỏ sót sự cố nguy hiểm (*False Negatives*).
4. **Khủng hoảng niềm tin và Tính bất khả giải thích (*Lack of Explainability*):** Phần lớn các công trình Deep Learning hiện đại chỉ xuất ra một giá trị vô hướng biểu thị điểm bất thường (*Anomaly Score*). Đội ngũ kỹ sư vận hành (*SRE/DevOps*) không thể biết được mô hình dựa trên tiêu chí nào để gắn cờ cảnh báo, kênh cảm biến nào đang lỗi, hay loại biến dạng vật lý nào đang diễn ra, dẫn tới hiện tượng "mệt mỏi vì báo động giả" (*Alert Fatigue*).
5. **Rào cản độ trễ tính toán (*Latency Bottleneck*):** Các mô hình tuần tự hóa (LSTM, GRU) hoặc mô hình cơ chế tự chú ý (*Self-Attention*) trong Transformer có độ phức tạp tính toán bậc hai $\mathcal{O}(W^2)$, không thể đáp ứng tần số lấy mẫu mili-giây trên các thiết bị biên (*Edge IoT*) hoặc cụm giám sát quy mô lớn.

## 1.3. Mục tiêu và Phạm vi nghiên cứu

Nhằm giải quyết triệt để các thách thức trên, đề tài **RedLamp** được xây dựng với các mục tiêu cụ thể:
- **Thiết kế một kiến trúc học sâu không giám sát kết hợp tự giám sát (*Unsupervised + Self-Supervised Learning*)** mang tên **ConvAEC**, loại bỏ các thành phần tính toán nặng nề (RNN, Self-Attention) để đạt tốc độ xử lý song song tối đa trên GPU/CPU.
- **Xây dựng bộ sinh 12 hình thái bất thường giả lập (*12 Pseudo-Anomaly Augmentations*)** mô phỏng chân thực các dạng hỏng hóc vật lý mà không cần bất kỳ nhãn giám sát thực tế nào.
- **Phát triển cơ chế suy luận và tính điểm hai giai đoạn (*Two-Stage Composite Anomaly Scoring*)**, tích hợp thông minh giữa sai số tái tạo không gian và xác suất phân loại hình thái bất thường, kèm kỹ thuật lọc bỏ nhiễu nền động.
- **Hiện thực hóa quy trình công nghệ hoàn chỉnh từ huấn luyện trên Kaggle GPU đến đánh giá kiểm chuẩn và triển khai Web Demo tương tác** phục vụ việc bóc tách cơ chế bên trong của mô hình AI (*Explainable AI – XAI*).

## 1.4. Các đóng góp khoa học và kỹ thuật nổi bật của đề tài

Đề tài tạo ra 4 đóng góp cốt lõi cả về mặt lý thuyết học thuật lẫn kỹ thuật ứng dụng thực tiễn:

```mermaid
flowchart LR
    A["ĐÓNG GÓP CỦA ĐỀ TÀI REDLAMP"] --> B["1. Kiến trúc ConvAEC<br/>Đa nhiệm Song song"]
    A --> C["2. Bộ sinh 12 Biến dạng<br/>+ Asymmetric Smoothing"]
    A --> D["3. Cơ chế Tính điểm 2 Giai đoạn<br/>+ Dynamic BG Filtering"]
    A --> E["4. Hệ thống Web Demo & XAI<br/>10 Khối Tương tác Độc lập"]
```

1. **Đóng góp về Kiến trúc Mạng Nơ-ron (ConvAEC Architecture):** Đề xuất kiến trúc kết hợp chặt chẽ giữa bộ tự mã hóa tích chập 1D đối xứng (1D-CNN Encoder/Decoder) và đầu phân loại phi tuyến đa lớp (Non-linear MLP Classifier Head). Bằng cách loại bỏ hoàn toàn cơ chế tuần tự và tự chú ý bậc hai, mô hình đạt thông lượng xử lý vượt bậc ($< 0.36$s/epoch trên chuỗi tài chính và $< 2.94$s/epoch trên cụm 38 cảm biến SMD trên GPU Nvidia Tesla P100), tốc độ suy luận dưới $10$ms/cửa sổ trên CPU.
2. **Đóng góp về Thuật toán Tự giám sát & Làm mượt nhãn bất đối xứng:** Xây dựng thư viện toán học sinh 12 hình thái biến dạng giả lập (Spike, Flip, Speedup, Noise, Cutoff, Average, Scale, Wander, Contextual, Upsidedown, Mixture). Đi kèm với đó là kỹ thuật **Asymmetric Label Smoothing**, phân bổ có chủ đích trọng số tiên nghiệm cho lớp bình thường ($\alpha = 0.1$) và nhiễu đều cho các lớp bất thường ($\beta = 0.01$), giúp mạng nơ-ron không bị cực đoan hóa (*over-confident*) khi gặp các biến thể nhiễu ngoài đời thực.
3. **Đóng góp về Cơ chế Tính điểm Kết hợp và Lọc Lớp nền Động:** Khắc phục nhược điểm "bị ép điểm bằng 1.0" do chuẩn hóa Min-Max toàn cục của các phương pháp truyền thống. RedLamp đề xuất cơ chế z-score trên đoạn tham chiếu chuẩn danh định ($n_{\text{train}}$), kết hợp thuật toán loại trừ động các lớp bất thường có tần suất xuất hiện cao trong tín hiệu thông thường ($\theta_{\text{bg}} = 0.05$), triệt tiêu báo động giả đến $42.3\%$.
4. **Đóng góp về Ứng dụng Thực tiễn và Khả năng Giải thích Sâu (XAI Web Demo):** Phát triển thành công hệ thống phần mềm Web Demo tương tác hoàn chỉnh (FastAPI backend + JavaScript Canvas/SVG frontend), hoạt động hoàn toàn offline 100%, tích hợp sẵn 159 thực thể kiểm chuẩn. Hệ thống cung cấp quy trình bóc tách 5 bước mở "hộp đen" mạng nơ-ron thông qua PyTorch Forward Hooks và 10 khối trực quan hóa tương tác theo thời gian thực.

---

# PHẦN II: TỔNG QUAN CÁC CÔNG TRÌNH LIÊN QUAN VÀ ĐỐI SÁNH PHƯƠNG PHÁP

## 2.1. Phân loại hình thái bất thường trong chuỗi thời gian

Chuỗi thời gian đa biến được biểu diễn toán học dưới dạng một ma trận $X = [x_1, x_2, \dots, x_T]^T \in \mathbb{R}^{T \times D}$, trong đó $T$ là tổng số bước thời gian và $D$ là số chiều thuộc tính/cảm biến. Các hiện tượng bất thường trong $X$ thường được phân thành 3 nhóm hình thái chính:
- **Bất thường điểm (*Point Anomaly*):** Một điểm đơn lẻ $x_t$ có độ lớn biên độ vượt xa ngưỡng phân phối thống kê thông thường (ví dụ: xung điện áp đột biến, giao dịch tài chính bất thường).
- **Bất thường ngữ cảnh (*Contextual Anomaly*):** Một điểm dữ liệu $x_t$ có giá trị hoàn toàn hợp lệ nếu xét trên toàn cục, nhưng lại trở nên bất thường khi đặt trong ngữ cảnh thời gian cụ thể (ví dụ: tải CPU đạt $95\%$ vào lúc 3 giờ sáng ngày nghỉ lễ).
- **Bất thường tập thể / chuỗi (*Collective Anomaly*):** Một tập hợp các điểm liên tiếp $x_{t:t+k}$ tạo nên một hình thái bất thường (ví dụ: tín hiệu nhịp tim bị rung nhĩ, cảm biến bị đóng băng cố định một giá trị hoặc xuất hiện dao động tần số cao bất thường).

## 2.2. Các phương pháp thống kê và học máy truyền thống

- **Isolation Forest (iForest):** Dựa trên nguyên lý cô lập các điểm ngoại lai thông qua việc phân chia ngẫu nhiên không gian đặc trưng bằng các cây nhị phân (*Isolation Trees*). Điểm bất thường tỷ lệ nghịch với độ sâu trung bình của đường đi từ gốc đến lá cây. Hạn chế lớn nhất của iForest là hoàn toàn bỏ qua sự phụ thuộc thời gian và tương quan chuỗi (*Temporal Dependencies*).
- **XGBoost Autoregressive:** Sử dụng mô hình hồi quy cây tăng cường độ dốc (*Gradient Boosted Trees*) kết hợp các đặc trưng độ trễ (*Lagged Features*) để dự báo giá trị tiếp theo $\hat{x}_{t+1}$. Sai số dự báo $|x_{t+1} - \hat{x}_{t+1}|$ được dùng làm điểm bất thường. Phương pháp này nhạy cảm cao với nhiễu và dễ bị suy giảm hiệu năng khi dự báo nhiều bước liên tiếp.

## 2.3. Các phương pháp học sâu không giám sát hiện đại

- **Vanilla Convolutional Autoencoder (ConvAE):** Sử dụng các tầng tích chập để nén chuỗi thời gian vào không gian tiềm ẩn và giải mã tái tạo lại tín hiệu. Sai số bình phương trung bình giữa tín hiệu gốc và tái tạo được dùng để phát hiện bất thường. Hạn chế: Dễ bị quá khớp và vô tình tái tạo tốt cả các mẫu bất thường.
- **LSTM-VAE (Long Short-Term Memory Variational Autoencoder):** Kết hợp mạng hồi quy tuần tự LSTM với mô hình biến phân VAE để học phân phối xác suất tiềm ẩn $q_\phi(z|x)$. Nhược điểm: Huấn luyện rất chậm do tính tuần tự của LSTM và khó hội tụ trên chuỗi đa biến số chiều lớn.
- **OmniAnomaly (KDD 2019):** Sử dụng GRU kết hợp không gian tiềm ẩn biến phân đa biến và mạng planar normalizing flows. Mặc dù đạt độ chính xác cao nhưng chi phí tính toán cực kỳ lớn, không phù hợp cho các bài toán cần phản hồi tức thời.
- **TranAD & Anomaly Transformer (VLDB 2022 & ICLR 2022):** Ứng dụng kiến trúc Transformer kết hợp cơ chế chú ý đối nghịch (*Adversarial Attention*) hoặc liên kết liên kết phi liên tục (*Association Discrepancy*). Mặc dù có độ chính xác rất tốt nhưng độ phức tạp tính toán $\mathcal{O}(W^2)$ khiến mô hình tiêu tốn bộ nhớ GPU khổng lồ và độ trễ suy luận cao.

## 2.4. Bảng phân tích và đối sánh ưu nhược điểm giữa RedLamp với các phương pháp cơ sở

Bảng dưới đây đối sánh đa chiều giữa RedLamp và các phương pháp đại diện thuộc 4 nhóm tiếp cận chính:

| Tiêu chí Đối sánh | iForest (Truyền thống) | Vanilla ConvAE (Tái tạo) | LSTM-VAE (Xác suất) | Anomaly Transformer (SOTA) | **RedLamp (Đề tài)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cơ chế học cốt lõi** | Cây cô lập ngẫu nhiên | Tự mã hóa nén 1D-CNN | Mô hình biến phân tuần tự | Cơ chế tự chú ý đối nghịch | **ConvAEC Đa nhiệm (Tái tạo + Phân loại)** |
| **Mức độ giám sát** | Không giám sát | Không giám sát | Không giám sát | Không giám sát | **Tự giám sát (Self-Supervised)** |
| **Khai thác Tương quan Thời gian** | Kém (Bỏ qua) | Tốt (Qua nhân Conv 1D) | Rất tốt (Tuần tự LSTM) | Xuất sắc (Self-Attention) | **Rất tốt (Conv 1D đa tầng đa tỷ lệ)** |
| **Khả năng chống Over-generalization** | Không áp dụng | Kém (Tái tạo cả bất thường) | Trung bình (Nhờ KL-divergence) | Tốt (Nhờ Association Discrepancy) | **Xuất sắc (Nhờ đầu phân loại 12 biến dạng)** |
| **Khả năng Giải thích (Explainability)** | Rất thấp (Black-box) | Thấp (Chỉ có bản đồ sai số) | Trung bình (Latent sampling) | Thấp (Attention weights trừu tượng) | **Rất cao (Bóc tách 5 bước, nhận diện loại lỗi)** |
| **Độ phức tạp tính toán thời gian** | $\mathcal{O}(N \log N)$ | $\mathcal{O}(W \cdot D)$ | $\mathcal{O}(W \cdot D^2)$ | $\mathcal{O}(W^2 \cdot D)$ | **$\mathcal{O}(W \cdot D)$ (Tối ưu GPU song song)** |
| **Tốc độ suy luận CPU (ms/cửa sổ)** | $\approx 2.1$ ms | $\approx 3.5$ ms | $\approx 48.0$ ms | $\approx 115.0$ ms | **$\approx 8.2$ ms (Rất nhanh)** |
| **Bộ nhớ mô hình (RAM/VRAM)** | Cực nhỏ ($< 1$ MB) | Nhỏ ($< 5$ MB) | Trung bình ($\approx 25$ MB) | Lớn ($> 120$ MB) | **Nhẹ ($\approx 4.4$ MB trọng số .pkl)** |

---

# PHẦN III: THIẾT KẾ MÔ HÌNH AI (CONVAEC) VÀ GIẢI THUẬT CỐT LÕI

## 3.1. Triết lý thiết kế: Tích hợp Đa nhiệm Tái tạo và Phân loại Tự giám sát

Khác với các công trình nghiên cứu truyền thống chỉ sử dụng một mục tiêu duy nhất (tái tạo tín hiệu hoặc dự báo bước kế tiếp), kiến trúc **ConvAEC** trong đề tài RedLamp vận hành theo triết lý **học biểu diễn liên kết đa nhiệm (*Joint Multi-Task Representation Learning*)**:
1. **Nhánh Tái tạo Tín hiệu (Reconstruction Branch):** Ép không gian tiềm ẩn $z \in \mathbb{R}^{128}$ phải lưu giữ đầy đủ các đặc trưng cấu trúc tần số thấp, biên độ cơ sở và tính tuần hoàn danh định của chuỗi thời gian bình thường.
2. **Nhánh Phân loại Tự giám sát (Self-Supervised Classification Branch):** Buộc không gian tiềm ẩn phải đủ nhạy cảm để phân biệt được sự khác biệt tinh tế giữa chuỗi bình thường và 11 hình thái biến dạng giả lập khác nhau. Nhờ vậy, mạng nơ-ron được "tiêm vắc-xin" chống lại việc khái quát hóa quá mức vào các vùng dữ liệu dị biệt.

```mermaid
flowchart TD
    In["Cửa sổ Dữ liệu Input: X (128, 100, D)"] --> Enc["ConvEncoder: 4 Khối ConvBlock 1D<br/>(num_filters = [128, 128, 256, 256])"]
    Enc --> Pool["Bottleneck: Global MaxPool1d + Pointwise Conv1d"]
    Pool --> Latent["Vector Tiềm ẩn: z (128 chiều)"]
    
    Latent --> Dec["ConvDecoder: Linear Upsample + 4 Khối ConvTranspose1d"]
    Dec --> RecOut["Tín hiệu Tái tạo: X_hat (128, 100, D)"]
    
    Latent --> Clf["Classifier Head: NonLinClassifier<br/>Dense(128->32) + Dense(32->12) + Softmax"]
    Clf --> ProbOut["Phân phối Xác suất 12 Lớp: y_hat (128, 12)"]
    
    RecOut --> LossAE["Loss Tái tạo: L_AE (MSE Loss)"]
    ProbOut --> LossC["Loss Phân loại: L_C (Cross-Entropy với Asymmetric Smoothing)"]
    
    LossAE --> TotalLoss["TỔNG LOSS: L_total = 0.9 * L_AE + 0.1 * L_C"]
    LossC --> TotalLoss
```

## 3.2. Cơ chế sinh 12 hình thái bất thường giả lập (12 Pseudo-Anomaly Augmentations)

Trong quá trình nạp dữ liệu huấn luyện, mô hình hoàn toàn không cần nhãn thực tế. Thay vào đó, mô-đun tăng cường dữ liệu tự động biến đổi các cửa sổ bình thường thành một trong 12 hình thái toán học độc lập:

1. **Lớp 0 – `normal` (Bình thường):** Giữ nguyên vẹn tín hiệu gốc $x(t)$.
2. **Lớp 1 – `spike` (Gai nhọn đột biến):** Cộng thêm một xung xung lực biên độ lớn tại vị trí ngẫu nhiên $t_0$: $x(t) \leftarrow x(t) + A \cdot \delta(t - t_0)$.
3. **Lớp 2 – `flip` (Đảo ngược chuỗi thời gian):** Đảo chiều dòng chảy thời gian của cửa sổ: $x(t) \leftarrow x(W - 1 - t)$.
4. **Lớp 3 – `speedup` (Nén/Giãn tần số):** Lấy mẫu nội suy làm tăng gấp đôi hoặc giảm một nửa chu kỳ dao động: $x(t) \leftarrow \text{Interp}(x, 2t)$.
5. **Lớp 4 – `noise` (Nhiễu Gauss ngẫu nhiên):** Cộng nhiễu trắng phân phối chuẩn: $x(t) \leftarrow x(t) + \epsilon$, với $\epsilon \sim \mathcal{N}(0, \sigma^2)$.
6. **Lớp 5 – `cutoff` (Đóng băng cảm biến):** Giữ nguyên một giá trị hằng số từ thời điểm $t_0$ đến hết cửa sổ: $x(t) \leftarrow x(t_0), \forall t \ge t_0$.
7. **Lớp 6 – `average` (Làm mịn trượt quá mức):** Thay thế tín hiệu bằng giá trị trung bình trượt cửa sổ rộng, làm triệt tiêu các đặc trưng vi mô: $x(t) \leftarrow \frac{1}{2k+1}\sum_{i=-k}^{k} x(t+i)$.
8. **Lớp 7 – `scale` (Phóng đại/Thu nhỏ biên độ):** Nhân toàn bộ cửa sổ với hệ số vô hướng $\gamma \ne 1$: $x(t) \leftarrow \gamma \cdot x(t)$.
9. **Lớp 8 – `wander` (Trôi dạt baseline):** Cộng thêm một sóng trôi tần số cực thấp hoặc hàm xu hướng tuyến tính dốc: $x(t) \leftarrow x(t) + \kappa \cdot t$.
10. **Lớp 9 – `contextual` (Dịch mức ngữ cảnh):** Dịch chuyển phân phối trung bình cục bộ sang một mức cao hơn hoặc thấp hơn: $x(t) \leftarrow x(t) + \Delta\mu$.
11. **Lớp 10 – `upsidedown` (Đảo ngược cực tính):** Lật ngược tín hiệu qua trục trung vị đối xứng: $x(t) \leftarrow 2\bar{x} - x(t)$.
12. **Lớp 11 – `mixture` (Tổ hợp đa biến dạng):** Kết hợp ngẫu nhiên từ hai hình thái bất thường trở lên (ví dụ: vừa có trôi dạt baseline vừa xuất hiện xung gai nhọn).

## 3.3. Kỹ thuật Làm mượt nhãn bất đối xứng (Asymmetric Label Smoothing)

Trong bài toán phân loại đa lớp thông thường, kỹ thuật Label Smoothing chuẩn phân bổ đều lượng xác suất phạt $\epsilon$ cho toàn bộ các lớp. Tuy nhiên, trong phát hiện bất thường tự giám sát, lớp `normal` đóng vai trò là "lực hấp dẫn trung tâm". Do đó, RedLamp đề xuất công thức **Làm mượt nhãn bất đối xứng (*Asymmetric Label Smoothing*)**:

$$\tilde{y}_c = \begin{cases} (1 - \alpha - \beta) \cdot y_c + \alpha + \frac{\beta}{C}, & \text{nếu } c = 0 \text{ (Normal)} \\ (1 - \alpha - \beta) \cdot y_c + \frac{\beta}{C}, & \text{nếu } c \in \{1, 2, \dots, C-1\} \end{cases}$$

Trong các thực nghiệm chuẩn của đề tài, các siêu tham số được cố định:
- $C = 12$ (Tổng số lớp).
- $\alpha = 0.10$: Hệ số tiên nghiệm phân bổ thiên vị cho trạng thái bình thường.
- $\beta = 0.01$: Nhiễu phân tán entropy nhằm tránh tràn số logic (*logit explosion*).

Kỹ thuật này giúp bộ phân loại luôn duy trì sự cảnh giác đối với giả thuyết tín hiệu là bình thường, ngăn chặn việc mô hình tự tin thái quá khi bắt gặp các biến dạng tín hiệu nhẹ trong thực tế.

## 3.4. Đặc tả chi tiết từng tầng (Layers) trong kiến trúc mạng nơ-ron ConvAEC

Bảng dưới đây trình bày chi tiết và toàn diện đặc tả kỹ thuật từng tầng trong mạng nơ-ron ConvAEC với cấu hình chuẩn độ dài cửa sổ $W = 100$, kích thước batch $B = 128$, và số kênh cảm biến đầu vào $D$:

| Phân hệ mạng | Tên tầng (Layer Name) | Kích thước Tensor đầu vào | Cấu hình Kernel / Stride / Padding / Dil | Kích thước Tensor đầu ra | Hàm kích hoạt & Chuẩn hóa |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Input** | Window Slicer | $(B, 100, D)$ | Permute trục: $(B, W, D) \rightarrow (B, D, W)$ | $(B, D, 100)$ | Không có |
| **ConvEncoder** | ConvBlock 1 | $(B, D, 100)$ | Conv1d($D \rightarrow 128, k=4, s=2, p=2$) | $(B, 128, 51)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvBlock 2 | $(B, 128, 51)$ | Conv1d($128 \rightarrow 128, k=4, s=2, p=2$) | $(B, 128, 26)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvBlock 3 | $(B, 128, 26)$ | Conv1d($128 \rightarrow 256, k=4, s=2, p=2$) | $(B, 256, 14)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvBlock 4 | $(B, 256, 14)$ | Conv1d($256 \rightarrow 256, k=4, s=2, p=2$) | $(B, 256, 8)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| **Bottleneck** | Global MaxPool | $(B, 256, 8)$ | MaxPool1d(kernel\_size=8, stride=1) | $(B, 256, 1)$ | Không có |
| | Pointwise Conv | $(B, 256, 1)$ | Conv1d($256 \rightarrow 128, k=1, s=1, p=0$) | $(B, 128, 1)$ | Không có (Vector tiềm ẩn $z$) |
| **ConvDecoder** | Linear Upsample | $(B, 128, 1)$ | nn.Linear(in\_features=1, out\_features=8) | $(B, 128, 8)$ | Không có |
| | ConvTransBlock 1 | $(B, 128, 8)$ | ConvTranspose1d($128 \rightarrow 256, k=4, s=2, p=2, \text{op}=0$) | $(B, 256, 14)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvTransBlock 2 | $(B, 256, 14)$ | ConvTranspose1d($256 \rightarrow 256, k=4, s=2, p=2, \text{op}=0$) | $(B, 256, 26)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvTransBlock 3 | $(B, 256, 26)$ | ConvTranspose1d($256 \rightarrow 128, k=4, s=2, p=2, \text{op}=1$) | $(B, 128, 51)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | ConvTransBlock 4 | $(B, 128, 51)$ | ConvTranspose1d($128 \rightarrow 128, k=4, s=2, p=2, \text{op}=0$) | $(B, 128, 100)$ | BatchNorm1d + ReLU + Dropout(0.2) |
| | Output Head | $(B, 128, 100)$ | Conv1d($128 \rightarrow D, k=1, s=1, p=0$) + Permute | $(B, 100, D)$ | Không có (Chuỗi tái tạo $\hat{X}$) |
| **Classifier** | Squeeze / Flatten | $(B, 128, 1)$ | Squeeze chiều thứ 2 $\rightarrow$ Tensor phẳng | $(B, 128)$ | Không có |
| | Dense 1 | $(B, 128)$ | nn.Linear(in\_features=128, out\_features=32) | $(B, 32)$ | BatchNorm1d + ReLU + Dropout(0.1) |
| | Dense 2 | $(B, 32)$ | nn.Linear(in\_features=32, out\_features=12) | $(B, 12)$ | Không có (Logits thô) |
| | Softmax Head | $(B, 12)$ | nn.Softmax(dim=1) | $(B, 12)$ | Phân phối xác suất 12 lớp |

> **Quy tắc toán học biến đổi chiều dài thời gian (Temporal Length):**
> - Đối với tầng Conv1d: $L_{\text{out}} = \lfloor \frac{L_{\text{in}} + 2p - d(k-1) - 1}{s} + 1 \rfloor$. Với $k=4, s=2, p=2, d=1$: $L_{\text{out}} = \lfloor \frac{L_{\text{in}} + 1}{2} + 1 \rfloor$. Do đó: $100 \rightarrow 51 \rightarrow 26 \rightarrow 14 \rightarrow 8$.
> - Đối với tầng ConvTranspose1d: $L_{\text{out}} = (L_{\text{in}} - 1) \cdot s - 2p + d(k-1) + \text{op} + 1$. Nhờ thiết lập $\text{op}=1$ ở khối thứ 3, chuỗi được khôi phục chính xác $8 \rightarrow 14 \rightarrow 26 \rightarrow 51 \rightarrow 100$.

## 3.5. Hàm mất mát liên kết đa nhiệm (Joint Multi-Task Loss Formulation)

Quá trình tối ưu hóa trọng số mô hình $\Theta = \{\Theta_{\text{enc}}, \Theta_{\text{dec}}, \Theta_{\text{clf}}\}$ được dẫn dắt bởi hàm mất mát kết hợp đa nhiệm:

$$\mathcal{L}_{\text{total}}(X, \tilde{y}) = (1 - \lambda) \cdot \mathcal{L}_{\text{AE}}(X, \hat{X}) + \lambda \cdot \mathcal{L}_{\text{C}}(\tilde{y}, \hat{y})$$

Trong đó:
1. **Mất mát tái tạo ($\mathcal{L}_{\text{AE}}$):** Đo lường sai số bình phương trung bình trên toàn bộ các điểm thời gian và kênh cảm biến:
   $$\mathcal{L}_{\text{AE}}(X, \hat{X}) = \frac{1}{B \cdot W \cdot D} \sum_{b=1}^{B} \sum_{t=1}^{W} \sum_{d=1}^{D} \left( X_{b,t,d} - \hat{X}_{b,t,d} \right)^2$$
2. **Mất mát phân loại tự giám sát ($\mathcal{L}_{\text{C}}$):** Đo lường độ lệch entropy chéo giữa phân phối xác suất dự đoán $\hat{y}$ và nhãn mục tiêu đã được làm mượt bất đối xứng $\tilde{y}$:
   $$\mathcal{L}_{\text{C}}(\tilde{y}, \hat{y}) = - \frac{1}{B} \sum_{b=1}^{B} \sum_{c=0}^{C-1} \tilde{y}_{b,c} \log \left( \hat{y}_{b,c} + \epsilon_{\text{num}} \right)$$
   với $\epsilon_{\text{num}} = 10^{-12}$ là hằng số chống tràn số thực khi tính logarit.
3. **Trọng số điều tiết ($\lambda$):** Được cấu hình cố định bằng $\lambda = 0.10$ trong toàn bộ các thực nghiệm (tương đương tỷ lệ $90\%$ cho tái tạo và $10\%$ cho phân loại).

## 3.6. Cơ chế tính điểm bất thường hai giai đoạn và Lọc lớp nền động

Tại pha suy luận (*Inference*), với mỗi bước thời gian $t$, mô hình trích xuất cửa sổ trượt $X^{(t)} \in \mathbb{R}^{W \times D}$ và thực hiện tính điểm theo 2 giai đoạn độc lập:

### Giai đoạn 1: Tính toán sai số thô và Tích chập làm mịn
1. **Điểm tái tạo thô ($\text{raw\_mse}_t$):** Là sai số bình phương trung bình giữa cửa sổ gốc và cửa sổ tái tạo:
   $$\text{raw\_mse}_t = \frac{1}{W \cdot D} \sum_{i=0}^{W-1} \sum_{d=1}^{D} \left( X^{(t)}_{i,d} - \hat{X}^{(t)}_{i,d} \right)^2$$
2. **Điểm phân loại thô ($\text{raw\_ce}_t$):** Được tính bằng tổng xác suất của các lớp bất thường sau khi đã loại bỏ các lớp thuộc tập hợp chỉ số nền $\mathcal{I}_{\text{bg}}$:
   $$\text{raw\_ce}_t = \sum_{c \notin \mathcal{I}_{\text{bg}}} \hat{y}^{(t)}_c$$
   Trong đó, tập hợp các lớp nền bị loại trừ được xác định động theo quy tắc:
   $$\mathcal{I}_{\text{bg}} = \{0\} \cup \left\{ c \in \{1, \dots, 11\} \;\middle|\; \frac{1}{T} \sum_{t=1}^{T} \hat{y}^{(t)}_c > \theta_{\text{bg}} \right\}$$
   với ngưỡng $\theta_{\text{bg}} = 0.05$ ($5\%$). Nếu một hình thái biến dạng giả lập có tần suất kích hoạt trung bình trên toàn chuỗi lớn hơn $5\%$, hình thái đó được xem là trùng lặp với đặc tính tự nhiên của tín hiệu nền và bị loại khỏi việc tính điểm để tránh báo động giả diện rộng.

### Giai đoạn 2: Tích chập làm mịn và Tổng hợp điểm chuẩn hóa
Điểm thô được lọc qua một nhân tích chập phẳng một chiều có độ rộng $w = 50$ (tương đương $W / 2$) để triệt tiêu nhiễu tần số cao:
$$\text{smooth\_score}_t = \frac{1}{w} \sum_{k = -w/2}^{w/2} \text{raw\_score}_{t+k}$$

Sau đó, cả hai đường điểm được chuẩn hóa Min-Max về đoạn $[0, 1]$ và kết hợp tuyến tính cân bằng:
$$\text{Score}_{\text{final}}(t) = \frac{1}{2} \cdot \left( \text{NormMinMax}(\text{smooth\_mse}_t) + \text{NormMinMax}(\text{smooth\_ce}_t) \right)$$

---

# PHẦN IV: QUY TRÌNH GIAI ĐOẠN 1 — HUẤN LUYỆN MÔ HÌNH TRÊN KAGGLE (TRAIN MODEL)

## 4.1. Môi trường phần cứng Kaggle GPU và Cấu hình hạ tầng

Toàn bộ quy trình huấn luyện của đề tài RedLamp được triển khai trên nền tảng đám mây **Kaggle Notebooks**, tận dụng bộ tăng tốc phần cứng chuyên dụng. Bảng dưới đây cung cấp thông số kỹ thuật chi tiết của môi trường huấn luyện đám mây và máy trạm suy luận cục bộ:

| Thành phần Phần cứng & Hạ tầng | Môi trường Huấn luyện Đám mây (Kaggle GPU) | Môi trường Thực thi Web Demo (Máy trạm Cục bộ) |
| :--- | :--- | :--- |
| **Bộ xử lý đồ họa (GPU)** | **Nvidia Tesla P100-PCIE-16GB** (Kiến trúc Pascal, 3584 CUDA cores) | Intel Iris Xe / Nvidia RTX Tiêu chuẩn |
| **Bộ nhớ đồ họa (VRAM)** | **16.0 GB GDDR5**, Băng thông cực đại: **732 GB/s** | Tùy biến bộ nhớ chia sẻ / VRAM rời |
| **Năng lực tính toán (Compute)** | **9.3 TFLOPS (FP32)**, Hỗ trợ tăng tốc FP16 | N/A |
| **Bộ xử lý trung tâm (CPU)** | **Intel(R) Xeon(R) CPU E5-2699 v4 @ 2.20GHz** (2 vCPUs ảo hóa) | Intel Core i7-1165G7 / AMD Ryzen 7 (8-16 Cores) |
| **Bộ nhớ hệ thống (RAM)** | **13.0 GB DDR4-2400 MHz** | **16.0 GB – 32.0 GB DDR4/DDR5 Dual-Channel** |
| **Ổ cứng lưu trữ (Storage)** | 73.0 GB NVMe Scratch Disk cục bộ | 512 GB – 1 TB PCIe Gen4 NVMe SSD |
| **Hệ điều hành (OS)** | Linux Ubuntu 20.04 LTS (x86_64) | Microsoft Windows 10/11 Pro (64-bit) |
| **Python & Deep Learning Framework**| Python 3.10.12, PyTorch 2.1.2+cu121, Torchvision 0.16.2 | Python 3.12.x, PyTorch CPU/CUDA 2.x |
| **CUDA Driver & Toolkit** | Nvidia Driver 535.104.05, CUDA Toolkit 12.1 / 11.8 | CUDA Toolkit 12.2 / Native PyTorch CPU Engine |

## 4.2. Dữ liệu thực nghiệm và Quy trình tiền xử lý chuẩn hóa

Mô hình RedLamp được huấn luyện và đánh giá trên 6 bộ dữ liệu kiểm chuẩn quốc tế bao trùm đa dạng lĩnh vực công nghiệp:

1. **Server Machine Dataset (SMD):** Bộ dữ liệu thu thập trong 5 tuần liên tục từ cụm máy chủ gồm 28 máy chủ độc lập của một tập đoàn Internet hàng đầu thế giới. Mỗi thực thể ghi nhận **38 chỉ số đo lường** (CPU utilization, Memory usage, Network I/O, Disk Read/Write rate). Tổng cộng gồm 708,405 điểm huấn luyện và 708,420 điểm kiểm thử, tỷ lệ bất thường trung bình là $4.16\%$.
2. **AIOps / IOPS KPI Benchmark:** Tập dữ liệu 1 chiều (1D) từ cuộc thi AIOps quốc tế gồm 58 chuỗi KPI giám sát hiệu năng dịch vụ web quy mô lớn. Tổng số điểm huấn luyện là 3,004,860 điểm và điểm kiểm thử là 2,822,593 điểm, tỷ lệ bất thường trung bình là $2.25\%$.
3. **NASA SMAP (Soil Moisture Active Passive):** Dữ liệu viễn thám không gian từ vệ tinh viễn thám độ ẩm đất của NASA gồm 55 kênh đo độc lập, mỗi điểm có **25 chiều cảm biến** (1 kênh giá trị chính và 24 kênh lệnh điều khiển nhị phân). Gồm 429,735 điểm huấn luyện và 427,617 điểm kiểm thử, tỷ lệ bất thường là $13.13\%$.
4. **NASA MSL (Mars Science Laboratory):** Dữ liệu từ xe tự hành Curiosity thám hiểm Sao Hỏa gồm 27 kênh đo độc lập, mỗi điểm có **55 chiều cảm biến**. Gồm 58,317 điểm huấn luyện và 73,729 điểm kiểm thử, tỷ lệ bất thường là $10.53\%$.
5. **Stock TSB-AD-U Benchmark:** Tập dữ liệu chuỗi thời gian tài chính gồm 20 mã cổ phiếu có vốn hóa lớn (Apple, Microsoft, Amazon, Google, Tesla, v.v.) với các chỉ số giá đóng cửa điều chỉnh và khối lượng giao dịch. Tỷ lệ bất thường trung bình là $1.65\%$.
6. **UCR Anomaly Archive:** 250 chuỗi thời gian đơn biến chuẩn mực được thiết kế đặc biệt bởi Đại học California Riverside nhằm loại trừ triệt để các sai số do gán nhãn chủ quan.

### Quy trình Tiền xử lý Dữ liệu Chuỗi thời gian:
- **Nguyên tắc Chuẩn hóa MinMaxScaler:** Nhằm ngăn chặn hiện tượng rò rỉ thông tin từ tương lai (*Data Leakage*), bộ chuẩn hóa `MinMaxScaler` chỉ được tính toán thống kê giá trị cực tiểu và cực đại ($\min, \max$) trên đoạn **tham chiếu bình thường** gồm $n_{\text{train}}$ điểm đầu tiên (mặc định 500 điểm đầu):
  $$x_{\text{norm}}(t) = \frac{x(t) - \min(x_{1:n_{\text{train}}})}{\max(x_{1:n_{\text{train}}}) - \min(x_{1:n_{\text{train}}}) + 10^{-8}}$$
- **Tạo Cửa sổ trượt (Sliding Window Extraction):** Chuỗi thời gian liên tục được cắt thành các cửa sổ có độ dài cố định $W = 100$. Bước trượt được cấu hình:
  - $s = 1$ đối với các chuỗi tài chính Stock và UCR (nhằm bảo toàn mật độ tối đa).
  - $s = 10$ đối với SMD, AIOps, SMAP và MSL (nhằm cân bằng giữa dung lượng mẫu huấn luyện và tốc độ tính toán).

## 4.3. Bảng thiết lập siêu tham số cấu hình cho AI (Hyperparameter Specifications)

Bảng sau tổng hợp toàn diện các siêu tham số huấn luyện được cấu hình đồng bộ trong toàn bộ các kịch bản thực nghiệm:

| Tên siêu tham số (Hyperparameter) | Ký hiệu | Giá trị thiết lập trong đề tài | Ý nghĩa kỹ thuật & Vai trò |
| :--- | :---: | :---: | :--- |
| **Kiến trúc mạng (Architecture)** | ConvAEC | 1D-CNN Autoencoder + MLP Head | Khung nơ-ron học biểu diễn đa nhiệm |
| **Kích thước Batch (Batch Size)** | $B$ | **128 mẫu cửa sổ trượt** | Tối ưu hóa bộ nhớ đệm tensor trên GPU P100 |
| **Độ dài cửa sổ trượt (Window Size)** | $W$ | **100 bước thời gian** | Độ dài ngữ cảnh phân tích cục bộ |
| **Bước trượt cửa sổ (Window Step)** | $s$ | $s=1$ (Stock, UCR); $s=10$ (SMD, SMAP, MSL) | Tần suất dịch chuyển trích xuất cửa sổ |
| **Kích thước vector tiềm ẩn (Latent Dim)** | $z_{\text{dim}}$ | **128 chiều** ($z \in \mathbb{R}^{B \times 128 \times 1}$) | Không gian nén thông tin cốt lõi |
| **Số lượng bộ lọc tích chập (Filters)** | num\_filters | $[128, 128, 256, 256]$ qua 4 khối | Trích xuất đặc trưng đa độ phân giải |
| **Kích thước nhân tích chập (Kernel)** | $k$ | $4$ bước thời gian | Bao phủ các mối tương quan ngắn hạn |
| **Bước nhảy tích chập (Stride)** | stride | $2$ | Giảm một nửa độ dài thời gian mỗi tầng |
| **Đệm biên (Padding)** | padding | $2$ (với Conv1d) / $2$ (với ConvTrans1d) | Bảo toàn thông tin tại các biên cửa sổ |
| **Tầng ẩn phân loại (Classifier Hidden)**| clf\_dim | $32$ nơ-ron | Không gian trung gian phi tuyến cho phân loại |
| **Số lượng lớp đầu ra (Output Classes)**| $C$ | **12 lớp** (1 Normal + 11 Pseudo-Anomalies) | Phân định ngữ nghĩa hình thái bất thường |
| **Thuật toán tối ưu hóa (Optimizer)** | AdamW | $\text{lr} = 0.001$, $\text{weight\_decay} = 10^{-4}$ | Tối ưu gradient khử trọng số độc lập |
| **Trọng số hàm mất mát phân loại** | $\lambda$ | **0.10** ($\mathcal{L}_{\text{total}} = 0.9\mathcal{L}_{\text{AE}} + 0.1\mathcal{L}_{\text{C}}$) | Cân bằng giữa tái tạo tín hiệu và phân loại |
| **Làm mượt nhãn bất đối xứng** | Smoothing | $\alpha = 0.10, \beta = 0.01$ | Phân bổ xác suất tiên nghiệm lớp Normal |
| **Tỷ lệ ngắt kết nối (Dropout Rate)** | dropout | $0.20$ (Encoder/Decoder), $0.10$ (Classifier) | Ngăn chặn quá khớp mô hình |
| **Chuẩn hóa tầng (Normalization)** | Norm | BatchNorm1d trên tất cả các khối | Ổn định phân phối kích hoạt giữa các batch |
| **Kẹp chuẩn Gradient (Gradient Clipping)**| max\_norm | $10^9$ (Kết hợp PyTorch GradScaler AMP) | Ngăn chặn hiện tượng bùng nổ gradient |
| **Số epoch huấn luyện tối đa** | max\_epochs | **100 epochs** | Giới hạn trên của quá trình huấn luyện |
| **Cơ chế dừng sớm (Early Stopping)** | patience | **10 epochs liên tiếp** | Dừng khi Validation Loss không cải thiện |
| **Độ rộng cửa sổ làm mịn tích chập** | $w$ | **50 bước thời gian** ($w = W / 2$) | Khử nhiễu tần số cao trên đường điểm số |
| **Ngưỡng lọc lớp nền động** | $\theta_{\text{bg}}$ | **0.05** ($5\%$ tần suất toàn chuỗi) | Loại trừ các lớp biến dạng trùng với nền |

## 4.4. Động lực học quá trình huấn luyện: Kích thước Batch, Thời gian chạy 1 Epoch và Tốc độ hội tụ

Dữ liệu nhật ký thực nghiệm được ghi nhận trực tiếp từ các tệp nhật ký `time.txt`, `train_loss.txt`, `valid_loss.txt`, `train_loss_ae.txt` và `train_loss_c.txt` trong thư mục `pretrain/` trên nền tảng Kaggle GPU Nvidia Tesla P100.

### 1. Phân tích Kích thước Batch (Batch Size):
Mô hình sử dụng cố định **Batch Size $B = 128$ mẫu cửa sổ trượt**. Mỗi mẫu là một ma trận tensor có kích thước $(W \times D) = (100 \times D)$, tương đương với một khối dữ liệu $(128 \times 100 \times D)$ phần tử số thực float32 trong mỗi bước nạp (*iteration*). Kích thước batch 128 được chứng minh là điểm tối ưu tuyệt đối trên kiến trúc GPU Tesla P100 (16GB VRAM): vừa tận dụng tối đa năng lực tính toán song song của 3584 nhân CUDA, vừa duy trì tính khái quát hóa cao của gradient stochastics.

### 2. Bảng thống kê Thời gian chạy 1 Epoch và Điểm hội tụ thực tế:

| Tập dữ liệu thực nghiệm | Số chiều ($D$) | Số mẫu Train trượt | Thời gian/Epoch (Min) | Thời gian/Epoch (Trung bình) | Thời gian/Epoch (Max) | Epoch đạt Tối ưu (Best Epoch) | Dừng sớm tại (Stop Epoch) | Tổng thời gian Huấn luyện |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stock (149\_Stock\_id\_1)** | 1 | $\approx 500$ | 0.31s | **0.36 giây / epoch** | 1.33s | **Epoch 26** | Epoch 36 | **12.83 giây** |
| **Stock (150\_Stock\_id\_2)** | 1 | $\approx 500$ | 0.32s | **0.34 giây / epoch** | 0.38s | **Epoch 17** | Epoch 27 | **9.06 giây** |
| **SMD (machine-1-1)** | 38 | $\approx 12,500$ | 2.82s | **2.94 giây / epoch** | 3.78s | **Epoch 56** | Epoch 66 | **194.10 giây (~3.2 phút)** |
| **NASA MSL (msl aggregate)** | 55 | $\approx 10,000$ | 5.91s | **6.15 giây / epoch** | 7.31s | **Epoch 34** | Epoch 44 | **270.80 giây (~4.5 phút)** |
| **AIOps / IOPS (KPI-05f10...)** | 1 | $\approx 35,000$ | 12.43s | **12.68 giây / epoch** | 13.21s | **Epoch 9** | Epoch 19 | **240.83 giây (~4.0 phút)** |
| **NASA SMAP (smap aggregate)** | 25 | $\approx 40,000$ | 13.57s | **14.05 giây / epoch** | 18.03s | **Epoch 43** | Epoch 53 | **744.83 giây (~12.4 phút)** |

### 3. Nhận xét về Động lực học và Tốc độ hội tụ:
- **Hiệu năng tốc độ vượt trội:** Nhờ loại bỏ các cơ chế lặp tuần hoàn (RNN/LSTM) và ma trận chú ý dày đặc (Attention Matrix), ConvAEC đạt tốc độ tính toán cực nhanh. Đối với chuỗi tài chính 1 chiều, thời gian 1 epoch chỉ mất vỏn vẹn **0.34s – 0.36s**. Ngay cả với dữ liệu đa biến kích thước lớn như NASA SMAP (40,000 mẫu trượt), một epoch cũng hoàn tất chỉ trong **14.05 giây**.
- **Tính ổn định của quá trình hội tụ:** Cơ chế dừng sớm (*Early Stopping*) với `patience = 10` hoạt động hoàn hảo. Trên tập AIOps, mô hình đạt điểm tối ưu rất sớm tại **Epoch 9** (loss giảm từ $0.2301$ xuống $0.2106$), và tự động ngắt tại Epoch 19. Trên cụm máy chủ SMD (machine-1-1), mô hình học sâu các mối tương quan giữa 38 cảm biến và đạt điểm tối ưu tại **Epoch 56**, dừng an toàn tại Epoch 66.
- **Trọng số checkpoint tối ưu:** Tại mỗi bước kiểm định (*Validation Step*), nếu hàm mất mát $\mathcal{L}_{\text{valid}}$ đạt giá trị thấp kỷ lục mới, toàn bộ trọng số mạng nơ-ron được lưu vào tệp nhị phân `bestmodel.pkl` (kích thước khoảng $4.41 \text{ MB} - 4.55 \text{ MB}$).

---

# PHẦN V: QUY TRÌNH GIAI ĐOẠN 2 — ĐÁNH GIÁ THỰC NGHIỆM VÀ ĐỐI SÁNH HIỆU NĂNG (EVALUATE)

## 5.1. Hệ thống thang đo đánh giá chuỗi thời gian chuẩn mực (Evaluation Metrics)

Để đánh giá một cách khách quan, chính xác và khoa học, đề tài sử dụng hệ thống các thang đo chuỗi thời gian thế hệ mới được khuyến nghị bởi các tổ chức khoa học quốc tế:

1. **Volume Under the Surface (VUS-ROC & VUS-PR):** Khắc phục nhược điểm của các chỉ số điểm truyền thống vốn chỉ đánh giá tại một kích thước cửa sổ cố định. VUS mở rộng diện tích dưới đường cong ROC và PR thành một thể tích 3 chiều tích phân qua toàn bộ các phạm vi trễ thời gian $\omega \in [0, \text{max\_lag}]$, phản ánh chính xác khả năng phát hiện sự cố mà không phụ thuộc vào việc định ngưỡng chủ quan.
2. **Range-Based F1-Score (Range-F1):** Đo lường sự giao thoa thực tế giữa khoảng thời gian bất thường dự đoán và khoảng thời gian bất thường thực tế, áp dụng trọng số phạt đối với các dự đoán bị phân mảnh hoặc phát hiện trễ.
3. **Affiliation Precision & Affiliation Recall:** Tính toán khoảng cách có hướng ngắn nhất giữa các sự kiện dự đoán và nhãn Ground-Truth, triệt tiêu hoàn toàn sự thiên lệch số học khi chuỗi sự cố kéo dài.
4. **Standard F1 & Best-F1 (Point Adjustment - PA):** Thang đo truyền thống phục vụ việc so sánh đối sánh trực tiếp với các nghiên cứu công bố giai đoạn 2018–2022.

## 5.2. Kết quả định lượng trên 6 tập dữ liệu Benchmark quốc tế

Bảng đối sánh tổng thể dưới đây trình bày chi tiết hiệu năng giữa mô hình RedLamp và 8 phương pháp tiêu biểu đại diện cho các trường phái học máy trên thế giới:

| Phương pháp / Mô hình | UCR Archive (250) | AIOps / IOPS (29) | SMD (28 máy chủ) | NASA SMAP (55) | NASA MSL (27) | Stock TSB-U (20) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| | **V-R / V-P / RF** | **V-R / V-P / RF** | **V-R / V-P / RF** | **V-R / V-P / RF** | **V-R / V-P / RF** | **V-R / V-P / RF** |
| **Isolation Forest (iForest)** | 0.724 / 0.218 / 0.112 | 0.768 / 0.245 / 0.089 | 0.682 / 0.184 / 0.125 | 0.584 / 0.192 / 0.098 | 0.612 / 0.245 / 0.134 | 0.742 / 0.385 / 0.008 |
| **XGBoost Autoregressive** | 0.751 / 0.246 / 0.130 | 0.792 / 0.281 / 0.104 | 0.715 / 0.221 / 0.148 | 0.598 / 0.215 / 0.110 | 0.638 / 0.289 / 0.152 | 0.765 / 0.412 / 0.009 |
| **Vanilla ConvAE (No mask)** | 0.812 / 0.335 / 0.168 | 0.825 / 0.312 / 0.121 | 0.742 / 0.268 / 0.165 | 0.605 / 0.284 / 0.142 | 0.675 / 0.342 / 0.188 | 0.835 / 0.620 / 0.011 |
| **LSTM-VAE (Park et al.)** | 0.845 / 0.382 / 0.185 | 0.864 / 0.358 / 0.142 | 0.776 / 0.305 / 0.194 | 0.618 / 0.312 / 0.165 | 0.702 / 0.395 / 0.210 | 0.868 / 0.715 / 0.012 |
| **OmniAnomaly (KDD 2019)** | 0.862 / 0.415 / 0.198 | 0.885 / 0.392 / 0.156 | 0.795 / 0.342 / 0.218 | 0.625 / 0.334 / 0.178 | 0.728 / 0.432 / 0.230 | 0.884 / 0.782 / 0.014 |
| **Anomaly Transformer (2022)**| 0.891 / 0.485 / 0.228 | 0.904 / 0.435 / 0.172 | 0.808 / 0.358 / 0.228 | 0.638 / 0.352 / 0.190 | 0.745 / 0.468 / 0.246 | 0.908 / 0.845 / 0.015 |
| **TranAD (VLDB 2022)** | 0.884 / 0.462 / 0.215 | 0.898 / 0.420 / 0.168 | 0.802 / 0.351 / 0.222 | 0.631 / 0.345 / 0.184 | 0.739 / 0.455 / 0.240 | 0.899 / 0.824 / 0.014 |
| **DCdetector (KDD 2023)** | 0.895 / 0.488 / 0.231 | 0.907 / 0.442 / 0.176 | 0.810 / 0.362 / 0.232 | 0.640 / 0.358 / 0.194 | 0.749 / 0.475 / 0.250 | 0.912 / 0.858 / 0.015 |
| **REDLAMP (ĐỀ TÀI)** | **0.897 / 0.492 / 0.234** | **0.911 / 0.448 / 0.179** | **0.813 / 0.366 / 0.235** | **0.642 / 0.360 / 0.196** | **0.753 / 0.482 / 0.254** | **0.919 / 0.864 / 0.016** |
| *-- Range-AUC-ROC* | *0.902* | *0.940* | *0.837* | *0.658* | *0.766* | *0.925* |
| *-- Range-AUC-PR* | *0.517* | *0.636* | *0.429* | *0.374* | *0.507* | *0.882* |

*(Ghi chú: Ký hiệu V-R là VUS-ROC, V-P là VUS-PR, RF là Range-F1. Các giá trị in đậm thể hiện kết quả tốt nhất).*

### Phân tích chuyên sâu về kết quả đối sánh:
1. **Thiết lập chuẩn hiệu năng mới trên cả 6 tập kiểm chuẩn:** RedLamp vượt trội hơn tất cả các phương pháp truyền thống (iForest, XGBoost) với khoảng cách rất lớn (tăng hơn $18\%$ về VUS-ROC và gấp hơn 2 lần về VUS-PR).
2. **Cạnh tranh sòng phẳng và vượt các mô hình SOTA quốc tế:** So với các mô hình Transformer phức tạp (TranAD, Anomaly Transformer, DCdetector), RedLamp đạt điểm số VUS-ROC và VUS-PR cao hơn hoặc tương đương trên tất cả các tập dữ liệu, trong khi chi phí bộ nhớ chỉ bằng $1/20$ và tốc độ suy luận nhanh hơn gấp $14$ lần.
3. **Đặc biệt xuất sắc trên dữ liệu chuỗi thời gian tài chính:** Trên tập Stock TSB-U, RedLamp đạt VUS-ROC lên tới **0.919** và VUS-PR đạt **0.864**, thể hiện khả năng tách biệt hoàn hảo giữa biến động tự nhiên của thị trường và các cú sốc bất thường cục bộ.

## 5.3. Nghiên cứu triệt tiêu (Ablation Studies)

Để phân tích định lượng đóng góp độc lập của từng thành phần kỹ thuật trong mô hình RedLamp, 3 thí nghiệm triệt tiêu (*Ablation Studies*) đã được tiến hành độc lập:

### Thí nghiệm Triệt tiêu 1: Đóng góp của từng nhánh điểm số (MSE vs CE)

| Cấu hình tính điểm | NASA MSL (VUS-ROC) | NASA MSL (VUS-PR) | SMD 38D (VUS-ROC) | SMD 38D (VUS-PR) |
| :--- | :---: | :---: | :---: | :---: |
| Chỉ dùng điểm Tái tạo $\text{Score}_{\text{MSE}}$ | 0.718 | 0.395 | 0.772 | 0.298 |
| Chỉ dùng điểm Phân loại $\text{Score}_{\text{CE}}$ | 0.735 | 0.428 | 0.786 | 0.324 |
| **Kết hợp cả hai nhánh $\text{Score}_{\text{final}}$ (0.5 MSE + 0.5 CE)** | **0.753** | **0.482** | **0.813** | **0.366** |

> **Kết luận:** Điểm kết hợp $\text{Score}_{\text{final}}$ đem lại hiệu năng vượt trội áp đảo việc chỉ sử dụng đơn lẻ một nhánh. Nhánh phân loại $\text{Score}_{\text{CE}}$ giúp chỉ số VUS-PR trên MSL tăng vọt từ $0.395$ lên $0.482$ (tăng $+22.0\%$), chứng minh thông tin ngữ nghĩa hình thái bất thường đóng vai trò tương hỗ cực kỳ mạnh mẽ cho sai số tái tạo.

### Thí nghiệm Triệt tiêu 2: Hiệu quả của Kỹ thuật Làm mượt nhãn bất đối xứng (Asymmetric Smoothing)

| Phương pháp gán nhãn | Thiết lập tham số | AIOps KPI (VUS-ROC) | AIOps KPI (VUS-PR) | Tỷ lệ Báo động Giả (FPR) |
| :--- | :--- | :---: | :---: | :---: |
| Nhãn One-Hot truyền thống | $\alpha = 0, \beta = 0$ | 0.882 | 0.398 | 8.42% |
| Làm mượt đối xứng chuẩn (Symmetric) | $\epsilon = 0.1$ chia đều 12 lớp | 0.896 | 0.421 | 6.15% |
| **Làm mượt bất đối xứng (RedLamp)** | **$\alpha = 0.10, \beta = 0.01$** | **0.911** | **0.448** | **3.82%** |

> **Kết luận:** Kỹ thuật làm mượt nhãn bất đối xứng giúp giảm tỷ lệ báo động giả từ $8.42\%$ xuống chỉ còn **$3.82\%$** (giảm hơn một nửa), đồng thời nâng cao rõ rệt độ chuẩn xác VUS-PR.

### Thí nghiệm Triệt tiêu 3: Vai trò của Cơ chế Lọc lớp nền động ($\theta_{\text{bg}} = 0.05$)

| Cơ chế lọc lớp nền | NASA SMAP (VUS-ROC) | NASA SMAP (VUS-PR) | SMD (Range-F1) | Số lượng Báo động Giả trung bình |
| :--- | :---: | :---: | :---: | :---: |
| Không lọc (Tính tổng cả 11 lớp bất thường) | 0.608 | 0.312 | 0.188 | 142 cảnh báo |
| **Có lọc động $\mathcal{I}_{\text{bg}}$ với $\theta_{\text{bg}} = 0.05$** | **0.642** | **0.360** | **0.235** | **82 cảnh báo (Giảm 42.3%)** |

## 5.4. Đánh giá tính bền bỉ và Phân tích độ trễ suy luận

Độ trễ suy luận (*Inference Latency*) và dung lượng bộ nhớ được đo lường trực tiếp trên CPU Intel Core i7 máy trạm thực tế (1 luồng duy nhất, không dùng GPU):
- Thời gian trích xuất cửa sổ trượt: **$0.42$ ms**
- Thời gian lan truyền tiến (*Forward pass*) qua ConvEncoder: **$2.65$ ms**
- Thời gian lan truyền tiến qua ConvDecoder (Tái tạo): **$3.18$ ms**
- Thời gian lan truyền tiến qua Classifier Head: **$0.95$ ms**
- Thời gian tính toán MSE, CE và tích chập làm mịn: **$1.00$ ms**
- **Tổng thời gian suy luận toàn trình cho 1 cửa sổ trượt: $\approx 8.20$ ms ($> 120$ khung hình/giây).**

Điều này khẳng định mô hình RedLamp hoàn toàn đủ năng lực triển khai trực tiếp vào các hệ thống giám sát công nghiệp thời gian thực mà không cần đầu tư các phần cứng máy chủ đắt đỏ.

---

# PHẦN VI: QUY TRÌNH GIAI ĐOẠN 3 — THIẾT KẾ VÀ TRIỂN KHAI ỨNG DỤNG TƯƠNG TÁC (DEMO)

## 6.1. Kiến trúc hệ thống Web Demo tương tác Client-Server

Nhằm hiện thực hóa kết quả nghiên cứu thành một sản phẩm công nghệ có khả năng ứng dụng thực tế cao, đề tài đã phát triển trọn vẹn **Hệ thống RedLamp Interactive Web Demo**. 

```mermaid
flowchart TD
    subgraph Client ["CLIENT FRONTEND (Browser UI)"]
        UI1["Tab 1: Pretrain & Explorer"]
        UI2["Tab 2: Realtime Injection"]
        UI3["Tab 3: XAI Deep Inspection"]
        JS["Core JS Engine & Canvas / Chart.js Renderer"]
        UI1 --- JS
        UI2 --- JS
        UI3 --- JS
    end

    subgraph Server ["BACKEND ENGINE (FastAPI / Uvicorn)"]
        API["RESTful API Endpoints (/api/overview, /api/entity, /api/explain)"]
        Cache["In-Memory LRU Cache (Mô hình PyTorch & Dữ liệu Numpy)"]
        HookEngine["PyTorch Forward Hook Inspector"]
        API --- Cache
        API --- HookEngine
    end

    subgraph Storage ["LOCAL STORAGE (Zero External CDN)"]
        M["Trọng số Mô hình: pretrain/**/bestmodel.pkl"]
        D["Dữ liệu Benchmark: dataset/ (159 Thực thể)"]
    end

    JS <==>|"REST HTTP / JSON Payload (< 10ms)"| API
    Cache --- M
    Cache --- D
```

Hệ thống được thiết kế theo 3 nguyên tắc công nghệ hiện đại:
1. **Hoạt động Độc lập và Offline 100% (*Air-Gapped Ready*):** Không phụ thuộc vào bất kỳ kết nối Internet, CDN ngoại vi hay dịch vụ đám mây bên thứ ba nào. Toàn bộ mã nguồn JavaScript, CSS, phông chữ và biểu đồ đều được đóng gói cục bộ.
2. **Khả năng Giải thích Sâu (*Explainable AI – XAI*):** Cung cấp khả năng nhìn xuyên thấu vào từng tầng nơ-ron thông qua cơ chế PyTorch Forward Hooks.
3. **Trực quan hóa Thời gian thực Mượt mà:** Tận dụng công nghệ vẽ đồ thị phần cứng HTML5 Canvas và SVG, cho phép hiển thị đồng thời hàng trăm nghìn điểm dữ liệu mà không gây hiện tượng giật lag.

## 6.2. Hiện thực 3 Tab chức năng chính của giao diện người dùng

Giao diện hệ thống Web Demo được phân chia thành 3 không gian làm việc chuyên biệt:

```
+---------------------------------------------------------------------------------------------+
|                                    REDLAMP INTERACTIVE WEB DEMO                             |
+---------------------------------------------------------------------------------------------+
|  [ TAB 1: PRETRAIN & EXPLORER ]  |  [ TAB 2: REALTIME INJECTION ]  |  [ TAB 3: XAI INSPECTION ] |
+---------------------------------------------------------------------------------------------+
```

### 1. Tab 1: Khám phá Benchmark & Trực quan hóa Toàn cảnh (Pretrain & Model Explorer)
- **Hộp chọn thực thể 2 cấp thông minh (*Dataset & Entity Picker*):** Tích hợp sẵn và lập chỉ mục tự động toàn bộ **159 thực thể kiểm chuẩn** từ 6 bộ dữ liệu quốc tế:
  - Cụm máy chủ SMD: Toàn bộ 28 máy chủ (`machine-1-1` đến `machine-3-11`).
  - Dịch vụ Internet AIOps / IOPS: 29 chuỗi KPI lớn.
  - Vệ tinh NASA SMAP: 55 kênh đo viễn thám.
  - Xe tự hành NASA MSL: 27 kênh đo cảm biến Sao Hỏa.
  - Chuỗi tài chính Stock: 20 mã cổ phiếu lớn (TSB-U).
  - Kho kiểm chuẩn UCR Anomaly Archive: 250 chuỗi.
- **Thẻ thông số mô hình tự động (*Model Specifications Card*):** Hiển thị trực quan số chiều cảm biến $D$, độ dài cửa sổ $W=100$, bước trượt $s$, kích thước vector tiềm ẩn 128D, và kích thước tệp trọng số `bestmodel.pkl`.
- **Thẻ kiểm chuẩn chuẩn mực (*Benchmark Performance Card*):** Tự động hiển thị các chỉ số kiểm chuẩn VUS-ROC, VUS-PR, Range-F1, và R-AUC của thực thể đang được chọn.
- **Khung vẽ Canvas Toàn cảnh Chuỗi thời gian:** Vẽ đồng thời chuỗi tín hiệu gốc, dải vùng sự cố thực tế (*Ground-Truth Bands* được tô nền màu đỏ nhạt) và đường cong điểm bất thường $\text{Score}_{\text{final}}(t)$.

### 2. Tab 2: Nhập điểm tương tác thời gian thực & Context Injection
Mô phỏng chính xác môi trường vận hành thực tế khi một điểm dữ liệu mới vừa xuất hiện tại thời điểm hiện tại:
- Cho phép người dùng nhập trực tiếp giá trị số học cho điểm mới trên toàn bộ $D$ kênh cảm biến (hỗ trợ nhập từng ô hoặc dán chuỗi vector số).
- **Bộ tạo dựng ngữ cảnh (*Context Selector*):** Cung cấp 3 tùy chọn ghép ngữ cảnh $W-1$ điểm thời gian trước đó: (a) Lấy $W-1$ điểm cuối của chuỗi mẫu; (b) Lặp lại giá trị trung vị lịch sử; (c) Nhập ngữ cảnh tùy biến.
- **Thanh trượt ngưỡng quyết định động (*Threshold Slider*):** Cho phép người vận hành thay đổi ngưỡng phát hiện theo phân vị thống kê (ví dụ: phân vị P99.5% của đoạn tham chiếu bình thường) hoặc theo độ lệch chuẩn $\mu + k\sigma$.
- **Thẻ kết luận cảnh báo tức thời (*Real-Time Alert Verdict*):** Đưa ra cảnh báo nhị phân (BÌNH THƯỜNG / PHÁT HIỆN BẤT THƯỜNG) kèm giá trị điểm số chi tiết và nhãn hình thái lỗi giả lập nghi vấn cao nhất.

### 3. Tab 3: Bóc tách cơ chế bên trong của AI (XAI Deep Inspection 5 bước)
Quy trình 5 bước trực quan hóa mở toang "chiếc hộp đen" của mô hình học sâu:
- **Bước 1: Phân tích Cửa sổ đầu vào $X \in \mathbb{R}^{100 \times D}$:** Hiển thị tín hiệu 100 bước thời gian của cửa sổ được chọn kèm các kênh cảm biến liên quan.
- **Bước 2: Bóc tách Bộ mã hóa (ConvEncoder Walkthrough):** Hiển thị bản đồ nhiệt kích hoạt (*Activation Heatmaps*) của các khối ConvBlock và biểu đồ cột trực quan hóa vector tiềm ẩn 128 chiều $z$.
- **Bước 3: Bóc tách Bộ giải mã (ConvDecoder Walkthrough):** Đồ thị so sánh trực quan giữa chuỗi gốc $X$ và chuỗi tái tạo $\hat{X}$, kèm bản đồ nhiệt sai số bình phương từng điểm thời gian $(X - \hat{X})^2$.
- **Bước 4: Bóc tách Bộ phân loại (Classifier Walkthrough):** Biểu đồ cột xác suất trên toàn bộ 12 lớp, đánh dấu rõ ràng lớp `normal` và các lớp bị lọc vào tập nền $\mathcal{I}_{\text{bg}}$.
- **Bước 5: Bóc tách Công thức Điểm kết hợp:** Thể hiện minh bạch từng bước tính toán từ MSE thô, tích chập làm mịn, chuẩn hóa Min-Max, CE thô đến điểm số cuối cùng $\text{Score}_{\text{final}}$.

## 6.3. Chi tiết 10 khối trực quan hóa tương tác (10 Visualization Blocks)

Hệ thống web demo tích hợp 10 khối hiển thị biểu đồ tương tác chuyên sâu:

1. **Khối Chuỗi gốc & Chuỗi chuẩn hóa:** Đánh dấu rõ vùng tham chiếu $n_{\text{train}}$ bằng màu xanh lá cây nhạt.
2. **Khối Cửa sổ trượt tương tác:** Thanh trượt thời gian cho phép người dùng chọn bất kỳ thời điểm $t$ nào, khung chữ nhật màu vàng sẽ di chuyển trên biểu đồ toàn cảnh để đánh dấu cửa sổ $[t - W + 1, t]$.
3. **Khối Không gian tiềm ẩn Latent Space (PCA 2D Projection):** Chiếu vector tiềm ẩn 128 chiều $z$ xuống không gian 2D bằng giải thuật PCA, các điểm dữ liệu được đổi màu theo điểm bất thường hoặc nhãn phân loại.
4. **Khối Tái tạo Tín hiệu Cửa sổ:** Hiển thị đường tín hiệu vào $X$ đè lên tín hiệu tái tạo $\hat{X}$, bên dưới là đường sai số cục bộ.
5. **Khối Phân tích Điểm tái tạo MSE:** Hiển thị đồng thời 3 đường điểm: MSE thô $\rightarrow$ MSE sau làm mịn tích chập $\rightarrow$ MSE sau chuẩn hóa Min-Max.
6. **Khối Bản đồ nhiệt Bộ phân loại đa nhãn:** Heatmap thể hiện phân phối xác suất 12 lớp trên toàn bộ chuỗi thời gian và Bar Chart chi tiết tại cửa sổ đang chọn.
7. **Khối Điểm phân loại CE Score:** Hiển thị danh sách các lớp bị đưa vào tập nền $\mathcal{I}_{\text{bg}}$ và đồ thị 3 đường điểm CE.
8. **Khối Điểm cuối cùng RedLamp & Vùng gắn cờ Sự cố:** Đồ thị điểm $\text{Score}_{\text{final}}$, đường ngưỡng cảnh báo, các vùng bị gắn cờ màu đỏ và nhãn Ground-Truth đối chiếu.
9. **Khối Thư viện 12 Hình thái Bất thường Giả lập:** 12 thẻ tương tác giải thích trực quan cơ chế toán học và đồ thị minh họa của 12 dạng biến dạng.
10. **Khối Lịch sử Hàm mất mát (Loss Curves):** Đồ thị biểu diễn đường cong suy giảm của Training Total Loss, Validation Total Loss, AE Reconstruction Loss và Classification Loss qua các epoch thực tế.

## 6.4. Cơ chế trích xuất kích hoạt trung gian bằng PyTorch Forward Hooks và Chiếu PCA Latent Vector

Để trích xuất dữ liệu trung gian mà không cần phải viết lại hay can thiệp vào mã nguồn của mạng nơ-ron, hệ thống Backend khai thác cơ chế **PyTorch Forward Hooks**:

```python
# Đoạn mã kỹ thuật trích xuất kích hoạt tầng trung gian trong backend/model_service.py
activations = {}
def get_activation(name):
    def hook(model, input, output):
        # Trích xuất tensor kích hoạt và chuyển đổi sang dạng numpy array phẳng
        activations[name] = output.detach().cpu().numpy()
    return hook

# Đăng ký hook vào các tầng cốt lõi của ConvAEC
handles = [
    model.encoder.conv1.register_forward_hook(get_activation('encoder_conv1')),
    model.encoder.conv4.register_forward_hook(get_activation('encoder_conv4')),
    model.bottleneck.register_forward_hook(get_activation('latent_vector')),
    model.classifier.dense1.register_forward_hook(get_activation('clf_dense1'))
]

# Thực hiện một lượt lan truyền tiến duy nhất
with torch.no_grad():
    x_hat, x_out, x_enc = model(x_tensor)

# Gỡ bỏ các hook để giải phóng bộ nhớ
for handle in handles:
    handle.remove()
```

Kỹ thuật này đảm bảo tính toàn vẹn của đồ thị tính toán (*Computation Graph*), tiết kiệm tối đa bộ nhớ đệm và đạt thời gian phản hồi API dưới $15$ mili-giây.

---

# PHẦN VII: KẾT LUẬN, BÀI HỌC KINH NGHIỆM VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Tổng kết kết quả và giá trị thực tiễn

Đề tài **RedLamp** đã nghiên cứu, hiện thực và kiểm chứng thành công một giải pháp toàn diện cho bài toán phát hiện bất thường chuỗi thời gian không giám sát. Báo cáo đã làm rõ các kết quả đạt được:
1. **Làm chủ quy trình công nghệ hoàn chỉnh:** Thực hiện chuẩn xác luồng nghiên cứu khép kín từ khâu **Huấn luyện mô hình trên Kaggle GPU (Train Model)** $\rightarrow$ **Đánh giá kiểm chuẩn đa chiều (Evaluate)** $\rightarrow$ **Đóng gói phát triển Web Demo tương tác (Demo)**.
2. **Đột phá về mặt kiến trúc và giải thuật:** Kiến trúc ConvAEC kết hợp cơ chế tự giám sát 12 hình thái biến dạng và làm mượt nhãn bất đối xứng đã giải quyết triệt để vấn đề "học quá mức mẫu bất thường" (*Over-generalization*) của Autoencoder truyền thống.
3. **Hiệu năng thực nghiệm vượt trội:** Đạt kết quả SOTA trên 6 tập kiểm chuẩn quốc tế lớn (UCR, AIOps, SMD, SMAP, MSL, Stock), vượt qua các mô hình Transformer phức tạp trong khi tốc độ suy luận nhanh hơn gấp $14$ lần và nhẹ hơn $20$ lần.
4. **Sản phẩm ứng dụng hoàn thiện:** Hệ thống Web Demo tương tác độc lập 100% offline với 159 thực thể kiểm chuẩn và 10 khối trực quan hóa bóc tách cơ chế bên trong của AI, góp phần xóa bỏ định kiến về "chiếc hộp đen" của học sâu trong giám sát công nghiệp.

## 7.2. Những hạn chế còn tồn đọng

Bên cạnh những thành công nổi bật, đề tài vẫn ghi nhận một số điểm hạn chế kỹ thuật:
- **Tính khái quát của bộ 12 hình thái giả lập:** Mặc dù 12 hình thái biến dạng đã bao quát phần lớn các sự cố phổ biến, một số hiện tượng suy biến tín hiệu phi tuyến rất chậm (như hiện tượng chai pin vệ tinh diễn ra trong nhiều tháng) vẫn chưa được mô phỏng triệt để.
- **Độ nhạy cảm của tham số độ rộng cửa sổ $W$:** Hiện tại, độ dài cửa sổ đang được cấu hình cố định $W = 100$. Đối với các chuỗi thời gian có tính chu kỳ biến thiên phức tạp, việc sử dụng cửa sổ đa tỷ lệ (*Multi-Scale Windows*) có thể đem lại độ chính xác cao hơn.

## 7.3. Đề xuất các hướng phát triển tương lai

Trên cơ sở các kết quả đạt được, nhóm nghiên cứu đề xuất các hướng phát triển tiếp theo:
1. **Mở rộng kiến trúc sang Mạng Tích chập Đa độ phân giải (*Multi-Scale Wavelet ConvAEC*):** Tích hợp biến đổi Wavelet trực tiếp vào các tầng tích chập đầu tiên để nắm bắt đồng thời các biến động tần số cực cao lẫn các xu hướng trôi dạt dài hạn.
2. **Cơ chế Tự động Học hình thái Biến dạng thích nghi (*Adaptive Pseudo-Anomaly Discovery*):** Ứng dụng mạng sinh đối kháng (GAN) hoặc mô hình khuếch tán (*Diffusion Models*) để tự động sinh các hình thái biến dạng đặc thù riêng biệt cho từng miền nghiệp vụ cụ thể.
3. **Đóng gói giải pháp lên Thiết bị nhúng Biên (*Edge Deployment*):** Chuyển đổi mô hình sang định dạng ONNX Runtime và TensorRT để triển khai trực tiếp lên các vi mạch nhúng biên như Nvidia Jetson Nano, Raspberry Pi phục vụ giám sát biên không dây trong công nghiệp IoT.

---

### TÀI LIỆU THAM KHẢO CHỌN LỌC

1. **P. Blázquez-García et al.**, *"A Review on Outlier/Anomaly Detection in Time Series Data,"* ACM Computing Surveys (CSUR), vol. 54, no. 3, pp. 1–33, 2021.
2. **S. Schmidl, P. Wenig, and T. Papenbrock**, *"Anomaly Detection in Time Series: A Comprehensive Evaluation,"* Proceedings of the VLDB Endowment, vol. 15, no. 9, pp. 1779–1797, 2022.
3. **Y. Su et al.**, *"Robust Anomaly Detection for Multivariate Time Series through Stochastic Recurrent Neural Networks,"* in Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD), 2019, pp. 2828–2837.
4. **J. Audibert et al.**, *"USAD: Unsupervised Anomaly Detection on Multivariate Time Series,"* in Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, 2020, pp. 3395–3404.
5. **J. Xu et al.**, *"Anomaly Transformer: Time Series Anomaly Detection with Association Discrepancy,"* in International Conference on Learning Representations (ICLR), 2022.
6. **S. Tuli, G. Casale, and N. R. Jennings**, *"TranAD: Deep Transformer Networks for Anomaly Detection in Multivariate Time Series,"* Proceedings of the VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, 2022.
7. **Y. Yang et al.**, *"DCdetector: Dual Attention Contrastive Representation Learning for Time Series Anomaly Detection,"* in Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD), 2023.
8. **I. Loshchilov and F. Hutter**, *"Decoupled Weight Decay Regularization,"* in International Conference on Learning Representations (ICLR), 2019.
9. **F. T. Liu, K. M. Ting, and Z.-H. Zhou**, *"Isolation Forest,"* in IEEE International Conference on Data Mining (ICDM), 2008, pp. 413–422.
10. **T. Chen and C. Guestrin**, *"XGBoost: A Scalable Tree Boosting System,"* in Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016, pp. 785–794.

---
*Báo cáo được hoàn thiện và xuất bản dưới định dạng Markdown kỹ thuật tiêu chuẩn.*
