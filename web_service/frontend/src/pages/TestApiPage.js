import React, { useState } from 'react';
import { getScore } from '../services/api.js';

import Header from '../components/Header.js';

function TestApiPage() {
  const [formData, setFormData] = useState({
    token: '',
    clientId: ''
  });
  
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.token || !formData.clientId) {
      setError('Token and Client ID are required.');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      
      const data = await getScore(formData.token, formData.clientId);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred while fetching the score.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header title="Протестировать API" showBackButton={true} backPath="/" />

      <div className="form-container">
        <div className="card">
          <div className="card-body">
            <h5 className="card-title">Запросить скор-балл</h5>
            
            {error && <div className="alert alert-danger">{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="token" className="form-label">API Токен</label>
                <input
                  type="text"
                  className="form-control"
                  id="token"
                  name="token"
                  value={formData.token}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="mb-3">
                <label htmlFor="clientId" className="form-label">ID клиента</label>
                <input
                  type="text"
                  className="form-control"
                  id="clientId"
                  name="clientId"
                  value={formData.clientId}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="d-flex justify-content-end">
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  disabled={loading}
                >
                  {loading ? (
                    <span>
                      <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                      <span className="ms-2">Загрузка...</span>
                    </span>
                  ) : 'Request'}
                </button>
              </div>
            </form>
            
            {result && (
              <div className="mt-4">
                <h6>Результат:</h6>
                <div className="alert alert-success">
                  <strong>ID клиента:</strong> {result.client_id}<br />
                  <strong>Скор-балл:</strong> {result.score}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TestApiPage;