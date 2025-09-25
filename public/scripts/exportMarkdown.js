export function htmlToMarkdown(element) {
  const lines = [];
  function walk(node) {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent.trim();
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    switch (tag) {
      case 'h1':
        lines.push(`# ${node.textContent.trim()}`);
        break;
      case 'h2':
        lines.push(`## ${node.textContent.trim()}`);
        break;
      case 'h3':
        lines.push(`### ${node.textContent.trim()}`);
        break;
      case 'p':
        lines.push(node.textContent.trim());
        break;
      case 'li':
        lines.push(`- ${node.textContent.trim()}`);
        break;
      case 'ul':
      case 'ol':
        Array.from(node.children).forEach((child) => walk(child));
        break;
      default:
        Array.from(node.childNodes).forEach((child) => walk(child));
    }
  }
  walk(element);
  return lines.join('\n\n');
}

export function exportMarkdownFromRecap(recapEl) {
  const md = htmlToMarkdown(recapEl);
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'recap.md';
  a.click();
  URL.revokeObjectURL(url);
}
