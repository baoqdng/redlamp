# RedLamp Web Demo (Phát hiện bất thường chuỗi thời gian không giám sát)

Hệ thống web demo trực quan hóa và tương tác với mô hình **RedLamp** (ConvAEC: Convolutional Autoencoder + NonLinear Classifier) đã huấn luyện sẵn. Chạy hoàn toàn offline trên Windows (CPU), không sử dụng CDN, tái sử dụng toàn bộ logic từ `D:\REDLAMP-danh\REDLAMP-main` và kết quả lưu tại `D:\REDLAMP-danh\result`.

---

## 1. Kiến trúc hệ thống & Chuyển đổi công nghệ

Theo mục 2 của yêu cầu kỹ thuật:
> *"Nếu worker Python từ Rust không khả thi, chuyển sang backend thuần Python (FastAPI), giữ nguyên API và frontend, và nói rõ trong báo cáo cuối."*

- **Lý do chuyển đổi:** Trên môi trường Windows hiện tại, các toolchain Rust (MSVC thiếu Windows SDK `kernel32.lib` và GNU LLVM thiếu `libgcc`) gặp lỗi liên kết nhị phân hệ thống. Do đó, hệ thống backend chính thức được triển khai bằng **FastAPI** (`server.py`), đồng thời vẫn giữ đầy đủ `Cargo.toml`, `src/index.rs`, `src/main.rs` và `worker/worker.py` (tiến trình con xử lý giao thức JSON lines qua stdin/stdout) theo đúng thiết kế ban đầu.
- **Frontend tĩnh & Offline:** Giao diện HTML5/CSS3/Vanilla JS thuần, sử dụng engine vẽ đồ thị Canvas tự xây dựng (`static/chart.js`), không phụ thuộc CDN, hỗ trợ xuất hình ảnh PNG trực tiếp và tương thích mọi trình duyệt.

---

## 2. Phiên bản thư viện sử dụng

### Thư viện Python (`py -3.12`):
- `torch`: 2.15.0+cpu
- `fastapi`: 0.162.0
- `uvicorn`: 0.54.0
- `numpy`: 2.5.2
- `pandas`: 3.0.5
- `scikit-learn`: 1.9.1
- `vus`: 0.0.6
- `pytest`: 9.2.0

### Crate Rust (khai báo trong `Cargo.toml`):
- `axum`: 0.7.9
- `tokio`: 1.54.1
- `serde`: 1.0.229
- `serde_json`: 1.0.154
- `tower-http`: 0.5.2
- `csv`: 1.4.0
- `walkdir`: 2.5.0

---

## 3. Hướng dẫn khởi chạy Demo

### Khởi động Web Server
Chạy lệnh sau trong PowerShell hoặc Terminal:

```bash
cd redlamp_demo
python server.py
```

Server sẽ khởi chạy tại: **http://127.0.0.1:8000**
Truy cập địa chỉ trên bằng trình duyệt (Chrome, Edge, Firefox).

### Chạy bộ kiểm thử tự động (Unit Test / Nghiệm thu)
Chạy lệnh sau để kiểm tra toàn bộ tiêu chí nghiệm thu:

```bash
cd redlamp_demo
pytest tests/test_demo.py -v
```

---

## 4. Các tính năng chính trong Web Demo

### Tab 1 — `1. Tổng quan`
- Hỗ trợ chọn 5 tập dữ liệu: `smd` (38 đặc trưng), `iops` (1 đặc trưng), `msl` (55 đặc trưng), `smap` (25 đặc trưng), `anomaly_archive` (250 thực thể, 1 đặc trưng).
- Danh sách thả xuống 2 cấp (`Dataset -> Entity`, bao gồm mục `ALL` tổng hợp toàn tập) và bộ chọn `Seed (0 - 4)` cho các dataset đa seed.
- Hiển thị đầy đủ thông số kiến trúc mô hình ConvAEC và đường dẫn file checkpoint `bestmodel.pkl`.
- Hiển thị 3 ô chỉ số đánh giá: **VUS-ROC**, **VUS-PR**, **RF** (với dataset 5 seed hiển thị cả giá trị seed đang chọn và Trung bình ± Độ lệch chuẩn của cả 5 seed) cùng biểu đồ tổng quan toàn bộ chuỗi thời gian (hỗ trợ chọn từng đặc trưng `D1..Dn`).

