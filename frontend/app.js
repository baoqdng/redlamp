// RedLamp Unsupervised Time Series Anomaly Detection Demo Client
let currentAnalysis = null;
let currentWindowDetail = null;
let currentLossData = null;
let activeModel = null;
let isDarkTheme = true;
let currentT = 0;
let uploadedCsvText = null;

const ANOMALY_CLASSES = [
  'normal', 'spike', 'flip', 'speedup', 'noise', 'cutoff',
  'average', 'scale', 'wander', 'contextual', 'upsidedown', 'mixture'
];

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initUpload();
  loadModels();
  loadSamples();
  loadAugmentations();
  bindEvents();
});

// THEME HANDLING
function initTheme() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  const themeText = document.getElementById('themeText');

  toggleBtn.addEventListener('click', () => {
    isDarkTheme = !isDarkTheme;
    document.body.className = isDarkTheme ? 'theme-dark' : 'theme-light';
    themeIcon.textContent = isDarkTheme ? '☀️' : '🌙';
    themeText.textContent = isDarkTheme ? 'Chế độ sáng' : 'Chế độ tối';
    // Re-render charts with new theme colors
    if (currentAnalysis) {
      renderAllCharts();
      updateSelectedWindow(currentT);
    }
  });
}

function getPlotlyTheme() {
  return {
    paper_bgcolor: isDarkTheme ? '#1e293b' : '#ffffff',
    plot_bgcolor: isDarkTheme ? '#1e293b' : '#ffffff',
    font: {
      color: isDarkTheme ? '#f8fafc' : '#0f172a',
      family: 'Inter, sans-serif'
    },
    gridcolor: isDarkTheme ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
    linecolor: isDarkTheme ? '#334155' : '#cbd5e1'
  };
}

// TABS NAVIGATION
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.getAttribute('data-tab'));
      if (target) target.classList.add('active');
    });
  });
}

// FILE UPLOAD
function initUpload() {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('csvFileInput');
  const browseLink = document.getElementById('browseLink');

  browseLink.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });
  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleCsvFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleCsvFile(fileInput.files[0]);
    }
  });
}

async function handleCsvFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const res = await fetch('/api/upload_csv', { method: 'POST', body: formData });
    const data = await res.json();
    uploadedCsvText = data.csv_text;
    document.getElementById('uploadFileName').textContent = data.filename;
    document.getElementById('uploadRowCount').textContent = data.total_rows;
    document.getElementById('uploadFileInfo').style.display = 'flex';
  } catch (err) {
    alert('Lỗi tải file CSV: ' + err.message);
  }
}

// API CALLS: MODELS & SAMPLES
async function loadModels() {
  const select = document.getElementById('modelSelect');
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    select.innerHTML = '';
    data.models.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m.model_id;
      opt.textContent = m.display_name;
      opt.dataset.features = m.n_features;
      opt.dataset.dataset = m.dataset;
      select.appendChild(opt);
    });

    // Default select stock 149
    const stock149 = data.models.find(m => m.model_id.includes('149_Stock'));
    if (stock149) {
      select.value = stock149.model_id;
    }
    updateModelInfo();
  } catch (err) {
    select.innerHTML = '<option value="">Lỗi tải danh sách model</option>';
  }
}

function updateModelInfo() {
  const select = document.getElementById('modelSelect');
  const infoText = document.getElementById('modelInfoText');
  const selectedOpt = select.options[select.selectedIndex];
  if (selectedOpt) {
    infoText.textContent = `Dataset: ${selectedOpt.dataset.dataset} | Số chiều input: ${selectedOpt.dataset.features} | W=100`;
  }
}

async function loadSamples() {
  const select = document.getElementById('sampleSelect');
  try {
    const res = await fetch('/api/sample_datasets');
    const data = await res.json();
    select.innerHTML = '';
    data.samples.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.filename;
      opt.textContent = `${s.filename} (tr=${s.n_train})`;
      opt.dataset.ntrain = s.n_train;
      select.appendChild(opt);
    });
    // Set n_train default from sample
    if (data.samples.length > 0) {
      document.getElementById('nTrainInput').value = data.samples[0].n_train;
    }
  } catch (err) {
    select.innerHTML = '<option value="">Lỗi tải dữ liệu mẫu</option>';
  }
}

