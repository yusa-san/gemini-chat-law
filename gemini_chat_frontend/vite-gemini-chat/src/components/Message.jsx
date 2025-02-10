import React from 'react';

// タイムスタンプを「YYYY/MM/DD HH:mm」形式にフォーマットする関数
//function formatDate(timestamp) {
//  const date = new Date(timestamp);
//  const year = date.getFullYear();
//  const month = String(date.getMonth() + 1).padStart(2, '0');
//  const day = String(date.getDate()).padStart(2, '0');
//  const hours = String(date.getHours()).padStart(2, '0');
//  const minutes = String(date.getMinutes()).padStart(2, '0');
//  return `${year}/${month}/${day} ${hours}:${minutes}`;
//}

function Message({ message }) {
  // message.parts が存在する場合、各パートの text を取り出して結合する
  const text = Array.isArray(message.parts)
    ? message.parts.map(part => part.text).join(" ")
    : '';
  
  return (
    <div className="message">
      <p className="message-text">{text}</p>
      {/* ここでtimestampの代わりにroleを表示する */}
      <span className="message-role">Role: {message.role}</span>
    </div>
  );
}

export default Message;