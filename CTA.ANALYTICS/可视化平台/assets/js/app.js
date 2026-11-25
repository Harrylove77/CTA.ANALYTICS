/* =========================================================
   CTA·ANALYTICS — 交互与图表
   数据源：assets/data/data.js（由 build_data.py 生成）
   ========================================================= */
(function () {
  'use strict';
  var directoryToggle = document.querySelector('.directory-toggle');
  if (directoryToggle) {
    var sidebar = directoryToggle.closest('.sidebar');
    function setDirectory(open) {
      directoryToggle.setAttribute('aria-expanded', String(open));
    }
    directoryToggle.addEventListener('click', function () {
      setDirectory(directoryToggle.getAttribute('aria-expanded') !== 'true');
    });
    sidebar.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && directoryToggle.getAttribute('aria-expanded') === 'true') {
        setDirectory(false);
        directoryToggle.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (!sidebar.contains(event.target)) setDirectory(false);
    });
    window.addEventListener('pageshow', function () { setDirectory(false); });
  }

  var D = window.DASH_DATA;
  if (!D) {
    document.body.insertAdjacentHTML('beforeend',
      '<div style="padding:40px;color:#995652">未找到 DASH_DATA，请先运行 build_data.py</div>');
    return;
  }

  var C = {
    cyan: '#697184', blue: '#527c8a', violet: '#8a7976', pink: '#936d7d',
    green: '#54796f', amber: '#986927', red: '#995652', orange: '#a4763f',
    txt: '#413f3d', dim: '#625f5d'
  };
  var PALETTE = [C.cyan, C.violet, C.green, C.amber, C.pink, C.blue, C.red, C.orange];
  var charts = [];
  var cache = {};

  function $(s, r) { return (r || document).querySelector(s); }
  function fmt(v, d) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    var s = Number(v).toFixed(d === undefined ? 2 : d);
    return s.indexOf('.') > -1 ? s.replace(/0+$/, '').replace(/\.$/, '') : s;
  }
  function num(v, d) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    return Number(v).toLocaleString('zh-CN',
      { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function mk(id) {
    if (cache[id]) return cache[id];
    var dom = document.getElementById(id);
    if (!dom) return null;
    var c = echarts.init(dom, null, { renderer: 'canvas' });
    cache[id] = c;
    charts.push(c);
    return c;
  }
  window.addEventListener('resize', function () {
    charts.forEach(function (c) { if (!c.isDisposed()) c.resize(); });
  });

  var TIP = {
    backgroundColor: 'rgba(255,254,252,.98)',
    borderColor: 'rgba(105,113,132,.35)',
    borderWidth: 1,
    padding: [9, 12],
    textStyle: { color: '#413f3d', fontSize: 12 },
    extraCssText: 'box-shadow:0 18px 40px -20px #000;border-radius:10px;'
  };
  function axisX(data, opt) {
    return Object.assign({
      type: 'category', data: data, boundaryGap: true,
      axisLine: { lineStyle: { color: 'rgba(105,113,132,.28)' } },
      axisTick: { show: false },
      axisLabel: { color: C.dim, fontSize: 11 },
      splitLine: { show: false }
    }, opt || {});
  }
  function axisY(name, opt) {
    return Object.assign({
      type: 'value', name: name || '',
      nameTextStyle: { color: C.dim, fontSize: 11, padding: [0, 0, 6, 0] },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: C.dim, fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(105,113,132,.09)', type: 'dashed' } }
    }, opt || {});
  }
  function grad(from, to, vertical) {
    return new echarts.graphic.LinearGradient(0, 0, vertical ? 0 : 1, vertical ? 1 : 0,
      [{ offset: 0, color: from }, { offset: 1, color: to }]);
  }

  function renderComposition(id, items, unit) {
    var host = document.getElementById(id);
    var palette = ['#a7b1be', '#cec0ba', '#bdcbc5', '#d9cdba', '#c9bdd0', '#acd0d3', '#d2cfd0', '#b9bdce'];
    var total = items.reduce(function (sum, item) { return sum + item.value; }, 0);
    host.classList.add('composition');
    var plot = el('div', 'composition-plot');
    plot.id = id + 'Plot';
    var list = el('ul', 'composition-key');
    items.forEach(function (item, index) {
      var row = el('li');
      var swatch = el('span', 'composition-swatch');
      swatch.style.backgroundColor = palette[index % palette.length];
      var name = el('span', 'composition-name');
      name.textContent = item.name;
      var value = el('span', 'composition-value');
      value.textContent = total ? (item.value / total * 100).toFixed(1) + '%' : '—';
      row.append(swatch, name, value);
      list.appendChild(row);
    });
    host.append(plot, list);
    var chart = mk(plot.id);
    chart.setOption({
      color: palette,
      tooltip: Object.assign({ trigger: 'item', formatter: '{b}<br/>{c} ' + unit + ' · {d}%' }, TIP),
      graphic: [{
        type: 'text', left: 'center', top: 'center', silent: true,
        style: { text: num(total) + '\n' + unit, fill: C.txt, fontSize: 15,
          fontFamily: 'system-ui, sans-serif', align: 'center', lineHeight: 20 }
      }],
      series: [{
        type: 'pie', radius: ['72%', '90%'], data: items,
        itemStyle: { borderColor: '#fbfaf8', borderWidth: 1 },
        label: { show: false }, labelLine: { show: false },
        emphasis: { scale: false, itemStyle: { opacity: .78 } }
      }]
    });
  }

  /* ---------------- 顶部信息 ---------------- */
  var ed = D.overview.editions;
  if ($('#heroLede')) $('#heroLede').innerHTML = '覆盖 <b>第 ' + ed[0] + '-' + ed[ed.length - 1] + ' 届</b>共 ' +
    ed.length + ' 届赛事、' + num(D.overview.rows) + ' 条参赛记录、' + num(D.overview.players) +
    ' 位十年特别奖选手。平台从 6 项核心交易指标出发，完成单项画像、多维聚类、排名区间对比、' +
    '届次趋势与交易风格识别，并提供跨届名次预测与历史回测。';


  /* ---------------- KPI 卡片 ---------------- */
  (function kpi() {
    if (!$('#hero')) return;
    var box = $('#kpiGrid');
    D.kpi.forEach(function (item) {
      var d = el('div', 'kpi');
      var isNum = typeof item.v === 'number';
      d.innerHTML = '<div class="k">' + item.k + '</div>' +
        '<div class="v" data-v="' + (isNum ? item.v : '') + '">' +
        (isNum ? '0' : item.v) + '<small>' + (item.u || '') + '</small></div>' +
        '<div class="s">' + item.s + '</div>';
      box.appendChild(d);
    });
    box.querySelectorAll('.v[data-v]').forEach(function (n) {
      var target = parseFloat(n.getAttribute('data-v'));
      if (isNaN(target)) return;
      var dec = (String(target).split('.')[1] || '').length;
      n.firstChild.nodeValue = target.toFixed(dec);   // 先落地终值，避免无动画环境显示 0
      var t0 = null, dur = 1200;
      function step(t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / dur);
        var e = 1 - Math.pow(1 - p, 3);
        n.firstChild.nodeValue = (target * e).toFixed(dec);
        if (p < 1) requestAnimationFrame(step);
        else n.firstChild.nodeValue = target.toFixed(dec);
      }
      requestAnimationFrame(step);
    });
  })();

  /* ---------------- 总览图 ---------------- */
  (function heroCharts() {
    if (!$('#hero')) return;
    var ec = D.overview.editionCount;
    var c1 = mk('cEditionCount');
    if (c1) c1.setOption({
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TIP),
      legend: { data: ['参赛记录数', '环比趋势'], right: 10, top: 0,
        textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
      grid: { left: 54, right: 24, top: 34, bottom: 30 },
      xAxis: axisX(ec.map(function (d) { return d.name; }), { axisLabel: { color: C.dim, fontSize: 11, interval: 0 } }),
      yAxis: axisY('记录数'),
      series: [{
        name: '参赛记录数', type: 'bar', barWidth: '46%',
        data: ec.map(function (d) { return d.value; }),
        itemStyle: { borderRadius: [6, 6, 0, 0], color: grad('rgba(105,113,132,.95)', 'rgba(177,166,164,.30)', true) },
        emphasis: { itemStyle: { color: grad('#7df9ff', 'rgba(177,166,164,.75)', true) } }
      }, {
        name: '环比趋势', type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
        data: ec.map(function (d) { return d.value; }),
        lineStyle: { width: 2, color: 'rgba(167,128,142,.8)' },
        itemStyle: { color: C.pink }, z: 3
      }]
    });

    renderComposition('cGroups', D.overview.groups, '条记录');

    var c4 = mk('cDealers');
    if (c4) {
      var dd = D.overview.dealers.slice().reverse();
      c4.setOption({
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TIP),
        grid: { left: 132, right: 56, top: 12, bottom: 22 },
        xAxis: axisY(''),
        yAxis: axisX(dd.map(function (d) { return d.name; }),
          { axisLabel: { color: C.dim, fontSize: 10.5, width: 120, overflow: 'truncate' }, axisLine: { show: false } }),
        series: [{
          type: 'bar', barWidth: '56%',
          data: dd.map(function (d) { return d.value; }),
          itemStyle: { borderRadius: [0, 4, 4, 0], color: grad('rgba(105,113,132,.85)', 'rgba(87,121,111,.45)') },
          label: { show: true, position: 'right', color: C.dim, fontSize: 10 }
        }]
      });
    }

    var tp = $('#topPlayers');
    D.overview.topPlayers.forEach(function (p) {
      var d = el('div', 'tp');
      d.innerHTML = '<div class="nm">' + p.name + '</div>' +
        '<div class="rk">' + (p.best ? 'BEST #' + p.best : '—') + ' · 参赛 ' + p.n +
        ' 届 · 均值净值 ' + fmt(p.net, 3) + '</div>' +
        '<div class="tx"><i>' + p.style + '</i><br>' + p.risk + '<br>' + p.profit + '</div>';
      tp.appendChild(d);
    });
  })();

  /* ---------------- 单项指标 ---------------- */
   (function singleCharts() {
    if (!document.getElementById('single')) return;
    var keys = Object.keys(D.single);
    var cur = keys[0];
    var chips = $('#metricChips');

    keys.forEach(function (k, i) {
      var m = D.single[k];
      var b = el('button', 'chip' + (i === 0 ? ' on' : ''), m.name + '<em>n=' + m.n + '</em>');
      b.addEventListener('click', function () {
        chips.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        cur = k;
        render(k);
      });
      chips.appendChild(b);
    });

    function nearestIdx(edges, v) {
      var best = 0, dif = Infinity;
      (edges || []).forEach(function (e, i) {
        var d = Math.abs(e - v);
        if (d < dif) { dif = d; best = i; }
      });
      return Math.max(0, Math.min(edges.length - 2, best));
    }

    function fillRank(ul, list) {
      ul.innerHTML = '';
      (list || []).forEach(function (p, i) {
        ul.appendChild(el('li', null,
          '<span class="no">' + (i + 1) + '</span>' +
          '<span class="nm">' + p.name + '</span>' +
          '<span class="vl">' + fmt(p.v, 3) + '</span>' +
          '<span class="sub">' + p.n + '届</span>'));
      });
    }

    function render(k) {
      var m = D.single[k], hist = m.hist, st = m.stats;
      $('#singleTitle').textContent = m.label + ' 分布';
      $('#singleHint').textContent = m.desc;
      $('#singleN').textContent = '有效样本 ' + num(m.n) + ' 人';

      var c = mk('cSingleHist');
      if (c) c.setOption({
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' },
          formatter: function (p) { return '区间起点 ' + p[0].name + '<br/>人数 ' + p[0].value; } }, TIP),
        grid: { left: 56, right: 24, top: 28, bottom: 54 },
        xAxis: axisX(hist.labels, { axisLabel: { color: C.dim, fontSize: 9.5, rotate: 38 } }),
        yAxis: axisY('人数'),
        series: [{
          type: 'bar', barWidth: '82%', data: hist.counts,
          itemStyle: { color: grad('rgba(105,113,132,.9)', 'rgba(177,166,164,.22)', true), borderRadius: [3, 3, 0, 0] },
          markLine: {
            symbol: 'none', silent: true,
            label: { color: C.amber, fontSize: 10, formatter: '均值' },
            lineStyle: { color: 'rgba(164,118,63,.75)', type: 'dashed', width: 1.5 },
            data: [{ xAxis: nearestIdx(hist.edges, st.mean) }]
          }
        }]
      }, true);

      var box = $('#singleStats');
      box.innerHTML = '';
      [['均值', st.mean], ['中位数', st.median], ['标准差', st.std], ['P10', st.p10],
       ['P90', st.p90], ['极差', st.max - st.min], ['最小值', st.min], ['最大值', st.max]]
        .forEach(function (r) {
          box.appendChild(el('div', 'stat', '<b>' + fmt(r[1], 3) + '</b><span>' + r[0] + '</span>'));
        });

      fillRank($('#singleTop'), m.top);
      fillRank($('#singleBottom'), m.bottom);

      var cf = mk('cSingleFreq');
      if (cf) cf.setOption({
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TIP),
        grid: { left: 54, right: 18, top: 24, bottom: 28 },
        xAxis: axisX(m.byFreq.map(function (d) { return d.name; })),
        yAxis: axisY('均值', { scale: true }),
        series: [{
          type: 'bar', barWidth: '44%',
          data: m.byFreq.map(function (d) { return d.v; }),
          itemStyle: { borderRadius: [6, 6, 0, 0], color: grad('rgba(87,121,111,.85)', 'rgba(105,113,132,.25)', true) },
          label: { show: true, position: 'top', color: C.txt, fontSize: 11,
            formatter: function (p) { return fmt(p.value, 2); } }
        }]
      }, true);
    }

    render(cur);

  })();

  /* ---------------- 聚类 ---------------- */
  (function clusterCharts() {
    if (!$('#cluster')) return;
    var K = D.cluster;
    $('#pcaHint').textContent = 'PC1 解释方差 ' + K.explained[0] + '% · PC2 ' + K.explained[1] + '%';

    var cr = mk('cRadarCluster');
    if (cr) cr.setOption({
      tooltip: Object.assign({ trigger: 'item' }, TIP),
      legend: { bottom: 0, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 10, itemHeight: 8 },
      radar: {
        center: ['50%', '45%'], radius: '60%',
        indicator: K.radarAxis.map(function (n) { return { name: n, max: 100 }; }),
        axisName: { color: C.dim, fontSize: 10.5 },
        splitLine: { lineStyle: { color: 'rgba(105,113,132,.18)' } },
        splitArea: { areaStyle: { color: ['rgba(105,113,132,.03)', 'rgba(177,166,164,.05)'] } },
        axisLine: { lineStyle: { color: 'rgba(105,113,132,.18)' } }
      },
      series: [{
        type: 'radar', symbolSize: 4,
        data: K.radar.map(function (r, i) {
          var p = K.profile[i] || {};
          return {
            name: '聚类 ' + i + ' · ' + (p.label || ''),
            value: r.value,
            areaStyle: { opacity: .2 },
            lineStyle: { width: 2 },
            itemStyle: { color: PALETTE[i] }
          };
        })
      }]
    });

    var cp = mk('cPca');
    if (cp) {
      var series = [0, 1].map(function (k) {
        var pts = K.scatter.filter(function (s) { return s[2] === k; });
        var prof = K.profile[k] || {};
        return {
          name: '聚类 ' + k + ' · ' + (prof.label || '') + '（' + (prof.size || pts.length) + ' 人）',
          type: 'scatter', symbolSize: 5,
          data: pts.map(function (s) { return [s[0], s[1], s[3], s[4], s[5], s[6]]; }),
          itemStyle: { color: PALETTE[k], opacity: .6 },
          emphasis: { itemStyle: { opacity: 1, shadowBlur: 14, shadowColor: PALETTE[k] } }
        };
      });
      cp.setOption({
        tooltip: Object.assign({
          formatter: function (p) {
            var v = p.value;
            return '<b>' + v[2] + '</b><br/>PC1 ' + v[0] + ' · PC2 ' + v[1] +
              '<br/>净值 ' + v[3] + ' · 胜率 ' + v[4] + '% · 回撤 ' + v[5] + '%';
          }
        }, TIP),
        legend: { right: 10, top: 0, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 10, itemHeight: 8 },
        grid: { left: 58, right: 26, top: 40, bottom: 42 },
        xAxis: axisY('PC1', { nameLocation: 'middle', nameGap: 26,
          axisLabel: { color: C.dim, fontSize: 10 } }),
        yAxis: axisY('PC2', { nameLocation: 'middle', nameGap: 34,
          axisLabel: { color: C.dim, fontSize: 10 } }),
        dataZoom: [{ type: 'inside' }, { type: 'slider', height: 13, bottom: 8,
          borderColor: 'transparent', fillerColor: 'rgba(105,113,132,.15)',
          handleStyle: { color: C.cyan }, textStyle: { color: C.dim, fontSize: 9 } }],
        series: series
      });
    }

    var wrap = $('#clusterProfiles');
    K.profile.forEach(function (p) {
      var d = el('div', 'card');
      d.innerHTML = '<div class="card-head"><h3>聚类 ' + p.cluster + ' · ' + p.label + '</h3>' +
        '<span class="hint">' + p.size + ' 人 · 占 ' + fmt(p.size / K.total * 100, 1) + '%</span></div>' +
        '<div class="pd-stats">' +
        '<div class="stat"><b>' + fmt(p.net, 3) + '</b><span>平均累计净值</span></div>' +
        '<div class="stat"><b>' + fmt(p.win, 2) + '%</b><span>平均胜率</span></div>' +
        '<div class="stat"><b>' + fmt(p.pl, 3) + '</b><span>平均盈亏比</span></div>' +
        '<div class="stat"><b>' + fmt(p.dd, 2) + '%</b><span>平均最大回撤</span></div>' +
        '<div class="stat"><b>' + fmt(p.risk, 2) + '%</b><span>平均风险度</span></div>' +
        '<div class="stat"><b>' + fmt(p.posRatio, 1) + '%</b><span>净值 &gt; 1 占比</span></div>' +
        '</div>' +
        '<div class="hint" style="margin-top:10px">平均参赛 ' + fmt(p.freq, 2) +
        ' 届 · 组内最高净值 ' + fmt(p.best, 3) + ' · 平均日收益率 ' + fmt(p.daily, 3) + '%</div>';
      wrap.appendChild(d);
    });
  })();

  /* ---------------- 排名区间 ---------------- */
  (function rankCharts() {
    if (!$('#rank')) return;
    var R = D.rankGroups, rows = R.rows, base = R.base;
    var cats = rows.map(function (r) { return r.group; });

    var cb = mk('cRankBar');
    if (cb) cb.setOption({
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TIP),
      legend: { top: 0, right: 8, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
      grid: { left: 52, right: 56, top: 38, bottom: 30 },
      xAxis: axisX(cats, { axisLabel: { color: C.dim, fontSize: 11, interval: 0 } }),
      yAxis: [axisY('累计净值 / 盈亏比'), axisY('%', { splitLine: { show: false }, position: 'right' })],
      series: [{
        name: '累计净值', type: 'bar', barWidth: '26%', yAxisIndex: 0,
        data: rows.map(function (r) { return r.net; }),
        itemStyle: { borderRadius: [5, 5, 0, 0], color: grad('rgba(105,113,132,.95)', 'rgba(105,113,132,.25)', true) },
        label: { show: true, position: 'top', color: C.cyan, fontSize: 10, formatter: function (p) { return fmt(p.value, 2); } }
      }, {
        name: '交易胜率', type: 'bar', barWidth: '26%', yAxisIndex: 1,
        data: rows.map(function (r) { return r.win; }),
        itemStyle: { borderRadius: [5, 5, 0, 0], color: grad('rgba(177,166,164,.9)', 'rgba(177,166,164,.2)', true) }
      }, {
        name: '最大回撤率', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'circle', symbolSize: 6,
        data: rows.map(function (r) { return r.dd; }),
        lineStyle: { width: 2.4, color: C.red },
        itemStyle: { color: C.red, borderColor: 'rgba(153,86,82,.3)', borderWidth: 6 }
      }, {
        name: '盈亏比', type: 'line', yAxisIndex: 0, smooth: true, symbol: 'emptyCircle', symbolSize: 6,
        data: rows.map(function (r) { return r.pl; }),
        lineStyle: { width: 2, type: 'dashed', color: C.green },
        itemStyle: { color: C.green }
      }]
    });

    // 头部 vs 尾部雷达（相对全体基准的比值）
    var cr = mk('cRankRadar');
    if (cr) {
      var pick = ['前10名', '前200名', '后20名'];
      var series = pick.map(function (name, i) {
        var r = rows.filter(function (x) { return x.group === name; })[0];
        if (!r) return null;
        return {
          name: name + '（' + r.n + ' 条）',
          value: D.metrics.map(function (m) {
            var b = base[m.key] || 1;
            var v = (r[m.key] || 0) / (b || 1) * 50;
            return Math.max(0, Math.min(100, v));
          }),
          lineStyle: { width: 2 }, areaStyle: { opacity: .14 }, itemStyle: { color: PALETTE[i * 2] }
        };
      }).filter(Boolean);
      cr.setOption({
        tooltip: Object.assign({ trigger: 'item' }, TIP),
        legend: { bottom: 0, textStyle: { color: C.dim, fontSize: 10.5 }, itemWidth: 10, itemHeight: 8 },
        radar: {
          center: ['50%', '45%'], radius: '58%',
          indicator: D.metrics.map(function (m) { return { name: m.name, max: 100 }; }),
          axisName: { color: C.dim, fontSize: 10 },
          splitLine: { lineStyle: { color: 'rgba(105,113,132,.18)' } },
          splitArea: { areaStyle: { color: ['rgba(105,113,132,.03)', 'rgba(177,166,164,.05)'] } },
          axisLine: { lineStyle: { color: 'rgba(105,113,132,.18)' } }
        },
        series: [{ type: 'radar', symbolSize: 3, data: series }]
      });
    }

    // 明细表
    var th = '<thead><tr><th>区间</th><th>记录数</th><th>选手数</th><th>平均名次</th>' +
      D.metrics.map(function (m) { return '<th>' + m.name + '</th>'; }).join('') +
      '<th>盈利占比</th></tr></thead>';
    var tb = '<tbody>' + rows.map(function (r) {
      return '<tr><td class="name">' + r.group + '<div class="hint">' + r.note + '</div></td>' +
        '<td>' + num(r.n) + '</td><td>' + num(r.players) + '</td><td>' + num(r.rankMean) + '</td>' +
        D.metrics.map(function (m) { return '<td>' + fmt(r[m.key], 3) + '</td>'; }).join('') +
        '<td>' + fmt(r.posRatio, 1) + '%</td></tr>';
    }).join('') +
      '<tr class="base"><td class="name">' + base.group + '<div class="hint">' + base.note + '</div></td>' +
      '<td>' + num(base.n) + '</td><td>' + num(base.players) + '</td><td>' + num(base.rankMean) + '</td>' +
      D.metrics.map(function (m) { return '<td>' + fmt(base[m.key], 3) + '</td>'; }).join('') +
      '<td>' + fmt(base.posRatio, 1) + '%</td></tr></tbody>';
    $('#rankTable').innerHTML = th + tb;
  })();

  /* ---------------- 届次趋势 ---------------- */
  (function trendCharts() {
    if (!$('#trend')) return;
    var T = D.trend;
    var edts = T.editions.map(function (e) { return '第' + e + '届'; });

    var c = mk('cTrend');
    if (c) {
      var pctKeys = ['win', 'dd', 'risk', 'daily'];
      var series = D.metrics.map(function (m, i) {
        var isPct = pctKeys.indexOf(m.key) > -1;
        return {
          name: m.name, type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
          yAxisIndex: isPct && m.key !== 'dd' ? 1 : 0,
          data: T[m.key],
          lineStyle: { width: 2, color: PALETTE[i] },
          itemStyle: { color: PALETTE[i] },
          emphasis: { focus: 'series' },
          connectNulls: true
        };
      });
      c.setOption({
        tooltip: Object.assign({ trigger: 'axis' }, TIP),
        legend: { top: 0, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
        grid: { left: 58, right: 58, top: 44, bottom: 34 },
        xAxis: axisX(edts, { boundaryGap: false }),
        yAxis: [axisY('净值 / 盈亏比', { scale: true }), axisY('%', { splitLine: { show: false }, position: 'right' })],
        series: series
      });
    }

    var cp = mk('cTrendPlayers');
    if (cp) cp.setOption({
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' } }, TIP),
      grid: { left: 58, right: 24, top: 20, bottom: 30 },
      xAxis: axisX(edts),
      yAxis: axisY('去重选手数'),
      series: [{
        type: 'bar', barWidth: '52%', data: T.players,
        itemStyle: { borderRadius: [5, 5, 0, 0], color: grad('rgba(177,166,164,.9)', 'rgba(105,113,132,.2)', true) }
      }, {
        type: 'line', smooth: true, symbol: 'none', data: T.players,
        lineStyle: { width: 2, color: 'rgba(164,118,63,.85)' }
      }]
    });

    var cd = mk('cTrendNetDd');
    if (cd) cd.setOption({
      tooltip: Object.assign({ trigger: 'axis' }, TIP),
      legend: { bottom: 0, left: 'center', itemGap: 16, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
      grid: { left: 54, right: 54, top: 36, bottom: 54 },
      xAxis: axisX(edts, { boundaryGap: false }),
      yAxis: [axisY('累计净值', { scale: true }), axisY('最大回撤率 %', { splitLine: { show: false }, position: 'right' })],
      series: [{
        name: '累计净值', type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
        data: T.net, lineStyle: { width: 2.4, color: C.cyan },
        itemStyle: { color: C.cyan },
        areaStyle: { color: grad('rgba(105,113,132,.35)', 'rgba(105,113,132,0)', true) }
      }, {
        name: '最大回撤率', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'circle', symbolSize: 4,
        data: T.dd, lineStyle: { width: 2, color: C.red }, itemStyle: { color: C.red }
      }]
    });
  })();

  /* ---------------- 交易风格 ---------------- */
  (function styleCharts() {
    if (!$('#style')) return;
    var S = D.style;
    $('#styleTotal').textContent = '共 ' + num(S.total) + ' 位选手';

    renderComposition('cStylePie', S.pie, '位选手');

    var c2 = mk('cStyleBox');
    if (c2) {
      var shortNames = { net: '累计净值', win: '交易胜率', pl: '盈亏比',
                         dd: '最大回撤', risk: '风险度', daily: '日收益' };
      var cats = S.metrics.map(function (k) { return shortNames[k] || k; });
      var series = S.boxCats.map(function (nm, si) {
        return {
          name: nm, type: 'boxplot', boxWidth: ['22%', '45%'],
          data: S.metrics.map(function (k) { return (S.box[k] || [])[si]; }),
          itemStyle: {
            borderColor: PALETTE[si], borderWidth: 1.6,
            color: si === 0 ? 'rgba(105,113,132,.16)' : 'rgba(177,166,164,.16)'
          },
          emphasis: { itemStyle: { borderColor: '#fff', shadowBlur: 12, shadowColor: PALETTE[si] } }
        };
      });
      c2.setOption({
        tooltip: Object.assign({
          trigger: 'item',
          formatter: function (p) {
            if (!p.value) return p.name;
            var v = p.value.length === 6 ? p.value.slice(1) : p.value;
            return p.seriesName + ' · ' + p.name + '<br/>最小 ' + fmt(v[0], 2) +
              '<br/>Q1 ' + fmt(v[1], 2) + '<br/>中位 ' + fmt(v[2], 2) +
              '<br/>Q3 ' + fmt(v[3], 2) + '<br/>最大 ' + fmt(v[4], 2);
          }
        }, TIP),
        legend: { top: 0, right: 8, textStyle: { color: C.dim, fontSize: 11 }, itemWidth: 10, itemHeight: 8 },
        grid: { left: 56, right: 24, top: 34, bottom: 34 },
        xAxis: axisX(cats, { axisLabel: { color: C.dim, fontSize: 11, interval: 0 } }),
        yAxis: axisY('指标值', { scale: true }),
        series: series
      });
    }

    var wrap = $('#styleCards');
    S.table.forEach(function (t, i) {
      var d = el('div', 'card');
      d.innerHTML = '<div class="card-head"><h3>' + t.name + '</h3>' +
        '<span class="hint">' + num(t.size) + ' 人 · 占 ' + t.share + '%</span></div>' +
        '<p class="hint" style="margin:0 0 12px;line-height:1.7;font-size:12px">' + t.desc + '</p>' +
        '<div class="pd-stats">' +
        '<div class="stat"><b>' + fmt(t.net, 3) + '</b><span>平均累计净值</span></div>' +
        '<div class="stat"><b>' + fmt(t.win, 2) + '%</b><span>平均胜率</span></div>' +
        '<div class="stat"><b>' + fmt(t.pl, 3) + '</b><span>平均盈亏比</span></div>' +
        '<div class="stat"><b>' + fmt(t.dd, 2) + '%</b><span>平均最大回撤</span></div>' +
        '</div>';
      wrap.appendChild(d);
    });
  })();

  (function awardCharts() {
    if (!$('#award')) return;
    var rows = D.award || [];
    if (!rows.length) {
      $('#awardFinding').textContent = '当前没有可关联的两届特别奖账户样本。';
      return;
    }
    var labels = rows.map(function (row) { return row.name; });
    function bar(id, fields) {
      mk(id).setOption({
        color: ['#78869a', '#a08d84', '#8b9d94'],
        tooltip: Object.assign({trigger:'axis'}, TIP),
        legend: {top:0},
        grid:{left:48,right:12,top:37,bottom:36},
        xAxis:axisX(labels),
        yAxis:axisY('%', {max:100}),
        series:fields.map(function (field) {
          return {type:'bar', name:field[0], barMaxWidth:44,
            data:rows.map(function (row) {return row[field[1]];})};
        })
      });
    }
    bar('cAwardStability', [['两届净值均大于 1', 'positiveBoth']]);
    bar('cAwardProfile', [['交易胜率', 'win'], ['最大回撤率', 'dd'], ['风险度均值', 'risk']]);
    var table = $('#awardTable'), header = table.createTHead().insertRow(), body = table.createTBody();
    ['特别奖名次','配对记录','两届净值均大于 1','19 届累计净值中位数','胜率中位数',
      '最大回撤率中位数','风险度中位数','日收益率中位数'].forEach(function (label) {
      var th = el('th'); th.scope = 'col'; th.textContent = label; header.appendChild(th);
    });
    function percent(value) { return value == null ? '—' : fmt(value, 2) + '%'; }
    rows.forEach(function (row) {
      var tr = body.insertRow();
      [row.name, row.n, percent(row.positiveBoth), fmt(row.net, 3), percent(row.win), percent(row.dd),
        percent(row.risk), percent(row.daily)].forEach(function (value) {tr.insertCell().textContent = value;});
    });
    var first = rows[0], last = rows[rows.length - 1];
    $('#awardFinding').textContent = first.name + '与' + last.name + '的两届净值均大于 1 的比例分别为 ' +
      percent(first.positiveBoth) + ' 和 ' + percent(last.positiveBoth) +
      '，第 19 届最大回撤率中位数分别为 ' + percent(first.dd) + ' 和 ' + percent(last.dd) + '。';
  })();

  /* ---------------- 排名预测 ---------------- */
  (function predictCharts() {
    if (!$('#predict')) return;
    var P = D.predict, M = P.metrics, W = P.window;

    var evaluated = W.test === 20;
    $('#predictLede').textContent = '目标是第 20 届同组选手的综合名次。模型读取第 11–19 届的历史名次，目前明细覆盖至第 ' +
      P.lastHistory + ' 届。' + (evaluated && P.archivedRanks ? '第 19 届名次来自离线账户归档，第 20 届沿用原看板的 ' + num(P.actualCount) + ' 条实际名次标签。' : evaluated ? '从官网收官特别奖前段名单核对账户；第 19 届取得 ' + num(P.official19) +
      ' 条详情，第 20 届取得 ' + num(P.official20) + ' 条详情。' + num(P.actualCount) +
      ' 条同组选手可评估，其中 ' + num(P.history19Matched) + ' 条使用了第 19 届名次。样本按赛后榜单选取。' :
      '第 20 届实际名次待补。下方评估为独立的第 18 届历史回测，仅使用该届之前的数据。');
    var cards = [
      ['评估样本', num(P.testSize), ' 条', '第 ' + W.test + ' 届 · ' + P.model],
      ['对数名次 R²', fmt(M.r2, 3), '', '第 ' + W.test + ' 届'],
      ['Spearman', fmt(M.spearman, 3), '', '实际与预测的名次秩相关'],
      ['名次中位误差', num(M.maeRank), ' 名', '预测与实际名次的绝对差'],
      ['区间命中率', fmt(M.hit, 2), ' %', P.intervalModel + ' · 宏 F1 ' + fmt(M.f1, 2) + '%'],
      ['第 20 届候选', num(P.forecastSize), ' 条', '按选手和组别统计']
    ];
    var validationEditions = P.selectionEditions || (P.selectionEdition ? [P.selectionEdition] : []);
    $('#evaluationNote').textContent = '具体名次候选包括随机森林、XGBoost 和历史基线。' +
      (validationEditions.length ? '按第 ' + validationEditions.join('、') + ' 届滚动验证的各届中位绝对误差均值选用「' +
        P.model + '」，共 ' + num(P.selectionSize) + ' 条验证记录。' : '当前使用「' + P.model + '」。') +
      '区间预测单独选模，采用「' + P.intervalModel + '」。' +
      '样本中人数最多的区间占 ' + fmt(P.majorityHit, 2) + '%。' +
      '前 200 名识别召回率 ' + fmt(P.headRecall, 2) + '%，精确率 ' + fmt(P.headPrecision, 2) + '%。';
    var box = $('#predMetrics');
    cards.forEach(function (c) {
      box.appendChild(el('div', 'pm',
        '<div class="k">' + c[0] + '</div>' +
        '<div class="v">' + c[1] + '<small>' + c[2] + '</small></div>' +
        '<div class="s">' + c[3] + '</div>'));
    });

    var cs = mk('cPredScatter');
    if (cs) {
      var groups = [[], [], [], [], []];
      P.scatter.forEach(function (s) {
        groups[s[2]].push([Math.max(1, s[0]), Math.max(1, s[1])]);
      });
      var mx = 1;
      P.scatter.forEach(function (s) { mx = Math.max(mx, s[0], s[1]); });
      // 取「1/2/5 × 10^n」中不小于最大值的最近刻度，避免坐标轴留白
      var pow = Math.pow(10, Math.floor(Math.log(mx) / Math.LN10));
      var cands = [pow, pow * 2, pow * 5, pow * 10];
      for (var ci = 0; ci < cands.length; ci++) {
        if (cands[ci] >= mx * 1.05) { mx = cands[ci]; break; }
      }
      cs.setOption({
        tooltip: Object.assign({
          formatter: function (p) {
            if (p.seriesType !== 'scatter') return '';
            return '实际第 ' + num(p.value[0]) + ' 名<br/>预测第 ' + num(p.value[1]) + ' 名';
          }
        }, TIP),
        legend: { top: 0, right: 8, textStyle: { color: C.dim, fontSize: 10.5 }, itemWidth: 9, itemHeight: 9 },
        grid: { left: 66, right: 26, top: 36, bottom: 46 },
        xAxis: axisY('实际名次', {
          type: 'log', min: 1, max: mx, nameLocation: 'middle', nameGap: 30,
          axisLabel: { color: C.dim, fontSize: 10 },
          splitLine: { lineStyle: { color: 'rgba(105,113,132,.09)', type: 'dashed' } }
        }),
        yAxis: axisY('预测名次', {
          type: 'log', min: 1, max: mx,
          axisLabel: { color: C.dim, fontSize: 10 },
          splitLine: { lineStyle: { color: 'rgba(105,113,132,.09)', type: 'dashed' } }
        }),
        series: groups.map(function (pts, i) {
          return {
            name: P.confusion.labels[i], type: 'scatter', symbolSize: 6,
            data: pts, itemStyle: { color: PALETTE[i], opacity: .72 },
            emphasis: { itemStyle: { opacity: 1, shadowBlur: 12, shadowColor: PALETTE[i] } }
          };
        }).concat([{
          name: '完全命中线', type: 'line', showSymbol: false, silent: true,
          data: [[1, 1], [mx, mx]],
          lineStyle: { color: 'rgba(105,113,132,.45)', type: 'dashed', width: 1 },
          tooltip: { show: false }
        }])
      });
    }

    var ci = mk('cPredImp');
    if (ci) {
      var imp = P.importance.slice().reverse();
      $('#impHint').textContent = '第 ' + validationEditions.join('、') + ' 届 · 各届中位绝对误差均值';
      ci.setOption({
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' },
          formatter: function (p) { return p[0].name + '<br/>中位绝对误差 ' + p[0].value + ' 名'; } }, TIP),
        grid: { left: 110, right: 54, top: 14, bottom: 22 },
        xAxis: axisY('', { axisLabel: { color: C.dim, fontSize: 10 } }),
        yAxis: axisX(imp.map(function (d) { return d.name; }),
          { axisLabel: { color: C.dim, fontSize: 10.5 }, axisLine: { show: false } }),
        series: [{
          type: 'bar', barWidth: '56%',
          data: imp.map(function (d) { return d.v; }),
          itemStyle: { borderRadius: [0, 5, 5, 0], color: grad('rgba(177,166,164,.9)', 'rgba(105,113,132,.55)') },
          label: { show: true, position: 'right', color: C.dim, fontSize: 9.5 }
        }]
      });
    }

    var cmap = mk('cPredCm');
    if (cmap) {
      var L = P.confusion.labels, mat = [], maxv = 0;
      P.confusion.matrix.forEach(function (row, i) {
        row.forEach(function (v, j) { mat.push([j, i, v]); if (v > maxv) maxv = v; });
      });
      cmap.setOption({
        tooltip: Object.assign({
          formatter: function (p) {
            return '实际 ' + L[p.value[1]] + '<br/>预测 ' + L[p.value[0]] + '<br/>样本 ' + p.value[2];
          }
        }, TIP),
        grid: { left: 86, right: 24, top: 22, bottom: 68 },
        xAxis: axisX(L, { axisLabel: { color: C.dim, fontSize: 10, rotate: 22 } }),
        yAxis: axisX(L, { axisLabel: { color: C.dim, fontSize: 10 }, inverse: true, axisLine: { show: false } }),
        visualMap: {
          min: 0, max: maxv || 1, calculable: false, orient: 'horizontal',
          left: 'center', bottom: 10, itemWidth: 12, itemHeight: 70,
          textStyle: { color: C.dim, fontSize: 10 },
          inRange: { color: ['rgba(242,241,239,.9)', 'rgba(105,113,132,.35)', 'rgba(177,166,164,.75)', 'rgba(167,128,142,.95)'] }
        },
        series: [{
          type: 'heatmap', data: mat,
          label: { show: true, color: '#413f3d', fontSize: 10.5 },
          itemStyle: { borderColor: 'rgba(255,255,255,.9)', borderWidth: 2, borderRadius: 4 },
          emphasis: { itemStyle: { shadowBlur: 14, shadowColor: 'rgba(105,113,132,.8)' } }
        }]
      });
    }

    var ck = mk('cPredTopK');
    if (ck) {
      var ks = ['p20', 'p50', 'p100'], kn = ['前20名', '前50名', '前100名'];
      ck.setOption({
        tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' },
          formatter: function (p) {
            var s = p[0].name;
            p.forEach(function (x) { s += '<br/>' + x.marker + x.seriesName + ' ' + x.value + '%'; });
            return s;
          } }, TIP),
        legend: { top: 0, right: 8, textStyle: { color: C.dim, fontSize: 10.5 }, itemWidth: 10, itemHeight: 8 },
        grid: { left: 52, right: 22, top: 36, bottom: 34 },
        xAxis: axisX(kn),
        yAxis: axisY('命中率 %', { axisLabel: { color: C.dim, fontSize: 10, formatter: '{value}%' } }),
        series: [{
          name: '样本内 Top-K 命中率', type: 'bar', barWidth: '30%',
          data: ks.map(function (k) { return P.precision[k]; }),
          itemStyle: { borderRadius: [5, 5, 0, 0], color: grad('rgba(105,113,132,.95)', 'rgba(105,113,132,.2)', true) },
          label: { show: true, position: 'top', color: C.cyan, fontSize: 10, formatter: '{c}%' }
        }, {
          name: '随机基线', type: 'bar', barWidth: '30%',
          data: ks.map(function (k) { return (P.baseline || {})[k]; }),
          itemStyle: { borderRadius: [5, 5, 0, 0], color: 'rgba(177,166,164,.45)' },
          label: { show: true, position: 'top', color: C.dim, fontSize: 9.5, formatter: '{c}%' }
        }]
      });
    }

    var cr = mk('cPredResid');
    if (cr) cr.setOption({
      tooltip: Object.assign({ trigger: 'axis', axisPointer: { type: 'shadow' },
        formatter: function (p) { return '残差 ' + p[0].name + '<br/>样本 ' + p[0].value; } }, TIP),
      grid: { left: 52, right: 22, top: 22, bottom: 44 },
      xAxis: axisX(P.resid.labels, { axisLabel: { color: C.dim, fontSize: 9.5, rotate: 32 } }),
      yAxis: axisY('样本数'),
      series: [{
        type: 'bar', barWidth: '80%', data: P.resid.counts,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: grad('rgba(164,118,63,.9)', 'rgba(153,86,82,.45)', true) }
      }]
    });

    var matched = P.actualRows || [];
    var tableRows = matched.length ? matched : P.top20;
    $('#predictionTableTitle').textContent = matched.length ? '第 20 届预测与实际名次明细' : '第 20 届名次预测';
    $('#top20Hint').textContent = matched.length ? '按实际同组名次排序 · 共 ' + num(matched.length) + ' 条已匹配记录' :
      '展示预测名次靠前的 20 条 · 实际名次待核验';
    var lastCol = matched.length ? '绝对误差' : '有效历史届数';
    var head = '<thead><tr><th>选手</th><th>组别</th><th>预测名次</th><th>第 20 届实际名次</th><th>' + lastCol + '</th>' + (matched.length ? '<th>预测区间</th><th>实际区间</th>' : '') + '</tr></thead>';
    var body = '<tbody>' + tableRows.map(function (r) {
      var row = document.createElement('tr');
      [r.name, r.grp, num(r.pred), num(r.actual), num(matched.length ? r.error : r.history)]
        .concat(matched.length ? [r.predBucket, r.actualBucket] : []).forEach(function (value) {
        row.insertCell().textContent = value;
      });
      return row.outerHTML;
    }).join('') + '</tbody>';
    $('#predTable').innerHTML = head + body;
  })();

  /* ---------------- 选手画像检索 ---------------- */
  (function playerModule() {
    if (!$('#players')) return;
    var list = $('#playerList'), detail = $('#playerDetail'), input = $('#playerSearch');
    var players = D.players.slice().sort(function (a, b) {
      var ra = a.best === null ? 1e9 : a.best, rb = b.best === null ? 1e9 : b.best;
      return ra - rb;
    });
    var LIMIT = 80, active = null;

    function disposeIn(ids) {
      ids.forEach(function (id) {
        var c = cache[id];
        if (c) {
          if (!c.isDisposed()) c.dispose();
          charts = charts.filter(function (x) { return x !== c; });
          delete cache[id];
        }
      });
    }

    function paint(kw) {
      kw = (kw || '').trim().toLowerCase();
      var hit = kw ? players.filter(function (p) {
        return p.name.toLowerCase().indexOf(kw) > -1 ||
          (p.style || '').toLowerCase().indexOf(kw) > -1;
      }) : players;
      list.innerHTML = '';
      $('#playerCount').textContent = hit.length + ' / ' + players.length;
      if (!hit.length) {
        list.appendChild(el('li', null, '<span class="nm">未匹配到选手</span>'));
        return;
      }
      hit.slice(0, LIMIT).forEach(function (p) {
        var li = el('li', active && active.name === p.name ? 'on' : '',
          '<span class="nm">' + p.name + '</span>' +
          '<span class="tagm">' + (p.best === null ? '—' : '#' + p.best) + '</span>' +
          '<span class="tagm">' + p.n + '届</span>');
        li.addEventListener('click', function () {
          list.querySelectorAll('li').forEach(function (x) { x.classList.remove('on'); });
          li.classList.add('on');
          show(p);
        });
        list.appendChild(li);
      });
      if (hit.length > LIMIT) {
        list.appendChild(el('li', null, '<span class="nm" style="color:#625f5d">仅显示前 ' +
          LIMIT + ' 条，可继续输入关键词筛选</span>'));
      }
    }

    function show(p) {
      active = p;
      disposeIn(['pdRadar', 'pdHist', 'pdDaily']);
      var h = p.h || [];
      var tagCls = p.cluster === 0 ? '' : 'gold';
      detail.innerHTML = '<div class="pd-head"><div>' +
        '<h3 class="pd-name">' + p.name + '</h3>' +
        '<div class="pd-sub">参赛 ' + p.n + ' 届 · 最佳综合排名 ' +
        (p.best === null ? '—' : '第 ' + p.best + ' 名') + '</div>' +
        '<div class="pd-tags">' +
        '<span class="badge ' + tagCls + '">' + (p.style || '未分类') + '</span>' +
        (p.cluster == null ? '' : '<span class="badge">聚类 ' + p.cluster + '</span>') +
        '</div></div></div>' +
        '<div class="profile-themes" id="profileThemes"></div>' +
        '<div class="pd-grid">' +
        '<div>' +
        '<div class="hint" style="margin-top:12px">历史画像样本百分位（回撤与风险度反向）</div>' +
        '<div id="pdRadar" style="height:268px"></div></div>' +
        '<div><div class="hint">历届净值与综合排名轨迹（最多 12 届）</div>' +
        '<div id="pdHist" style="height:300px"></div>' +
        '<div class="hint" style="margin-top:6px">共 ' + h.length + ' 条历届记录</div></div>' +
        '</div>';

      var themes = [
        ['收益表现', [['届均累计净值', p.net, ' 倍'], ['日收益率均值', p.daily, '%']]],
        ['风险控制', [['平均最大回撤率', p.dd, '%'], ['平均风险度', p.risk, '%']]],
        ['交易表现', [['平均交易胜率', p.win, '%'], ['平均盈亏比', p.pl, '']]]
      ];
      themes.forEach(function (theme) {
        var card = el('section', 'profile-theme');
        var title = el('h4');
        title.textContent = theme[0];
        var metrics = el('dl');
        theme[1].forEach(function (metric) {
          var row = el('div'), label = el('dt'), value = el('dd');
          label.textContent = metric[0];
          value.textContent = metric[1] == null ? '—' : fmt(metric[1], 3) + metric[2];
          row.append(label, value);
          metrics.appendChild(row);
        });
        card.append(title, metrics);
        $('#profileThemes').appendChild(card);
      });
      var history = el('section', 'profile-history',
        '<h4>历届账户明细</h4><p class="hint">按账户记录展示。空值表示未采集。' +
        '已采集账户可查看日度净值。毛利润、手续费、多空、日内隔夜和品种级数据尚未接入。</p>');
      var wrap = el('div', 'table-wrap');
      var table = el('table', 'dtable');
      var headings = ['届次','组别','账户昵称','期初权益（元）','期末权益（元）','累计净值',
        '累计净利润（元）','最大本金收益率（%）','日收益率均值（%）','最大回撤率（%）',
        '风险度均值（%）','交易胜率（%）','盈亏比','盈利天数','亏损天数','综合排名'];
      var header = table.createTHead().insertRow();
      headings.forEach(function (name) {
        var th = el('th');
        th.textContent = name;
        th.scope = 'col';
        header.appendChild(th);
      });
      var body = table.createTBody();
      (p.accounts || []).forEach(function (record) {
        var row = body.insertRow();
        record.forEach(function (value, index) {
          row.insertCell().textContent = value == null || value === 'nan' ? '—' :
            (index < 3 ? value : fmt(value, 3));
        });
      });
      wrap.appendChild(table);
      history.appendChild(wrap);
      detail.appendChild(history);

      var series = p.dailySeries || [];
      if (series.length && series.some(function (entry) { return entry.points.length; })) {
        var daily = el('section', 'profile-history', '<h4>日度净值</h4><label>届次与账户 <select id="pdDailySelect"></select></label>' +
          '<div id="pdDaily" style="height:260px"></div>');
        detail.insertBefore(daily, history);
        var select = $('#pdDailySelect');
        series.filter(function (entry) { return entry.points.length; }).forEach(function (entry, index) {
          select.add(new Option('第 ' + entry.edition + ' 届 · ' + entry.account, index));
        });
        var valid = series.filter(function (entry) { return entry.points.length; });
        var chart = mk('pdDaily');
        function drawDaily() {
          var points = valid[Number(select.value)].points;
          chart.setOption({
            tooltip: Object.assign({trigger: 'axis'}, TIP),
            grid: {left: 46, right: 18, top: 24, bottom: 32},
            xAxis: axisX(points.map(function (point) { return point[0]; }), {boundaryGap: false}),
            yAxis: axisY('累计净值', {scale: true}),
            series: [{type:'line', showSymbol:false, data:points.map(function (point) { return point[1]; }),
              lineStyle:{color:C.cyan,width:2}, itemStyle:{color:C.cyan}}]
          }, true);
        }
        select.addEventListener('change', drawDaily);
        drawDaily();
      }
      if (!p.p.length) $('#pdRadar').textContent = '该选手暂无可比的历史画像百分位。';
      var radar = p.p.length ? mk('pdRadar') : null;
      if (radar) radar.setOption({
        tooltip: Object.assign({ trigger: 'item' }, TIP),
        radar: {
          center: ['50%', '50%'], radius: '66%',
          indicator: D.metrics.map(function (m) { return { name: m.name, max: 100 }; }),
          axisName: { color: C.dim, fontSize: 9.5 },
          splitLine: { lineStyle: { color: 'rgba(105,113,132,.16)' } },
          splitArea: { areaStyle: { color: ['rgba(105,113,132,.03)', 'rgba(177,166,164,.05)'] } },
          axisLine: { lineStyle: { color: 'rgba(105,113,132,.16)' } }
        },
        series: [{
          type: 'radar', symbolSize: 3,
          data: [{
            name: '百分位', value: p.p,
            lineStyle: { color: C.cyan, width: 2 },
            itemStyle: { color: C.cyan },
            areaStyle: { color: grad('rgba(105,113,132,.42)', 'rgba(177,166,164,.12)') }
          }]
        }]
      });

      var line = mk('pdHist');
      if (line) line.setOption({
        tooltip: Object.assign({ trigger: 'axis' }, TIP),
        legend: { top: 0, right: 6, textStyle: { color: C.dim, fontSize: 10.5 }, itemWidth: 10, itemHeight: 8 },
        grid: { left: 50, right: 52, top: 34, bottom: 30 },
        xAxis: axisX(h.map(function (r) { return '第' + r[0] + '届'; }),
          { axisLabel: { color: C.dim, fontSize: 9.5, rotate: 26 } }),
        yAxis: [axisY('累计净值', { scale: true }),
                axisY('综合排名', { splitLine: { show: false }, position: 'right',
                  inverse: true, minInterval: 1, nameLocation: 'middle', nameGap: 42 })],
        series: [{
          name: '累计净值', type: 'line', smooth: true, symbol: 'circle', symbolSize: 5,
          data: h.map(function (r) { return r[1]; }),
          lineStyle: { width: 2.2, color: C.cyan }, itemStyle: { color: C.cyan },
          areaStyle: { color: grad('rgba(105,113,132,.3)', 'rgba(105,113,132,0)', true) },
          markLine: {
            symbol: 'none', silent: true,
            label: { color: C.dim, fontSize: 9, formatter: '净值 1.0' },
            lineStyle: { color: 'rgba(255,255,255,.22)', type: 'dashed' },
            data: [{ yAxis: 1 }]
          }
        }, {
          name: '综合排名', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'emptyCircle', symbolSize: 5,
          data: h.map(function (r) { return r[4]; }),
          lineStyle: { width: 1.8, color: C.amber }, itemStyle: { color: C.amber },
          connectNulls: true
        }]
      });
    }

    input.addEventListener('input', function () { paint(input.value); });
    if (players.length) {
      show(players[0]);
      paint('');
    }
  })();

})();