async function loadAugmentations() {
  const grid = document.getElementById('augGrid');
  try {
    const res = await fetch('/api/augmentations');
    const data = await res.json();
    grid.innerHTML = '';

    for (const [key, item] of Object.entries(data.augmentations)) {
      const card = document.createElement('div');
      card.className = 'aug-card';
      const chartId = `aug_chart_${key}`;
      card.innerHTML = `
        <div class="aug-card-title">
          <span>${item.name}</span>
          <span class="aug-tag">${key}</span>
        </div>
        <div id="${chartId}" class="aug-chart-mini"></div>
        <p class="aug-card-desc">${item.desc}</p>
      `;
      grid.appendChild(card);

      // Render mini chart
      const trace = {
        y: item.series,
        type: 'scatter',
        mode: 'lines',
        line: { color: key === 'normal' ? '#10b981' : '#ef4444', width: 2 }
      };
      const layout = {
        margin: { l: 20, r: 10, t: 10, b: 20 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        xaxis: { showgrid: false, zeroline: false, showticklabels: false },
        yaxis: { showgrid: false, zeroline: false, showticklabels: false }
      };
      Plotly.newPlot(chartId, [trace], layout, { responsive: true, displayModeBar: false });
    }
  } catch (err) {
    grid.innerHTML = '<div class="loading-aug">Lỗi tải thư viện augmentation</div>';
  }
}

// EVENT BINDINGS
function bindEvents() {
  document.getElementById('modelSelect').addEventListener('change', updateModelInfo);

  document.getElementById('sampleSelect').addEventListener('change', (e) => {
    const selected = e.target.options[e.target.selectedIndex];
    if (selected && selected.dataset.ntrain) {
      document.getElementById('nTrainInput').value = selected.dataset.ntrain;
    }
  });

  // Threshold slider
  const threshSlider = document.getElementById('threshValSlider');
  const threshBadge = document.getElementById('threshValBadge');
  const threshType = document.getElementById('threshTypeSelect');

  threshType.addEventListener('change', () => {
    if (threshType.value === 'percentile') {
      threshSlider.min = 90.0;
      threshSlider.max = 99.9;
      threshSlider.step = 0.1;
      threshSlider.value = 99.5;
      threshBadge.textContent = '99.5%';
    } else {
      threshSlider.min = 1.0;
      threshSlider.max = 5.0;
      threshSlider.step = 0.1;
      threshSlider.value = 3.0;
      threshBadge.textContent = '3.0σ';
    }
  });

  threshSlider.addEventListener('input', () => {
    const unit = threshType.value === 'percentile' ? '%' : 'σ';
    threshBadge.textContent = threshSlider.value + unit;
  });

  // Run analysis buttons
  document.getElementById('runSampleBtn').addEventListener('click', () => runAnalysis(false));
  document.getElementById('runUploadBtn').addEventListener('click', () => runAnalysis(true));

  // Time slider
  const timeSlider = document.getElementById('timeSlider');
  timeSlider.addEventListener('input', (e) => {
    currentT = parseInt(e.target.value);
    updateSelectedWindow(currentT);
  });

  // PCA color mode
  document.getElementById('pcaColorMode').addEventListener('change', () => {
    if (currentAnalysis) renderPCAChart();
  });

  // 5-feature point prediction
  document.getElementById('predictPointBtn').addEventListener('click', runPointPrediction);
}

// RUN ANALYSIS
async function runAnalysis(useUploaded) {
  const modelId = document.getElementById('modelSelect').value;
  if (!modelId) {
    alert('Vui lòng chọn mô hình pre-trained!');
    return;
  }

  const spinner = document.getElementById('runSpinner');
  spinner.style.display = 'inline-block';

  const nTrain = parseInt(document.getElementById('nTrainInput').value) || 500;
  const threshType = document.getElementById('threshTypeSelect').value;
  const threshVal = parseFloat(document.getElementById('threshValSlider').value);

  const payload = {
    model_id: modelId,
    n_train: nTrain,
    threshold_type: threshType,
    threshold_val: threshVal,
    ce_threshold: 0.05,
    step: 1
  };

  if (useUploaded) {
    if (!uploadedCsvText) {
      alert('Vui lòng chọn hoặc kéo thả file CSV trước!');
      spinner.style.display = 'none';
      return;
    }
    payload.csv_text = uploadedCsvText;
  } else {
    payload.sample_name = document.getElementById('sampleSelect').value;
  }

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Lỗi server');
    }

    currentAnalysis = await res.json();
    renderConclusion();

    // Fetch loss data
    try {
      const lossRes = await fetch(`/api/model_loss/${encodeURIComponent(modelId)}`);
      currentLossData = await lossRes.json();
    } catch (_) {
      currentLossData = null;
    }

    // Set time slider max
    const maxWin = currentAnalysis.total_windows - 1;
    const timeSlider = document.getElementById('timeSlider');
    timeSlider.max = maxWin;
    timeSlider.value = 0;
    currentT = 0;

    // Show viz sections
    document.getElementById('conclusionSection').style.display = 'block';
    document.getElementById('vizContainer').style.display = 'block';

    // Render all 10 visual blocks
    renderAllCharts();
    updateSelectedWindow(0);

    // Scroll to conclusion
    document.getElementById('conclusionSection').scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert('Lỗi phân tích: ' + err.message);
  } finally {
    spinner.style.display = 'none';
  }
}

