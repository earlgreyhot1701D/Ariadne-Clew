
// scripts/main_js.js
// Deterministic rendering of EXACT sections from structured JSON.
// Sections: Summary, Key Insights, MVP Changes, Design Tradeoffs, Code Discovered, Post-MVP Ideas

import { getRecap } from './api_js.js';

let currentRecapData = null;

function setStatus(message, isError = false) {
  const statusEl = document.getElementById('status');
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.className = isError ? 'error' : 'loading';
  statusEl.style.display = 'block';
  if (!isError && /complete|success/i.test(message)) {
    statusEl.className = 'success';
    setTimeout(() => { statusEl.style.display = 'none'; }, 2000);
  }
}

function resolvePayload(data) {
  // Accept either {status, result:{...}} or {...}
  return (data && typeof data === 'object' && 'result' in data && data.result) ? data.result : data;
}

function esc(s) {
  const t = document.createElement('textarea');
  t.textContent = String(s == null ? '' : s);
  return t.value;
}

function pickReadable(item) {
  if (item == null) return '';
  if (typeof item === 'string') return item;
  if (typeof item === 'number' || typeof item === 'boolean') return String(item);
  // object: try common keys
  const candidates = ['insight','text','issue','message','note','context','rationale','value','title'];
  for (const k of candidates) {
    if (k in item && item[k]) return String(item[k]);
  }
  // last resort: concise JSON
  try { return JSON.stringify(item); } catch { return String(item); }
}

function listHTML(items) {
  if (!items || !items.length) return '<p class="subtle">None.</p>';
  const lis = items.map(i => `<li>${esc(pickReadable(i))}</li>`).join('');
  return `<ul>${lis}</ul>`;
}

function codeDiscoveredHTML(snippets) {
  if (!snippets || !snippets.length) return '<p class="subtle">None.</p>';
  const lis = snippets.slice(0, 5).map(s => {
    const lang = esc((s && s.language) || 'text');
    const ctx  = pickReadable(s && (s.context ?? s.description ?? ''));
    const code = (s && (s.content ?? s.code ?? '')) || '';
    const preview = esc(code.length > 160 ? code.slice(0,160) + '…' : code);
    const ctxPart = ctx ? ` <em>(${esc(ctx)})</em>` : '';
    return `<li><strong>[${lang}]</strong> <code>${preview}</code>${ctxPart}</li>`;
  }).join('');
  return `<ul>${lis}</ul>`;
}

function buildHumanFromStructured(structured) {
  const sess = esc(structured.session_id || 'agentcore-session');
  const sum  = esc(structured.summary || '');
  const aha  = structured.aha_moments || [];
  const mvp  = structured.mvp_changes || [];
  const trade= structured.design_tradeoffs || [];
  const code = structured.code_snippets || [];
  const post = structured.post_mvp_ideas || [];

  const parts = [];
  parts.push(`<h2>Session: ${sess}</h2>`);
  parts.push(`<h3>Summary</h3>`, sum ? `<p>${sum}</p>` : `<p class="subtle">No summary.</p>`);
  parts.push(`<h3>Key Insights</h3>`, listHTML(aha));
  parts.push(`<h3>MVP Changes</h3>`, listHTML(mvp));
  parts.push(`<h3>Design Tradeoffs</h3>`, listHTML(trade));
  parts.push(`<h3>Code Discovered</h3>`, codeDiscoveredHTML(code));
  parts.push(`<h3>Post-MVP Ideas</h3>`, listHTML(post));
  return parts.join('');
}

function displayResults(payloadLike) {
  const payload = resolvePayload(payloadLike);
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  const jsonPanel  = document.querySelector('#jsonOutput .panel-content');
  if (!humanPanel || !jsonPanel) { console.error('Output panels not found'); return; }

  // Prefer structured_data (or raw_json), build HTML from that.
  const structured = payload.structured_data || payload.raw_json || payload || {};
  let html = '';
  try {
    html = buildHumanFromStructured(structured);
  } catch (e) {
    console.warn('[AC] buildHumanFromStructured failed, falling back to backend HTML', e);
    html = String(payload.human_readable || 'Analysis complete.');
  }

  humanPanel.innerHTML = `<div class="recap-html">${html}</div>`;
  jsonPanel.textContent = JSON.stringify(structured, null, 2);

  const copyBtn = document.getElementById('copy-btn');
  const exportBtn = document.getElementById('export-md');
  if (copyBtn) copyBtn.disabled = false;
  if (exportBtn) exportBtn.disabled = false;
}

function clearResults() {
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  const jsonPanel = document.querySelector('#jsonOutput .panel-content');
  if (humanPanel) {
    humanPanel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🧶</div>
        <p>Your reasoning extraction will appear here</p>
        <p style="font-size: 0.85rem;">Enter a chat transcript above to get started</p>
      </div>`;
  }
  if (jsonPanel) {
    jsonPanel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">{ }</div>
        <p>Machine-readable output will appear here</p>
        <p style="font-size: 0.85rem;">Perfect for integrations and automation</p>
      </div>`;
  }
}

async function handleSubmit(e) {
  e.preventDefault();
  const sessionInput = document.getElementById('session-id');
  if (!sessionInput) return;
  const chatLog = (sessionInput.value || '').trim();
  if (!chatLog) { setStatus('Please enter a chat transcript', true); return; }

  try {
    setStatus('🔄 Processing transcript...');
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.disabled = true;

    const data = await getRecap(chatLog);
    currentRecapData = data;
    displayResults(data);
    setStatus('✅ Extraction complete!');
  } catch (error) {
    console.error('Error:', error);
    clearResults();
    let msg = '❌ ';
    const m = (error && error.message) ? error.message : String(error);
    if (/Failed to fetch/i.test(m)) msg += 'Connection failed. Is bridge_server.py running?';
    else if (/HTTP 5\d\d/.test(m)) msg += 'Server error. Check AgentCore connection.';
    else msg += m;
    setStatus(msg, true);
  } finally {
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.disabled = false;
  }
}

function handleCopy() {
  if (!currentRecapData) { setStatus('No output to copy', true); return; }
  const jsonPanel = document.querySelector('#jsonOutput .panel-content');
  if (!jsonPanel) return;
  navigator.clipboard.writeText(jsonPanel.textContent)
    .then(() => setStatus('📋 Copied to clipboard!'))
    .catch(() => setStatus('Failed to copy', true));
}

function handleExport() {
  if (!currentRecapData) { setStatus('No output to export', true); return; }
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  if (!humanPanel) return;
  const markdown = `# Ariadne Clew Recap\n\n${humanPanel.textContent}\n\n## Raw Data\n\n\`\`\`json\n${JSON.stringify(resolvePayload(currentRecapData).structured_data || currentRecapData, null, 2)}\n\`\`\``;
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'ariadne-recap.md'; a.click();
  URL.revokeObjectURL(url);
  setStatus('💾 Exported successfully!');
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('Ariadne Clew UI initialized');

  const form = document.getElementById('recap-form');
  if (form) form.addEventListener('submit', handleSubmit);

  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) { copyBtn.addEventListener('click', handleCopy); copyBtn.disabled = true; }

  const exportBtn = document.getElementById('export-md');
  if (exportBtn) { exportBtn.addEventListener('click', handleExport); exportBtn.disabled = true; }

  const dropZone = document.getElementById('drop-zone');
  if (dropZone) dropZone.addEventListener('click', () => setStatus('💡 Paste transcript in the field above', true));

  setStatus('Ready to extract reasoning');
});
