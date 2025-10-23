// metrics_severity.js
const fs = require('fs');

function loadReport(path) {
  if (!fs.existsSync(path)) {
    console.error(`❌ Report file not found: ${path}`);
    process.exit(1);
  }
  const raw = fs.readFileSync(path, 'utf8');
  try {
    return JSON.parse(raw);
  } catch (e) {
    console.error('❌ Invalid JSON in report:', e.message);
    process.exit(1);
  }
}

function pickIssues(obj) {
  // Snyk “test --json” (Open Source) normalmente usa 'vulnerabilities'
  // Em versões/targets diferentes pode vir 'issues'
  if (Array.isArray(obj.vulnerabilities)) return obj.vulnerabilities;
  if (Array.isArray(obj.issues)) return obj.issues;
  return [];
}

function severityOf(item) {
  // Snyk usa: 'critical' | 'high' | 'medium' | 'low'
  // Alguns objetos podem ter outro formato; protegemos:
  return (item.severity || item.severityLevel || 'unknown').toLowerCase();
}

function pct(n, total) {
  if (total === 0) return '0.0%';
  return `${((n / total) * 100).toFixed(1)}%`;
}

(function main() {
  const reportPath = process.argv[2] || 'snyk-report.json';
  const outPath = process.argv[3] || 'severity-summary.md';

  const data = loadReport(reportPath);

  if (data.error) {
    console.error(`❌ Snyk error in report: ${data.error}`);
    process.exit(2);
  }

  const issues = pickIssues(data);
  const counts = { critical: 0, high: 0, medium: 0, low: 0, unknown: 0 };

  for (const i of issues) {
    const sev = severityOf(i);
    if (counts.hasOwnProperty(sev)) counts[sev]++;
    else counts.unknown++;
  }

  const total = issues.length;
  const lines = [];
  lines.push(`# Severidade – Resumo`);
  lines.push('');
  lines.push(`Total de vulnerabilidades: **${total}**`);
  lines.push('');
  lines.push(`| Severidade | Qtde | % |`);
  lines.push(`|---|---:|---:|`);
  lines.push(`| Critical | ${counts.critical} | ${pct(counts.critical, total)} |`);
  lines.push(`| High     | ${counts.high}     | ${pct(counts.high, total)}     |`);
  lines.push(`| Medium   | ${counts.medium}   | ${pct(counts.medium, total)}   |`);
  lines.push(`| Low      | ${counts.low}      | ${pct(counts.low, total)}      |`);
  if (counts.unknown > 0) {
    lines.push(`| Unknown  | ${counts.unknown}  | ${pct(counts.unknown, total)}  |`);
  }
  lines.push('');
  lines.push(`_Fonte: snyk-report.json_`);

  fs.writeFileSync(outPath, lines.join('\n'), 'utf8');
  console.log(`✅ Gerado resumo de severidade em: ${outPath}`);
})();
