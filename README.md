# RedLamp Web Demo: Phát Hiện Bất Thường Chuỗi Thời Gian Không Giám Sát

Hệ thống web demo tương tác cho **RedLamp** (Unsupervised Time Series Anomaly Detection) dựa trên kiến trúc **ConvAEC** kết hợp tái tạo tín hiệu và phân loại 12 loại bất thường giả tự giám sát (self-supervised augmentations).

Ứng dụng sử dụng trực tiếp các mô hình đã được huấn luyện sẵn (pre-trained) chia sẻ từ Google Drive (`redlamp/result` và `redlamp/metrics`), **KHÔNG huấn luyện lại**, và tái sử dụng nguyên bản logic tính điểm từ `main.py` và `datautils.py`.

---

## 🚀 Cách Chạy Nhanh (1 Lệnh Duy Nhất)

### Cách 1: Chạy bằng Python (khuyến nghị)
```bash
py -3.12 run_demo.py
# hoặc: python run_demo.py
```
> Trình duyệt sẽ tự động mở tại địa chỉ: **`http://127.0.0.1:8000`**

### Cách 2: Chạy trên Windows bằng batch file
Click đúp chuột vào file:
```text
run.bat
```

### Chạy kiểm thử tự động (Unit Tests)
```bash
py -3.12 -m pytest tests -v
```
> Bộ test kiểm tra 10 bài test độc lập: chuẩn hóa MinMaxScaler, tái tạo shape ConvAEC, tính toán sai số MSE, loại trừ indices trong CE score, tái tạo khớp bit-for-bit `anomaly_score.npy` gốc, và các endpoint API.

---

## 📋 Báo Cáo Khám Phá (Bước 0)

### 1. Cây thư mục `pretrain/` và các mô hình đã xác nhận
Các mô hình pre-trained được tải trực tiếp từ Google Drive và đặt trong `pretrain/`:
```text
pretrain/
├── stock/
│   ├── 149_Stock_id_1_Finance_tr_500_1st_7/d1_b128_w100_s1/0/
│   │   ├── bestmodel.pkl (4.41 MB)
│   │   ├── train_loss.txt, train_loss_ae.txt, train_loss_c.txt
│   │   ├── valid_loss.txt, valid_loss_ae.txt, valid_loss_c.txt
│   │   ├── time.txt
│   │   └── test_all/ (input.npy, pred.npy, label.npy, pred_label.npy, enc.npy, anomaly_score.npy)
│   └── 150_Stock_id_2_Finance_tr_500_1st_7/d1_b128_w100_s1/0/
│       ├── bestmodel.pkl, *_loss.txt, time.txt, test_all/
├── iops/
│   └── KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa/d1_b128_w100_s10/0/
│       ├── bestmodel.pkl, *_loss.txt, time.txt, test_all/
├── smd/
│   └── machine-1-1/d1_b128_w100_s10/0/
│       ├── bestmodel.pkl (4.51 MB), *_loss.txt, time.txt
├── msl/
│   └── msl/d1_b128_w100_s10/0/
│       ├── bestmodel.pkl (4.55 MB), *_loss.txt, time.txt
└── smap/
    └── smap/d1_b128_w100_s10/0/
        ├── bestmodel.pkl (4.47 MB), *_loss.txt, time.txt
```

### 2. Thông số kiến trúc ConvAEC (`models/meta.py` & `models/classifier.py`)
- **`forward(x)` trả về**: `(x_hat, x_out, x_enc)` tương ứng với `(predicted, pred_label, pred_enc)`.
- **Đặc tính `pred_label` (`x_out`)**: Là **Softmax Probabilities** (được tính qua `nn.Softmax(dim=1)` trong `NonLinClassifier.layers`), tổng xác suất qua 12 lớp luôn bằng $1.0$, giá trị từng lớp nằm trong đoạn $[0, 1]$.
- **Kích thước các đầu ra**:
  - `predicted` (`x_hat`): shape `(batch, window_size, n_features)` = `(batch, 100, D)`
  - `pred_label` (`x_out`): shape `(batch, classes)` = `(batch, 12)`
  - `pred_enc` (`x_enc`): shape `(batch, embedding_dim, 1)` = `(batch, 128, 1)`
- **Thứ tự 12 lớp bất thường**:
  1. `normal` (Lớp bình thường)
  2. `spike` (Gai nhọn / Đột biến tức thời)
  3. `flip` (Đảo ngược chuỗi thời gian)
  4. `speedup` (Nén / Giãn tần số dao động)
  5. `noise` (Nhiễu Gauss cộng dồn)
  6. `cutoff` (Treo giá trị / Sensor freeze)
  7. `average` (Làm mịn trượt quá mức)
  8. `scale` (Phóng đại biên độ)
  9. `wander` (Trôi dạt xu hướng baseline)
  10. `contextual` (Lệch ngữ cảnh / Dịch mức trung bình)
  11. `upsidedown` (Đảo ngược cực tính tín hiệu)
  12. `mixture` (Tổ hợp đa biến dạng)

---

## 🧠 Nguyên Lý Tính Điểm & Cơ Chế Chọn Ngưỡng

