import React from 'react';
import './CheckButton.css';

function CheckButton({ onSearch }) {
  return (
    <button className="check-button" onClick={onSearch}>
      Controleer
    </button>
  );
}

export default CheckButton;