import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getUser, getStatsForUser } from '../services/api.js';

import Header from '../components/Header.js';
import StatsTable from '../components/StatsTable.js';

function UserDetailsPage() {
  const { id } = useParams();
  
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showToken, setShowToken] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const userData = await getUser(id);
        const statsData = await getStatsForUser(id);
        setUser(userData);
        setStats(statsData);
      } catch (err) {
        setError('Failed to load user data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const copyToClipboard = (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text)
        .then(() => alert('Copied!'))
        .catch(() => alert('Copy failed'));
    } else {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        try {
          document.execCommand('copy');
          alert('Copied!');
        } catch (err) {
          alert('Copy failed');
        }
        document.body.removeChild(textarea);
    }
  }

  if (loading) return <div className="app-container text-center mt-5"><div className="spinner-border" role="status"></div></div>;
  if (error) return <div className="app-container"><div className="alert alert-danger">{error}</div></div>;
  if (!user) return <div className="app-container"><div className="alert alert-warning">User not found</div></div>;

  return (
    <div className="app-container">
      <Header title="Подробнее о пользователе" showBackButton={true} backPath="/admin" />

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Инфо о пользователе</h5>
          
          <div className="mb-3">
            <strong>Логин:</strong> {user.username}
          </div>
          
          
          <div className="mb-3">
            <strong>Токен:</strong> 
            <span className="ms-2">
              {showToken ? user.token : '••••••••••••'}
              <button 
                className="btn btn-sm btn-outline-secondary ms-2"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? 'Спрятать' : 'Показать'}
              </button>
              <button 
                className="btn btn-sm btn-outline-primary ms-2"
                onClick={() => copyToClipboard(user.token)}
              >
                Копировать
              </button>
            </span>
          </div>
        </div>
      </div>

      {stats && <StatsTable stats={stats} title="Статистика пользователя" />}
    </div>
  );
}

export default UserDetailsPage;