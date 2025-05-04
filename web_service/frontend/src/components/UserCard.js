import React from 'react';
import { useNavigate } from 'react-router-dom';

function UserCard({ user, onDelete }) {
  const navigate = useNavigate();

  return (
    <div className="card user-card">
      <div className="card-body d-flex justify-content-between align-items-center">
        <div>
          <h5 className="card-title">{user.username}</h5>
        </div>
        <div>
          <button 
            className="btn btn-info me-2" 
            onClick={() => navigate(`/user/${user.id}`)}
          >
            Подробнее
          </button>
          <button 
            className="btn btn-danger" 
            onClick={() => onDelete(user.id)}
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  );
}

export default UserCard;