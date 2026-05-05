#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="${PROJECT_DIR}/reports"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$REPORTS_DIR"

BASE_URL="${BASE_URL:-http://localhost}"
DURATION="${DURATION:-3m}"
VUS="${VUS:-1000}"

echo "========================================="
echo " k6 压力测试"
echo "========================================="
echo " 目标地址: ${BASE_URL}"
echo " 持续时间: ${DURATION}"
echo " 最大VUs:  ${VUS}"
echo " 报告目录: ${REPORTS_DIR}"
echo "========================================="

JSON_REPORT="${REPORTS_DIR}/load-test-${TIMESTAMP}.json"
SUMMARY_REPORT="${REPORTS_DIR}/load-test-${TIMESTAMP}-summary.txt"

if ! command -v k6 &>/dev/null; then
  echo "错误: 未找到 k6，请先安装: https://k6.io/docs/get-started/installation/"
  exit 1
fi

echo ""
echo "正在运行 k6 压力测试..."
k6 run \
  --env BASE_URL="${BASE_URL}" \
  --out json="${JSON_REPORT}" \
  --summary-export="${REPORTS_DIR}/load-test-${TIMESTAMP}-summary.json" \
  "${SCRIPT_DIR}/load-test.js" \
  2>&1 | tee "${SUMMARY_REPORT}"

echo ""
echo "正在生成 HTML 报告..."

HTML_REPORT="${REPORTS_DIR}/load-test-${TIMESTAMP}.html"

cat > "${HTML_REPORT}" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>k6 压力测试报告</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { text-align: center; font-size: 2rem; margin-bottom: 2rem; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .meta { text-align: center; color: #94a3b8; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
    .card { background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }
    .card h3 { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .card .value { font-size: 2rem; font-weight: 700; }
    .card .value.green { color: #4ade80; }
    .card .value.yellow { color: #facc15; }
    .card .value.red { color: #f87171; }
    .card .value.blue { color: #60a5fa; }
    .card .value.purple { color: #a78bfa; }
    table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; border: 1px solid #334155; }
    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #0f172a; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    td { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.9rem; }
    .section-title { font-size: 1.25rem; margin: 2rem 0 1rem; color: #cbd5e1; }
    .pass { color: #4ade80; }
    .fail { color: #f87171; }
  </style>
</head>
<body>
  <div class="container">
    <h1>k6 压力测试报告</h1>
    <div class="meta" id="meta"></div>
    <div class="grid" id="summary-cards"></div>
    <h2 class="section-title">请求指标</h2>
    <table id="metrics-table"><thead><tr><th>指标</th><th>平均值</th><th>最小值</th><th>最大值</th><th>P90</th><th>P95</th><th>P99</th></tr></thead><tbody></tbody></table>
    <h2 class="section-title">阈值检查</h2>
    <table id="thresholds-table"><thead><tr><th>阈值</th><th>值</th><th>结果</th></tr></thead><tbody></tbody></table>
  </div>
  <script>
HTMLEOF

cat >> "${HTML_REPORT}" << EOF
    const summaryData = $(cat "${REPORTS_DIR}/load-test-${TIMESTAMP}-summary.json" 2>/dev/null || echo '{}');
    const timestamp = '${TIMESTAMP}';
    const baseUrl = '${BASE_URL}';
EOF

cat >> "${HTML_REPORT}" << 'JSEOF'
    document.getElementById('meta').textContent = `测试时间: ${timestamp} | 目标: ${baseUrl}`;
    if (summaryData.root_group) {
      const metrics = summaryData.metrics || {};
      const httpReqs = metrics.http_reqs || {};
      const httpDur = metrics.http_req_duration || {};
      const iterations = metrics.iterations || {};
      const dataReceived = metrics.data_received || {};
      const dataSent = metrics.data_sent || {};
      const vusMax = metrics.vus_max || {};
      function fmt(val) { return val !== undefined ? val.toFixed(2) : 'N/A'; }
      function fmtBytes(bytes) {
        if (bytes === undefined) return 'N/A';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
      }
      const cards = [
        { title: '总请求数', value: httpReqs.values?.count || 0, cls: 'blue' },
        { title: '请求速率', value: fmt(httpReqs.values?.rate) + ' req/s', cls: 'purple' },
        { title: '平均延迟', value: fmt(httpDur.values?.avg) + ' ms', cls: httpDur.values?.avg < 100 ? 'green' : httpDur.values?.avg < 200 ? 'yellow' : 'red' },
        { title: 'P99 延迟', value: fmt(httpDur.values?.['p(99)']) + ' ms', cls: httpDur.values?.['p(99)'] < 200 ? 'green' : 'yellow' },
        { title: '最大VUs', value: vusMax.values?.value || 0, cls: 'blue' },
        { title: '迭代次数', value: iterations.values?.count || 0, cls: 'purple' },
        { title: '接收数据', value: fmtBytes(dataReceived.values?.count), cls: 'green' },
        { title: '发送数据', value: fmtBytes(dataSent.values?.count), cls: 'green' },
      ];
      const cardsEl = document.getElementById('summary-cards');
      cards.forEach(c => {
        cardsEl.innerHTML += `<div class="card"><h3>${c.title}</h3><div class="value ${c.cls}">${c.value}</div></div>`;
      });
      const metricsRows = [
        { name: 'HTTP 请求延迟', data: httpDur.values },
        { name: 'API 延迟 (自定义)', data: metrics.api_latency?.values },
      ];
      const tbody = document.querySelector('#metrics-table tbody');
      metricsRows.forEach(row => {
        if (!row.data) return;
        tbody.innerHTML += `<tr><td>${row.name}</td><td>${fmt(row.data.avg)}</td><td>${fmt(row.data.min)}</td><td>${fmt(row.data.max)}</td><td>${fmt(row.data['p(90)'])}</td><td>${fmt(row.data['p(95)'])}</td><td>${fmt(row.data['p(99)'])}</td></tr>`;
      });
      const thresholdsTbody = document.querySelector('#thresholds-table tbody');
      Object.entries(metrics).forEach(([key, m]) => {
        if (m.thresholds) {
          Object.entries(m.thresholds).forEach(([tKey, tVal]) => {
            const ok = tVal.ok;
            thresholdsTbody.innerHTML += `<tr><td>${key}: ${tKey}</td><td>${fmt(tVal.value)}</td><td class="${ok ? 'pass' : 'fail'}">${ok ? 'PASS ✓' : 'FAIL ✗'}</td></tr>`;
          });
        }
      });
    }
  </script>
</body>
</html>
JSEOF

echo ""
echo "========================================="
echo " 测试完成！"
echo "========================================="
echo " JSON 报告:  ${JSON_REPORT}"
echo " 摘要报告:   ${SUMMARY_REPORT}"
echo " HTML 报告:  ${HTML_REPORT}"
echo "========================================="
