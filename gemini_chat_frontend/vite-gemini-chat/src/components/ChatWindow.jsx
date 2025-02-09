import React, { useEffect, useRef } from 'react';
import Message from './Message';

function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  // 新規メッセージ時に自動スクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <Message key={index} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;