import React, { useState, useEffect } from 'react';
import { listAllUsers, deleteUser, getStatsForAll, createUser } from '../services/api.js';

import Header from '../components/Header.js';
import UserCard from '../components/UserCard.js';
import StatsTable from '../components/StatsTable.js';
import CreateUserForm from '../components/CreateUserForm.js';

function AdminPage() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({ totals: { queries_made: 0, queries_succeeded: 0, queries_failed: 0 } });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const usersData = await listAllUsers();
        const statsData = await getStatsForAll();
        setUsers(usersData);
        setStats(statsData);
      } catch (err) {
        setError('Failed to load data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await deleteUser(userId);
        setUsers(users.filter(user => user.id !== userId));
        const statsData = await getStatsForAll();
        setStats(statsData);
      } catch (err) {
        setError('Failed to delete user. Please try again.');
        console.error(err);
      }
    }
  };


  const handleCreateUser = async (userData) => {
    try {
      await createUser(userData);
      const usersData = await listAllUsers();
      const statsData = await getStatsForAll();
      setUsers(usersData);
      setStats(statsData);
      
      setShowCreateForm(false);
      setError(null);
    } catch (err) {
      setError('Failed to create user. The username might already exist.');
      console.error(err);
    }
  };

  if (loading) return <div className="app-container text-center mt-5"><div className="spinner-border" role="status"></div></div>;

  return (
    <div className="app-container">
      <div className="position-relative d-flex align-items-center mb-3">
        <div className="w-100">
          <Header title="Панель админа" backPath="/" />
        </div>
        <button 
          className="btn btn-primary" 
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          Создать пользователя
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {showCreateForm && (
        <CreateUserForm 
          onSubmit={handleCreateUser} 
          onCancel={() => setShowCreateForm(false)} 
        />
      )}

      <h2>Пользователи</h2>
      {users.length === 0 ? (
        <p className="text-muted">Нет пользователей. Создайте</p>
      ) : (
        <div className="user-list">
          {users.map(user => (
            <UserCard 
              key={user.id} 
              user={user} 
              onDelete={handleDeleteUser} 
            />
          ))}
        </div>
      )}

      <StatsTable stats={stats.totals} title="Общая статистика" />
    </div>
  );
}

export default AdminPage;