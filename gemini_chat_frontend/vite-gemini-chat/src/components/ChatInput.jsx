import React, { useState } from 'react';

function ChatInput({ onSend }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() === '') return;
    onSend(text);
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
    </form>
  );
}

export default ChatInput;