// RENDER CONCLUSION
function renderConclusion() {
  const d = currentAnalysis;
  const badge = document.getElementById('conclusionBadge');
  const verdictText = document.getElementById('verdictText');
  const confVal = document.getElementById('confVal');
  const flaggedCount = document.getElementById('flaggedCount');
  const flaggedPct = document.getElementById('flaggedPct');
  const regionsCount = document.getElementById('regionsCount');
  const nTrainExplain = document.getElementById('nTrainExplain');
  const threshActiveDesc = document.getElementById('threshActiveDesc');
  const top3List = document.getElementById('top3List');

  if (d.has_anomaly) {
    badge.className = 'status-badge status-anomaly';
    badge.textContent = 'Phát Hiện Bất Thường';
    verdictText.textContent = 'CÓ BẤT THƯỜNG';
    verdictText.style.color = 'var(--accent-red)';
  } else {
    badge.className = 'status-badge status-normal';
    badge.textContent = 'Bình Thường';
    verdictText.textContent = 'KHÔNG CÓ BẤT THƯỜNG';
    verdictText.style.color = 'var(--accent-green)';
  }

  confVal.textContent = d.confidence;
  flaggedCount.textContent = (d.display.flagged_windows.filter(Boolean).length);
  flaggedPct.textContent = `${d.flagged_pct}%`;
  regionsCount.textContent = d.flagged_regions.length;
  nTrainExplain.textContent = d.n_train;
  threshActiveDesc.textContent = d.threshold_desc;

  // Render Top-3 non-normal predicted classes
  if (d.overall_top3 && d.overall_top3.length > 0) {
    top3List.innerHTML = '';
    d.overall_top3.forEach(item => {
      const pct = (item.prob * 100).toFixed(1);
      const row = document.createElement('div');
      row.className = 'top3-item';
      row.innerHTML = `
        <div class="top3-label-row">
          <span>${item.class_name}</span>
          <span>${pct}%</span>
        </div>
        <div class="top3-progress-bg">
          <div class="top3-progress-fill" style="width: ${pct}%"></div>
        </div>
      `;
      top3List.appendChild(row);
    });
  } else {
    top3List.innerHTML = '<span class="empty-hint">Không có bất thường nào được gắn cờ.</span>';
  }

  // Update excluded classes badge
  document.getElementById('excludedClassesBadge').textContent = d.indices_excluded_names.join(', ');
}

// RENDER ALL CHARTS (10 Blocks)
function renderAllCharts() {
  renderSeriesChart();         // Block 1 & 2
  renderPCAChart();            // Block 3
  renderMSEScoreChart();       // Block 5
  renderHeatmapChart();        // Block 6 (part A)
  renderCEScoreChart();        // Block 7
  renderFinalScoreChart();     // Block 8
  renderLossCurvesChart();     // Block 10
}

