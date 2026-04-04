import React, { useEffect, useState } from 'react';
import { indieService } from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    indieService.getDashboard()
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load dashboard. Is the Independent Site backend running?'));
  }, []);

  if (error) return <div style={styles.error}>{error}</div>;
  if (!data) return <div style={styles.loading}>Loading dashboard...</div>;

  const { user } = data;

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Welcome, {user.name}</h1>
      <div style={styles.infoCard}>
        <div style={styles.infoRow}>
          <span style={styles.label}>Name</span>
          <span style={styles.value}>{user.name}</span>
        </div>
        <div style={styles.infoRow}>
          <span style={styles.label}>Roll No.</span>
          <span style={styles.value}>{user.roll_number}</span>
        </div>
      </div>
    </div>
  );
};

const styles = {
  page: { maxWidth: '800px', margin: '40px auto', padding: '0 24px' },
  heading: { color: '#1a1a2e', marginBottom: '4px' },
  infoCard: { background: '#fff', borderRadius: '10px', padding: '24px 28px', boxShadow: '0 2px 12px rgba(0,0,0,0.08)', marginTop: '24px' },
  infoRow: { display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f0f0f0' },
  label: { color: '#888', fontSize: '0.9rem' },
  value: { color: '#1a1a2e', fontWeight: '600' },
  loading: { textAlign: 'center', padding: '80px', color: '#888' },
  error: { textAlign: 'center', padding: '40px', color: '#c00', background: '#fee', margin: '40px', borderRadius: '8px' },
};

export default Dashboard;
