const API_BASE = 'https://gemini-chat-law-backend-233096540107.asia-northeast1.run.app'; // Cloud Run のURLに置き換えてください

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/history`, {
    cache: 'no-cache' // , credentials: 'include' // クロスオリジンでクッキーを含め送信する場合
  });
  if (!response.ok) {
    throw new Error('チャット履歴の取得に失敗しました');
  }
  const data = await response.json();
  return data.history;  // historyキーの中の配列を返す
}

export async function sendMessage(payload) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    // credentials: 'include', // POSTリクエストでもクッキーを含める場合
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('メッセージ送信に失敗しました');
  }
  return response.json();
}