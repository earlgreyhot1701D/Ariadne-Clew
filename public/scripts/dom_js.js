
// scripts/dom_js.js
// Null-safe DOM helpers (no-throw), good for multi-page reuse.
export function byId(id) {
  return document.getElementById(id);
}

export function qs(selector, root = document) {
  return root.querySelector(selector);
}

export function show(id) {
  const el = byId(id); if (!el) return false;
  el.style.display = 'block'; return true;
}

export function hide(id) {
  const el = byId(id); if (!el) return false;
  el.style.display = 'none'; return true;
}

export function setText(id, text) {
  const el = byId(id); if (!el) return false;
  el.textContent = text; return true;
}

export function setHTML(id, html) {
  const el = byId(id); if (!el) return false;
  el.innerHTML = html; return true;
}

export function enableElement(id) {
  const el = byId(id); if (!el) return false;
  if ('disabled' in el) el.disabled = false;
  return true;
}

export function disableElement(id) {
  const el = byId(id); if (!el) return false;
  if ('disabled' in el) el.disabled = true;
  return true;
}

export function onClick(id, cb) {
  const el = byId(id); if (!el) return false;
  el.addEventListener('click', cb); return true;
}

export function onSubmit(id, cb) {
  const el = byId(id); if (!el) return false;
  el.addEventListener('submit', cb); return true;
}

export function getValue(id) {
  const el = byId(id); return el ? el.value : '';
}