### 1. Chuẩn hóa Min-Max
Chuỗi dữ liệu được chuẩn hóa `MinMaxScaler` chỉ fit trên đoạn tham chiếu bình thường ($n_{train}$ điểm đầu, mặc định 500 điểm), sau đó áp dụng biến đổi cho toàn chuỗi theo đúng quy trình trong `datautils.py`.

### 2. Vì sao KHÔNG dùng điểm cuối cùng để kết luận "có/không bất thường"?
Điểm `anomaly_score` cuối cùng của RedLamp được tính bằng công thức:
$$\text{anomaly\_score} = \frac{\text{mse\_score} + \text{ce\_score}}{2}$$
Trong đó cả `mse_score` và `ce_score` đều trải qua bước `convolve_minmax_score(..., minmax=True)`. Do bị chuẩn hóa Min-Max trên toàn chuỗi, giá trị lớn nhất trong chuỗi **luôn bị ép bằng 1.0**, ngay cả khi chuỗi hoàn toàn không có bất thường nào.

### 3. Giải pháp: Ngưỡng phát hiện dựa trên điểm thô đoạn tham chiếu
Hệ thống sử dụng **z-score điểm thô** (kết hợp `raw_mse` và `raw_ce` trước khi Min-Max) so sánh với phân phối của các cửa sổ nằm trong đoạn tham chiếu $n_{train}$:
$$z_{raw} = \frac{1}{2} \left( \frac{\text{raw\_mse} - \mu_{ref\_mse}}{\sigma_{ref\_mse}} + \frac{\text{raw\_ce} - \mu_{ref\_ce}}{\sigma_{ref\_ce}} \right)$$
- Người dùng có thể điều chỉnh ngưỡng bằng slider theo **Phân vị (%)** (ví dụ phân vị 99.5% của đoạn tham chiếu) hoặc theo **Mean + $k\sigma$** (ví dụ $\mu + 3.0\sigma$).
- Các cửa sổ có $z_{raw} > \text{threshold}$ được gắn cờ bất thường.

### 4. Gắn nhãn phân loại cho vùng bất thường
Đối với mỗi vùng bị gắn cờ liên tiếp, nhãn bất thường được xác định bằng:
$$\text{label} = \arg\max_{c \notin \text{indices}} \frac{1}{|R|} \sum_{i \in R} \text{pred\_label}[i, c]$$
với $\text{indices} = \{0 \text{ (normal)}\} \cup \{c \mid \text{mean}(\text{pred\_label}[:, c]) > 0.05 \text{ trên toàn chuỗi}\}$. Nếu xác suất cao nhất của các lớp hợp lệ $< 0.02$, vùng được ghi nhận là *"Không xác định"*.

---

## 📊 10 Khối Trực Quan Hóa (Interactive Visualization Blocks)

1. **Chuỗi gốc & Chuỗi chuẩn hóa Min-Max**: Đánh dấu vùng tham chiếu $n_{train}$ màu xanh lá.
2. **Cửa sổ trượt**: Thanh trượt chọn thời điểm $t$, khung chữ nhật vàng đánh dấu cửa sổ $[t - W + 1, t]$.
3. **Không gian tiềm ẩn Encoder (PCA 2D)**: Chiếu 128D latent vector xuống 2D, đổi màu theo điểm số hoặc nhãn.
4. **Tái tạo tín hiệu**: Input $x$ vs Reconstructed $\hat{x}$ kèm sai số bình phương từng điểm $(x - \hat{x})^2$.
5. **Điểm tái tạo**: 3 đường thể hiện MSE thô $\rightarrow$ Smooth ($w=50$) $\rightarrow$ Min-Max $[0, 1]$.
6. **Bộ phân loại đa nhãn**: Heatmap 12 lớp toàn chuỗi và Bar Chart xác suất cho cửa sổ $t$.
7. **Điểm phân loại (CE Score)**: Hiển thị các lớp bị loại trừ vào `indices` và 3 đường CE score.
8. **Điểm cuối cùng RedLamp & Vùng gắn cờ**: Điểm tổng hợp, đường ngưỡng, vùng gắn cờ màu đỏ và nhãn Ground Truth (nếu có).
9. **Thư viện Augmentation**: 12 card tương tác minh họa 12 loại bất thường giả sinh từ `loaders/loader_aug.py`.
10. **Lịch sử hàm mất mát (Loss Curves)**: Train/Valid Total Loss, AE Loss (MSE), Classification Loss qua các Epoch.

---

## ⚠️ Lưu Ý Khoa Học (Disclaimer)

Các nhãn phân loại (*spike, flip, speedup, noise, cutoff, average, scale, wander, contextual, upsidedown, mixture*) là các loại **bất thường GIẢ** được sinh tự động trong quá trình huấn luyện tự giám sát (self-supervised augmentation). Kết luận phân loại của mô hình mang tính **gợi ý đặc tính tín hiệu**, KHÔNG phải nguyên nhân thực tế trong miền ứng dụng; mọi diễn giải mang tính tài chính/hệ thống chỉ là **giả thuyết**.
