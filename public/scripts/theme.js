
const THEME_KEY = 'theme';

export function initThemeToggle(toggleEl) {
  const body = document.body;
  const saved = localStorage.getItem(THEME_KEY);
  if (saved) {
    body.dataset.theme = saved;
    toggleEl.checked = saved === 'dark';
  }

  toggleEl.addEventListener('change', (e) => {
    const newTheme = e.target.checked ? 'dark' : 'light';
    body.dataset.theme = newTheme;
    localStorage.setItem(THEME_KEY, newTheme);
  });
}
