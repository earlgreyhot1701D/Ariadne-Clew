// scripts/api_js.js
const API_BASE_URL = 'http://localhost:5000';

export async function getRecap(chatLog, sessionId = 'default') {
  const response = await fetch(`${API_BASE_URL}/v1/recap`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      chat_log: chatLog,
      session_id: sessionId,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}

