
export function setStatus(message, isError = false) {
  const statusRegion = document.getElementById('status');
  statusRegion.textContent = message;
  statusRegion.style.color = isError ? 'red' : 'black';
  statusRegion.setAttribute('aria-busy', 'false');
}
