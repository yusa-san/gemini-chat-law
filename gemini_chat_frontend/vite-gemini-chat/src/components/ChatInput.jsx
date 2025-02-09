import React, { useState } from 'react';

function ChatInput({ onSend }) {
  const [text, setText] = useState('');

  // onSend をコンソール出力して確認する
  console.log('ChatInput received onSend:', onSend);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('ChatInput: onSubmit fired, text =', text); // デバッグ用ログを追加
    if (text.trim() === '') return;
    onSend(text); // App.jsx の handleSend を呼び出す
    setText('');
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="メッセージを入力"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      {/* エンターキー送信のため、送信ボタンは省略も可 */}
      <button type="submit">送信</button>
    </form>
  );
}

export default ChatInput;