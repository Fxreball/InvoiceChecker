import React from 'react';
import './CheckButton.css';

function CheckButton({ onSearch }) {
  return (
    <button className="check-button" onClick={onSearch}>
      Controleren
    </button>
  );
}

export default CheckButton;