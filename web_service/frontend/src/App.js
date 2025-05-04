import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import HomePage from './pages/HomePage';
import AdminPage from './pages/AdminPage';
import UserDetailsPage from './pages/UserDetailsPage';
import TestApiPage from './pages/TestApiPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/user/:id" element={<UserDetailsPage />} />
          <Route path="/test-api" element={<TestApiPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;