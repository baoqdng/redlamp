// RedLamp Web Demo - Frontend Controller
document.addEventListener('DOMContentLoaded', () => {
  // App State
  let indexData = {};
  let currentDataset = 'smd';
  let currentEntity = '';
  let currentSeed = 0;
  let currentEntityMeta = null;
  let currentEntityDetail = null;
  let explainData = null;
  let currentStep = 0; // 0..4
  let seriesOverviewData = null;
  let currentOverviewFeature = '0';
  let currentOverviewMetric = 'vus_pr';
  let lastPredictedWindow = null;
  let lastPredictedPoint = null;
  let lastPredictedResult = null;
  let isCustomPointExplain = false;
  let isDecoderMaskEnabled = false;

  // Charts
  let chartOverview = null;
  let chartPredict = null;
  let chartSlide1 = null;
  let chartSlide2 = null;
  let chartSlide3Target = null;
  let chartSlide3Normal = null;
  let chartSlide4Target = null;
  let chartSlide4Normal = null;
  let chartSlide5 = null;

  function initCharts() {
    chartOverview = new SimpleCanvasChart('canvas-overview');
    chartPredict = new SimpleCanvasChart('canvas-predict-window');
    chartSlide1 = new SimpleCanvasChart('canvas-slide-1');
    chartSlide2 = new SimpleCanvasChart('canvas-slide-2');
    chartSlide3Target = new SimpleCanvasChart('canvas-slide-3-target');
    chartSlide3Normal = new SimpleCanvasChart('canvas-slide-3-normal');
    chartSlide4Target = new SimpleCanvasChart('canvas-slide-4-target');
    chartSlide4Normal = new SimpleCanvasChart('canvas-slide-4-normal');
    chartSlide5 = new SimpleCanvasChart('canvas-slide-5');
  }

  // Loading Indicator Helpers
  let loadingCount = 0;
  function showLoading(title = 'Đang xử lý dữ liệu...', subtitle = 'Hệ thống đang nạp mô hình và tính toán, vui lòng chờ trong giây lát') {
    loadingCount++;
    const overlay = document.getElementById('app-loading-overlay');
    const titleEl = document.getElementById('loading-title');
    const subEl = document.getElementById('loading-subtitle');
    if (titleEl) titleEl.textContent = title;
    if (subEl) subEl.textContent = subtitle;
    if (overlay) overlay.style.display = 'flex';
  }

  function hideLoading() {
    loadingCount = Math.max(0, loadingCount - 1);
    if (loadingCount === 0) {
      const overlay = document.getElementById('app-loading-overlay');
      if (overlay) overlay.style.display = 'none';
    }
  }

  // API Call Helpers
  async function fetchJSON(url, options = {}) {
    try {
      const resp = await fetch(url, options);
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(err.detail || 'Lỗi kết nối máy chủ');
      }
      return await resp.json();
    } catch (e) {
      console.error('Fetch error:', e);
      throw e;
    }
  }

  // 1. Initial Load: /api/index
  async function loadIndex() {
    showLoading('Đang khởi tạo danh mục Dataset...', 'Đang đọc chỉ số đánh giá của 5 bộ dữ liệu chuẩn');
    try {
      indexData = await fetchJSON('/api/index');
      setupDatasetDropdown();
      // Select default dataset
      if (indexData['smd']) {
        currentDataset = 'smd';
      } else {
        currentDataset = Object.keys(indexData)[0];
      }
      const selDs = document.getElementById('select-dataset');
      if (selDs) selDs.value = currentDataset;
      await updateEntityDropdown();
    } catch (e) {
      alert('Không thể nạp danh mục dataset: ' + e.message);
    } finally {
      hideLoading();
    }
  }

  function closeEntityPicker() {
    const btn = document.getElementById('btn-entity-picker');
    const pop = document.getElementById('popover-entity-picker');
    if (btn) btn.classList.remove('open');
    if (pop) pop.style.display = 'none';
  }

  function syncEntityPickerDisplay() {
    const lbl = document.getElementById('lbl-entity-picker');
    const btnAll = document.getElementById('btn-entity-pick-all');
    const grid = document.getElementById('grid-entity-picker');
    const ents = getEntitiesWithAll(currentDataset);
    const curObj = ents.find(e => e.entity === currentEntity);

    if (lbl) {
      if (currentEntity === 'ALL') {
        lbl.textContent = 'ALL';
      } else if (curObj && !curObj.has_model) {
        lbl.textContent = `${currentEntity} (chỉ có số liệu)`;
      } else {
        lbl.textContent = currentEntity || 'ALL';
      }
    }
    if (btnAll) {
      btnAll.classList.toggle('active', currentEntity === 'ALL');
    }
    if (grid) {
      grid.querySelectorAll('[data-ent]').forEach(el => {
        el.classList.toggle('active', el.dataset.ent === currentEntity);
      });
    }
  }

  function renderEntityPickerGrid(filterQuery = '') {
    const grid = document.getElementById('grid-entity-picker');
    const countLbl = document.getElementById('lbl-entity-picker-count');
    if (!grid) return;

    const realEnts = getEntitiesWithAll(currentDataset).filter(e => e.entity !== 'ALL');
    const q = filterQuery.toLowerCase().trim();
    const filtered = q
      ? realEnts.filter(e => e.entity.toLowerCase().includes(q))
      : realEnts;

    const colClass = currentDataset === 'iops'
      ? 'cols-2'
      : (currentDataset === 'smd' ? 'cols-3' : 'cols-5');
    grid.className = `ep-chip-grid ${colClass}`;

    if (countLbl) {
      countLbl.textContent = q
        ? `Kết quả lọc: ${filtered.length} / ${realEnts.length} thực thể`
        : `Chọn thực thể cụ thể (${realEnts.length} thực thể)`;
    }

    if (filtered.length === 0) {
      grid.innerHTML = '<div class="ep-empty">Không tìm thấy thực thể phù hợp</div>';
      return;
    }

    let html = '';
    filtered.forEach(e => {
      const isAct = e.entity === currentEntity;
      const chipText = e.entity.startsWith('KPI-') ? `${e.entity.slice(0, 14)}…` : e.entity;
      const tipText = e.has_model ? e.entity : `${e.entity} (chỉ có chỉ số kiểm nghiệm)`;
      html += `<button type="button" class="ep-chip ${isAct ? 'active' : ''} ${!e.has_model ? 'metrics-only' : ''}" data-ent="${e.entity}" title="${tipText}">${chipText}</button>`;
    });
    grid.innerHTML = html;

    grid.querySelectorAll('[data-ent]').forEach(el => {
      el.addEventListener('click', (ev) => {
        ev.stopPropagation();
        const chosen = el.dataset.ent;
        closeEntityPicker();
        selectSpecificEntity(chosen);
      });
    });
  }

  function positionEntityPickerPopover(btn, pop) {
    const bRect = btn.getBoundingClientRect();
    pop.style.width = `${Math.round(Math.max(bRect.width, 350))}px`;
    const pRect = pop.getBoundingClientRect();
    let left = bRect.left;
    if (left + pRect.width > window.innerWidth - 10) {
      left = window.innerWidth - pRect.width - 10;
    }
    if (left < 10) left = 10;
    let top = bRect.bottom + 6;
    if (top + pRect.height > window.innerHeight - 10) {
      top = Math.max(10, bRect.top - pRect.height - 6);
    }
    pop.style.left = `${Math.round(left)}px`;
    pop.style.top = `${Math.round(top)}px`;
  }

  function setupDatasetDropdown() {
    const sel = document.getElementById('select-dataset');
    if (sel) {
      sel.addEventListener('change', (e) => {
        closeEntityPicker();
        currentDataset = e.target.value;
        updateEntityDropdown();
      });
    }

    const entSel = document.getElementById('select-entity');
    if (entSel) {
      entSel.addEventListener('change', (e) => {
        currentEntity = e.target.value;
        syncEntityPickerDisplay();
        onEntityChanged();
      });
    }

    const btnEnt = document.getElementById('btn-entity-picker');
    const popEnt = document.getElementById('popover-entity-picker');
    const wrapEnt = document.getElementById('wrap-entity-picker');
    const searchInp = document.getElementById('input-entity-picker-search');
    const btnAll = document.getElementById('btn-entity-pick-all');

    if (btnEnt && popEnt) {
      btnEnt.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = popEnt.style.display !== 'none';
        if (isOpen) {
          closeEntityPicker();
        } else {
          closeFeaturePicker();
          if (searchInp) searchInp.value = '';
          renderEntityPickerGrid('');
          syncEntityPickerDisplay();
          popEnt.style.display = 'block';
          btnEnt.classList.add('open');
          positionEntityPickerPopover(btnEnt, popEnt);
          if (searchInp) searchInp.focus();
          const actEl = popEnt.querySelector('.ep-chip.active');
          if (actEl) actEl.scrollIntoView({ block: 'nearest' });
        }
      });
    }

    if (searchInp) {
      searchInp.addEventListener('click', (e) => e.stopPropagation());
      searchInp.addEventListener('input', (e) => {
        renderEntityPickerGrid(e.target.value);
      });
      searchInp.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const q = searchInp.value.toLowerCase().trim();
          if (q === 'all') {
            closeEntityPicker();
            selectSpecificEntity('ALL');
            return;
          }
          const firstChip = popEnt && popEnt.querySelector('.ep-chip[data-ent]');
          if (firstChip) {
            closeEntityPicker();
            selectSpecificEntity(firstChip.dataset.ent);
          }
        } else if (e.key === 'Escape') {
          closeEntityPicker();
        }
      });
    }

    if (btnAll) {
      btnAll.addEventListener('click', (e) => {
        e.stopPropagation();
        closeEntityPicker();
        selectSpecificEntity('ALL');
      });
    }

    document.addEventListener('click', (e) => {
      if (wrapEnt && !wrapEnt.contains(e.target)) {
        closeEntityPicker();
      }
    });

    const selSeed = document.getElementById('select-seed');
    if (selSeed) {
      selSeed.addEventListener('change', (e) => {
        closeEntityPicker();
        currentSeed = parseInt(e.target.value, 10);
        onEntityChanged();
      });
    }
  }

  function getEntitiesWithAll(ds) {
    const raw = indexData[ds] || [];
    if (raw.length > 0 && raw[0].entity !== 'ALL') {
      const rep = raw[0];
      return [{
        ...rep,
        entity: 'ALL',
        display_name: 'ALL',
        representative_entity: rep.entity,
        num_entities: raw.length,
      }, ...raw];
    }
    return raw.map(e => (e.entity === 'ALL' ? { ...e, display_name: 'ALL' } : e));
  }

  function updateEntityDropdown(autoLoad = true) {
    const ents = getEntitiesWithAll(currentDataset);
    const sel = document.getElementById('select-entity');
    if (sel) {
      sel.innerHTML = '';
      ents.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.entity;
        const label = e.display_name || e.entity;
        opt.textContent = label + (e.has_model ? '' : ' (chỉ có số liệu)');
        sel.appendChild(opt);
      });
    }

    const seedGroup = document.getElementById('group-seed');
    if (seedGroup) {
      seedGroup.style.display = 'none';
    }
    currentSeed = 0;

    if (ents.length > 0) {
      currentEntity = ents[0].entity;
      if (sel) sel.value = currentEntity;
      renderEntityPickerGrid('');
      syncEntityPickerDisplay();
      if (autoLoad) {
        return onEntityChanged();
      }
    }
  }

  // 2. Load Entity Details: /api/entity
  async function onEntityChanged() {
    if (!currentEntity) return;
    showLoading(
      `Đang nạp thực thể ${currentEntity}...`,
      'Đang tải dữ liệu chuỗi thời gian, checkpoint mô hình ConvAEC và tính toán giải thích'
    );
    try {
      const data = await fetchJSON(`/api/entity?dataset=${currentDataset}&entity=${currentEntity}&seed=${currentSeed}`);
      currentEntityMeta = data.meta;
      currentEntityDetail = data.detail;

      // Update 3 Metrics
      updateMetricsDisplay();

      // Setup Point Inputs & Overview Controls
      setupPointInputs(currentEntityMeta.n_features);
      setupOverviewControls(currentEntityMeta.n_features);

      // Load Overview Chart, Explain Data & Baseline Tab 3 Prediction
      if (currentEntityMeta.has_model) {
        if (isAllComparisonMode()) {
          renderOverviewChart();
          await Promise.all([
            loadExplainData(null, false),
            runPointPrediction(false),
          ]);
        } else {
          await Promise.all([
            loadSeriesOverview(),
            loadExplainData(null, false),
            runPointPrediction(false),
          ]);
        }
      } else if (isAllComparisonMode()) {
        renderOverviewChart();
      }
    } catch (e) {
      console.error(e);
    } finally {
      hideLoading();
    }
  }

  function updateMetricsDisplay() {
    const meta = currentEntityMeta;
    if (!meta) return;

    const rocEl = document.getElementById('metric-vus-roc');
    const rocSub = document.getElementById('metric-vus-roc-sub');
    const prEl = document.getElementById('metric-vus-pr');
    const prSub = document.getElementById('metric-vus-pr-sub');
    const rfEl = document.getElementById('metric-rf');
    const rfSub = document.getElementById('metric-rf-sub');
    const subTitle = document.getElementById('metrics-subtitle');

    const m = meta.single_metrics || (meta.per_seed_metrics && meta.per_seed_metrics[0]) || {};
    const dsM = meta.dataset_metrics || meta.single_metrics || {};
    const safeFmt = (v, d = 4) => (v != null && !isNaN(v)) ? Number(v).toFixed(d) : '--';

    if (currentEntity === 'ALL') {
      const nEnt = meta.num_entities || '';
      subTitle.textContent = `Trung bình toàn tập (${nEnt} thực thể — Kết quả Drive):`;

      rocEl.textContent = safeFmt(m.vus_roc, 4);
      if (m.paper_vus_roc) {
        const diff = (m.diff_vus_roc != null) ? m.diff_vus_roc : (m.vus_roc - m.paper_vus_roc);
        const sign = diff >= 0 ? '+' : '';
        rocSub.textContent = `Paper gốc: ${m.paper_vus_roc.toFixed(3)} (${sign}${diff.toFixed(3)}) · R-AUC: ${safeFmt(m.r_auc_roc, 3)}`;
      } else {
        rocSub.textContent = `R-AUC-ROC: ${safeFmt(m.r_auc_roc, 4)}`;
      }

      prEl.textContent = safeFmt(m.vus_pr, 4);
      if (m.paper_vus_pr) {
        const diff = (m.diff_vus_pr != null) ? m.diff_vus_pr : (m.vus_pr - m.paper_vus_pr);
        const sign = diff >= 0 ? '+' : '';
        prSub.textContent = `Paper gốc: ${m.paper_vus_pr.toFixed(3)} (${sign}${diff.toFixed(3)}) · R-AUC: ${safeFmt(m.r_auc_pr, 3)}`;
      } else {
        prSub.textContent = `R-AUC-PR: ${safeFmt(m.r_auc_pr, 4)}`;
      }

      rfEl.textContent = safeFmt(m.rf, 4);
      if (m.paper_rf) {
        const diff = (m.diff_rf != null) ? m.diff_rf : (m.rf - m.paper_rf);
        const sign = diff >= 0 ? '+' : '';
        rfSub.textContent = `Paper gốc: ${m.paper_rf.toFixed(3)} (${sign}${diff.toFixed(3)}) | Oracle: ${safeFmt(m.rf_oracle, 3)}`;
      } else {
        rfSub.textContent = `RF (oracle): ${safeFmt(m.rf_oracle, 4)}`;
      }
    } else {
      subTitle.textContent = `Thực thể ${currentEntity} (Kết quả Drive):`;

      rocEl.textContent = safeFmt(m.vus_roc, 4);
      const avgRoc = (dsM.vus_roc != null) ? `TB tập: ${Number(dsM.vus_roc).toFixed(3)} · ` : '';
      rocSub.textContent = `${avgRoc}R-AUC-ROC: ${safeFmt(m.r_auc_roc, 3)}`;

      prEl.textContent = safeFmt(m.vus_pr, 4);
      const avgPr = (dsM.vus_pr != null) ? `TB tập: ${Number(dsM.vus_pr).toFixed(3)} · ` : '';
      prSub.textContent = `${avgPr}R-AUC-PR: ${safeFmt(m.r_auc_pr, 3)}`;

      rfEl.textContent = safeFmt(m.rf, 4);
      const avgRf = (dsM.rf != null) ? `TB tập: ${Number(dsM.rf).toFixed(3)} | ` : '';
      rfSub.textContent = `${avgRf}Oracle: ${safeFmt(m.rf_oracle, 3)}`;
    }
  }

  // 3. Overview Controls: All-Entities Comparison (ALL) vs Single-Entity Time Series
  function isAllComparisonMode() {
    return Boolean(currentEntity === 'ALL' && currentEntityMeta);
  }

  function selectSpecificEntity(entName) {
    if (!entName) return;
    SimpleCanvasChart.hideTooltip();
    closeEntityPicker();
    const sel = document.getElementById('select-entity');
    if (sel) {
      const hasOpt = Array.from(sel.options).some(o => o.value === entName);
      if (!hasOpt) {
        updateEntityDropdown(false);
      }
      sel.value = entName;
    }
    currentEntity = entName;
    syncEntityPickerDisplay();
    onEntityChanged();
  }

  function compactEntityLabel(name) {
    if (!name) return '';
    if (name.startsWith('machine-')) return 'm' + name.slice('machine-'.length);
    if (name.startsWith('KPI-')) return name.slice(0, 8);
    return name.length > 10 ? name.slice(0, 9) + '…' : name;
  }

  function closeFeaturePicker() {
    const btn = document.getElementById('btn-feature-picker');
    const pop = document.getElementById('popover-feature-picker');
    if (btn) btn.classList.remove('open');
    if (pop) pop.style.display = 'none';
  }

  function formatFeaturePickerLabel(val, nFeatures) {
    const idx = Math.max(0, Math.min(nFeatures - 1, parseInt(val, 10) || 0));
    return `Đặc trưng D${idx + 1}`;
  }

  function positionFeaturePickerPopover(btn, pop) {
    const bRect = btn.getBoundingClientRect();
    const pRect = pop.getBoundingClientRect();
    let left = bRect.right - pRect.width;
    if (left < 10) left = 10;
    if (left + pRect.width > window.innerWidth - 10) {
      left = window.innerWidth - pRect.width - 10;
    }
    let top = bRect.bottom + 6;
    if (top + pRect.height > window.innerHeight - 10) {
      top = Math.max(10, bRect.top - pRect.height - 6);
    }
    pop.style.left = `${Math.round(left)}px`;
    pop.style.top = `${Math.round(top)}px`;
  }

  let featurePickerEventsBound = false;
  function bindFeaturePickerGlobalEvents() {
    if (featurePickerEventsBound) return;
    featurePickerEventsBound = true;

    const btn = document.getElementById('btn-feature-picker');
    const pop = document.getElementById('popover-feature-picker');
    const wrap = document.getElementById('wrap-feature-picker');

    if (btn && pop) {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = pop.style.display !== 'none';
        if (isOpen) {
          closeFeaturePicker();
        } else {
          closeEntityPicker();
          pop.style.display = 'block';
          btn.classList.add('open');
          positionFeaturePickerPopover(btn, pop);
          const actChip = pop.querySelector('.fp-chip.active');
          if (actChip) actChip.scrollIntoView({ block: 'nearest' });
        }
      });
    }

    document.addEventListener('click', (e) => {
      if (wrap && !wrap.contains(e.target)) {
        closeFeaturePicker();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeFeaturePicker();
        closeEntityPicker();
      }
    });
  }

  function setupOverviewControls(nFeatures) {
    bindFeaturePickerGlobalEvents();
    closeFeaturePicker();

    const titleEl = document.getElementById('overview-card-title');
    const grpMetric = document.getElementById('group-overview-metric');
    const selMetric = document.getElementById('select-overview-metric');
    const grpFeat = document.getElementById('group-overview-feature');
    const lblFeat = document.getElementById('lbl-feature-picker');
    const popFeat = document.getElementById('popover-feature-picker');

    const allComp = isAllComparisonMode();

    if (titleEl) {
      titleEl.textContent = allComp
        ? 'So sánh chỉ số đánh giá giữa các thực thể trong tập dữ liệu'
        : `Tổng quan toàn bộ chuỗi thời gian của Entity (${currentEntity === 'ALL' && currentEntityMeta?.representative_entity ? currentEntityMeta.representative_entity : currentEntity})`;
    }

    if (grpMetric && selMetric) {
      grpMetric.style.display = allComp ? 'flex' : 'none';
      selMetric.value = currentOverviewMetric;
      selMetric.onchange = (e) => {
        currentOverviewMetric = e.target.value;
        renderOverviewChart();
      };
    }

    if (!grpFeat || !lblFeat || !popFeat) return;
    if (allComp || nFeatures <= 1) {
      grpFeat.style.display = 'none';
      if (nFeatures <= 1) currentOverviewFeature = '0';
      return;
    }

    grpFeat.style.display = 'flex';
    const prevVal = currentOverviewFeature;
    const parsedPrev = parseInt(prevVal, 10);
    const validNumeric = !isNaN(parsedPrev) && parsedPrev >= 0 && parsedPrev < nFeatures;
    currentOverviewFeature = validNumeric ? String(parsedPrev) : '0';
    lblFeat.textContent = formatFeaturePickerLabel(currentOverviewFeature, nFeatures);

    let chipsHtml = '';
    for (let i = 0; i < nFeatures; i++) {
      const valStr = String(i);
      const isAct = currentOverviewFeature === valStr;
      chipsHtml += `<button type="button" class="fp-chip ${isAct ? 'active' : ''}" data-feat="${valStr}">D${i + 1}</button>`;
    }

    popFeat.innerHTML = `
      <div class="fp-section-title">Chọn đặc trưng riêng lẻ (D1 – D${nFeatures})</div>
      <div class="fp-chip-grid">${chipsHtml}</div>
    `;

    popFeat.querySelectorAll('[data-feat]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        const chosen = el.dataset.feat;
        currentOverviewFeature = chosen;
        lblFeat.textContent = formatFeaturePickerLabel(chosen, nFeatures);
        popFeat.querySelectorAll('[data-feat]').forEach(item => {
          item.classList.toggle('active', item.dataset.feat === chosen);
        });
        closeFeaturePicker();
        loadSeriesOverview();
      });
    });
  }

  async function loadSeriesOverview() {
    try {
      const featParam = (currentEntityMeta && currentEntityMeta.n_features > 1)
        ? currentOverviewFeature
        : '0';
      const data = await fetchJSON(
        `/api/series?dataset=${currentDataset}&entity=${currentEntity}&seed=${currentSeed}&feature=${encodeURIComponent(featParam)}`
      );
      seriesOverviewData = data;
      renderOverviewChart();
    } catch (e) {
      console.warn('Overview not available:', e);
    }
  }

  function jumpToExplainAt(realT) {
    if (typeof realT !== 'number' || isNaN(realT)) return;
    SimpleCanvasChart.hideTooltip();
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.tab === 'tab-explain');
    });
    document.querySelectorAll('.tab-content').forEach(c => {
      c.classList.toggle('active', c.id === 'tab-explain');
    });
    isCustomPointExplain = false;
    loadExplainData(realT, true);
  }

  function renderAllEntitiesComparisonChart() {
    if (!chartOverview) return;
    const realEnts = (indexData[currentDataset] || []).filter(e => e.entity !== 'ALL');
    if (realEnts.length === 0) return;

    const metricInfoMap = {
      vus_pr: { label: 'VUS-PR' },
      vus_roc: { label: 'VUS-ROC' },
      rf: { label: 'RF (Range F-score)' },
    };
    const mInfo = metricInfoMap[currentOverviewMetric] || metricInfoMap.vus_pr;
    const dsLabelMap = {
      smd: 'SMD',
      iops: 'AIOps / IOPS',
      msl: 'MSL',
      smap: 'SMAP',
      anomaly_archive: 'UCR (Anomaly Archive)',
    };
    const dsTitle = dsLabelMap[currentDataset] || currentDataset.toUpperCase();

    const vals = realEnts.map(e => {
      const sm = e.single_metrics || (e.per_seed_metrics && e.per_seed_metrics[0]);
      return sm ? (sm[currentOverviewMetric] ?? 0) : 0;
    });
    const datasetMean = (currentEntityMeta && (currentEntityMeta.single_metrics || (currentEntityMeta.per_seed_metrics && currentEntityMeta.per_seed_metrics[0])))
      ? ((currentEntityMeta.single_metrics || currentEntityMeta.per_seed_metrics[0])[currentOverviewMetric] ?? 0)
      : (vals.reduce((a, b) => a + b, 0) / (vals.length || 1));

    let bestIdx = 0;
    for (let i = 1; i < vals.length; i++) {
      if (vals[i] > vals[bestIdx]) bestIdx = i;
    }

    const bars = realEnts.map((e, i) => {
      const v = vals[i];
      return {
        label: compactEntityLabel(e.entity),
        clickValue: e.entity,
        value: v,
        isTop: i === bestIdx,
        topColor: '#15803d',
        color: v >= datasetMean ? '#2563eb' : '#93c5fd',
      };
    });

    chartOverview.drawBarChart(bars, {
      title: `Phân bố ${mInfo.label} trên ${realEnts.length} thực thể tập ${dsTitle} (Dữ liệu Drive)`,
      xLabel: 'Thực thể (Entity)',
      valueFormat: 'decimal',
      meanLine: {
        value: datasetMean,
        label: `Trung bình toàn tập (${dsTitle}): ${datasetMean.toFixed(4)}`,
        color: '#dc2626',
      },
      badgeText: `Cao nhất: ${compactEntityLabel(realEnts[bestIdx].entity)} (${vals[bestIdx].toFixed(3)})`,
      onPointClick: (_idx, entName) => selectSpecificEntity(entName),
      tooltipFormatter: (idx) => {
        const e = realEnts[idx];
        if (!e) return '';
        const sm = e.single_metrics || (e.per_seed_metrics && e.per_seed_metrics[0]) || { vus_roc: 0, vus_pr: 0, rf: 0, rf_oracle: 0, r_auc_roc: 0, r_auc_pr: 0 };
        const curVal = sm[currentOverviewMetric] ?? 0;
        const isAbove = curVal >= datasetMean;
        const pill = idx === bestIdx
          ? '<span class="tt-pill ok">★ Cao nhất tập</span>'
          : (isAbove ? '<span class="tt-pill info">≥ Trung bình tập</span>' : '<span class="tt-pill muted">&lt; Trung bình tập</span>');
        return `
          <div class="tt-header"><span>Entity: ${e.entity}</span>${pill}</div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:${idx === bestIdx ? '#15803d' : (isAbove ? '#2563eb' : '#93c5fd')}"></span>${mInfo.label} (Drive)</span>
            <span class="tt-val">${curVal.toFixed(4)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label">VUS-ROC · VUS-PR · RF</span>
            <span class="tt-val">ROC ${(sm.vus_roc || 0).toFixed(3)} · PR ${(sm.vus_pr || 0).toFixed(3)} · RF ${(sm.rf || 0).toFixed(3)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label">Range-AUC &amp; Oracle</span>
            <span class="tt-val">R-ROC ${(sm.r_auc_roc || 0).toFixed(3)} · R-PR ${(sm.r_auc_pr || 0).toFixed(3)} · Ora ${(sm.rf_oracle || 0).toFixed(3)}</span>
          </div>
          <div class="tt-hint">🖱️ Double-click cột này để xem chuỗi thời gian của ${e.entity}</div>
        `;
      },
    });
  }

  function renderOverviewChart() {
    if (!chartOverview) return;
    if (isAllComparisonMode()) {
      renderAllEntitiesComparisonChart();
      return;
    }
    if (!seriesOverviewData) return;
    const nFeat = (currentEntityMeta && currentEntityMeta.n_features) ? currentEntityMeta.n_features : 1;
    let inputLabel = 'Tín hiệu chuỗi thời gian gốc';
    let shortFeatLabel = 'Tín hiệu gốc';
    if (nFeat > 1) {
      const idx = Math.max(0, Math.min(nFeat - 1, parseInt(currentOverviewFeature, 10) || 0));
      inputLabel = `Tín hiệu gốc (Đặc trưng D${idx + 1} / ${nFeat} đặc trưng)`;
      shortFeatLabel = `Tín hiệu gốc (D${idx + 1})`;
    }
    const inputLine = {
      label: inputLabel,
      data: seriesOverviewData.input_first_feature,
      color: '#334155', // dark slate blue
      width: 2,
    };
    const scoreLine = {
      label: 'Điểm bất thường tương đối',
      data: seriesOverviewData.anomaly_score,
      color: '#dc2626', // red
      width: 2,
    };
    const chartEntityLabel =
      (currentEntity === 'ALL' && currentEntityMeta && currentEntityMeta.representative_entity)
        ? `ALL — Chuỗi mẫu đại diện: ${currentEntityMeta.representative_entity}`
        : currentEntity;
    const indices = seriesOverviewData.indices || [];
    const th = seriesOverviewData.threshold;

    chartOverview.drawLineChart([inputLine, scoreLine], {
      title: `Chuỗi dữ liệu & Điểm bất thường (${chartEntityLabel})`,
      xLabel: 'Chỉ số thời gian (t)',
      xValues: indices,
      onPointClick: (_idx, realT) => jumpToExplainAt(realT),
      tooltipFormatter: (idx) => {
        const realT = indices[idx] !== undefined ? indices[idx] : idx;
        const sigVal = seriesOverviewData.input_first_feature[idx];
        const relVal = seriesOverviewData.anomaly_score[idx];
        const rawVal = seriesOverviewData.raw_score ? seriesOverviewData.raw_score[idx] : null;
        const isAnom = (rawVal !== null && th !== undefined) ? (rawVal > th) : (relVal > 0.5);
        const pill = isAnom
          ? '<span class="tt-pill anom">⚠️ Bất thường (&gt; μ + 3σ)</span>'
          : '<span class="tt-pill ok">✓ Bình thường</span>';
        const rawRow = (rawVal !== null && th !== undefined)
          ? `
            <div class="tt-row">
              <span class="tt-label">Raw Combined / μ + 3σ</span>
              <span class="tt-val">${rawVal.toFixed(4)} / ${th.toFixed(4)}</span>
            </div>
          `
          : '';
        return `
          <div class="tt-header"><span>Vị trí t = ${realT}</span>${pill}</div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>${shortFeatLabel}</span>
            <span class="tt-val">${sigVal !== undefined ? sigVal.toFixed(4) : '--'}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#dc2626"></span>Điểm tương đối [0, 1]</span>
            <span class="tt-val">${relVal !== undefined ? relVal.toFixed(4) : '--'}</span>
          </div>
          ${rawRow}
          <div class="tt-hint">🖱️ Double-click để mở Giải thích mô hình tại t = ${realT}</div>
        `;
      },
    });
  }

  // 4. Manual Point Prediction (Clean Presentation Mode)
  let baselinePoint = [];

  function getNormalBaseline(nFeatures) {
    const src = (currentEntityDetail && Array.isArray(currentEntityDetail.normal_point) && currentEntityDetail.normal_point.length === nFeatures)
      ? currentEntityDetail.normal_point
      : (currentEntityDetail && Array.isArray(currentEntityDetail.feat_median) && currentEntityDetail.feat_median.length === nFeatures)
        ? currentEntityDetail.feat_median
        : Array(nFeatures).fill(0.1);
    const digits = nFeatures === 1 ? 4 : 3;
    return src.map(v => parseFloat(Number(v).toFixed(digits)));
  }

  function getSpikePreset(nFeatures) {
    if (currentEntityDetail && Array.isArray(currentEntityDetail.spike_point) && currentEntityDetail.spike_point.length === nFeatures) {
      const digits = nFeatures === 1 ? 4 : 3;
      return currentEntityDetail.spike_point.map(v => parseFloat(Number(v).toFixed(digits)));
    }
    const fallback = baselinePoint.slice();
    const spikeCount = Math.min(5, nFeatures);
    for (let i = 0; i < spikeCount; i++) {
      fallback[i] = fallback[i] >= 0.5 ? 0 : 1;
    }
    return fallback;
  }

  function updateModifiedHighlights() {
    const badgeMod = document.getElementById('badge-modified-count');
    let modCount = 0;
    if (baselinePoint.length === 1) {
      const inp = document.getElementById('pt-feat-0');
      if (inp) {
        const val = parseFloat(inp.value || '0');
        const isMod = Math.abs(val - baselinePoint[0]) > 1.5e-3;
        inp.classList.toggle('pt-modified', isMod);
        if (isMod) modCount = 1;
      }
    } else {
      document.querySelectorAll('.pt-feat').forEach(inp => {
        const idx = parseInt(inp.dataset.idx, 10);
        const val = parseFloat(inp.value || '0');
        const base = baselinePoint[idx] ?? 0;
        const isMod = Math.abs(val - base) > 1.5e-3;
        inp.classList.toggle('pt-modified', isMod);
        if (inp.parentElement) inp.parentElement.classList.toggle('modified', isMod);
        if (isMod) modCount++;
      });
    }
    if (badgeMod) {
      if (modCount > 0) {
        badgeMod.style.display = 'inline-block';
        badgeMod.textContent = `Đã sửa ${modCount} kênh`;
      } else {
        badgeMod.style.display = 'none';
      }
    }
  }

  function setupPointInputs(nFeatures) {
    const container = document.getElementById('container-point-inputs');
    container.innerHTML = '';
    baselinePoint = getNormalBaseline(nFeatures);

    if (nFeatures === 1) {
      const inp = document.createElement('input');
      inp.type = 'number';
      inp.step = 'any';
      inp.className = 'form-control pt-feat';
      inp.id = 'pt-feat-0';
      inp.placeholder = 'Ví dụ: 1.0 (miền [0, 1])';
      inp.value = baselinePoint[0];
      inp.addEventListener('input', updateModifiedHighlights);
      inp.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') runPointPrediction(true);
      });
      container.appendChild(inp);
    } else {
      const grid = document.createElement('div');
      grid.className = 'pt-grid';
      if (nFeatures <= 12) {
        grid.style.gridTemplateColumns = 'repeat(4, minmax(0, 1fr))';
      }

      for (let i = 0; i < nFeatures; i++) {
        const wrap = document.createElement('div');
        wrap.className = 'pt-feat-wrap';
        wrap.innerHTML = `<small>D${i + 1}</small>`;
        const inp = document.createElement('input');
        inp.type = 'number';
        inp.step = 'any';
        if (i === 0) inp.id = 'pt-feat-0';
        inp.className = 'form-control pt-feat';
        inp.dataset.idx = i;
        inp.value = baselinePoint[i];
        inp.title = `Kênh D${i + 1} · Giá trị chuẩn: ${baselinePoint[i]}`;
        inp.addEventListener('input', updateModifiedHighlights);
        inp.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') runPointPrediction(true);
        });
        wrap.appendChild(inp);
        grid.appendChild(wrap);
      }
      container.appendChild(grid);
    }

    updateModifiedHighlights();

    // Setup optional chart channel selector
    const selChartFeat = document.getElementById('select-predict-chart-feat');
    if (selChartFeat) {
      if (nFeatures > 1) {
        selChartFeat.style.display = 'inline-block';
        let optsHtml = '<option value="auto">Tự động (kênh nổi bật)</option>';
        for (let i = 0; i < nFeatures; i++) {
          optsHtml += `<option value="${i}">Kênh D${i + 1}</option>`;
        }
        selChartFeat.innerHTML = optsHtml;
        selChartFeat.value = 'auto';
        selChartFeat.onchange = () => {
          if (lastPredictedResult) {
            renderPredictWindowChart(
              lastPredictedResult.window_input,
              lastPredictedResult.reconstructed,
              lastPredictedResult.raw_mse,
              lastPredictedResult.is_anomaly
            );
          }
        };
      } else {
        selChartFeat.style.display = 'none';
        selChartFeat.value = 'auto';
      }
    }

    const btnSample = document.getElementById('btn-fill-point-sample');
    if (btnSample) {
      btnSample.onclick = () => {
        if (nFeatures === 1) {
          const inp = document.getElementById('pt-feat-0');
          if (inp) inp.value = baselinePoint[0];
        } else {
          document.querySelectorAll('.pt-feat').forEach(inp => {
            const idx = parseInt(inp.dataset.idx, 10);
            inp.value = baselinePoint[idx];
          });
        }
        if (selChartFeat) selChartFeat.value = 'auto';
        updateModifiedHighlights();
        if (currentEntityMeta && currentEntityMeta.has_model) {
          runPointPrediction(true);
        }
      };
    }

    const btnSpike = document.getElementById('btn-fill-point-spike');
    if (btnSpike) {
      btnSpike.onclick = () => {
        const spikePt = getSpikePreset(nFeatures);
        if (nFeatures === 1) {
          const inp = document.getElementById('pt-feat-0');
          if (inp) inp.value = spikePt[0];
        } else {
          document.querySelectorAll('.pt-feat').forEach(inp => {
            const idx = parseInt(inp.dataset.idx, 10);
            inp.value = spikePt[idx];
          });
        }
        if (selChartFeat) selChartFeat.value = 'auto';
        updateModifiedHighlights();
        const firstMod = container.querySelector('.pt-modified');
        if (firstMod) firstMod.scrollIntoView({ block: 'nearest' });
        if (currentEntityMeta && currentEntityMeta.has_model) {
          runPointPrediction(true);
        }
      };
    }
  }

  async function runPointPrediction(showOverlay = true) {
    if (!currentEntityMeta || !currentEntityMeta.has_model) {
      if (showOverlay) alert('Entity này chưa có checkpoint model được tải về.');
      return;
    }

    const nFeatures = currentEntityMeta.n_features;
    let point = [];
    if (nFeatures === 1) {
      const inp0 = document.getElementById('pt-feat-0');
      point = [parseFloat((inp0 && inp0.value) || '0')];
    } else {
      document.querySelectorAll('.pt-feat').forEach(inp => {
        point.push(parseFloat(inp.value || '0'));
      });
    }

    const btnPredict = document.getElementById('btn-run-predict');
    const origBtnText = btnPredict ? btnPredict.textContent : '⚡ Dự đoán bất thường';
    if (btnPredict) {
      btnPredict.disabled = true;
      if (showOverlay) btnPredict.textContent = '⏳ Đang suy luận bất thường...';
    }
    if (showOverlay) {
      showLoading(
        'Đang dự đoán điểm dữ liệu mới...',
        `Đang chạy cửa sổ 100 điểm qua ConvAEC cho ${currentEntity}`
      );
    }

    try {
      const res = await fetchJSON('/api/predict_point', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset: currentDataset,
          entity: currentEntity,
          seed: currentSeed,
          point: point,
          context_type: 'normal_window',
        }),
      });

      const boxConc = document.getElementById('box-conclusion');
      const badge = document.getElementById('badge-conclusion');
      const desc = document.getElementById('desc-conclusion');
      const cardComb = document.getElementById('card-raw-comb');
      const cardPseudo = document.getElementById('card-pseudo-winner');

      if (res.is_anomaly) {
        if (boxConc) boxConc.className = 'prediction-conclusion-box is-abnormal';
        badge.className = 'conclusion-badge abnormal';
        badge.textContent = '⚠️ BẤT THƯỜNG';
        desc.textContent = `Combined (${res.raw_combined.toFixed(4)}) > Ngưỡng μ+3σ (${res.threshold.toFixed(4)})`;
        if (cardComb) cardComb.className = 'score-card highlight is-abnormal';
        if (cardPseudo) cardPseudo.className = 'pseudo-anomaly-card is-abnormal';
      } else {
        if (boxConc) boxConc.className = 'prediction-conclusion-box is-normal';
        badge.className = 'conclusion-badge normal';
        badge.textContent = '✓ BÌNH THƯỜNG';
        desc.textContent = `Combined (${res.raw_combined.toFixed(4)}) < Ngưỡng μ+3σ (${res.threshold.toFixed(4)})`;
        if (cardComb) cardComb.className = 'score-card highlight is-normal';
        if (cardPseudo) cardPseudo.className = 'pseudo-anomaly-card is-normal';
      }

      document.getElementById('res-raw-mse').textContent = res.raw_mse.toFixed(4);
      document.getElementById('res-raw-ce').textContent = res.raw_ce.toFixed(4);
      document.getElementById('res-raw-comb').textContent = res.raw_combined.toFixed(4);
      document.getElementById('res-threshold').textContent = res.threshold.toFixed(4);

      // Save last prediction for Explainable Sync
      lastPredictedWindow = res.custom_window || res.window_input;
      lastPredictedPoint = res.new_point;
      lastPredictedResult = res;

      // Update 12 Pseudo Anomaly Classification Card
      const pseudoBadge = document.getElementById('badge-pseudo-winner');
      const pseudoDesc = document.getElementById('desc-pseudo-winner');
      if (res.predicted_group) {
        const pg = res.predicted_group;
        if (pg.is_anomaly) {
          pseudoBadge.style.background = '#dc2626';
          pseudoBadge.style.color = '#ffffff';
          pseudoBadge.textContent = `${pg.name_vi} (${(pg.prob * 100).toFixed(1)}%)`;
          pseudoDesc.innerHTML = `<strong>Đặc trưng:</strong> ${pg.desc_vi}<br><span style="color:#b91c1c; font-weight:600;">Cơ sở:</span> ${pg.reason}`;
        } else {
          pseudoBadge.style.background = '#16a34a';
          pseudoBadge.style.color = '#ffffff';
          pseudoBadge.textContent = `${pg.name_vi} (${(pg.prob * 100).toFixed(1)}%)`;
          pseudoDesc.innerHTML = `<strong>Đặc trưng:</strong> ${pg.desc_vi}<br><span style="color:#15803d; font-weight:600;">Cơ sở:</span> ${pg.reason}`;
        }
      }

      // Enable Sync Button
      const btnSync = document.getElementById('btn-sync-explain-point');
      if (btnSync) {
        btnSync.disabled = false;
      }

      // Draw Predict window reconstruction chart
      renderPredictWindowChart(res.window_input, res.reconstructed, res.raw_mse, res.is_anomaly);
    } catch (e) {
      if (showOverlay) alert('Lỗi dự đoán: ' + e.message);
      else console.error('Silent predict failed:', e);
    } finally {
      if (btnPredict) {
        btnPredict.disabled = false;
        btnPredict.textContent = origBtnText;
      }
      if (showOverlay) hideLoading();
    }
  }

  // Run Prediction Button
  const btnRunPredict = document.getElementById('btn-run-predict');
  if (btnRunPredict) {
    btnRunPredict.addEventListener('click', () => {
      runPointPrediction(true);
    });
  }

  // Sync Button Listener
  const btnSyncExplain = document.getElementById('btn-sync-explain-point');
  if (btnSyncExplain) {
    btnSyncExplain.addEventListener('click', async () => {
      if (!lastPredictedWindow) return;
      // Switch to tab-explain
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === 'tab-explain'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === 'tab-explain'));

      isCustomPointExplain = true;
      await loadExplainCustomPoint();
    });
  }

  async function loadExplainCustomPoint() {
    if (!lastPredictedWindow) return;
    showLoading(
      'Đang đồng bộ giải thích 5 bước cho điểm mới...',
      'Đang trích xuất đặc trưng Encoder, tái tạo Decoder và phân loại 12 lớp tại t=100'
    );
    try {
      explainData = await fetchJSON('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset: currentDataset,
          entity: currentEntity,
          seed: currentSeed,
          custom_window: lastPredictedWindow,
          point: lastPredictedPoint,
          is_custom_point: true,
        }),
      });

      updateExplainModeBanner();
      goToStep(0);
    } catch (e) {
      alert('Không thể giải thích điểm này: ' + e.message);
    } finally {
      hideLoading();
    }
  }

  function updateExplainModeBanner() {
    const banner = document.getElementById('explain-mode-banner');
    const modeText = document.getElementById('explain-mode-text');
    const modeBadge = document.getElementById('explain-mode-badge');
    const btnBack = document.getElementById('btn-explain-back-to-series');
    const metaControls = document.querySelector('.step-meta-controls');

    if (!banner) return;
    if (isCustomPointExplain) {
      const isAnom = !!(explainData && explainData.winner_group && explainData.winner_group.is_anomaly);
      banner.style.background = isAnom ? '#fef2f2' : '#f0fdf4';
      banner.style.borderColor = isAnom ? '#fecaca' : '#86efac';
      modeText.style.color = isAnom ? '#991b1b' : '#166534';
      modeText.innerHTML = `Điểm nạp Tab 3: <strong>t = 100</strong>`;
      modeText.title = 'Đang giải thích điểm nạp thủ công từ Tab 3 tại t = 100';
      if (modeBadge) {
        modeBadge.style.display = 'inline-block';
        modeBadge.style.background = isAnom ? '#dc2626' : '#16a34a';
        modeBadge.textContent = explainData?.winner_group?.name_vi || 'Điểm nạp mới';
      }
      if (btnBack) btnBack.style.display = 'inline-block';
      if (metaControls) metaControls.style.opacity = '0.35';
    } else {
      banner.style.background = '#e0f2fe';
      banner.style.borderColor = '#7dd3fc';
      modeText.style.color = '#0c4a6e';
      const isAll = currentEntity === 'ALL' && currentEntityMeta && currentEntityMeta.representative_entity;
      const fullEnt = isAll ? currentEntityMeta.representative_entity : currentEntity;
      modeText.innerHTML = isAll
        ? `Mẫu (ALL): <strong>${fullEnt}</strong>`
        : `Entity: <strong>${fullEnt}</strong>`;
      modeText.title = isAll
        ? `Mẫu đại diện khi chọn ALL: ${fullEnt}`
        : `Chuỗi kiểm thử của Entity: ${fullEnt}`;
      if (modeBadge) modeBadge.style.display = 'none';
      if (btnBack) btnBack.style.display = 'none';
      if (metaControls) metaControls.style.opacity = '1.0';
    }
  }

  function renderPredictWindowChart(windowIn, windowRec, mseVal, isAnomaly = false) {
    if (!chartPredict || !windowIn) return;
    const nFeat = (windowIn[0] && windowIn[0].length) ? windowIn[0].length : 1;
    const selChartFeat = document.getElementById('select-predict-chart-feat');
    let featIdx = 0;

    if (nFeat > 1 && selChartFeat && selChartFeat.value !== 'auto') {
      featIdx = Math.max(0, Math.min(nFeat - 1, parseInt(selChartFeat.value, 10) || 0));
    } else if (nFeat > 1 && windowRec && windowRec.length === windowIn.length) {
      const lastRow = windowIn.length - 1;
      const prevRow = Math.max(0, lastRow - 1);
      const histLen = Math.max(1, lastRow);
      let maxJump = -1;
      const jumps = [];
      const sqErrs = [];
      const histStds = [];

      for (let f = 0; f < nFeat; f++) {
        const j = Math.abs((windowIn[lastRow][f] ?? 0) - (windowIn[prevRow][f] ?? 0));
        const d = (windowIn[lastRow][f] ?? 0) - (windowRec[lastRow][f] ?? 0);
        jumps.push(j);
        sqErrs.push(d * d);
        if (j > maxJump) maxJump = j;

        let sum = 0;
        for (let r = 0; r < histLen; r++) sum += (windowIn[r][f] ?? 0);
        const mean = sum / histLen;
        let varSum = 0;
        for (let r = 0; r < histLen; r++) {
          const dv = (windowIn[r][f] ?? 0) - mean;
          varSum += dv * dv;
        }
        histStds.push(Math.sqrt(varSum / histLen));
      }

      if (maxJump > 1e-2) {
        // Among jumped channels, strongly prefer active oscillating channels (std > 1e-3) over dead-flat 0.000 channels (like D5 on SMD)
        const cand = [];
        for (let f = 0; f < nFeat; f++) {
          if (jumps[f] >= 0.5 * maxJump) cand.push(f);
        }
        const activeCand = cand.filter(f => histStds[f] > 1e-3);
        if (activeCand.length > 0) {
          featIdx = activeCand.reduce((best, f) => (histStds[f] > histStds[best] ? f : best), activeCand[0]);
        } else if (cand.length > 0) {
          featIdx = cand.reduce((best, f) => (sqErrs[f] > sqErrs[best] ? f : best), cand[0]);
        }
      } else {
        // Normal baseline: pick the liveliest channel in the first 5 channels (so Mẫu chuẩn & ⚡ Mẫu đột biến stay on the same clear waveform!)
        const topK = Math.min(5, nFeat);
        let bestTop = 0;
        for (let f = 1; f < topK; f++) {
          if (histStds[f] > histStds[bestTop]) bestTop = f;
        }
        if (histStds[bestTop] > 1e-3) {
          featIdx = bestTop;
        } else {
          for (let f = 0; f < nFeat; f++) {
            if (histStds[f] > histStds[featIdx]) featIdx = f;
          }
        }
      }
    }

    const origData = windowIn.map(p => p[featIdx] ?? p[0]);
    const recData = windowRec.map(p => p[featIdx] ?? p[0]);
    const featTag = nFeat > 1 ? ` — D${featIdx + 1}` : '';
    const xSteps = Array.from({ length: origData.length }, (_, i) => i + 1);
    const lastIdx = origData.length - 1;
    const accentColor = isAnomaly ? '#dc2626' : '#16a34a';

    chartPredict.drawLineChart([
      { label: `Đầu vào (kèm t=100${featTag})`, data: origData, color: '#334155', width: 2 },
      { label: `Tái tạo Autoencoder${featTag}`, data: recData, color: '#2563eb', width: 2 },
    ], {
      title: `Cửa sổ 100 điểm & chuỗi tái tạo${featTag}`,
      xLabel: 'Thời gian trong cửa sổ (1 -> 100)',
      xValues: xSteps,
      fillBetween: true,
      fillBetweenColor: isAnomaly ? 'rgba(220, 38, 38, 0.15)' : 'rgba(22, 163, 74, 0.08)',
      badgeText: `MSE = ${mseVal.toFixed(4)}`,
      badgeColor: accentColor,
      pointMarker: lastIdx >= 0
        ? { index: lastIdx, value: origData[lastIdx], label: 'Điểm mới (t=100)', color: accentColor }
        : undefined,
      tooltipFormatter: (idx) => {
        const stepNum = idx + 1;
        const vOrig = origData[idx] ?? 0;
        const vRec = recData[idx] ?? 0;
        const sqErr = (vOrig - vRec) * (vOrig - vRec);
        const pill = idx === lastIdx
          ? `<span class="tt-pill ${isAnomaly ? 'anom' : 'ok'}">Điểm nạp mới (t=100)</span>`
          : '<span class="tt-pill muted">Ngữ cảnh chuẩn</span>';
        return `
          <div class="tt-header"><span>Bước t = ${stepNum} / ${origData.length}</span>${pill}</div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>Tín hiệu gốc</span>
            <span class="tt-val">${vOrig.toFixed(4)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#2563eb"></span>Tái tạo Decoder</span>
            <span class="tt-val">${vRec.toFixed(4)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label">Sai số bình phương (x - x̂)²</span>
            <span class="tt-val">${sqErr.toFixed(5)}</span>
          </div>
        `;
      },
    });
  }

  // 5. Explainable 5-minute Mode
  async function loadExplainData(t = null, showOverlay = true) {
    if (!currentEntityMeta || !currentEntityMeta.has_model) return;
    if (showOverlay) {
      showLoading(
        t !== null ? `Đang tính toán giải thích tại cửa sổ t = ${t}...` : `Đang tải giải thích cho ${currentEntity}...`,
        'Đang trích xuất kích hoạt trung gian qua 4 khối ConvBlock, Decoder và Classifier'
      );
    }
    try {
      isCustomPointExplain = false;
      explainData = await fetchJSON('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset: currentDataset,
          entity: currentEntity,
          seed: currentSeed,
          t: t,
        }),
      });

      // Update T slider
      const sliderT = document.getElementById('slider-explain-t');
      const lblT = document.getElementById('lbl-explain-t');
      sliderT.max = currentEntityDetail.length - 1;
      sliderT.value = explainData.t;
      lblT.textContent = explainData.t;

      updateExplainModeBanner();
      renderCurrentStep();
    } catch (e) {
      console.warn('Explain load failed:', e);
    } finally {
      if (showOverlay) hideLoading();
    }
  }

  function setupWalkthroughControls() {
    document.getElementById('btn-step-prev').onclick = () => {
      if (currentStep > 0) goToStep(currentStep - 1);
    };
    document.getElementById('btn-step-next').onclick = () => {
      if (currentStep < 4) goToStep(currentStep + 1);
    };

    document.querySelectorAll('.step-pill').forEach(pill => {
      pill.onclick = () => {
        goToStep(parseInt(pill.dataset.step, 10));
      };
    });

    const btnBackToSeries = document.getElementById('btn-explain-back-to-series');
    if (btnBackToSeries) {
      btnBackToSeries.onclick = () => {
        isCustomPointExplain = false;
        loadExplainData();
      };
    }

    // Keyboard navigation
    window.addEventListener('keydown', (e) => {
      const activeTab = document.querySelector('.tab-content.active');
      if (activeTab && activeTab.id === 'tab-explain') {
        if (e.key === 'ArrowRight' && currentStep < 4) {
          goToStep(currentStep + 1);
        } else if (e.key === 'ArrowLeft' && currentStep > 0) {
          goToStep(currentStep - 1);
        }
      }
    });

    // Slider T
    const sliderT = document.getElementById('slider-explain-t');
    if (sliderT) {
      sliderT.addEventListener('change', (e) => {
        loadExplainData(parseInt(e.target.value, 10));
      });
    }

    const btnExpNorm = document.getElementById('btn-explain-normal');
    if (btnExpNorm) {
      btnExpNorm.onclick = () => {
        if (explainData) loadExplainData(explainData.normal_t);
      };
    }

    const btnExpAbnorm = document.getElementById('btn-explain-abnormal');
    if (btnExpAbnorm) {
      btnExpAbnorm.onclick = () => {
        if (currentEntityDetail) loadExplainData(currentEntityDetail.max_anomaly_idx);
      };
    }
  }

  function goToStep(stepIndex) {
    SimpleCanvasChart.hideTooltip();
    currentStep = stepIndex;
    document.querySelectorAll('.step-pill').forEach((p, idx) => {
      p.classList.toggle('active', idx === currentStep);
    });
    document.querySelectorAll('.explain-slide').forEach((s, idx) => {
      s.classList.toggle('active', idx === currentStep);
    });
    renderCurrentStep();
  }

  function renderCurrentStep() {
    if (!explainData) return;

    if (currentStep === 0) {
      if (explainData.is_custom_point) {
        const lastIdx = explainData.input_slice.length - 1;
        const ptVal = explainData.input_slice[lastIdx];
        const fIdx = explainData.plot_feature_idx ?? 0;
        const featSuffix = explainData.n_features > 1 ? ` — D${fIdx + 1}` : '';
        chartSlide1.drawLineChart([
          { label: `Cửa sổ 100 điểm (99 ngữ cảnh + điểm nạp${featSuffix})`, data: explainData.input_slice, color: '#334155', width: 2 }
        ], {
          title: `Cửa sổ 100 điểm & điểm nạp mới (t=100${featSuffix})`,
          xLabel: 'Bước thời gian trong cửa sổ (1 -> 100)',
          xValues: explainData.time_slice,
          highlightWindow: [88, 99],
          badgeText: `Điểm nạp = ${ptVal.toFixed(3)}`,
          pointMarker: { index: lastIdx, value: ptVal, label: 'Điểm nạp mới (t=100)' },
          tooltipFormatter: (idx) => {
            const stepNum = idx + 1;
            const val = explainData.input_slice[idx] ?? 0;
            const pill = idx === lastIdx
              ? '<span class="tt-pill anom">Điểm nạp mới</span>'
              : '<span class="tt-pill muted">99 điểm ngữ cảnh</span>';
            return `
              <div class="tt-header"><span>Bước cửa sổ t = ${stepNum} / 100</span>${pill}</div>
              <div class="tt-row">
                <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>Giá trị đầu vào</span>
                <span class="tt-val">${val.toFixed(4)}</span>
              </div>
            `;
          },
        });
      } else {
        // Step 1: Input series slice with window highlighted
        const t = explainData.t;
        const winStartT = Math.max(0, t - 99);
        const sliceStart = explainData.time_slice[0];
        const winStartRel = t - sliceStart - 99;
        const winEndRel = t - sliceStart;

        chartSlide1.drawLineChart([
          { label: 'Chuỗi dữ liệu gốc', data: explainData.input_slice, color: '#334155', width: 2 }
        ], {
          title: `Chuỗi thời gian & vùng cửa sổ khảo sát tại t=${t}`,
          xLabel: 'Thời gian (t)',
          xValues: explainData.time_slice,
          highlightWindow: [winStartRel, winEndRel],
          badgeText: `Cửa sổ [${winStartT}, ${t}]`,
          onPointClick: (_idx, realT) => loadExplainData(realT, true),
          tooltipFormatter: (idx) => {
            const realT = explainData.time_slice[idx] !== undefined ? explainData.time_slice[idx] : idx;
            const val = explainData.input_slice[idx] ?? 0;
            const inWin = realT >= winStartT && realT <= t;
            const pill = realT === t
              ? '<span class="tt-pill anom">Đầu cửa sổ (t)</span>'
              : (inWin ? '<span class="tt-pill info">Trong Input Window</span>' : '<span class="tt-pill muted">Ngoài cửa sổ</span>');
            return `
              <div class="tt-header"><span>t = ${realT}</span>${pill}</div>
              <div class="tt-row">
                <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>Chuỗi dữ liệu gốc</span>
                <span class="tt-val">${val.toFixed(4)}</span>
              </div>
              <div class="tt-hint">🖱️ Double-click để dời cửa sổ khảo sát về t = ${realT}</div>
            `;
          },
        });
      }
      document.getElementById('exp-text-1').textContent = explainData.explanations[0];
    } else if (currentStep === 1) {
      // Step 2: Encoder visual funnel pipeline & 128-D Signed Embedding chart
      const pipelineEl = document.getElementById('pipeline-shapes');
      pipelineEl.innerHTML = '';
      const maxTime = explainData.window_size || 100;

      explainData.conv_shapes.forEach((n, idx) => {
        const role = n.role || (idx === 0 ? 'input' : (idx === explainData.conv_shapes.length - 1 ? 'bottleneck' : 'conv'));
        const timeLen = n.time_len || 1;
        const timePct = Math.max(5, Math.round((timeLen / maxTime) * 100));

        const div = document.createElement('div');
        div.className = `pipeline-node role-${role}`;
        div.innerHTML = `
          <div class="node-rail">
            <span class="node-dot"></span>
          </div>
          <div class="node-main">
            <div class="node-top-row">
              <span class="layer-name">${n.layer}</span>
              <div class="node-badges">
                <span class="layer-shape">${n.shape}</span>
              </div>
            </div>
            <div class="node-bottom-row">
              <div class="temporal-bar-track" title="Độ dài trục thời gian: ${timeLen}/${maxTime}">
                <div class="temporal-bar-fill" style="width: ${timePct}%;"></div>
              </div>
              <span class="layer-sub">${n.sub || ''}</span>
            </div>
          </div>
        `;
        pipelineEl.appendChild(div);
      });

      // Render 128-D Signed Latent Embedding (Dual Heatmap + Zero-Centered Diverging Bars)
      const targetTag = explainData.is_custom_point ? 'Điểm nạp' : `t=${explainData.t}`;
      chartSlide2.drawEmbeddingChart(
        explainData.embedding,
        explainData.embedding_normal || null,
        {
          title: explainData.is_custom_point
            ? `Phân bố Vector Embedding 128 chiều (Điểm nạp vs. Chuẩn t=${explainData.normal_t})`
            : `Phân bố Vector Embedding 128 chiều (${targetTag} vs. Chuẩn t=${explainData.normal_t})`,
          targetLabel: targetTag,
          normalLabel: 'Normal',
          xLabel: `Latent Dimension (d0 → d${explainData.embedding.length - 1})`,
        }
      );
      document.getElementById('exp-text-2').textContent = explainData.explanations[1];
    } else if (currentStep === 2) {
      // Step 3: Decoder Target vs Normal + Interactive Binary Anomaly Mask {0, 1}
      const isCustom = explainData.is_custom_point;
      const winLen = explainData.win_target.length;
      const lastIdx = winLen - 1;
      const winSteps = Array.from({ length: winLen }, (_, i) => i + 1);
      const nFeat = explainData.n_features || 1;
      const fIdx = explainData.plot_feature_idx ?? 0;
      const featSuffix = nFeat > 1 ? ` — D${fIdx + 1}` : '';

      const mInfo = explainData.mask_info || {};
      const totalCells = mInfo.total_cells || (winLen * nFeat);
      const maskedCells = mInfo.masked_cells_target ?? 0;
      const keptCells = mInfo.kept_cells_target ?? (totalCells - maskedCells);
      const maskStepTarget = Array.isArray(mInfo.mask_step_target) ? mInfo.mask_step_target : Array(winLen).fill(1);
      const maskStepNormal = Array.isArray(mInfo.mask_step_normal) ? mInfo.mask_step_normal : Array(winLen).fill(1);
      const maskedChCountTarget = Array.isArray(mInfo.masked_ch_count_target) ? mInfo.masked_ch_count_target : Array(winLen).fill(0);
      const maskedChCountNormal = Array.isArray(mInfo.masked_ch_count_normal) ? mInfo.masked_ch_count_normal : Array(winLen).fill(0);
      const errTargetMaskedArr = Array.isArray(mInfo.err_sq_target_masked) ? mInfo.err_sq_target_masked : explainData.err_sq_target;
      const mseTargetUnmasked = explainData.mse_target;
      const mseTargetMasked = mInfo.mse_target_masked ?? mseTargetUnmasked;
      const mseNormalUnmasked = explainData.mse_normal;
      const mseNormalMasked = mInfo.mse_normal_masked ?? mseNormalUnmasked;

      // Sync Toggle Button & Card visual state
      const btnMaskToggle = document.getElementById('btn-toggle-decoder-mask');
      const lblMaskToggle = document.getElementById('lbl-toggle-decoder-mask');
      const maskCardEl = document.getElementById('decoder-mask-card');
      const maskTitleEl = document.getElementById('decoder-mask-title');
      if (btnMaskToggle) btnMaskToggle.classList.toggle('mask-on', isDecoderMaskEnabled);
      if (maskCardEl) maskCardEl.classList.toggle('mask-on', isDecoderMaskEnabled);
      if (lblMaskToggle) {
        lblMaskToggle.textContent = isDecoderMaskEnabled
          ? 'Anomaly Mask: BẬT (Huấn luyện)'
          : 'Anomaly Mask: TẮT (Kiểm thử)';
      }
      if (maskTitleEl) {
        maskTitleEl.textContent = isDecoderMaskEnabled
          ? 'MÔ PHỎNG HUẤN LUYỆN (BẬT MASK):'
          : 'CHẾ ĐỘ KIỂM THỬ (TẮT MASK):';
      }

      // Sync Anomaly Mask Summary Chips
      const chipShape = document.getElementById('mask-chip-shape');
      const chipKeep = document.getElementById('mask-chip-keep');
      const chipZero = document.getElementById('mask-chip-zero');
      if (chipShape) {
        chipShape.textContent = `Kích thước: ${nFeat} × ${winLen} (${totalCells.toLocaleString()} phần tử)`;
      }
      if (isDecoderMaskEnabled) {
        const keepPct = ((keptCells / Math.max(1, totalCells)) * 100).toFixed(1);
        const zeroPct = ((maskedCells / Math.max(1, totalCells)) * 100).toFixed(1);
        if (chipKeep) chipKeep.textContent = `Giữ lại (1): ${keptCells.toLocaleString()} phần tử (${keepPct}%)`;
        if (chipZero) chipZero.textContent = `Che lỗi (0): ${maskedCells.toLocaleString()} phần tử (${zeroPct}%)`;
      } else {
        if (chipKeep) chipKeep.textContent = `Giữ lại (1): ${totalCells.toLocaleString()} phần tử (100%)`;
        if (chipZero) chipZero.textContent = `Che lỗi (0): 0 phần tử (0%)`;
      }

      const makeStep3Tooltip = (isTargetChart) => (idx) => {
        const stepNum = idx + 1;
        const pillLabel = isTargetChart
          ? (isCustom ? (idx === lastIdx ? 'Điểm nạp (t=100)' : 'Ngữ cảnh') : `t = ${Math.max(0, explainData.t - 99 + idx)}`)
          : `Chuẩn t = ${Math.max(0, explainData.normal_t - 99 + idx)}`;
        const origVal = isTargetChart ? explainData.win_target[idx] : explainData.win_normal[idx];
        const recVal = isTargetChart ? explainData.rec_target[idx] : explainData.rec_normal[idx];
        const errT = explainData.err_sq_target[idx] ?? 0;
        const errTM = errTargetMaskedArr[idx] ?? errT;
        const errN = explainData.err_sq_normal[idx] ?? 0;
        const stepBit = isTargetChart ? maskStepTarget[idx] : maskStepNormal[idx];
        const chMaskedCnt = isTargetChart ? (maskedChCountTarget[idx] ?? 0) : (maskedChCountNormal[idx] ?? 0);

        const maskValStr = !isDecoderMaskEnabled
          ? '1 (Đang tắt Mask — mở 100%)'
          : (stepBit === 0
            ? `<span style="color:#d97706;font-weight:800">0 — Che lỗi${nFeat > 1 ? ` (${chMaskedCnt}/${nFeat} kênh)` : ''}</span>`
            : `<span style="color:#16a34a;font-weight:800">1 — Giữ lại${chMaskedCnt > 0 ? ` (che ${chMaskedCnt}/${nFeat} kênh khác)` : ''}</span>`);

        const mseRowHtml = isDecoderMaskEnabled
          ? `<div class="tt-row">
               <span class="tt-label">MSE bước này (Sau che Mask)</span>
               <span class="tt-val">${errT.toFixed(4)} &rarr; <strong>${errTM.toFixed(5)}</strong></span>
             </div>`
          : `<div class="tt-row">
               <span class="tt-label">MSE bước này (Khảo sát)</span>
               <span class="tt-val">${errT.toFixed(5)}</span>
             </div>`;

        return `
          <div class="tt-header"><span>Bước cửa sổ ${stepNum}/100</span><span class="tt-pill ${isTargetChart ? 'anom' : 'info'}">${pillLabel}</span></div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>Gốc${featSuffix}</span>
            <span class="tt-val">${(origVal ?? 0).toFixed(4)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#2563eb"></span>Tái tạo${featSuffix}</span>
            <span class="tt-val">${(recVal ?? 0).toFixed(4)}</span>
          </div>
          <div class="tt-row">
            <span class="tt-label">Trạng thái Mask</span>
            <span class="tt-val">${maskValStr}</span>
          </div>
          ${mseRowHtml}
          <div class="tt-row">
            <span class="tt-label">MSE bước này (Chuẩn)</span>
            <span class="tt-val">${errN.toFixed(5)}</span>
          </div>
        `;
      };

      const isStep3Anom = mseTargetUnmasked > Math.max(1e-4, mseNormalUnmasked * 2.0) || (explainData.winner_group && explainData.winner_group.is_anomaly);
      const activeTargetMse = isDecoderMaskEnabled ? mseTargetMasked : mseTargetUnmasked;
      const activeNormalMse = isDecoderMaskEnabled ? mseNormalMasked : mseNormalUnmasked;
      const step3TargetColor = isDecoderMaskEnabled
        ? '#d97706'
        : (isStep3Anom ? '#dc2626' : '#16a34a');

      chartSlide3Target.drawLineChart([
        { label: isCustom ? `Gốc (kèm t=100${featSuffix})` : `Gốc${featSuffix}`, data: explainData.win_target, color: '#334155', width: 2 },
        { label: `Tái tạo${featSuffix}`, data: explainData.rec_target, color: '#2563eb', width: 2 },
      ], {
        title: isCustom ? `Cửa sổ điểm nạp (t=100${featSuffix})` : `Cửa sổ khảo sát (t=${explainData.t}${featSuffix})`,
        xLabel: 'Thời gian trong cửa sổ (1 -> 100)',
        xValues: winSteps,
        syncCharts: [chartSlide3Normal],
        tooltipFormatter: makeStep3Tooltip(true),
        maskStrip: {
          enabled: isDecoderMaskEnabled,
          stepMask: maskStepTarget,
          maskedChCount: maskedChCountTarget,
          nFeatures: nFeat,
        },
        fillBetween: true,
        fillBetweenColor: isStep3Anom ? 'rgba(220, 38, 38, 0.16)' : 'rgba(22, 163, 74, 0.10)',
        badgeText: isDecoderMaskEnabled
          ? `MSE (Mask) = ${activeTargetMse.toFixed(4)}`
          : `MSE = ${activeTargetMse.toFixed(4)}`,
        badgeColor: step3TargetColor,
        pointMarker: isCustom ? { index: lastIdx, value: explainData.win_target[lastIdx], label: 'Điểm nạp (t=100)', color: step3TargetColor } : undefined,
      });

      const badgeMseTarget = document.getElementById('badge-mse-target');
      if (badgeMseTarget) {
        if (isDecoderMaskEnabled) {
          badgeMseTarget.textContent = `MSE (Mask) = ${activeTargetMse.toFixed(4)} (Gốc: ${mseTargetUnmasked.toFixed(4)})`;
          badgeMseTarget.style.background = '#fef3c7';
          badgeMseTarget.style.color = '#92400e';
        } else {
          badgeMseTarget.textContent = `MSE = ${mseTargetUnmasked.toFixed(4)}`;
          badgeMseTarget.style.background = isStep3Anom ? '#fee2e2' : '#dcfce7';
          badgeMseTarget.style.color = isStep3Anom ? '#b91c1c' : '#15803d';
        }
      }

      chartSlide3Normal.drawLineChart([
        { label: `Gốc${featSuffix}`, data: explainData.win_normal, color: '#334155', width: 2 },
        { label: `Tái tạo${featSuffix}`, data: explainData.rec_normal, color: '#2563eb', width: 2 },
      ], {
        title: `Cửa sổ chuẩn đối chứng (t=${explainData.normal_t}${featSuffix})`,
        xLabel: 'Thời gian trong cửa sổ (1 -> 100)',
        xValues: winSteps,
        syncCharts: [chartSlide3Target],
        tooltipFormatter: makeStep3Tooltip(false),
        maskStrip: {
          enabled: isDecoderMaskEnabled,
          stepMask: maskStepNormal,
          maskedChCount: maskedChCountNormal,
          nFeatures: nFeat,
        },
        fillBetween: true,
        fillBetweenColor: 'rgba(22, 163, 74, 0.10)',
        badgeText: isDecoderMaskEnabled
          ? `MSE (Mask) = ${activeNormalMse.toFixed(4)}`
          : `MSE = ${activeNormalMse.toFixed(4)}`,
        badgeColor: '#16a34a',
      });

      const badgeMseNormal = document.getElementById('badge-mse-normal');
      if (badgeMseNormal) {
        badgeMseNormal.textContent = isDecoderMaskEnabled
          ? `MSE (Mask) = ${activeNormalMse.toFixed(4)}`
          : `MSE = ${mseNormalUnmasked.toFixed(4)}`;
        badgeMseNormal.style.background = '#dcfce7';
        badgeMseNormal.style.color = '#15803d';
      }

      const maskNoteEl = document.getElementById('decoder-mask-note');
      const expText3El = document.getElementById('exp-text-3');
      if (isDecoderMaskEnabled) {
        const dropPct = mseTargetUnmasked > 1e-7
          ? Math.max(0, ((mseTargetUnmasked - mseTargetMasked) / mseTargetUnmasked) * 100).toFixed(1)
          : '0.0';
        if (maskNoteEl) {
          maskNoteEl.innerHTML = `Khóa <strong>${maskedCells.toLocaleString()}</strong> phần tử vượt chuẩn về 0 để Decoder chỉ học quy luật sóng bình thường — MSE giảm từ <strong>${mseTargetUnmasked.toFixed(4)}</strong> xuống <strong>${mseTargetMasked.toFixed(4)}</strong> (-${dropPct}%).`;
        }
        if (expText3El) {
          expText3El.textContent = `Khi bật Anomaly Mask: ${maskedCells.toLocaleString()}/${totalCells.toLocaleString()} phần tử vượt chuẩn bị che về 0 (vùng sọc vàng), hạ MSE từ ${mseTargetUnmasked.toFixed(4)} xuống ${mseTargetMasked.toFixed(4)} (cửa sổ chuẩn giữ nguyên MSE = ${activeNormalMse.toFixed(4)}).`;
        }
      } else {
        const ratio = mseNormalUnmasked > 1e-7 ? (mseTargetUnmasked / mseNormalUnmasked) : 1.0;
        if (maskNoteEl) {
          if (ratio >= 2.0) {
            maskNoteEl.innerHTML = `Mở toàn bộ <strong>${totalCells.toLocaleString()}</strong> phần tử làm lộ rõ độ lệch tại vùng sự cố: <strong>MSE = ${mseTargetUnmasked.toFixed(4)}</strong> (gấp <strong>${ratio.toFixed(0)} lần</strong> mức chuẩn ${mseNormalUnmasked.toFixed(4)}).`;
          } else {
            maskNoteEl.innerHTML = `Mở toàn bộ <strong>${totalCells.toLocaleString()}</strong> phần tử — Cửa sổ khảo sát <strong>MSE = ${mseTargetUnmasked.toFixed(4)}</strong> đối chiếu Cửa sổ chuẩn <strong>MSE = ${mseNormalUnmasked.toFixed(4)}</strong>.`;
          }
        }
        if (expText3El) {
          expText3El.textContent = explainData.explanations[2];
        }
      }
    } else if (currentStep === 3) {
      // Step 4: Classifier 12 Classes Target vs Normal (Synced Bar Highlight)
      const isCustom = explainData.is_custom_point;
      const targetBars = explainData.classes_target.map((c) => ({
        label: c.label,
        name_vi: c.name_vi,
        desc_vi: c.desc_vi,
        reason: c.reason,
        value: c.prob,
        isExcluded: c.excluded,
        isTop: c.is_winner,
      }));
      const normalBars = explainData.classes_normal.map((c) => ({
        label: c.label,
        name_vi: c.name_vi,
        desc_vi: c.desc_vi,
        reason: c.reason,
        value: c.prob,
        isExcluded: c.excluded,
        isTop: c.is_winner,
      }));

      const makeStep4Tooltip = (idx) => {
        const cT = explainData.classes_target[idx];
        const cN = explainData.classes_normal[idx];
        if (!cT) return '';
        const pill = cT.excluded
          ? '<span class="tt-pill muted">Đã lọc FAA</span>'
          : (cT.is_winner ? '<span class="tt-pill anom">Top Class</span>' : '<span class="tt-pill info">Hợp lệ</span>');
        const noteHtml = cT.excluded
          ? `<div class="tt-sub">Lý do loại trừ FAA: ${cT.reason || 'Mean Prob > 0.05'}</div>`
          : (cT.desc_vi ? `<div class="tt-sub">${cT.desc_vi}</div>` : '');
        return `
          <div class="tt-header"><span>#${idx} · ${cT.name_vi || cT.label}</span>${pill}</div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:${cT.excluded ? '#94a3b8' : (cT.is_winner ? '#dc2626' : '#2563eb')}"></span>Cửa sổ khảo sát</span>
            <span class="tt-val">${(cT.prob * 100).toFixed(2)}%</span>
          </div>
          <div class="tt-row">
            <span class="tt-label"><span class="tt-dot" style="background:#64748b"></span>Cửa sổ chuẩn (t=${explainData.normal_t})</span>
            <span class="tt-val">${cN ? (cN.prob * 100).toFixed(2) + '%' : '--'}</span>
          </div>
          ${noteHtml}
        `;
      };

      const topTargetLabel = explainData.winner_group?.name_vi || targetBars.find(b => b.isTop)?.label || 'normal';
      const topNormalBar = normalBars.find(b => b.isTop) || normalBars[0];
      const topNormalLabel = topNormalBar ? (topNormalBar.name_vi || topNormalBar.label) : 'normal';

      const badgeTopT = document.getElementById('badge-top-class-target');
      const badgeTopN = document.getElementById('badge-top-class-normal');
      if (badgeTopT) badgeTopT.textContent = `Top: ${topTargetLabel}`;
      if (badgeTopN) badgeTopN.textContent = `Top: ${topNormalLabel}`;

      chartSlide4Target.drawBarChart(targetBars, {
        title: isCustom ? 'Cửa sổ điểm nạp (t=100)' : `Cửa sổ khảo sát (t=${explainData.t})`,
        badgeText: `Top: ${topTargetLabel}`,
        syncCharts: [chartSlide4Normal],
        tooltipFormatter: makeStep4Tooltip,
      });

      chartSlide4Normal.drawBarChart(normalBars, {
        title: `Cửa sổ chuẩn đối chứng (t=${explainData.normal_t})`,
        badgeText: `Top: ${topNormalLabel}`,
        syncCharts: [chartSlide4Target],
        tooltipFormatter: makeStep4Tooltip,
      });

      document.getElementById('exp-text-4').textContent = explainData.explanations[3];
    } else if (currentStep === 4) {
      // Step 5: Combined score over time
      const isCustom = explainData.is_custom_point;
      const n5 = explainData.raw_comb_slice.length;
      const step5X = isCustom
        ? Array.from({ length: n5 }, (_, i) => (i === n5 - 1 ? 't=100 (Điểm nạp)' : `Lịch sử -${n5 - 1 - i}`))
        : explainData.time_slice;
      const curSliceIdx = !isCustom ? explainData.time_slice.indexOf(explainData.t) : (n5 - 1);
      const isTargetAnom = explainData.raw_combined > explainData.threshold;
      const step5Accent = isTargetAnom ? '#dc2626' : '#16a34a';

      chartSlide5.drawLineChart([
        { label: 'Raw MSE', data: explainData.score_rec_slice, color: '#334155', width: 2 },
        { label: 'Raw CE', data: explainData.score_ce_slice, color: '#2563eb', width: 2 },
        { label: 'Raw Combined Score', data: explainData.raw_comb_slice, color: '#dc2626', width: 2.5 },
      ], {
        title: isCustom ? 'Raw Combined Score của điểm nạp so với ngữ cảnh chuẩn' : 'Biến thiên Raw MSE, Raw CE & Raw Combined Score',
        xLabel: isCustom ? '50 bước chuẩn đối chứng & điểm nạp mới' : 'Chỉ số thời gian (t)',
        xValues: step5X,
        thresholdLine: explainData.threshold,
        badgeText: `Combined = ${explainData.raw_combined.toFixed(3)}`,
        badgeColor: step5Accent,
        pointMarker: curSliceIdx >= 0
          ? {
            index: curSliceIdx,
            value: explainData.raw_comb_slice[curSliceIdx],
            label: isCustom ? 'Điểm nạp mới' : `t=${explainData.t}`,
            color: step5Accent,
          }
          : undefined,
        onPointClick: !isCustom ? (_idx, realT) => loadExplainData(realT, true) : undefined,
        tooltipFormatter: (idx) => {
          const xTitle = isCustom ? step5X[idx] : `t = ${step5X[idx]}`;
          const rMse = explainData.score_rec_slice[idx] ?? 0;
          const rCe = explainData.score_ce_slice[idx] ?? 0;
          const rComb = explainData.raw_comb_slice[idx] ?? 0;
          const isAnom = rComb > explainData.threshold;
          const pill = isAnom
            ? '<span class="tt-pill anom">⚠️ BẤT THƯỜNG</span>'
            : '<span class="tt-pill ok">✓ BÌNH THƯỜNG</span>';
          const hint = !isCustom
            ? `<div class="tt-hint">🖱️ Double-click để xem giải thích chi tiết tại t = ${step5X[idx]}</div>`
            : '';
          return `
            <div class="tt-header"><span>${xTitle}</span>${pill}</div>
            <div class="tt-row">
              <span class="tt-label"><span class="tt-dot" style="background:#334155"></span>Raw MSE</span>
              <span class="tt-val">${rMse.toFixed(4)}</span>
            </div>
            <div class="tt-row">
              <span class="tt-label"><span class="tt-dot" style="background:#2563eb"></span>Raw CE</span>
              <span class="tt-val">${rCe.toFixed(4)}</span>
            </div>
            <div class="tt-row">
              <span class="tt-label"><span class="tt-dot" style="background:#dc2626"></span>Raw Combined Score</span>
              <span class="tt-val">${rComb.toFixed(4)}</span>
            </div>
            <div class="tt-row">
              <span class="tt-label">Ngưỡng μ + 3σ</span>
              <span class="tt-val">${explainData.threshold.toFixed(4)}</span>
            </div>
            ${hint}
          `;
        },
      });

      // Update Formula Card
      const eqEl = document.getElementById('formula-equation');
      const conclusionBadge = isTargetAnom
        ? '<span style="color:#dc2626; font-weight:bold;">BẤT THƯỜNG</span>'
        : '<span style="color:#16a34a; font-weight:bold;">BÌNH THƯỜNG</span>';
      eqEl.innerHTML = `
        (MSE + CE) / 2
        = (${explainData.raw_mse.toFixed(4)} + ${explainData.raw_ce.toFixed(4)}) / 2 
        = <strong>${explainData.raw_combined.toFixed(4)}</strong>
        (Ngưỡng μ + 3σ = ${explainData.threshold.toFixed(4)} &rArr; ${conclusionBadge})
      `;

      document.getElementById('exp-text-5').textContent = explainData.explanations[4];
    }
  }

  // 6. Navigation Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      SimpleCanvasChart.hideTooltip();
      closeFeaturePicker();
      closeEntityPicker();
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetId = btn.dataset.tab;
      document.getElementById(targetId).classList.add('active');

      // Trigger redraw of charts on tab display
      setTimeout(() => {
        if (targetId === 'tab-pretrain') renderOverviewChart();
        else if (targetId === 'tab-predict') {
          if (lastPredictedResult) {
            renderPredictWindowChart(
              lastPredictedResult.window_input,
              lastPredictedResult.reconstructed,
              lastPredictedResult.raw_mse,
              lastPredictedResult.is_anomaly
            );
          } else if (explainData && explainData.win_normal) {
            renderPredictWindowChart(
              explainData.win_normal.map(v => [v]),
              explainData.rec_normal.map(v => [v]),
              explainData.mse_normal,
              false
            );
          }
        }
        else if (targetId === 'tab-explain') renderCurrentStep();
      }, 50);
    });
  });

  window.addEventListener('resize', () => {
    SimpleCanvasChart.hideTooltip();
    closeFeaturePicker();
    closeEntityPicker();
    const activeTab = document.querySelector('.tab-content.active');
    if (!activeTab) return;
    if (activeTab.id === 'tab-pretrain') renderOverviewChart();
    else if (activeTab.id === 'tab-predict' && lastPredictedResult) {
      renderPredictWindowChart(
        lastPredictedResult.window_input,
        lastPredictedResult.reconstructed,
        lastPredictedResult.raw_mse,
        lastPredictedResult.is_anomaly
      );
    } else if (activeTab.id === 'tab-explain') renderCurrentStep();
  });

  // Export PNG buttons (use live chart instances so offscreen snapshot is preserved)
  const btnToggleMask = document.getElementById('btn-toggle-decoder-mask');
  if (btnToggleMask) {
    btnToggleMask.addEventListener('click', () => {
      isDecoderMaskEnabled = !isDecoderMaskEnabled;
      SimpleCanvasChart.hideTooltip();
      renderCurrentStep();
    });
  }

  const btnExpOverview = document.getElementById('btn-export-overview');
  if (btnExpOverview) {
    btnExpOverview.onclick = () => chartOverview && chartOverview.exportPNG(`overview_${currentEntity}.png`);
  }
  const btnExpPredict = document.getElementById('btn-export-predict-chart');
  if (btnExpPredict) {
    btnExpPredict.onclick = () => chartPredict && chartPredict.exportPNG(`predict_${currentEntity}.png`);
  }
  const exportChartMap = {
    'canvas-slide-1': () => chartSlide1,
    'canvas-slide-2': () => chartSlide2,
    'canvas-slide-3-target': () => chartSlide3Target,
    'canvas-slide-4-target': () => chartSlide4Target,
    'canvas-slide-5': () => chartSlide5,
  };
  document.querySelectorAll('.btn-export').forEach(btn => {
    btn.onclick = () => {
      const cid = btn.dataset.canvas;
      const getter = exportChartMap[cid];
      const inst = getter ? getter() : null;
      if (inst) inst.exportPNG(`${cid}_${currentEntity}.png`);
    };
  });

  // Init
  initCharts();
  setupWalkthroughControls();
  loadIndex();
});