### Tab 2 — `2. Giải thích mô hình` (Walkthrough 5 bước Explainable)
Thiết kế theo luồng trình chiếu 5 bước chuyển tiếp mượt mà, hỗ trợ bàn phím (mũi tên Trái/Phải), chế độ toàn màn hình và nút Tải PNG cho mọi biểu đồ:
1. **Bước 1 (~0,5 phút) - Đầu vào:** Chuỗi gốc và tô sáng cửa sổ 100 điểm đang khảo sát. Mặc định chọn cửa sổ có điểm bất thường cao nhất, có thanh trượt vị trí $t$ và nút xem cửa sổ bình thường đối chứng.
2. **Bước 2 (~1 phút) - Encoder -> Embedding:** Sơ đồ khối pipeline tensor thật (Window 100 $\rightarrow$ ConvBlock 0..3 $\rightarrow$ MaxPool1D $\rightarrow$ Conv1x1 $\rightarrow$ Embedding 128 chiều), biểu đồ cột véc-tơ Embedding, mục "Chi tiết kỹ thuật" hiển thị năng lượng kích hoạt các tầng tích chập.
3. **Bước 3 (~1 phút) - Decoder:** Chuỗi gốc chồng chuỗi tái tạo, hai biểu đồ đặt cạnh nhau (cửa sổ khảo sát vs cửa sổ bình thường) cùng thang đo, đánh dấu rõ giá trị MSE.
4. **Bước 4 (~1 phút) - Classifier:** Biểu đồ cột xác suất 12 lớp; các lớp bị loại (lớp bình thường và các lớp có tần suất trung bình chuỗi > 0,05) được tô màu xám nhạt kèm lý do; lớp có xác suất cao nhất được gắn nhãn và tô màu đỏ.
5. **Bước 5 (~1,5 phút) - Điểm kết hợp:** Đường theo thời gian gồm 3 đường (Điểm tái tạo, Điểm phân loại, Điểm kết hợp cuối cùng), đường ngưỡng nét đứt; thẻ công thức tính toán với số liệu thực tế: `Điểm cuối = (Điểm tái tạo + Điểm phân loại) / 2`.

### Tab 3 — `3. Thử nghiệm dự đoán` (Live Inference)
- Điểm mới cần ngữ cảnh: Người dùng chọn 1 trong 3 nguồn 99 điểm ngữ cảnh trước đó:
  1. 99 điểm cuối của chuỗi mẫu thực tế.
  2. Lặp lại giá trị trung vị của chuỗi.
  3. Tự dán / tải lên lịch sử 99 điểm.
- Nhập giá trị điểm mới (có nút hỗ trợ điền mẫu gợi ý theo phân phối thực tế).
- Thanh trượt chỉnh ngưỡng so sánh (mặc định lấy theo phân vị 99,5% của phân phối điểm thô các cửa sổ chuẩn).
- Kết quả trả về: Điểm tái tạo thô (MSE), Điểm phân loại thô, Điểm kết hợp thô, Huy hiệu kết luận **BẤT THƯỜNG** hoặc **BÌNH THƯỜNG**, Top-3 nhãn bất thường giả kèm xác suất %, bảng giải thích các lớp bị loại khỏi CE score, và nút đồng bộ trực tiếp về **Tab 2 (`2. Giải thích mô hình`)**.

---

## 5. Lưu ý & Tuyên bố miễn trừ trách nhiệm
- Toàn bộ 12 nhãn (normal, spike, flip, speedup, noise, cutoff, average, scale, wander, contextual, upsidedown, mixture) là các loại **bất thường giả lập** được sinh ra tự động trong quá trình huấn luyện tự giám sát của tác giả bài báo RedLamp.
- Nhãn phân loại chỉ mang tính chất tham khảo toán học và hỗ trợ định lượng độ lệch tín hiệu, không khẳng định bản chất vật lý hay nguyên nhân sự cố thực tế của hệ thống.