// BLOCK 1: Raw & MinMax Normalized Series
function renderSeriesChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;

  const traceRaw = {
    x: d.display.disp_time,
    y: d.display.disp_series_raw,
    name: 'Chuỗi gốc (Raw)',
    line: { color: '#64748b', width: 1.2 },
    yaxis: 'y1'
  };

  const traceNorm = {
    x: d.display.disp_time,
    y: d.display.disp_series_norm,
    name: 'Sau chuẩn hóa MinMax (Fit tr)',
    line: { color: '#3b82f6', width: 1.5 },
    yaxis: 'y2'
  };

  const layout = {
    ...p,
    title: { text: 'Chuỗi Tín Hiệu Gốc vs Chuẩn Hóa Min-Max (Xanh: Đoạn tham chiếu n_train)' },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { gridcolor: p.gridcolor, linecolor: p.linecolor },
    yaxis: { title: 'Giá trị gốc', gridcolor: p.gridcolor, linecolor: p.linecolor },
    yaxis2: { title: 'Chuẩn hóa MinMax', overlaying: 'y', side: 'right', gridcolor: p.gridcolor },
    shapes: [{
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: 0,
      x1: d.n_train,
      y0: 0,
      y1: 1,
      fillcolor: 'rgba(16, 185, 129, 0.15)',
      line: { width: 1, color: '#10b981', dash: 'dash' }
    }],
    annotations: [{
      x: d.n_train / 2,
      y: 0.95,
      yref: 'paper',
      text: `Đoạn tham chiếu chuẩn hóa (tr=${d.n_train})`,
      showarrow: false,
      font: { color: '#10b981', size: 11 }
    }],
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartSeries', [traceRaw, traceNorm], layout, { responsive: true });
}

// BLOCK 2: Sliding Window Visualizer
function renderSlidingWindowChart(windowIdx) {
  const p = getPlotlyTheme();
  const d = currentAnalysis;
  const W = d.W;
  const startT = windowIdx;
  const endT = windowIdx + W;

  const traceNorm = {
    x: d.display.disp_time,
    y: d.display.disp_series_norm,
    name: 'Chuỗi chuẩn hóa',
    line: { color: '#3b82f6', width: 1.5 }
  };

  const layout = {
    ...p,
    title: { text: `Vùng Cửa Sổ Trượt [t - W + 1, t] = [${startT}, ${endT - 1}] trên toàn chuỗi` },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { gridcolor: p.gridcolor, linecolor: p.linecolor },
    yaxis: { title: 'MinMax Giá Trị', gridcolor: p.gridcolor, linecolor: p.linecolor },
    shapes: [{
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: startT,
      x1: endT,
      y0: 0,
      y1: 1,
      fillcolor: 'rgba(245, 158, 11, 0.35)',
      line: { width: 2, color: '#f59e0b' }
    }],
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartSlidingWindow', [traceNorm], layout, { responsive: true });
}

// BLOCK 3: PCA 2D Latent Space Projection
function renderPCAChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;
  const mode = document.getElementById('pcaColorMode').value;

  let markerColors = [];
  let colorTitle = '';

  if (mode === 'score') {
    markerColors = d.display.anomaly_score;
    colorTitle = 'Score';
  } else if (mode === 'flagged') {
    markerColors = d.display.flagged_windows.map(f => f ? '#ef4444' : '#10b981');
    colorTitle = 'Flagged';
  } else {
    markerColors = (d.display.disp_labels && d.display.disp_labels.length > 0)
      ? d.display.disp_labels.map(l => l > 0 ? '#ef4444' : '#3b82f6')
      : d.display.anomaly_score;
    colorTitle = 'Label';
  }

  const tracePoints = {
    x: d.display.pca_x,
    y: d.display.pca_y,
    mode: 'markers',
    type: 'scatter',
    name: 'Cửa sổ trượt',
    marker: {
      size: 5,
      color: markerColors,
      colorscale: mode === 'score' ? 'Viridis' : undefined,
      colorbar: mode === 'score' ? { title: colorTitle, len: 0.8 } : undefined,
      opacity: 0.75
    }
  };

  // Find nearest PCA index to currentT
  const currentPcaIdx = Math.min(
    Math.floor(currentT / Math.max(1, Math.floor(d.total_windows / d.display.pca_x.length))),
    d.display.pca_x.length - 1
  );

  const traceActive = {
    x: [d.display.pca_x[currentPcaIdx]],
    y: [d.display.pca_y[currentPcaIdx]],
    mode: 'markers',
    type: 'scatter',
    name: `Cửa sổ đang chọn (t=${currentT})`,
    marker: {
      size: 14,
      symbol: 'star',
      color: '#ef4444',
      line: { color: '#ffffff', width: 2 }
    }
  };

  const layout = {
    ...p,
    title: { text: 'Chiếu 2D PCA của Latent Vector 128D (pred_enc)' },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Principal Component 1', gridcolor: p.gridcolor, linecolor: p.linecolor },
    yaxis: { title: 'Principal Component 2', gridcolor: p.gridcolor, linecolor: p.linecolor },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartPCA', [tracePoints, traceActive], layout, { responsive: true });
}

// BLOCK 4 & 6B: Window Details (Input vs Pred & Probabilities Bar Chart)
async function updateSelectedWindow(windowIdx) {
  if (!currentAnalysis) return;

  const W = currentAnalysis.W;
  document.getElementById('currentTBadge').textContent = windowIdx;
  document.getElementById('winRangeBadge').textContent = `${windowIdx} - ${windowIdx + W - 1}`;

  renderSlidingWindowChart(windowIdx);

  try {
    const res = await fetch(`/api/window_detail?window_idx=${windowIdx}`);
    const detail = await res.json();
    currentWindowDetail = detail;

    // Render Block 4
    renderReconstructionChart(detail);
    // Render Block 6B (Bar chart for window)
    renderWindowProbsBarChart(detail);
  } catch (err) {
    console.error('Lỗi tải chi tiết cửa sổ:', err);
  }
}

function renderReconstructionChart(detail) {
  const p = getPlotlyTheme();
  const timeSteps = Array.from({ length: detail.input_norm.length }, (_, i) => i);

  const traceIn = {
    x: timeSteps,
    y: detail.input_norm,
    name: 'Input x (Thực tế)',
    line: { color: '#3b82f6', width: 2 }
  };

  const tracePred = {
    x: timeSteps,
    y: detail.pred_norm,
    name: 'Predicted x̂ (Tái tạo)',
    line: { color: '#10b981', width: 2, dash: 'dot' }
  };

  const traceErr = {
    x: timeSteps,
    y: detail.squared_error,
    name: 'Sai số bình phương (x - x̂)²',
    type: 'bar',
    yaxis: 'y2',
    marker: { color: 'rgba(239, 68, 68, 0.4)' }
  };

  const layout = {
    ...p,
    title: { text: `Tái Tạo Cửa Sổ [${detail.time_start} - ${detail.time_end}] & Sai Số Điểm` },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Vị trí trong cửa sổ (0 &rarr; 99)', gridcolor: p.gridcolor },
    yaxis: { title: 'Tín hiệu chuẩn hóa', gridcolor: p.gridcolor },
    yaxis2: { title: 'Squared Error', overlaying: 'y', side: 'right', gridcolor: p.gridcolor },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartReconstruction', [traceIn, tracePred, traceErr], layout, { responsive: true });
}

// BLOCK 5: Reconstruction MSE Score Curves
function renderMSEScoreChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;
  const x = d.display.disp_window_t;

  const traceRaw = {
    x: x,
    y: d.display.raw_mse,
    name: '1. MSE thô (Raw MSE)',
    line: { color: '#94a3b8', width: 1, dash: 'dot' }
  };

  const traceConv = {
    x: x,
    y: d.display.mse_conv,
    name: '2. Làm mịn trượt w=50 (Conv)',
    line: { color: '#f59e0b', width: 1.8 }
  };

  const traceMinMax = {
    x: x,
    y: d.display.mse_minmax,
    name: '3. Min-Max [0, 1] (mse_score)',
    line: { color: '#ef4444', width: 2 }
  };

  const layout = {
    ...p,
    title: { text: 'Quá Trình Tính MSE Score: Raw &rarr; Smooth (w=W/2) &rarr; Min-Max' },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Thời gian kết thúc cửa sổ (t)', gridcolor: p.gridcolor },
    yaxis: { title: 'Điểm tái tạo', gridcolor: p.gridcolor },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartMSEScores', [traceRaw, traceConv, traceMinMax], layout, { responsive: true });
}

// BLOCK 6A: Classification Heatmap
function renderHeatmapChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;

  // matrix shape: (12, N_samples)
  const z = [];
  for (let c = 0; c < 12; c++) {
    z.push(d.display.pred_label_sampled.map(row => row[c]));
  }

  const trace = {
    z: z,
    x: d.display.disp_window_t,
    y: ANOMALY_CLASSES,
    type: 'heatmap',
    colorscale: 'Reds',
    colorbar: { title: 'P(class)', len: 0.8 }
  };

  const layout = {
    ...p,
    title: { text: 'Heatmap Xác Suất 12 Lớp Bất Thường Giả Trên Toàn Chuỗi' },
    margin: { l: 100, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Thời gian (t)', gridcolor: p.gridcolor },
    yaxis: { autorange: 'reversed' }
  };

  Plotly.react('chartHeatmap', [trace], layout, { responsive: true });
}

// BLOCK 6B: 12-Class Probabilities Bar Chart for Current Window
function renderWindowProbsBarChart(detail) {
  const p = getPlotlyTheme();
  const probs = detail.pred_label;

  const colors = ANOMALY_CLASSES.map((cls, idx) => {
    if (idx === 0) return '#10b981'; // normal
    return currentAnalysis.indices_excluded.includes(idx) ? '#94a3b8' : '#ef4444';
  });

  const trace = {
    x: probs,
    y: ANOMALY_CLASSES,
    type: 'bar',
    orientation: 'h',
    marker: { color: colors }
  };

  const layout = {
    ...p,
    title: { text: `Phân Phối Xác Suất Cửa Sổ t=${currentT}` },
    margin: { l: 90, r: 30, t: 40, b: 40 },
    xaxis: { title: 'Xác suất P', range: [0, 1], gridcolor: p.gridcolor },
    yaxis: { autorange: 'reversed' }
  };

  Plotly.react('chartWindowProbs', [trace], layout, { responsive: true });
}

// BLOCK 7: Classification CE Score Curves
function renderCEScoreChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;
  const x = d.display.disp_window_t;

  const traceRaw = {
    x: x,
    y: d.display.raw_ce,
    name: '1. CE thô (tổng p các lớp ∉ indices)',
    line: { color: '#94a3b8', width: 1, dash: 'dot' }
  };

  const traceConv = {
    x: x,
    y: d.display.ce_conv,
    name: '2. Làm mịn trượt w=50 (Conv)',
    line: { color: '#f59e0b', width: 1.8 }
  };

  const traceMinMax = {
    x: x,
    y: d.display.ce_minmax,
    name: '3. Min-Max [0, 1] (ce_score)',
    line: { color: '#ef4444', width: 2 }
  };

  const layout = {
    ...p,
    title: { text: 'Quá Trình Tính CE Score: Loại Trừ Indices &rarr; Smooth &rarr; Min-Max' },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Thời gian kết thúc cửa sổ (t)', gridcolor: p.gridcolor },
    yaxis: { title: 'Điểm phân loại (CE)', gridcolor: p.gridcolor },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartCEScores', [traceRaw, traceConv, traceMinMax], layout, { responsive: true });
}

// BLOCK 8: Final RedLamp Score, Threshold & Detected Regions
function renderFinalScoreChart() {
  const p = getPlotlyTheme();
  const d = currentAnalysis;
  const x = d.display.disp_window_t;

  const traces = [];

  // 1. RedLamp Final Score
  traces.push({
    x: x,
    y: d.display.anomaly_score,
    name: 'Điểm RedLamp (mse + ce)/2',
    line: { color: '#ef4444', width: 2 }
  });

  // 2. Raw Z-score Combined Score (detection score)
  traces.push({
    x: x,
    y: d.display.raw_combined_score,
    name: 'Điểm thô z-score (so sánh tham chiếu)',
    line: { color: '#3b82f6', width: 1.5, dash: 'dot' },
    yaxis: 'y2'
  });

  // Shapes for Flagged Regions and Ground Truth
  const shapes = [];

  // Flagged Regions (Red shading)
  d.flagged_regions.forEach(reg => {
    shapes.push({
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: reg.time_start,
      x1: reg.time_end,
      y0: 0,
      y1: 1,
      fillcolor: 'rgba(239, 68, 68, 0.25)',
      line: { width: 1.5, color: '#ef4444' }
    });
  });

  // Ground Truth Labels if present (Orange outline)
  if (d.display.disp_labels && d.display.disp_labels.some(l => l > 0)) {
    // Find contiguous label 1 segments
    let inGt = false;
    let gtStart = 0;
    d.display.disp_time.forEach((t, i) => {
      const isAnom = d.display.disp_labels[i] > 0;
      if (isAnom && !inGt) {
        inGt = true;
        gtStart = t;
      } else if (!isAnom && inGt) {
        inGt = false;
        shapes.push({
          type: 'rect',
          xref: 'x',
          yref: 'paper',
          x0: gtStart,
          x1: t,
          y0: 0,
          y1: 1,
          fillcolor: 'rgba(245, 158, 11, 0.2)',
          line: { width: 1, color: '#f59e0b', dash: 'dot' }
        });
      }
    });
    if (inGt) {
      shapes.push({
        type: 'rect',
        xref: 'x',
        yref: 'paper',
        x0: gtStart,
        x1: d.display.disp_time[d.display.disp_time.length - 1],
        y0: 0,
        y1: 1,
        fillcolor: 'rgba(245, 158, 11, 0.2)',
        line: { width: 1, color: '#f59e0b', dash: 'dot' }
      });
    }
  }

  // Threshold horizontal line on yaxis2
  shapes.push({
    type: 'line',
    xref: 'paper',
    yref: 'y2',
    x0: 0,
    x1: 1,
    y0: d.threshold,
    y1: d.threshold,
    line: { color: '#3b82f6', width: 2, dash: 'dash' }
  });

  const layout = {
    ...p,
    title: { text: `Điểm Tổng Hợp RedLamp vs Ngưỡng Tham Chiếu (Vùng đỏ: Bị gắn cờ | Vàng: Ground Truth)` },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Thời gian (t)', gridcolor: p.gridcolor },
    yaxis: { title: 'Điểm RedLamp (Min-Max)', range: [0, 1.05], gridcolor: p.gridcolor },
    yaxis2: { title: 'Z-score thô', overlaying: 'y', side: 'right', gridcolor: p.gridcolor },
    shapes: shapes,
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.react('chartFinalScore', traces, layout, { responsive: true });
}

// BLOCK 10: Training & Validation Loss Curves
function renderLossCurvesChart() {
  const p = getPlotlyTheme();
  if (!currentLossData || !currentLossData.loss || !currentLossData.loss.train_loss || currentLossData.loss.train_loss.length === 0) {
    document.getElementById('chartLossCurves').innerHTML = '<div style="padding:2rem;text-align:center;color:var(--text-muted)">Mô hình này không có file *_loss.txt kèm theo.</div>';
    return;
  }

  const loss = currentLossData.loss;
  const epochs = Array.from({ length: loss.train_loss.length }, (_, i) => i + 1);

  const traces = [
    { x: epochs, y: loss.train_loss, name: 'Train Total Loss', line: { color: '#3b82f6', width: 2 } },
    { x: epochs, y: loss.valid_loss, name: 'Valid Total Loss', line: { color: '#3b82f6', width: 2, dash: 'dot' } },
    { x: epochs, y: loss.train_loss_ae, name: 'Train AE Loss (MSE)', line: { color: '#10b981', width: 1.5 } },
    { x: epochs, y: loss.valid_loss_ae, name: 'Valid AE Loss (MSE)', line: { color: '#10b981', width: 1.5, dash: 'dot' } },
    { x: epochs, y: loss.train_loss_c, name: 'Train C Loss (CE)', line: { color: '#ef4444', width: 1.5 } },
    { x: epochs, y: loss.valid_loss_c, name: 'Valid C Loss (CE)', line: { color: '#ef4444', width: 1.5, dash: 'dot' } },
  ];

  const layout = {
    ...p,
    title: { text: `Lịch Sử Huấn Luyện (Loss) Qua ${epochs.length} Epochs` },
    margin: { l: 50, r: 50, t: 40, b: 40 },
    xaxis: { title: 'Epoch', gridcolor: p.gridcolor },
    yaxis: { title: 'Loss', type: 'log', gridcolor: p.gridcolor },
    legend: { orientation: 'h', y: 1.18 }
  };

  Plotly.react('chartLossCurves', traces, layout, { responsive: true });
}

// 5-FEATURE INTERACTIVE PREDICTION
async function runPointPrediction() {
  const modelId = document.getElementById('modelSelect').value;
  if (!modelId) {
    alert('Vui lòng chọn model trước!');
    return;
  }

  const inputs = document.querySelectorAll('.feat-input');
  const values = Array.from(inputs).map(inp => parseFloat(inp.value) || 0.0);

  try {
    const res = await fetch('/api/predict_point', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, feature_values: values })
    });
    const data = await res.json();
    const box = document.getElementById('pointResultBox');
    box.style.display = 'flex';
    document.getElementById('pointTop1').textContent = `${data.top1.name} (${(data.top1.prob * 100).toFixed(1)}%)`;

    const top3Str = data.top3.map(c => `${c.name}: ${(c.prob * 100).toFixed(1)}%`).join(' | ');
    document.getElementById('pointTop3').textContent = `[ ${top3Str} ]`;
  } catch (err) {
    alert('Lỗi dự đoán: ' + err.message);
  }
}

