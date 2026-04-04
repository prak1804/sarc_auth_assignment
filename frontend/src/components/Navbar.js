import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.brand}>
        <Link to="/" style={styles.brandLink}>SARC Portal</Link>
      </div>
      <div style={styles.links}>
        {isAuthenticated ? (
          <>
            <Link to="/dashboard" style={styles.link}>Dashboard</Link>
            <span style={styles.userInfo}>
              👤 {user?.name} ({user?.roll_number})
            </span>
            <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" style={styles.link}>Login</Link>
            <Link to="/register" style={styles.link}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '12px 24px', background: '#1a1a2e', color: '#fff',
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
  },
  brand: { fontWeight: 'bold', fontSize: '1.3rem' },
  brandLink: { color: '#e94560', textDecoration: 'none' },
  links: { display: 'flex', alignItems: 'center', gap: '16px' },
  link: { color: '#ccc', textDecoration: 'none', fontSize: '0.95rem' },
  userInfo: { color: '#a0a0b0', fontSize: '0.85rem' },
  logoutBtn: {
    background: '#e94560', color: '#fff', border: 'none',
    padding: '6px 14px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.9rem',
  },
};

export default Navbar;
