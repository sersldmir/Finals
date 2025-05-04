import React from 'react';

function StatsTable({ stats, title = "Statistics" }) {
  const calculatePercentage = (part, total) => {
    if (total === 0) return '0%';
    return ((part / total) * 100).toFixed(1) + '%';
  };

  return (
    <div className="stats-container mt-4">
      <h2>{title}</h2>
      <table className="table table-striped">
        <thead>
          <tr>
            <th>Метрика</th>
            <th>Значение</th>
            <th>Доля (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Общее количество запросов</td>
            <td>{stats.queries_made}</td>
            <td>100%</td>
          </tr>
          <tr>
            <td>Успешные запросы</td>
            <td>{stats.queries_succeeded}</td>
            <td>{calculatePercentage(stats.queries_succeeded, stats.queries_made)}</td>
          </tr>
          <tr>
            <td>Ошибочные запросы</td>
            <td>{stats.queries_failed}</td>
            <td>{calculatePercentage(stats.queries_failed, stats.queries_made)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default StatsTable;