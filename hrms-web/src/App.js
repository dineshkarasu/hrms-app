import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Employees from './components/Employees';
import Departments from './components/Departments';
import Leaves from './components/Leaves';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('employees');
  const environment = process.env.REACT_APP_ENVIRONMENT || 'dev';
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost';

  useEffect(() => {
    console.log(`🌐 HRMS Web running in ${environment.toUpperCase()} environment`);
    console.log(`📡 API Base URL: ${apiUrl}`);
    console.log(`🔧 Environment: ${environment}`);
  }, [environment, apiUrl]);

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <div className="nav-brand">
              <h2>🏢 HRMS</h2>
              <span className="nav-subtitle">Human Resource Management System</span>
            </div>
            <div className="nav-links">
              <Link 
                to="/employees" 
                className={`nav-link ${activeTab === 'employees' ? 'active' : ''}`}
                onClick={() => setActiveTab('employees')}
              >
                👥 Employees
              </Link>
              <Link 
                to="/departments" 
                className={`nav-link ${activeTab === 'departments' ? 'active' : ''}`}
                onClick={() => setActiveTab('departments')}
              >
                🏛️ Departments
              </Link>
              <Link 
                to="/leaves" 
                className={`nav-link ${activeTab === 'leaves' ? 'active' : ''}`}
                onClick={() => setActiveTab('leaves')}
              >
                📅 Leave Requests
              </Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/employees" replace />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/leaves" element={<Leaves />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="container">
            <p>© 2024 HRMS - Human Resource Management System</p>
            <p style={{ fontSize: '12px', color: '#64748b' }}>
              Environment: <strong style={{ 
                color: environment === 'prod' ? '#ef4444' : 
                       environment === 'staging' ? '#f59e0b' : 
                       environment === 'test' ? '#3b82f6' : '#10b981',
                textTransform: 'uppercase'
              }}>{environment}</strong> | API: {apiUrl}
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
