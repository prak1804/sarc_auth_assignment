import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { indieService } from '../services/api';

const Register = () => {
  const [form, setForm] = useState({
    username: '', name: '', roll_number: '', hostel_number: '',
    password: '', confirmPassword: '', department: '', year_of_study: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        username: form.username,
        name: form.name,
        roll_number: form.roll_number,
        hostel_number: form.hostel_number,
        password: form.password,
        department: form.department,
        year_of_study: form.year_of_study ? parseInt(form.year_of_study) : null,
      };
      // Registration via independent site → forwarded to centralized auth service
      await indieService.register(payload);
      setSuccess('Registration successful! Redirecting to login...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`);
        setError(msgs.join(' | '));
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Create Account</h2>
        <p style={styles.subtitle}>Registration is forwarded securely to Centralized Auth</p>
        {error && <div style={styles.error}>{error}</div>}
        {success && <div style={styles.success}>{success}</div>}
        <form onSubmit={handleSubmit}>
          {[
            { name: 'username', label: 'Username', placeholder: 'e.g. john_doe' },
            { name: 'name', label: 'Full Name', placeholder: 'e.g. John Doe' },
            { name: 'roll_number', label: 'Roll Number', placeholder: 'e.g. 23CS001' },
            { name: 'hostel_number', label: 'Hostel Number', placeholder: 'e.g. H7' },
            { name: 'department', label: 'Department (optional)', placeholder: 'e.g. Computer Science' },
            { name: 'year_of_study', label: 'Year of Study (optional)', placeholder: '1-5', type: 'number' },
          ].map(({ name, label, placeholder, type }) => (
            <div style={styles.field} key={name}>
              <label style={styles.label}>{label}</label>
              <input
                name={name} value={form[name]} onChange={handleChange}
                style={styles.input} placeholder={placeholder} type={type || 'text'}
                required={!label.includes('optional')}
              />
            </div>
          ))}
          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              name="password" type="password" value={form.password} onChange={handleChange}
              style={styles.input} placeholder="Min 8 characters" required minLength={8}
            />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Confirm Password</label>
            <input
              name="confirmPassword" type="password" value={form.confirmPassword} onChange={handleChange}
              style={styles.input} placeholder="Re-enter password" required
            />
          </div>
          <button type="submit" style={styles.btn} disabled={loading}>
            {loading ? 'Registering...' : 'Create Account'}
          </button>
        </form>
        <p style={styles.footer}>
          Already have an account? <Link to="/login" style={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: { minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f2f5', padding: '24px 0' },
  card: { background: '#fff', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', width: '100%', maxWidth: '480px' },
  title: { textAlign: 'center', color: '#1a1a2e', marginBottom: '4px' },
  subtitle: { textAlign: 'center', color: '#888', fontSize: '0.82rem', marginBottom: '24px' },
  error: { background: '#fee', color: '#c00', padding: '10px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.88rem' },
  success: { background: '#e6f9f0', color: '#0a7a3c', padding: '10px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.88rem' },
  field: { marginBottom: '14px' },
  label: { display: 'block', marginBottom: '5px', fontWeight: '500', color: '#333', fontSize: '0.88rem' },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: '6px', fontSize: '0.95rem', boxSizing: 'border-box' },
  btn: { width: '100%', padding: '12px', background: '#e94560', color: '#fff', border: 'none', borderRadius: '6px', fontSize: '1rem', fontWeight: '600', cursor: 'pointer', marginTop: '8px' },
  footer: { textAlign: 'center', marginTop: '20px', color: '#666', fontSize: '0.9rem' },
  link: { color: '#e94560' },
};

export default Register;
