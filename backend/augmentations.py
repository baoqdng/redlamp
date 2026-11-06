import numpy as np

def generate_augmentation_samples(seed=42):
    """
    Generates representative 100-step time series windows for each of the 12 synthetic
    anomaly types used in RedLamp self-supervised training, along with Vietnamese descriptions.
    """
    np.random.seed(seed)
    W = 100
    t = np.linspace(0, 4 * np.pi, W)
    base_normal = np.sin(t) * 0.4 + np.sin(2.5 * t) * 0.2 + 0.5 # smooth periodic signal in [0, 1]

    samples = {}

    # 0. Normal
    samples["normal"] = {
        "name": "Normal (Chuỗi bình thường)",
        "desc": "Tín hiệu gốc không bị chèn bất thường giả; làm cơ sở đối chuẩn.",
        "series": base_normal.tolist(),
        "anomaly_mask": [1] * W
    }

    # 1. Spike
    spike_s = base_normal.copy()
    mask_s = [1] * W
    spike_pos = [35, 70]
    for p in spike_pos:
        spike_s[p] += 0.8 * (1 if np.random.rand() > 0.5 else -1)
        mask_s[p] = 0
    samples["spike"] = {
        "name": "Spike (Gai nhọn / Đột biến tức thời)",
        "desc": "Thêm xung biên độ lớn tại một hoặc nhiều điểm thời gian ngẫu nhiên.",
        "series": spike_s.tolist(),
        "anomaly_mask": mask_s
    }

    # 2. Flip
    flip_s = base_normal.copy()
    mask_fl = [1] * W
    flip_s[40:70] = flip_s[40:70][::-1]
    for i in range(40, 70): mask_fl[i] = 0
    samples["flip"] = {
        "name": "Flip (Đảo ngược thời gian)",
        "desc": "Đảo ngược trật tự thời gian [::-1] của một phân đoạn, phá vỡ động học chuỗi.",
        "series": flip_s.tolist(),
        "anomaly_mask": mask_fl
    }

    # 3. Speedup
    sp_s = base_normal.copy()
    mask_sp = [1] * W
    t_seg = np.linspace(0, 1, 30)
    sp_s[35:65] = 0.5 + 0.5 * np.sin(t_seg * 12 * np.pi)
    for i in range(35, 65): mask_sp[i] = 0
    samples["speedup"] = {
        "name": "Speedup (Nén / Giãn tần số)",
        "desc": "Nội suy co giãn tần số theo thời gian, làm chuỗi dao động nhanh hoặc chậm hơn bình thường.",
        "series": sp_s.tolist(),
        "anomaly_mask": mask_sp
    }

    # 4. Noise
    noise_s = base_normal.copy()
    mask_n = [1] * W
    noise_s[30:70] += np.random.normal(0, 0.25, 40)
    for i in range(30, 70): mask_n[i] = 0
    samples["noise"] = {
        "name": "Noise (Nhiễu Gauss bổ sung)",
        "desc": "Cộng thêm nhiễu ngẫu nhiên phân phối chuẩn N(0, σ²) vào một đoạn tín hiệu.",
        "series": noise_s.tolist(),
        "anomaly_mask": mask_n
    }

    # 5. Cutoff
    cut_s = base_normal.copy()
    mask_cut = [1] * W
    val = float(cut_s[40])
    cut_s[40:75] = val
    for i in range(40, 75): mask_cut[i] = 0
    samples["cutoff"] = {
        "name": "Cutoff (Mất tín hiệu / Treo giá trị)",
        "desc": "Tín hiệu bị gán cố định bằng một hằng số trong suốt một đoạn thời gian (sensor freeze).",
        "series": cut_s.tolist(),
        "anomaly_mask": mask_cut
    }

    # 6. Average
    avg_s = base_normal.copy()
    mask_avg = [1] * W
    w_ma = 15
    for i in range(35, 75):
        avg_s[i] = np.mean(base_normal[max(0, i - w_ma):min(W, i + w_ma)])
        mask_avg[i] = 0
    samples["average"] = {
        "name": "Average (Làm mịn trượt quá mức)",
        "desc": "Thay thế phân đoạn bằng trung bình trượt, triệt tiêu mọi dao động tần số cao.",
        "series": avg_s.tolist(),
        "anomaly_mask": mask_avg
    }

    # 7. Scale
    sc_s = base_normal.copy()
    mask_sc = [1] * W
    sc_s[35:70] *= 2.2
    for i in range(35, 70): mask_sc[i] = 0
    samples["scale"] = {
        "name": "Scale (Phóng đại biên độ)",
        "desc": "Nhân phân đoạn tín hiệu với một hệ số khuếch đại (co hoặc giãn độ lớn biên độ).",
        "series": sc_s.tolist(),
        "anomaly_mask": mask_sc
    }

    # 8. Wander
    wan_s = base_normal.copy()
    mask_wan = [1] * W
    drift = np.linspace(0, 0.8, 35)
    wan_s[35:70] += drift
    wan_s[70:] += 0.8
    for i in range(35, W): mask_wan[i] = 0
    samples["wander"] = {
        "name": "Wander (Trôi dạt xu hướng)",
        "desc": "Tạo đường trôi baseline tuyến tính hoặc bước đi ngẫu nhiên kéo tín hiệu lệch khỏi quỹ đạo chuẩn.",
        "series": wan_s.tolist(),
        "anomaly_mask": mask_wan
    }

    # 9. Contextual
    ctx_s = base_normal.copy()
    mask_ctx = [1] * W
    ctx_s[40:70] = ctx_s[40:70] + 0.6
    for i in range(40, 70): mask_ctx[i] = 0
    samples["contextual"] = {
        "name": "Contextual (Lệch ngữ cảnh / Dịch mức)",
        "desc": "Tín hiệu giữ nguyên hình dạng cục bộ nhưng bị dịch chuyển mức trung bình sang một vùng giá trị khác.",
        "series": ctx_s.tolist(),
        "anomaly_mask": mask_ctx
    }

    # 10. Upsidedown
    up_s = base_normal.copy()
    mask_up = [1] * W
    mean_seg = np.mean(up_s[35:70])
    up_s[35:70] = -(up_s[35:70] - mean_seg) + mean_seg
    for i in range(35, 70): mask_up[i] = 0
    samples["upsidedown"] = {
        "name": "Upsidedown (Đảo ngược cực tính)",
        "desc": "Lật ngược hình dạng tín hiệu qua đường trục trung bình cục bộ: -(y - mean) + mean.",
        "series": up_s.tolist(),
        "anomaly_mask": mask_up
    }

    # 11. Mixture
    mix_s = base_normal.copy()
    mask_mix = [1] * W
    mix_s[30:50] = mix_s[30:50][::-1] * 1.5
    mix_s[50:75] += np.random.normal(0, 0.2, 25) + 0.3
    for i in range(30, 75): mask_mix[i] = 0
    samples["mixture"] = {
        "name": "Mixture (Tổ hợp đa bất thường)",
        "desc": "Kết hợp đồng thời nhiều dạng biến dạng (như đảo chiều + phóng đại + nhiễu cộng dồn).",
        "series": mix_s.tolist(),
        "anomaly_mask": mask_mix
    }

    return samples

