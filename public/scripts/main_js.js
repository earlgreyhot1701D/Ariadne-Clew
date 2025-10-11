import { getRecap } from './api_js.js';

let currentRecapData = null;

// Simple status updater
function setStatus(message, isError = false) {
  const statusEl = document.getElementById('status');
  if (!statusEl) return;
  
  statusEl.textContent = message;
  statusEl.className = isError ? 'error' : 'loading';
  statusEl.style.display = 'block';
  
  if (!isError && message.includes('success')) {
    statusEl.className = 'success';
    setTimeout(() => {
      statusEl.style.display = 'none';
    }, 3000);
  }
}

// Populate split panels with results
function displayResults(data) {
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  const jsonPanel = document.querySelector('#jsonOutput .panel-content');
  
  if (!humanPanel || !jsonPanel) {
    console.error('Output panels not found');
    return;
  }
  
  // Clear empty states
  humanPanel.innerHTML = '';
  jsonPanel.innerHTML = '';
  
  // Format human-readable output
  const humanReadable = data.human_readable || 'Analysis complete';
  humanPanel.innerHTML = `<div style="line-height: 1.8;">${humanReadable}</div>`;
  
  // Format JSON output
  const jsonData = data.raw_json || data;
  jsonPanel.textContent = JSON.stringify(jsonData, null, 2);
  
  // Enable action buttons
  document.getElementById('copy-btn').disabled = false;
  document.getElementById('export-md').disabled = false;
}

// Clear output panels
function clearResults() {
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  const jsonPanel = document.querySelector('#jsonOutput .panel-content');
  
  if (humanPanel) {
    humanPanel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🧶</div>
        <p>Your reasoning extraction will appear here</p>
        <p style="font-size: 0.85rem;">Enter a chat transcript above to get started</p>
      </div>
    `;
  }
  
  if (jsonPanel) {
    jsonPanel.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">{ }</div>
        <p>Machine-readable output will appear here</p>
        <p style="font-size: 0.85rem;">Perfect for integrations and automation</p>
      </div>
    `;
  }
}

// Handle form submission
async function handleSubmit(e) {
  e.preventDefault();
  
  const sessionInput = document.getElementById('session-id');
  if (!sessionInput) return;
  
  const chatLog = sessionInput.value.trim();
  
  if (!chatLog) {
    setStatus('Please enter a chat transcript', true);
    return;
  }
  
  try {
    setStatus('🔄 Processing transcript...');
    
    // Disable form during processing
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.disabled = true;
    
    // Call API
    const data = await getRecap(chatLog);
    currentRecapData = data;
    
    // Display results
    displayResults(data);
    setStatus('✅ Extraction complete!');
    
  } catch (error) {
    console.error('Error:', error);
    clearResults();
    
    let errorMessage = '❌ ';
    if (error.message.includes('Failed to fetch')) {
      errorMessage += 'Connection failed. Is bridge_server.py running?';
    } else if (error.message.includes('HTTP 500')) {
      errorMessage += 'Server error. Check AgentCore connection.';
    } else {
      errorMessage += error.message;
    }
    
    setStatus(errorMessage, true);
    
  } finally {
    // Re-enable form
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.disabled = false;
  }
}

// Copy to clipboard
function handleCopy() {
  if (!currentRecapData) {
    setStatus('No output to copy', true);
    return;
  }
  
  const jsonPanel = document.querySelector('#jsonOutput .panel-content');
  if (!jsonPanel) return;
  
  navigator.clipboard.writeText(jsonPanel.textContent)
    .then(() => setStatus('📋 Copied to clipboard!'))
    .catch(() => setStatus('Failed to copy', true));
}

// Export as markdown
function handleExport() {
  if (!currentRecapData) {
    setStatus('No output to export', true);
    return;
  }
  
  const humanPanel = document.querySelector('#humanOutput .panel-content');
  if (!humanPanel) return;
  
  const markdown = `# Ariadne Clew Recap\n\n${humanPanel.textContent}\n\n## Raw Data\n\n\`\`\`json\n${JSON.stringify(currentRecapData, null, 2)}\n\`\`\``;
  
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'ariadne-recap.md';
  a.click();
  URL.revokeObjectURL(url);
  
  setStatus('💾 Exported successfully!');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  console.log('Ariadne Clew UI initialized');
  
  // Form submission
  const form = document.getElementById('recap-form');
  if (form) {
    form.addEventListener('submit', handleSubmit);
  }
  
  // Copy button
  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', handleCopy);
    copyBtn.disabled = true;
  }
  
  // Export button
  const exportBtn = document.getElementById('export-md');
  if (exportBtn) {
    exportBtn.addEventListener('click', handleExport);
    exportBtn.disabled = true;
  }
  
  // Drop zone (basic implementation)
  const dropZone = document.getElementById('drop-zone');
  if (dropZone) {
    dropZone.addEventListener('click', () => {
      setStatus('💡 Paste transcript in the field above', true);
    });
  }
  
  setStatus('Ready to extract reasoning');
});
