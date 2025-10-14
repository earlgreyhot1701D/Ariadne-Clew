
// scripts/api_js.js
// Flexible base URL + timeout + better errors (original filename).

const DEFAULT_BASE = (typeof window !== 'undefined' && window.AC_API_BASE)
  ? window.AC_API_BASE
  : (location && location.origin ? location.origin.replace(/\/$/, '') : '');

const API_BASE_URL = `${DEFAULT_BASE}`.replace(/\/$/, '');

export async function getRecap(chatLog, sessionId = 'default', { timeoutMs = 30000 } = {}) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(new Error('Request timeout')), timeoutMs);

  let resp;
  try {
    resp = await fetch(`${API_BASE_URL}/v1/recap`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_log: chatLog, session_id: sessionId }),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(t);
  }

  let data;
  try {
    data = await resp.json();
  } catch {
    const text = await resp.text().catch(() => '');
    throw new Error(`Bad JSON from server (status ${resp.status}): ${text.slice(0,200)}`);
    }

  if (!resp.ok) {
    const errMsg = (data && (data.error || data.message)) || `HTTP ${resp.status}`;
    throw new Error(errMsg);
  }
  return data;
}
