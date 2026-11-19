/**
 * RedLamp Canvas Charting Engine
 * 100% Offline, Zero external dependencies.
 * Features:
 * - High-DPI Retina rendering + Offscreen Base Snapshot for 60 FPS interactive hover.
 * - Floating HTML Tooltip (auto-flips near viewport edges) + Crosshair & Point Snapping.
 * - Synced Crosshair / Bar Highlight across paired comparison charts.
 * - Click-to-Inspect callback (e.g., jump directly to timestep t).
 * - Clean PNG export (always exports base snapshot without hover overlays).
 */

class SimpleCanvasChart {
  static _tooltipEl = null;

  static _getTooltipEl() {
    if (!SimpleCanvasChart._tooltipEl) {
      let el = document.getElementById('redlamp-chart-tooltip');
      if (!el) {
        el = document.createElement('div');
        el.id = 'redlamp-chart-tooltip';
        el.className = 'chart-tooltip';
        el.style.display = 'none';
        document.body.appendChild(el);
      }
      SimpleCanvasChart._tooltipEl = el;
    }
    return SimpleCanvasChart._tooltipEl;
  }

  static showTooltip(clientX, clientY, html) {
    if (!html) {
      SimpleCanvasChart.hideTooltip();
      return;
    }
    const el = SimpleCanvasChart._getTooltipEl();
    el.innerHTML = html;
    el.style.display = 'block';

    const rect = el.getBoundingClientRect();
    const pad = 14;
    let left = clientX + pad;
    let top = clientY - rect.height / 2;

    if (left + rect.width > window.innerWidth - 10) {
      left = clientX - rect.width - pad;
    }
    if (left < 8) left = 8;
    if (top + rect.height > window.innerHeight - 10) {
      top = window.innerHeight - rect.height - 10;
    }
    if (top < 8) top = 8;

    el.style.left = `${Math.round(left)}px`;
    el.style.top = `${Math.round(top)}px`;
  }

  static hideTooltip() {
    const el = SimpleCanvasChart._tooltipEl;
    if (el) el.style.display = 'none';
  }

  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this._lastDraw = null;
    this._baseCanvas = null;
    this._meta = null;
    this._hoverIdx = -1;
    this.resize();

    const onResize = () => {
      if (this._resizeRaf) cancelAnimationFrame(this._resizeRaf);
      this._resizeRaf = requestAnimationFrame(() => {
        SimpleCanvasChart.hideTooltip();
        if (this._lastDraw) {
          this._lastDraw();
        } else {
          this.resize();
        }
      });
    };

    window.addEventListener('resize', onResize);
    if (window.ResizeObserver && this.canvas.parentElement) {
      this._ro = new ResizeObserver(onResize);
      this._ro.observe(this.canvas.parentElement);
    }

