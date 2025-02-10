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
        .then(data => {
          console.log('Fetched history:', data);  // ここで取得データを確認
          setMessages(data);
        })
        .catch(err => setError(err.message));
    };

    loadHistory();

    // 5秒ごとに自動更新（ポーリング）
    const intervalId = setInterval(loadHistory, 5000);
    return () => clearInterval(intervalId);
  }, []);

  // 新規メッセージ送信時のハンドラ
  const handleSend = (text) => {
    console.log('App: Sending message:', text); // 送信テキストを確認
    const payload = { question: text }; // キーをquestionに変更
    sendMessage(payload)
      .then(response => {
        console.log('App: Message sent, response:', response); // 送信後のレスポンスを確認
        // 送信成功後、即時メッセージを追加（または履歴の再取得でも可）
      // 送信後、履歴の再取得を実施
      fetchHistory()
        .then(data => setMessages(data))
        .catch(err => setError(err.message));
      })
      .catch(err => setError(err.message));
  };

  // チャット履歴をクリアするハンドラ
  const handleClearChat = () => {
    // ここではフロントエンド側の state をクリアする
    setMessages([]);
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
      {/* onSend プロパティとして handleSend を渡す */}
      <ChatInput onSend={handleSend} />
      {error && <ErrorModal message={error} onClose={handleCloseError} />}
    </div>
  );
}

export default App;