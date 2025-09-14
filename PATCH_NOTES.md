# Proposed front-end improvements

Scope
- Keep simple static hosting with public folder.
- Add resilient fetch with timeout and clear errors.
- Add a11y: labels, aria-live status, keyboard shortcut, focusable output.
- Add copy to clipboard for output.
- Add toggle between summary and raw JSON.
- Use safe textContent rendering to avoid XSS.
- Keep your branding line and tone. No em dashes.

How to test
1. Open public/index.html.
2. Set window.AC_API_BASE in the devtools console if needed:
   window.AC_API_BASE = "https://example.com";
3. Enter a test session id and submit.
4. Toggle Summary and Raw JSON to validate both renderers.
5. Simulate errors by pointing AC_API_BASE to a 404 to confirm user friendly errors.

Drop-in
- Replace your public/index.html, public/script.js, public/style.css with these versions or diff them into your repo.