    this.canvas.style.userSelect = 'none';
    this.canvas.addEventListener('mousemove', (e) => this._handleMouseMove(e));
    this.canvas.addEventListener('mouseleave', () => this._handleMouseLeave());
    this.canvas.addEventListener('dblclick', (e) => this._handleDblClick(e));
  }

  resize() {
    if (!this.canvas) return false;
    const host = this.canvas.parentElement || this.canvas;
    const rect = host.getBoundingClientRect();
    if (!rect.width || !rect.height) return false;
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = Math.round(rect.width * dpr);
    this.canvas.height = Math.round(rect.height * dpr);
    this.dpr = dpr;
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    return true;
  }

  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    this.ctx.fillStyle = '#ffffff';
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  _saveBaseSnapshot() {
    if (!this.width || !this.height) return;
    if (!this._baseCanvas) {
      this._baseCanvas = document.createElement('canvas');
    }
    this._baseCanvas.width = this.width;
    this._baseCanvas.height = this.height;
    const bctx = this._baseCanvas.getContext('2d');
    bctx.clearRect(0, 0, this.width, this.height);
    bctx.drawImage(this.canvas, 0, 0);
    this._hoverIdx = -1;
  }

  _restoreBaseSnapshot() {
    if (!this._baseCanvas || !this.width || !this.height) return false;
    this.ctx.clearRect(0, 0, this.width, this.height);
    this.ctx.drawImage(this._baseCanvas, 0, 0);
    return true;
  }

  clearHover() {
    this._hoverIdx = -1;
    this._restoreBaseSnapshot();
  }

  exportPNG(filename = 'chart.png') {
    const srcCanvas = this._baseCanvas || this.canvas;
    if (!srcCanvas) return;
    const link = document.createElement('a');
    link.download = filename;
    link.href = srcCanvas.toDataURL('image/png');
    link.click();
  }

  _hitTestIndex(e) {
    if (!this._meta || !this.canvas) return -1;
    const rect = this.canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return -1;
    const mx = (e.clientX - rect.left) * this.dpr;
    const my = (e.clientY - rect.top) * this.dpr;
    const m = this._meta;
    const dpr = this.dpr;

    if (m.type === 'line') {
      if (
        mx < m.padLeft - 8 * dpr ||
        mx > m.padLeft + m.plotW + 8 * dpr ||
        my < m.padTop - 10 * dpr ||
        my > m.padTop + m.plotH + 18 * dpr
      ) {
        return -1;
      }
      if (m.maxLen <= 1) return 0;
      const ratio = (mx - m.padLeft) / m.plotW;
      return Math.max(0, Math.min(m.maxLen - 1, Math.round(ratio * (m.maxLen - 1))));
    }

    if (m.type === 'bar') {
      if (
        mx < m.padLeft ||
        mx > m.padLeft + m.plotW ||
        my < m.padTop - 8 * dpr ||
        my > m.padTop + m.plotH + 30 * dpr
      ) {
        return -1;
      }
      return Math.max(0, Math.min(m.n - 1, Math.floor((mx - m.padLeft) / m.barStep)));
    }

    if (m.type === 'embedding') {
      if (
        mx < m.padLeft ||
        mx > m.padLeft + m.plotW ||
        my < m.stripTop - 6 * dpr ||
        my > m.barTop + m.plotH + 20 * dpr
      ) {
        return -1;
      }
      return Math.max(0, Math.min(m.n - 1, Math.floor((mx - m.padLeft) / m.cellW)));
    }

    return -1;
  }

  _handleMouseMove(e) {
    const idx = this._hitTestIndex(e);
    if (idx < 0) {
      this._handleMouseLeave();
      return;
    }

    const m = this._meta;
    this._renderHoverOverlay(idx, false);

    // Sync partner charts if configured
    if (m.options && Array.isArray(m.options.syncCharts)) {
      m.options.syncCharts.forEach(partner => {
        if (partner && partner !== this) {
          partner._renderHoverOverlay(idx, true);
        }
      });
    }

    let html = '';
    if (m.options && typeof m.options.tooltipFormatter === 'function') {
      html = m.options.tooltipFormatter(idx);
    } else if (m.type === 'line') {
      html = this._defaultLineTooltip(idx);
    } else if (m.type === 'bar') {
      html = this._defaultBarTooltip(idx);
    } else if (m.type === 'embedding') {
      html = this._defaultEmbeddingTooltip(idx);
    }
    SimpleCanvasChart.showTooltip(e.clientX, e.clientY, html);
  }

  _handleMouseLeave() {
    this.clearHover();
    if (this._meta && this._meta.options && Array.isArray(this._meta.options.syncCharts)) {
      this._meta.options.syncCharts.forEach(partner => {
        if (partner && partner !== this) partner.clearHover();
      });
    }
    SimpleCanvasChart.hideTooltip();
  }

  _handleDblClick(e) {
    if (!this._meta || !this._meta.options || typeof this._meta.options.onPointClick !== 'function') {
      return;
    }
    e.preventDefault();
    const idx = this._hitTestIndex(e);
    if (idx < 0) return;
    let payload = idx;
    if (this._meta.type === 'bar' && this._meta.bars && this._meta.bars[idx]) {
      const b = this._meta.bars[idx];
      payload = b.clickValue !== undefined ? b.clickValue : b.label;
    } else {
      const xVals = this._meta.options.xValues;
      payload = Array.isArray(xVals) && xVals[idx] !== undefined ? xVals[idx] : idx;
    }
    SimpleCanvasChart.hideTooltip();
    this._meta.options.onPointClick(idx, payload);
  }

  _renderHoverOverlay(idx, isPartnerSync = false) {
    if (!this._meta || !this._restoreBaseSnapshot()) return;
    const m = this._meta;
    const ctx = this.ctx;
    const dpr = this.dpr;
    const fontStack = "'Segoe UI', Roboto, Arial, sans-serif";
    this._hoverIdx = idx;

    if (m.type === 'line') {
      if (idx < 0 || idx >= m.maxLen) return;
      const x = m.getX(idx);

      // Vertical dashed crosshair
      ctx.save();
      ctx.strokeStyle = isPartnerSync ? '#64748b' : '#0f172a';
      ctx.lineWidth = 1.5 * dpr;
      ctx.setLineDash([4 * dpr, 4 * dpr]);
      ctx.beginPath();
      ctx.moveTo(x, m.padTop);
      ctx.lineTo(x, m.padTop + m.plotH);
      ctx.stroke();
      ctx.setLineDash([]);

      // Snap dots on each series
      m.lines.slice(0, 3).forEach(line => {
        if (!line.data || line.data[idx] === undefined) return;
        const y = m.getY(line.data[idx]);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(x, y, 6 * dpr, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = line.color || '#334155';
        ctx.beginPath();
        ctx.arc(x, y, 4.2 * dpr, 0, Math.PI * 2);
        ctx.fill();
      });

      // Partner sync compact readout pill right on partner canvas
      if (isPartnerSync) {
        const xVal = (m.options.xValues && m.options.xValues[idx] !== undefined) ? m.options.xValues[idx] : idx;
        const parts = [`t=${xVal}`];
        m.lines.slice(0, 2).forEach(line => {
          if (line.data && line.data[idx] !== undefined) {
            parts.push(`${line.label}: ${line.data[idx].toFixed(3)}`);
          }
        });
        const pillTxt = parts.join(' | ');
        ctx.font = `bold ${Math.round(12 * m.scale * dpr)}px ${fontStack}`;
        const pw = ctx.measureText(pillTxt).width + 16 * dpr;
        const ph = 24 * dpr;
        const px = Math.max(m.padLeft + 4 * dpr, Math.min(m.padLeft + m.plotW - pw - 4 * dpr, x - pw / 2));
        const py = m.padTop + 6 * dpr;

        ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(px, py, pw, ph, 4 * dpr) : ctx.rect(px, py, pw, ph);
        ctx.fill();

        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pillTxt, px + pw / 2, py + ph / 2);
      }
      ctx.restore();
    } else if (m.type === 'bar') {
      if (idx < 0 || idx >= m.n) return;
      const bar = m.bars[idx];
      const val = Math.max(0, bar.value || 0);
      const barMaxH = m.barMaxH || m.plotH;
      const bH = (val / m.yMax) * barMaxH;
      const colX = m.padLeft + idx * m.barStep;
      const bx = colX + (m.barStep - m.barWidth) / 2;
      const by = m.padTop + m.plotH - bH;

      ctx.save();
      ctx.fillStyle = 'rgba(37, 99, 235, 0.08)';
      ctx.fillRect(colX, m.padTop, m.barStep, m.plotH);

      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2 * dpr;
      ctx.strokeRect(bx, by, m.barWidth, Math.max(2 * dpr, bH));

      if (isPartnerSync) {
        const pctTxt = `${(val * 100).toFixed(1)}%`;
        ctx.font = `bold ${Math.round(12.5 * m.scale * dpr)}px ${fontStack}`;
        const tw = ctx.measureText(pctTxt).width + 10 * dpr;
        const th = 20 * dpr;
        const tx = Math.max(m.padLeft, Math.min(m.padLeft + m.plotW - tw, bx + m.barWidth / 2 - tw / 2));
        const ty = Math.max(m.padTop + 2 * dpr, by - th - 5 * dpr);

        ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(tx, ty, tw, th, 4 * dpr) : ctx.rect(tx, ty, tw, th);
        ctx.fill();

        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pctTxt, tx + tw / 2, ty + th / 2);
      }
      ctx.restore();
    } else if (m.type === 'embedding') {
      if (idx < 0 || idx >= m.n) return;
      const colX = m.padLeft + idx * m.cellW;
      const cx = colX + m.cellW / 2;
      const v = m.embTarget[idx];
      const vy = m.getY(v);

      ctx.save();
      // Highlight column across bar area
      ctx.fillStyle = 'rgba(37, 99, 235, 0.11)';
      ctx.fillRect(colX - 1 * dpr, m.barTop, Math.max(3 * dpr, m.cellW + 2 * dpr), m.plotH);

      // Highlight cell on heatmap strip(s)
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = 2 * dpr;
      ctx.strokeRect(colX - 0.5 * dpr, m.stripTop - 1 * dpr, Math.max(3 * dpr, m.cellW + 1 * dpr), m.stripTotalH + 2 * dpr);

      // Verticalhair inside bar plot
      ctx.strokeStyle = 'rgba(15, 23, 42, 0.55)';
      ctx.lineWidth = 1.2 * dpr;
      ctx.setLineDash([3 * dpr, 3 * dpr]);
      ctx.beginPath();
      ctx.moveTo(cx, m.barTop);
      ctx.lineTo(cx, m.barTop + m.plotH);
      ctx.stroke();
      ctx.setLineDash([]);

      // Normal reference dot if available
      if (m.hasNormal) {
        const ny = m.getY(m.embNormal[idx]);
        ctx.fillStyle = '#64748b';
        ctx.beginPath();
        ctx.arc(cx, ny, 3.8 * dpr, 0, Math.PI * 2);
        ctx.fill();
      }

      // Target value dot
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(cx, vy, 5.5 * dpr, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = v >= 0 ? '#2563eb' : '#dc2626';
      ctx.beginPath();
      ctx.arc(cx, vy, 4 * dpr, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  _defaultLineTooltip(idx) {
    const m = this._meta;
    const xVal = (m.options.xValues && m.options.xValues[idx] !== undefined) ? m.options.xValues[idx] : idx;
    let rows = '';
    m.lines.slice(0, 3).forEach(line => {
      if (!line.data || line.data[idx] === undefined) return;
      rows += `
        <div class="tt-row">
          <span class="tt-label"><span class="tt-dot" style="background:${line.color || '#334155'}"></span>${line.label}</span>
          <span class="tt-val">${line.data[idx].toFixed(4)}</span>
        </div>
      `;
    });
    return `<div class="tt-header"><span>t = ${xVal}</span></div>${rows}`;
  }

  _defaultBarTooltip(idx) {
    const bar = this._meta.bars[idx];
    const title = bar.name_vi || bar.label;
    const pill = bar.isExcluded
      ? '<span class="tt-pill muted">Đã lọc FAA</span>'
      : (bar.isTop ? '<span class="tt-pill anom">Top Class</span>' : '<span class="tt-pill info">Hợp lệ</span>');
    const faaRow = bar.isExcluded
      ? `<div class="tt-sub">FAA loại trừ: ${bar.reason || 'Mean Prob > 0.05'}</div>`
      : (bar.desc_vi ? `<div class="tt-sub">${bar.desc_vi}</div>` : '');
    return `
      <div class="tt-header"><span>${title}</span>${pill}</div>
      <div class="tt-row">
        <span class="tt-label">Xác suất dự đoán</span>
        <span class="tt-val">${(bar.value * 100).toFixed(2)}%</span>
      </div>
      ${faaRow}
    `;
  }

  _defaultEmbeddingTooltip(idx) {
    const m = this._meta;
    const tv = m.embTarget[idx];
    const tSign = tv >= 0 ? '+' : '';
    const pill = tv >= 0
      ? '<span class="tt-pill info">Dương (+)</span>'
      : '<span class="tt-pill anom">Âm (-)</span>';
    let normRows = '';
    if (m.hasNormal) {
      const nv = m.embNormal[idx];
      const dv = tv - nv;
      normRows = `
        <div class="tt-row">
          <span class="tt-label"><span class="tt-dot" style="background:#94a3b8"></span>Baseline Normal</span>
          <span class="tt-val">${nv >= 0 ? '+' : ''}${nv.toFixed(4)}</span>
        </div>
        <div class="tt-row">
          <span class="tt-label">Độ lệch (z - z_norm)</span>
          <span class="tt-val">${dv >= 0 ? '+' : ''}${dv.toFixed(4)}</span>
        </div>
      `;
    }
    return `
      <div class="tt-header"><span>Chiều d${idx} / d${m.n - 1}</span>${pill}</div>
      <div class="tt-row">
        <span class="tt-label"><span class="tt-dot" style="background:${tv >= 0 ? '#2563eb' : '#dc2626'}"></span>${m.options.targetLabel || 'Đang xét'}</span>
        <span class="tt-val">${tSign}${tv.toFixed(4)}</span>
      </div>
      ${normRows}
    `;
  }

  /**
   * Draw Line Chart
   * lines: Array of { label, data: number[], color, width, dashed }
   * options: { title, xLabel, xValues, yMin, yMax, highlightWindow: [start, end], thresholdLine: val, badgeText: str, pointMarker, tooltipFormatter, onPointClick, syncCharts }
   */
  drawLineChart(lines, options = {}) {
    this._lastDraw = () => this.drawLineChart(lines, options);
    if (!this.resize()) return;
    this.clear();
    const ctx = this.ctx;
    const dpr = this.dpr;
    this.canvas.style.cursor = 'crosshair';

    const cssH = this.height / dpr;
    const scale = Math.min(1.0, Math.max(0.72, cssH / 300));
    const fontStack = "'Segoe UI', Roboto, Arial, sans-serif";

    const FONT_TITLE = `bold ${Math.round(17 * scale * dpr)}px ${fontStack}`;
    const FONT_LABEL = `600 ${Math.round(13.5 * scale * dpr)}px ${fontStack}`;
    const FONT_XTICK = `600 ${Math.round(12 * scale * dpr)}px ${fontStack}`;
    const FONT_BADGE = `bold ${Math.round(14.5 * scale * dpr)}px ${fontStack}`;

    const visibleLegendLines = lines.slice(0, 3).filter(l => l && l.label);
    const hasLegend = visibleLegendLines.length > 0;

    const hasMaskStrip = Boolean(options.maskStrip && Array.isArray(options.maskStrip.stepMask) && options.maskStrip.stepMask.length > 0);
    const maskStripExtra = hasMaskStrip ? Math.round(16 * scale * dpr) : 0;

    const padLeft = Math.round(64 * scale * dpr);
    const padRight = Math.round(26 * scale * dpr);
    const padTop = (options.title
      ? Math.round((hasLegend ? 55 : 42) * scale * dpr)
      : Math.round((hasLegend ? 32 : 22) * scale * dpr)) + maskStripExtra;
    const padBottom = Math.round(48 * scale * dpr);

    const plotW = this.width - padLeft - padRight;
    const plotH = this.height - padTop - padBottom;

    if (plotW <= 0 || plotH <= 0) return;

    // Determine clean Y-axis domain + inner pixel headroom (prevents distorted ticks like -0.08..1.08)
    let allVals = [];
    lines.forEach(l => {
      if (l.data) allVals = allVals.concat(l.data);
    });
    if (options.thresholdLine !== undefined) allVals.push(options.thresholdLine);

    let rawMin = options.yMin !== undefined ? options.yMin : (allVals.length ? Math.min(...allVals) : 0);
    let rawMax = options.yMax !== undefined ? options.yMax : (allVals.length ? Math.max(...allVals) : 1);
    if (!Number.isFinite(rawMin) || !Number.isFinite(rawMax)) {
      rawMin = 0;
      rawMax = 1;
    }

    let axisMin = rawMin;
    let axisMax = rawMax;
    let tickStep = 0.25;

    if (options.yMin !== undefined && options.yMax !== undefined && options.yMax > options.yMin) {
      axisMin = options.yMin;
      axisMax = options.yMax;
      tickStep = (axisMax - axisMin) / 4;
    } else if (rawMin >= -1e-6 && rawMax <= 1.0001 && (rawMax - rawMin) >= 0.45) {
      axisMin = 0;
      axisMax = 1.0;
      tickStep = 0.25;
    } else {
      if (Math.abs(rawMax - rawMin) < 1e-9) {
        if (Math.abs(rawMin) < 1e-9) {
          rawMin = 0;
          rawMax = 1;
        } else if (rawMin > 0) {
          rawMin = Math.max(0, rawMin * 0.9);
          rawMax = rawMax * 1.1;
        } else {
          rawMin = rawMin * 1.1;
          rawMax = rawMax * 0.9;
        }
      }
      const span = Math.max(1e-6, rawMax - rawMin);
      const basePow = Math.pow(10, Math.floor(Math.log10(span / 4)));
      const mults = [1, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20];
      let matched = false;
      for (const mVal of mults) {
        const s = basePow * mVal;
        let lo = Math.floor((rawMin + 1e-11) / s) * s;
        if (rawMin >= -1e-9 && lo < 0) lo = 0;
        if (rawMin >= 0 && lo > 0 && rawMin < 0.75 * s) lo = 0;
        const hi = lo + 4 * s;
        if (hi >= rawMax - 1e-9) {
          axisMin = lo;
          axisMax = hi;
          tickStep = s;
          matched = true;
          break;
        }
      }
      if (!matched) {
        tickStep = span / 4;
        axisMin = rawMin;
        axisMax = rawMax;
      }
    }

    let yDecimals = 2;
    if (tickStep >= 100) yDecimals = 0;
    else if (tickStep >= 10) yDecimals = 1;
    else if (Math.abs(Math.round(tickStep * 100) - tickStep * 100) < 1e-6) yDecimals = 2;
    else if (Math.abs(Math.round(tickStep * 1000) - tickStep * 1000) < 1e-6) yDecimals = 3;
    else yDecimals = 4;

    const maxLen = Math.max(...lines.map(l => (l.data ? l.data.length : 0)), 1);
    const padInnerY = Math.round(7 * scale * dpr);
    const innerH = Math.max(10, plotH - padInnerY * 2);

    // Coordinate conversion (clean axis domain with subtle inner pixel breathing room)
    const getX = (idx) => padLeft + (idx / (maxLen - 1 || 1)) * plotW;
    const getY = (val) => padTop + padInnerY + (1 - (val - axisMin) / (axisMax - axisMin || 1)) * innerH;

    // 1. Draw Highlight Window if specified (e.g. 100 points window in red/pink area)
    if (options.highlightWindow && options.highlightWindow.length === 2) {
      const [hStart, hEnd] = options.highlightWindow;
      const x1 = Math.max(padLeft, getX(hStart));
      const x2 = Math.min(padLeft + plotW, getX(hEnd));
      ctx.fillStyle = 'rgba(220, 38, 38, 0.16)';
      ctx.fillRect(x1, padTop, x2 - x1, plotH);
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 2 * dpr;
      ctx.setLineDash([4 * dpr, 4 * dpr]);
      ctx.strokeRect(x1, padTop, x2 - x1, plotH);
      ctx.setLineDash([]);
    }

    // 2. Draw Axes and Grid
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1 * dpr;
    ctx.beginPath();
    for (let i = 0; i <= 4; i++) {
      const v = axisMin + (i / 4) * (axisMax - axisMin);
      const y = getY(v);
      ctx.moveTo(padLeft, y);
      ctx.lineTo(padLeft + plotW, y);

      ctx.fillStyle = '#64748b';
      ctx.font = FONT_LABEL;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      const cleanV = Math.abs(v) < 1e-10 ? 0 : v;
      ctx.fillText(cleanV.toFixed(yDecimals), padLeft - 10 * dpr, y);
    }
    ctx.stroke();

    // 2.5. Draw X-Axis Numeric Ticks (5 clean ticks showing real t)
    const axisBottomY = padTop + plotH;
    const tickCount = Math.min(5, maxLen);
    if (tickCount >= 2) {
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1 * dpr;
      ctx.beginPath();
      ctx.moveTo(padLeft, axisBottomY);
      ctx.lineTo(padLeft + plotW, axisBottomY);
      for (let k = 0; k < tickCount; k++) {
        const idx = Math.round((k * (maxLen - 1)) / (tickCount - 1));
        const tx = getX(idx);
        ctx.moveTo(tx, axisBottomY);
        ctx.lineTo(tx, axisBottomY + 4 * dpr);
      }
      ctx.stroke();

      ctx.fillStyle = '#64748b';
      ctx.font = FONT_XTICK;
      ctx.textBaseline = 'top';
      for (let k = 0; k < tickCount; k++) {
        const idx = Math.round((k * (maxLen - 1)) / (tickCount - 1));
        const tx = getX(idx);
        const rawX = (Array.isArray(options.xValues) && options.xValues[idx] !== undefined)
          ? options.xValues[idx]
          : idx;
        ctx.textAlign = k === 0 ? 'left' : (k === tickCount - 1 ? 'right' : 'center');
        ctx.fillText(String(rawX), tx, axisBottomY + 5 * dpr);
      }
    }

    // 2.7. Optional Binary Anomaly Mask Strip (top barcode 0/1) & Masked Curtain Overlay
    const maskCfg = hasMaskStrip ? options.maskStrip : null;
    const isMaskActive = Boolean(maskCfg && maskCfg.enabled);
    if (maskCfg) {
      const stripArr = maskCfg.stepMask;
      const chCounts = maskCfg.maskedChCount || [];
      const sLen = stripArr.length;
      const stripH = Math.round(9 * scale * dpr);
      const stripY = padTop - stripH - Math.round(4 * scale * dpr);

      ctx.save();
      ctx.font = `bold ${Math.round(11 * scale * dpr)}px ${fontStack}`;
      ctx.fillStyle = isMaskActive ? '#b45309' : '#64748b';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText('Mask:', padLeft - 8 * dpr, stripY + stripH / 2);

      for (let i = 0; i < sLen; i++) {
        const xStart = sLen > 1
          ? (i === 0 ? padLeft : (getX(i - 1) + getX(i)) / 2)
          : padLeft;
        const xEnd = sLen > 1
          ? (i === sLen - 1 ? padLeft + plotW : (getX(i) + getX(i + 1)) / 2)
          : padLeft + plotW;
        let cellColor = '#bbf7d0'; // Mask OFF: all 1s (open)
        if (isMaskActive) {
          if (stripArr[i] === 0) cellColor = '#f59e0b'; // 0 = masked out on this channel
          else if ((chCounts[i] || 0) > 0) cellColor = '#fde68a'; // 0 on other channels
          else cellColor = '#22c55e'; // 1 = kept across all channels
        }
        ctx.fillStyle = cellColor;
        ctx.fillRect(xStart, stripY, Math.max(1, xEnd - xStart + 0.5), stripH);
      }
      ctx.strokeStyle = isMaskActive ? '#d97706' : '#86efac';
      ctx.lineWidth = 1 * dpr;
      ctx.strokeRect(padLeft, stripY, plotW, stripH);

      // Draw hatched amber curtain over masked spans (stepMask[i] === 0) when Mask is ON
      if (isMaskActive) {
        let spanStart = -1;
        const drawMaskedSpan = (a, b) => {
          const sx1 = sLen > 1 ? (a === 0 ? padLeft : (getX(a - 1) + getX(a)) / 2) : padLeft;
          const sx2 = sLen > 1 ? (b === sLen - 1 ? padLeft + plotW : (getX(b) + getX(b + 1)) / 2) : padLeft + plotW;
          const sw = Math.max(3 * dpr, sx2 - sx1);
          ctx.save();
          ctx.fillStyle = 'rgba(245, 158, 11, 0.14)';
          ctx.fillRect(sx1, padTop, sw, plotH);

          // Diagonal hatch lines inside masked zone
          ctx.beginPath();
          ctx.rect(sx1, padTop, sw, plotH);
          ctx.clip();
          ctx.strokeStyle = 'rgba(217, 119, 6, 0.24)';
          ctx.lineWidth = 1.2 * dpr;
          const stepPx = Math.round(11 * scale * dpr);
          for (let hx = sx1 - plotH; hx < sx2 + plotH; hx += stepPx) {
            ctx.moveTo(hx, padTop + plotH);
            ctx.lineTo(hx + plotH, padTop);
          }
          ctx.stroke();
          ctx.restore();

          ctx.save();
          ctx.strokeStyle = 'rgba(217, 119, 6, 0.65)';
          ctx.lineWidth = 1.3 * dpr;
          ctx.setLineDash([4 * dpr, 3 * dpr]);
          ctx.strokeRect(sx1, padTop, sw, plotH);
          ctx.restore();
        };

        for (let i = 0; i < sLen; i++) {
          if (stripArr[i] === 0) {
            if (spanStart < 0) spanStart = i;
          } else if (spanStart >= 0) {
            drawMaskedSpan(spanStart, i - 1);
            spanStart = -1;
          }
        }
        if (spanStart >= 0) drawMaskedSpan(spanStart, sLen - 1);
      }
      ctx.restore();
    }

    // 2.8. Optional Shaded Divergence Area Between Line 0 (Original) & Line 1 (Reconstructed)
    if (options.fillBetween && lines.length >= 2 && lines[0].data && lines[1].data) {
      const len = Math.min(lines[0].data.length, lines[1].data.length);
      if (len > 1) {
        const fillSpan = (a, b) => {
          if (b <= a) return;
          ctx.save();
          ctx.fillStyle = options.fillBetweenColor || 'rgba(220, 38, 38, 0.14)';
          ctx.beginPath();
          for (let i = a; i <= b; i++) {
            const x = getX(i);
            const y = getY(lines[0].data[i]);
            if (i === a) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          for (let i = b; i >= a; i--) {
            ctx.lineTo(getX(i), getY(lines[1].data[i]));
          }
          ctx.closePath();
          ctx.fill();
          ctx.restore();
        };

        if (isMaskActive && maskCfg && Array.isArray(maskCfg.stepMask)) {
          let segStart = -1;
          for (let i = 0; i < len; i++) {
            if (maskCfg.stepMask[i] !== 0) {
              if (segStart < 0) segStart = i;
            } else if (segStart >= 0) {
              fillSpan(segStart, i - 1);
              segStart = -1;
            }
          }
          if (segStart >= 0) fillSpan(segStart, len - 1);
        } else {
          fillSpan(0, len - 1);
        }
      }
    }

    // 3. Draw Lines (Max 3 lines)
    lines.slice(0, 3).forEach((line) => {
      if (!line.data || line.data.length === 0) return;
      ctx.strokeStyle = line.color || '#334155';
      ctx.lineWidth = (line.width || 2) * dpr;
      if (line.dashed) {
        ctx.setLineDash([5 * dpr, 5 * dpr]);
      } else {
        ctx.setLineDash([]);
      }

      ctx.beginPath();
      for (let i = 0; i < line.data.length; i++) {
        const x = getX(i);
        const y = getY(line.data[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // 4. Threshold Line if specified (Dashed Red Line + Opaque Pill Label)
    if (options.thresholdLine !== undefined) {
      const ty = getY(options.thresholdLine);
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 2.2 * dpr;
      ctx.setLineDash([6 * dpr, 5 * dpr]);
      ctx.beginPath();
      ctx.moveTo(padLeft, ty);
      ctx.lineTo(padLeft + plotW, ty);
      ctx.stroke();
      ctx.setLineDash([]);

      const thTxt = options.thresholdLabel || `Ngưỡng μ+3σ: ${options.thresholdLine.toFixed(3)}`;
      ctx.font = `bold ${Math.round(12.5 * scale * dpr)}px ${fontStack}`;
      const thW = ctx.measureText(thTxt).width + 12 * dpr;
      const thH = Math.round(20 * scale * dpr);
      const thX = padLeft + 8 * dpr;
      const thY = Math.max(padTop + 4 * dpr, ty - thH - 4 * dpr);

      ctx.fillStyle = 'rgba(255, 255, 255, 0.93)';
      ctx.strokeStyle = '#dc2626';
      ctx.lineWidth = 1.3 * dpr;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(thX, thY, thW, thH, 4 * dpr) : ctx.rect(thX, thY, thW, thH);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#dc2626';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(thTxt, thX + thW / 2, thY + thH / 2);
    }

    // 5. Draw Title & X-Axis Label
    if (options.title) {
      ctx.fillStyle = '#0f172a';
      ctx.font = FONT_TITLE;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const titleY = hasLegend ? Math.round(15 * scale * dpr) : Math.round(20 * scale * dpr);
      ctx.fillText(options.title, padLeft + plotW / 2, titleY);
    }

    if (options.xLabel) {
      ctx.fillStyle = '#64748b';
      ctx.font = `600 ${Math.round(12.5 * scale * dpr)}px ${fontStack}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(options.xLabel, padLeft + plotW / 2, this.height - Math.round(4 * scale * dpr));
    }

    // 6. Draw Key Value Badge on Chart
    let badgeBox = null;
    if (options.badgeText) {
      const bColor = options.badgeColor || '#dc2626';
      ctx.font = FONT_BADGE;
      const bText = options.badgeText;
      const bMetrics = ctx.measureText(bText);
      const bPadX = Math.round(11 * scale * dpr);
      const bW = bMetrics.width + bPadX * 2;
      const bH = Math.round(28 * scale * dpr);
      const bx = padLeft + plotW - bW - 8 * dpr;
      const by = padTop + 6 * dpr;
      badgeBox = { x1: bx, y1: by, x2: bx + bW, y2: by + bH };

      ctx.fillStyle = 'rgba(255, 255, 255, 0.94)';
      ctx.strokeStyle = bColor;
      ctx.lineWidth = 2 * dpr;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(bx, by, bW, bH, 4 * dpr) : ctx.rect(bx, by, bW, bH);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = bColor;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(bText, bx + bW / 2, by + bH / 2);
    }

    // 6.5. Draw Point Marker if specified (with automatic badge collision avoidance)
    if (options.pointMarker) {
      const pIdx = options.pointMarker.index !== undefined ? options.pointMarker.index : (maxLen - 1);
      const px = getX(pIdx);
      const py = getY(options.pointMarker.value !== undefined ? options.pointMarker.value : 0);
      const mColor = options.pointMarker.color || '#dc2626';
      const mGlow = options.pointMarker.glowColor || (mColor === '#16a34a' ? 'rgba(22, 163, 74, 0.22)' : 'rgba(220, 38, 38, 0.25)');

      ctx.fillStyle = mGlow;
      ctx.beginPath();
      ctx.arc(px, py, Math.round(12 * scale * dpr), 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = mColor;
      ctx.beginPath();
      ctx.arc(px, py, Math.round(5 * scale * dpr), 0, Math.PI * 2);
      ctx.fill();

      const markerLabel = options.pointMarker.label || 'Điểm nạp mới';
      const markerFontPx = Math.round(13.5 * scale * dpr);
      ctx.font = `bold ${markerFontPx}px ${fontStack}`;
      const mW = ctx.measureText(markerLabel).width;
      const mH = markerFontPx + 4 * dpr;
      const isRightSide = px > padLeft + plotW - 150 * dpr;

      const overlapsBadge = (lx1, ly1, lx2, ly2) => {
        if (!badgeBox) return false;
        const pad = 6 * dpr;
        return !(lx2 + pad < badgeBox.x1 || lx1 - pad > badgeBox.x2 || ly2 + pad < badgeBox.y1 || ly1 - pad > badgeBox.y2);
      };

      // Candidate 1: above marker
      let align = isRightSide ? 'right' : 'left';
      let tx = px + (isRightSide ? -12 * dpr : 12 * dpr);
      let ty = py - 12 * dpr; // alphabetic baseline
      let boxX1 = align === 'right' ? tx - mW : tx;
      let boxY1 = ty - markerFontPx;

      if (boxY1 < padTop + 4 * dpr || overlapsBadge(boxX1, boxY1, boxX1 + mW, boxY1 + mH)) {
        // Candidate 2: below marker
        const belowTop = py + 12 * dpr;
        const belowBase = belowTop + markerFontPx * 0.85;
        if (
          belowTop + mH <= padTop + plotH - 2 * dpr &&
          !overlapsBadge(boxX1, belowTop, boxX1 + mW, belowTop + mH)
        ) {
          ty = belowBase;
        } else if (badgeBox) {
          // Candidate 3: place cleanly to the left of the top-right badge
          align = 'right';
          tx = badgeBox.x1 - 10 * dpr;
          ty = Math.max(padTop + markerFontPx + 6 * dpr, Math.min(padTop + plotH - 6 * dpr, py + markerFontPx * 0.35));
        }
      }

      ctx.save();
      ctx.textAlign = align;
      ctx.textBaseline = 'alphabetic';
      ctx.lineJoin = 'round';
      ctx.lineWidth = 3.5 * dpr;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.92)';
      ctx.strokeText(markerLabel, tx, ty);
      ctx.fillStyle = mColor;
      ctx.fillText(markerLabel, tx, ty);
      ctx.restore();
    }

    // 7. Legend (Dedicated row ABOVE padTop so plot lines never obscure labels)
    if (hasLegend) {
      const legY = options.title ? Math.round(37 * scale * dpr) : Math.round(15 * scale * dpr);
      let legFontPx = Math.round(13 * scale * dpr);
      ctx.font = `600 ${legFontPx}px ${fontStack}`;

      const swatchSize = Math.round(11 * scale * dpr);
      const swatchTextGap = Math.round(6 * scale * dpr);
      const itemGap = Math.round(22 * scale * dpr);
      const maxAvailW = this.width - 20 * dpr;

      const measureLegendWidth = () => visibleLegendLines.reduce((acc, l, i) => {
        const itemW = swatchSize + swatchTextGap + ctx.measureText(l.label).width;
        return acc + itemW + (i > 0 ? itemGap : 0);
      }, 0);

      let totalLegW = measureLegendWidth();
      if (totalLegW > maxAvailW && totalLegW > 0) {
        legFontPx = Math.max(Math.round(10.5 * dpr), Math.floor(legFontPx * (maxAvailW / totalLegW)));
        ctx.font = `600 ${legFontPx}px ${fontStack}`;
        totalLegW = measureLegendWidth();
      }

      const idealStartX = padLeft + (plotW - totalLegW) / 2;
      let legX = Math.max(10 * dpr, Math.min(this.width - totalLegW - 10 * dpr, idealStartX));

      visibleLegendLines.forEach((line) => {
        ctx.fillStyle = line.color || '#334155';
        ctx.beginPath();
        ctx.roundRect
          ? ctx.roundRect(legX, legY - swatchSize / 2, swatchSize, swatchSize, 2.5 * dpr)
          : ctx.rect(legX, legY - swatchSize / 2, swatchSize, swatchSize);
        ctx.fill();

        ctx.fillStyle = '#1e293b';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        ctx.fillText(line.label, legX + swatchSize + swatchTextGap, legY);
        legX += swatchSize + swatchTextGap + ctx.measureText(line.label).width + itemGap;
      });
    }

    this._meta = {
      type: 'line',
      padLeft,
      padTop,
      plotW,
      plotH,
      maxLen,
      scale,
      getX,
      getY,
      lines,
      options,
    };
    this._saveBaseSnapshot();
  }

  /**
   * Draw Bar Chart
   * bars: Array of { label, name_vi, desc_vi, reason, value, color, isExcluded, isTop }
   * options: { title, xLabel, yLabel, yMax, badgeText, tooltipFormatter, syncCharts }
   */
  drawBarChart(bars, options = {}) {
    this._lastDraw = () => this.drawBarChart(bars, options);
    if (!this.resize()) return;
    this.clear();
    const ctx = this.ctx;
    const dpr = this.dpr;
    this.canvas.style.cursor = 'crosshair';

    const cssH = this.height / dpr;
    const scale = Math.min(1.0, Math.max(0.72, cssH / 300));
    const fontStack = "'Segoe UI', Roboto, Arial, sans-serif";

    const FONT_TITLE = `bold ${Math.round(18 * scale * dpr)}px ${fontStack}`;
    const FONT_LABEL = `600 ${Math.round(14 * scale * dpr)}px ${fontStack}`;
    const FONT_BAR_LABEL = `bold ${Math.round((bars.length > 20 ? 11.5 : 13.5) * scale * dpr)}px ${fontStack}`;
    const FONT_BADGE = `bold ${Math.round(15 * scale * dpr)}px ${fontStack}`;

    const padLeft = Math.round(62 * scale * dpr);
    const padRight = Math.round(24 * scale * dpr);
    const padTop = options.title ? Math.round(44 * scale * dpr) : Math.round(26 * scale * dpr);
    const padBottom = Math.round((options.xLabel ? 64 : 56) * scale * dpr);

    const plotW = this.width - padLeft - padRight;
    const plotH = this.height - padTop - padBottom;
    if (plotW <= 0 || plotH <= 0 || !bars || bars.length === 0) return;

    const maxBarVal = Math.max(
      ...bars.map(b => b.value || 0),
      options.meanLine && typeof options.meanLine.value === 'number' ? options.meanLine.value : 0,
      0.1
    );
    let yMax;
    if (options.yMax !== undefined) {
      yMax = options.yMax;
    } else if (maxBarVal <= 1.0001) {
      const unitCeils = [0.20, 0.40, 0.60, 0.80, 1.00];
      yMax = unitCeils.find(c => c >= maxBarVal - 1e-6) || 1.00;
    } else {
      const roughStep = maxBarVal / 4;
      const bPow = Math.pow(10, Math.floor(Math.log10(roughStep)));
      const bMult = [1, 2, 2.5, 5, 10].find(m => 4 * bPow * m >= maxBarVal) || 10;
      yMax = 4 * bPow * bMult;
    }

    // Reserve subtle top headroom above the yMax gridline for peak value labels
    const barTopPad = Math.round(18 * scale * dpr);
    const barMaxH = Math.max(10, plotH - barTopPad);

    const n = bars.length;
    const barStep = plotW / n;
    const barWidth = Math.max(4 * dpr, barStep * 0.72);

    // 1. Draw Grid
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1 * dpr;
    ctx.beginPath();
    for (let i = 0; i <= 4; i++) {
      const v = (i / 4) * yMax;
      const y = padTop + plotH - (v / yMax) * barMaxH;
      ctx.moveTo(padLeft, y);
      ctx.lineTo(padLeft + plotW, y);

      ctx.fillStyle = '#64748b';
      ctx.font = FONT_LABEL;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(v.toFixed(2), padLeft - 10 * dpr, y);
    }
    ctx.stroke();

    // 2. Draw Bars
    const minSlotPx = n > 20 ? 28 * dpr : 38 * dpr;
    const maxLabels = Math.max(6, Math.floor(plotW / minSlotPx));
    const labelStride = n > maxLabels ? Math.ceil(n / maxLabels) : 1;

    bars.forEach((bar, i) => {
      const val = Math.max(0, bar.value || 0);
      const bH = (val / yMax) * barMaxH;
      const bx = padLeft + i * barStep + (barStep - barWidth) / 2;
      const by = padTop + plotH - bH;

      let barColor = bar.color || '#2563eb';
      if (bar.isExcluded) {
        barColor = '#cbd5e1';
      } else if (bar.isTop) {
        barColor = bar.topColor || '#dc2626';
      }

      ctx.fillStyle = barColor;
      ctx.fillRect(bx, by, barWidth, Math.max(1.5 * dpr, bH));

      if (i % labelStride === 0 || i === n - 1) {
        ctx.save();
        ctx.translate(bx + barWidth / 2, padTop + plotH + 8 * dpr);
        const shouldRotate = n > 8;
        ctx.rotate(shouldRotate ? -Math.PI / 5 : 0);
        ctx.fillStyle = bar.isExcluded ? '#94a3b8' : '#1e293b';
        ctx.font = FONT_BAR_LABEL;
        ctx.textAlign = shouldRotate ? 'right' : 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(bar.label, 0, 0);
        ctx.restore();
      }

      if (bar.isTop && val > 0.02) {
        const topColor = bar.topColor || '#dc2626';
        ctx.fillStyle = topColor;
        ctx.font = `bold ${Math.round(13.5 * scale * dpr)}px ${fontStack}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'alphabetic';
        const topTxt = options.valueFormat === 'decimal'
          ? val.toFixed(3)
          : `${(val * 100).toFixed(1)}%`;
        ctx.fillText(topTxt, bx + barWidth / 2, by - 5 * dpr);
      }
    });

    // 2.5. Draw Horizontal Reference / Mean Line if provided
    if (options.meanLine && typeof options.meanLine.value === 'number') {
      const mVal = options.meanLine.value;
      const my = padTop + plotH - (mVal / yMax) * barMaxH;
      const mColor = options.meanLine.color || '#dc2626';

      ctx.save();
      ctx.strokeStyle = mColor;
      ctx.lineWidth = 2.2 * dpr;
      ctx.setLineDash([6 * dpr, 5 * dpr]);
      ctx.beginPath();
      ctx.moveTo(padLeft, my);
      ctx.lineTo(padLeft + plotW, my);
      ctx.stroke();
      ctx.setLineDash([]);

      if (options.meanLine.label) {
        ctx.font = `bold ${Math.round(13.5 * scale * dpr)}px ${fontStack}`;
        const mTxt = options.meanLine.label;
        const mW = ctx.measureText(mTxt).width + 14 * dpr;
        const mH = 22 * dpr;
        const mx = padLeft + 10 * dpr;
        const mBoxY = Math.max(padTop + 4 * dpr, my - mH - 5 * dpr);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
        ctx.strokeStyle = mColor;
        ctx.lineWidth = 1.4 * dpr;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(mx, mBoxY, mW, mH, 4 * dpr) : ctx.rect(mx, mBoxY, mW, mH);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = mColor;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(mTxt, mx + mW / 2, mBoxY + mH / 2);
      }
      ctx.restore();
    }

    // 3. Title, XLabel & Badge
    if (options.title) {
      ctx.fillStyle = '#0f172a';
      ctx.font = FONT_TITLE;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(options.title, padLeft + plotW / 2, Math.round(22 * scale * dpr));
    }

    if (options.xLabel) {
      ctx.fillStyle = '#64748b';
      ctx.font = `600 ${Math.round(12.5 * scale * dpr)}px ${fontStack}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(options.xLabel, padLeft + plotW / 2, this.height - Math.round(4 * scale * dpr));
    }

    if (options.badgeText) {
      ctx.font = FONT_BADGE;
      const bText = options.badgeText;
      const bMetrics = ctx.measureText(bText);
      const bPadX = Math.round(11 * scale * dpr);
      const bW = bMetrics.width + bPadX * 2;
      const bH = Math.round(30 * scale * dpr);
      const bx = padLeft + plotW - bW - 8 * dpr;
      const by = padTop + 8 * dpr;

      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
      ctx.strokeStyle = '#2563eb';
      ctx.lineWidth = 2 * dpr;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(bx, by, bW, bH, 4 * dpr) : ctx.rect(bx, by, bW, bH);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#1e3a8a';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(bText, bx + bW / 2, by + bH / 2);
    }

    this._meta = {
      type: 'bar',
      padLeft,
      padTop,
      plotW,
      plotH,
      barMaxH,
      barStep,
      barWidth,
      yMax,
      n,
      scale,
      bars,
      options,
    };
    this._saveBaseSnapshot();
  }

  /**
   * Draw 128-D Signed Latent Embedding Chart (Dual Heatmap Barcode + Zero-Centered Diverging Bars)
   */
  drawEmbeddingChart(embTarget, embNormal = null, options = {}) {
    this._lastDraw = () => this.drawEmbeddingChart(embTarget, embNormal, options);
    if (!this.resize()) return;
    this.clear();
    if (!embTarget || embTarget.length === 0) return;

    const ctx = this.ctx;
    const dpr = this.dpr;
    const n = embTarget.length;
    const hasNormal = Array.isArray(embNormal) && embNormal.length === n;
    this.canvas.style.cursor = 'crosshair';

    const cssH = this.height / dpr;
    const scale = Math.min(1.0, Math.max(0.74, cssH / 310));
    const fontStack = "'Segoe UI', Roboto, Arial, sans-serif";

    const FONT_SUBTITLE = `bold ${Math.round(14.5 * scale * dpr)}px ${fontStack}`;
    const FONT_AXIS = `600 ${Math.round(13 * scale * dpr)}px ${fontStack}`;
    const FONT_STRIP = `700 ${Math.round(11.5 * scale * dpr)}px ${fontStack}`;
    const FONT_PEAK = `bold ${Math.round(12 * scale * dpr)}px ${fontStack}`;

    const padLeft = Math.round(72 * scale * dpr);
    const padRight = Math.round(22 * scale * dpr);
    const titleOffset = options.title ? Math.round(26 * scale * dpr) : Math.round(8 * scale * dpr);
    const stripRowH = Math.round(12 * scale * dpr);
    const stripGap = Math.round(4 * scale * dpr);
    const stripTotalH = hasNormal ? (stripRowH * 2 + stripGap) : stripRowH;
    const barTop = titleOffset + stripTotalH + Math.round(18 * scale * dpr);
    const padBottom = Math.round(38 * scale * dpr);

    const plotW = this.width - padLeft - padRight;
    const plotH = this.height - barTop - padBottom;
    if (plotW <= 0 || plotH <= 20) return;

    let rawAbsMax = 0.5;
    for (let i = 0; i < n; i++) {
      rawAbsMax = Math.max(rawAbsMax, Math.abs(embTarget[i]));
      if (hasNormal) rawAbsMax = Math.max(rawAbsMax, Math.abs(embNormal[i]));
    }
    const paddedMax = rawAbsMax * 1.18;
    const niceSteps = [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 30, 40, 50, 60, 80, 100];
    let niceMax = niceSteps.find(s => s >= paddedMax) || Math.ceil(paddedMax / 10) * 10;

    if (options.title) {
      ctx.fillStyle = '#0f172a';
      ctx.font = FONT_SUBTITLE;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(options.title, padLeft + plotW / 2, Math.round(14 * scale * dpr));
    }

    const getHeatColor = (val) => {
      const u = Math.max(-1, Math.min(1, val / niceMax));
      const g = Math.pow(Math.abs(u), 0.7);
      if (u >= 0) {
        const r = Math.round(248 + (29 - 248) * g);
        const gr = Math.round(250 + (78 - 250) * g);
        const b = Math.round(252 + (216 - 252) * g);
        return `rgb(${r},${gr},${b})`;
      } else {
        const r = Math.round(248 + (220 - 248) * g);
        const gr = Math.round(250 + (38 - 250) * g);
        const b = Math.round(252 + (38 - 252) * g);
        return `rgb(${r},${gr},${b})`;
      }
    };

    const cellW = plotW / n;
    const drawStripRow = (vec, yTop, rowLabel, labelColor) => {
      for (let i = 0; i < n; i++) {
        const x = padLeft + i * cellW;
        ctx.fillStyle = getHeatColor(vec[i]);
        ctx.fillRect(x, yTop, Math.ceil(cellW + 0.5), stripRowH);
      }
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1 * dpr;
      ctx.strokeRect(padLeft, yTop, plotW, stripRowH);

      ctx.fillStyle = labelColor;
      ctx.font = FONT_STRIP;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(rowLabel, padLeft - 8 * dpr, yTop + stripRowH / 2);
    };

    if (hasNormal) {
      drawStripRow(embNormal, titleOffset, options.normalLabel || 'Normal', '#64748b');
      drawStripRow(embTarget, titleOffset + stripRowH + stripGap, options.targetLabel || 'Đang xét', '#0f172a');
    } else {
      drawStripRow(embTarget, titleOffset, options.targetLabel || 'Embedding', '#0f172a');
    }

    const yZero = barTop + plotH / 2;
    const getY = (val) => yZero - (val / niceMax) * (plotH / 2);

    const tickLevels = [-1, -0.5, 0, 0.5, 1];
    tickLevels.forEach(frac => {
      const v = frac * niceMax;
      const y = getY(v);
      ctx.strokeStyle = frac === 0 ? '#64748b' : '#e2e8f0';
      ctx.lineWidth = (frac === 0 ? 1.5 : 1) * dpr;
      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(padLeft + plotW, y);
      ctx.stroke();

      ctx.fillStyle = frac === 0 ? '#1e293b' : '#64748b';
      ctx.font = FONT_AXIS;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      const vStr = v === 0 ? '0.0' : (v > 0 ? `+${v.toFixed(1)}` : v.toFixed(1));
      ctx.fillText(vStr, padLeft - 8 * dpr, y);
    });

    let diffSum = 0;
    if (hasNormal) {
      for (let i = 0; i < n; i++) diffSum += Math.abs(embTarget[i] - embNormal[i]);
    }

    if (hasNormal && diffSum > 1e-4) {
      const normW = Math.max(1.5 * dpr, cellW * 0.82);
      ctx.fillStyle = 'rgba(148, 163, 184, 0.36)';
      for (let i = 0; i < n; i++) {
        const nv = embNormal[i];
        const ny = getY(nv);
        const bx = padLeft + i * cellW + (cellW - normW) / 2;
        const topY = Math.min(yZero, ny);
        const h = Math.max(1 * dpr, Math.abs(ny - yZero));
        ctx.fillRect(bx, topY, normW, h);
      }
    }

    const barW = Math.max(1.6 * dpr, cellW * 0.62);
    let maxPosIdx = -1;
    let maxPosVal = 0;
    let minNegIdx = -1;
    let minNegVal = 0;

    for (let i = 0; i < n; i++) {
      const v = embTarget[i];
      if (v > maxPosVal) {
        maxPosVal = v;
        maxPosIdx = i;
      }
      if (v < minNegVal) {
        minNegVal = v;
        minNegIdx = i;
      }
      const y = getY(v);
      const bx = padLeft + i * cellW + (cellW - barW) / 2;
      const topY = Math.min(yZero, y);
      const h = Math.max(1 * dpr, Math.abs(y - yZero));
      ctx.fillStyle = v >= 0 ? '#2563eb' : '#dc2626';
      ctx.fillRect(bx, topY, barW, h);
    }

    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 1.4 * dpr;
    ctx.beginPath();
    ctx.moveTo(padLeft, yZero);
    ctx.lineTo(padLeft + plotW, yZero);
    ctx.stroke();

    const drawPeakTag = (idx, val, isPositive) => {
      if (idx < 0 || Math.abs(val) < niceMax * 0.12) return;
      const cx = padLeft + (idx + 0.5) * cellW;
      const cy = getY(val);
      const txt = `d${idx} (${val >= 0 ? '+' : ''}${val.toFixed(1)})`;
      ctx.font = FONT_PEAK;
      const tw = ctx.measureText(txt).width;
      const clampedX = Math.max(padLeft + tw / 2 + 4 * dpr, Math.min(padLeft + plotW - tw / 2 - 4 * dpr, cx));

      ctx.fillStyle = isPositive ? '#1d4ed8' : '#b91c1c';
      ctx.beginPath();
      ctx.arc(cx, cy, 3 * dpr, 0, Math.PI * 2);
      ctx.fill();

      ctx.textAlign = 'center';
      ctx.textBaseline = isPositive ? 'bottom' : 'top';
      ctx.fillText(txt, clampedX, isPositive ? (cy - 4 * dpr) : (cy + 4 * dpr));
    };
    drawPeakTag(maxPosIdx, maxPosVal, true);
    drawPeakTag(minNegIdx, minNegVal, false);

    const tickIndices = n === 128
      ? [0, 16, 32, 48, 64, 80, 96, 112, 127]
      : Array.from({ length: 9 }, (_, k) => Math.round((k * (n - 1)) / 8));

    const axisBottomY = barTop + plotH;
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1 * dpr;
    ctx.beginPath();
    ctx.moveTo(padLeft, axisBottomY);
    ctx.lineTo(padLeft + plotW, axisBottomY);
    tickIndices.forEach(idx => {
      const tx = padLeft + (idx + 0.5) * cellW;
      ctx.moveTo(tx, axisBottomY);
      ctx.lineTo(tx, axisBottomY + 4 * dpr);
    });
    ctx.stroke();

    ctx.fillStyle = '#475569';
    ctx.font = FONT_AXIS;
    ctx.textBaseline = 'top';
    tickIndices.forEach((idx, k) => {
      const tx = padLeft + (idx + 0.5) * cellW;
      ctx.textAlign = k === 0 ? 'left' : (k === tickIndices.length - 1 ? 'right' : 'center');
      const drawX = k === 0 ? padLeft : (k === tickIndices.length - 1 ? padLeft + plotW : tx);
      ctx.fillText(`d${idx}`, drawX, axisBottomY + 6 * dpr);
    });

    if (options.xLabel) {
      ctx.fillStyle = '#64748b';
      ctx.font = `600 ${Math.round(12 * scale * dpr)}px ${fontStack}`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'bottom';
      ctx.fillText(options.xLabel, padLeft + plotW / 2, this.height - 2 * dpr);
    }

    this._meta = {
      type: 'embedding',
      padLeft,
      stripTop: titleOffset,
      stripTotalH,
      barTop,
      plotW,
      plotH,
      cellW,
      yZero,
      getY,
      n,
      hasNormal,
      scale,
      embTarget,
      embNormal,
      options,
    };
    this._saveBaseSnapshot();
  }
}
window.SimpleCanvasChart = SimpleCanvasChart;
