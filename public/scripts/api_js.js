const API_BASE_URL = 'http://localhost:5001';

export async function getRecap(chatLog) {
  const response = await fetch(`${API_BASE_URL}/recap`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      chat_log: chatLog
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}