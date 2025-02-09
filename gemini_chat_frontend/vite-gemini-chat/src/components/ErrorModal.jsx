import React from 'react';

function ErrorModal({ message, onClose }) {
  return (
    <div className="error-modal-overlay">
      <div className="error-modal">
        <h2>エラーが発生しました</h2>
        <p>{message}</p>
        <button onClick={onClose}>閉じる</button>
      </div>
    </div>
  );
}

export default ErrorModal;