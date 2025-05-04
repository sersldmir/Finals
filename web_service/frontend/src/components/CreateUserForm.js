import React, { useState } from 'react';

function CreateUserForm({ onSubmit, onCancel }) {
  const [userData, setUserData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!userData.username || !userData.password) {
      setError('Username and password are required.');
      return;
    }
    
    onSubmit(userData);
  };

  return (
    <div className="card mb-4">
      <div className="card-body">
        <h5 className="card-title">Создать нового пользователя</h5>
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="username" className="form-label">Логин</label>
            <input
              type="text"
              className="form-control"
              id="username"
              name="username"
              value={userData.username}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">Пароль</label>
            <input
              type="password"
              className="form-control"
              id="password"
              name="password"
              value={userData.password}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="d-flex justify-content-end">
            {onCancel && (
              <button 
                type="button" 
                className="btn btn-secondary me-2" 
                onClick={onCancel}
              >
                Отменить
              </button>
            )}
            <button type="submit" className="btn btn-success">Создать пользователя</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateUserForm;