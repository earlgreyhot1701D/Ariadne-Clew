import { getRecap } from './api_js.js';
import { setStatus } from './utils.js';
import {
  getElement,
  getValue,
  setElementContent,
  disableElement,
  enableElement,
  addClickListener,
  addSubmitListener,
} from './dom.js';
import { initThemeToggle } from './theme.js';
import { exportMarkdownFromRecap } from './exportMarkdown.js';
import { setupDragDrop } from './dragDrop.js';

let currentRecapData = null;

async function handleRecapRequest(chatLog) {
  const statusEl = getElement('status');
  const outputEl = getElement('recap-output');

  try {
    setStatus('Generating recap...');
    disableElement('recap-form');

    const data = await getRecap(chatLog);
    currentRecapData = data;

    // Display the recap
    const humanReadable = data.human_readable || 'No summary available';
    const rawJson = JSON.stringify(data.raw_json, null, 2);

    outputEl.innerHTML = `
      <h3>Summary</h3>
      <p>${humanReadable}</p>
      <h3>Raw Data</h3>
      <pre>${rawJson}</pre>
    `;

    setStatus('Recap generated successfully!');
    enableElement('copy-btn');
    enableElement('export-md');
  } catch (error) {
    setStatus(`Error: ${error.message}`, true);
    outputEl.innerHTML = '';
    currentRecapData = null;
  } finally {
    enableElement('recap-form');
  }
}

async function handleFileUpload(file) {
  try {
    const text = await file.text();
    const jsonData = JSON.parse(text);

    // Extract chat log from JSON - adjust this based on your JSON structure
    let chatLog = '';
    if (typeof jsonData === 'string') {
      chatLog = jsonData;
    } else if (jsonData.chat_log) {
      chatLog = jsonData.chat_log;
    } else if (jsonData.messages) {
      chatLog = jsonData.messages
        .map((msg) => `${msg.role}: ${msg.content}`)
        .join('\n');
    } else {
      chatLog = JSON.stringify(jsonData);
    }

    await handleRecapRequest(chatLog);
  } catch (error) {
    setStatus(`Error processing file: ${error.message}`, true);
  }
}

function copyRecapToClipboard() {
  const outputEl = getElement('recap-output');
  if (!outputEl.textContent.trim()) {
    setStatus('No recap to copy', true);
    return;
  }

  navigator.clipboard
    .writeText(outputEl.textContent)
    .then(() => setStatus('Recap copied to clipboard!'))
    .catch(() => setStatus('Failed to copy recap', true));
}

function exportRecap() {
  const outputEl = getElement('recap-output');
  if (!outputEl.innerHTML.trim()) {
    setStatus('No recap to export', true);
    return;
  }

  try {
    exportMarkdownFromRecap(outputEl);
    setStatus('Recap exported successfully!');
  } catch (error) {
    setStatus(`Export failed: ${error.message}`, true);
  }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  // Form submission
  addSubmitListener('recap-form', async (e) => {
    e.preventDefault();
    const sessionId = getValue('session-id');

    if (!sessionId.trim()) {
      setStatus('Please enter a session ID or upload a file', true);
      return;
    }

    // For now, use session ID as chat log - replace with actual session lookup
    await handleRecapRequest(`Session ID: ${sessionId}`);
  });

  // Copy button
  addClickListener('copy-btn', copyRecapToClipboard);

  // Export button
  addClickListener('export-md', exportRecap);

  // Theme toggle
  const themeToggle = getElement('theme-toggle');
  initThemeToggle(themeToggle);

  // Drag and drop setup
  const dropZone = getElement('drop-zone');
  const fileInput = getElement('file-upload');
  setupDragDrop(dropZone, fileInput, handleFileUpload);

  // Initialize UI state
  disableElement('copy-btn');
  disableElement('export-md');
  setStatus('Ready to generate recap');
});
