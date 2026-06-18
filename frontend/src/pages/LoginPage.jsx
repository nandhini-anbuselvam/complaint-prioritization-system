import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DEMO_ACCOUNTS = [
  ['student1', 'Student'],
  ['hod_cse', 'HOD · CSE'],
  ['dean1', 'Dean'],
  ['final1', 'Final Authority'],
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Incorrect username or password.');
    } finally {
      setLoading(false);
    }
  }

  function fillDemo(uname) {
    setUsername(uname);
    setPassword('password123');
  }

  return (
    <div className="login-screen">
      <div className="login-brand">
        <div className="login-brand-seal">CR</div>
        <h1>The Campus Registry of Complaints &amp; Resolutions.</h1>
        <p>
          Every complaint filed here is read, classified, and routed automatically —
          then tracked from the department office to the final authority until it's closed.
        </p>
        <div className="login-ledger-strip">
          <span>Step 01 — <b>Submit</b> a complaint in your own words</span>
          <span>Step 02 — NLP engine assigns <b>category &amp; priority</b></span>
          <span>Step 03 — Routed to <b>HOD → Dean → Final Authority</b> on a deadline</span>
        </div>
      </div>

      <div className="login-form-wrap">
        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Sign in to your file</h2>
          <p>Use your institution credentials to continue.</p>

          {error && <div className="form-error">{error}</div>}

          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username" value={username} onChange={(e) => setUsername(e.target.value)}
              autoComplete="username" required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password" type="password" value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password" required
            />
          </div>

          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          <div className="demo-box">
            <h4>Demo accounts (password: password123)</h4>
            <div className="demo-grid">
              {DEMO_ACCOUNTS.map(([uname, label]) => (
                <button type="button" key={uname} onClick={() => fillDemo(uname)}>
                  {uname} <span style={{ color: 'var(--muted)' }}>· {label}</span>
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
