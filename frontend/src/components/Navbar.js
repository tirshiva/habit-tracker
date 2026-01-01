import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/dashboard" className="navbar-brand">
          Habit Tracker
        </Link>
        <div className="navbar-links">
          <Link
            to="/dashboard"
            className={`navbar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link
            to="/habits"
            className={`navbar-link ${location.pathname === '/habits' ? 'active' : ''}`}
          >
            Habits
          </Link>
          <Link
            to="/analytics"
            className={`navbar-link ${location.pathname === '/analytics' ? 'active' : ''}`}
          >
            Analytics
          </Link>
          <span className="navbar-user">{user?.username}</span>
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

