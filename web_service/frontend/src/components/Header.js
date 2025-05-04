import React from 'react';
import { useNavigate } from 'react-router-dom';

function Header({ title, backPath = '/' }) {
  const navigate = useNavigate();

  return (
    <div className="page-header d-flex align-items-center mb-4 position-relative">
      <button 
        className="btn btn-secondary" 
        onClick={() => navigate(backPath)}
      >
        Назад
      </button>
      <h1 className="w-100 text-center">{title}</h1>
    </div>
  );
}

export default Header;