import React from 'react';
import { useNavigate } from 'react-router-dom';

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="app-container text-center">
      <h1 className="mt-5 mb-5">Кредитный скоринг</h1>
      
      <div className="main-buttons d-flex justify-content-center flex-column align-items-center">
        <button 
          className="btn btn-primary main-button" 
          onClick={() => navigate('/admin')}
        >
          Панель админа
        </button>
        
        <button 
          className="btn btn-secondary main-button" 
          onClick={() => navigate('/test-api')}
          >
            Протестировать API
          </button>
        </div>
      </div>
    );
}
  
export default HomePage;