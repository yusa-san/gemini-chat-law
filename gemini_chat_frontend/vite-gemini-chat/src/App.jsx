import React, { useEffect, useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import ErrorModal from './components/ErrorModal';
import { fetchHistory, sendMessage } from './services/api';
import './styles/app.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  // 初回ロード時にチャット履歴を取得
  useEffect(() => {
    const loadHistory = () => {
      fetchHistory()
        .then(data => setMessages(data))
        .catch(err => setError(err.message));
    };

    loadHistory();

    // 5秒ごとに自動更新（ポーリング）
    const intervalId = setInterval(loadHistory, 5000);
    return () => clearInterval(intervalId);
  }, []);

  // 新規メッセージ送信時のハンドラ
  const handleSend = (text) => {
    const payload = { question: text }; // キーをquestionに変更
    sendMessage(payload)
      .then(response => {
        // 送信成功後、即時メッセージを追加（または履歴の再取得でも可）
        setMessages(prev => [...prev, response]);
      })
      .catch(err => setError(err.message));
  };

  // エラーモーダルの閉じるときの処理を修正：前のページに戻るのではなく、単にエラーをクリアする
  const handleCloseError = () => {
    setError(null);
    // もしリロードを行いたい場合は、下記を使用することもできます
    // window.location.reload();
  };

  return (
    <div className="app-container">
      <ChatWindow messages={messages} />
      <ChatInput onSend={handleSend} />
      {error && <ErrorModal message={error} onClose={handleCloseError} />}
    </div>
  );
}

export default App;