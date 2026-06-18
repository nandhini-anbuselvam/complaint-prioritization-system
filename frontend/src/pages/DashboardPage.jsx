import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { complaints as complaintApi } from '../api/client';
import { AppShell } from '../components/AppShell';
import { PriorityPill, CategoryPill } from '../components/Pills';
import { StatusStamp } from '../components/StatusStamp';
import { useAuth } from '../context/AuthContext';
import { formatDateTime } from '../utils/format';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isStudent = user?.role === 'student';

  const [stats, setStats] = useState(null);
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [statsRes, listRes] = await Promise.all([
        complaintApi.stats(),
        complaintApi.list(),
      ]);
      setStats(statsRes.data);
      setList(listRes.data.results || listRes.data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  const title = isStudent ? 'My Complaints' : 'Case Queue';

  return (
    <AppShell title={title}>
      <div className="page-head">
        <div>
          <p>
            {isStudent
              ? 'Track every complaint you have filed, end to end.'
              : `Complaints currently sitting at your level for action.`}
          </p>
        </div>
        {isStudent && (
          <button className="btn btn-primary" onClick={() => navigate('/raise')}>
            + Raise a Complaint
          </button>
        )}
      </div>

      {stats && (
        <div className="stat-grid">
          <StatCard label="Total" value={stats.total} />
          <StatCard label="Pending" value={stats.pending} />
          <StatCard label="In Progress" value={stats.in_progress} />
          <StatCard label="Escalated" value={stats.escalated} accent="gold" />
          <StatCard label="Resolved" value={stats.resolved} accent="low" />
          <StatCard label="High Priority Open" value={stats.high_priority_open} accent="high" />
        </div>
      )}

      <div className="ledger">
        <div className="ledger-head">
          <span>Ticket</span>
          <span>Title</span>
          <span>Category</span>
          <span>Priority</span>
          <span>Status</span>
          <span>Filed</span>
          <span></span>
        </div>

        {loading && (
          <div className="ledger-empty"><div className="spinner" style={{ margin: '0 auto' }} /></div>
        )}

        {!loading && list.length === 0 && (
          <div className="ledger-empty">
            <h3>No complaints here yet</h3>
            <p>{isStudent ? 'File one and it will be classified instantly.' : 'Nothing is currently assigned to your level.'}</p>
          </div>
        )}

        {!loading && list.map((c) => (
          <div className="ledger-row" key={c.id} onClick={() => navigate(`/complaint/${c.id}`)}>
            <span className="ledger-ticket">{c.ticket_number}</span>
            <div>
              <div className="ledger-title">{c.title}</div>
              <div className="ledger-meta">
                {isStudent ? `Assigned to ${c.assigned_to_name || '—'}` : `Filed by ${c.created_by_name}`}
                {c.is_overdue && c.status !== 'Resolved' ? ' · overdue' : ''}
              </div>
            </div>
            <CategoryPill category={c.category} />
            <PriorityPill priority={c.priority} />
            <StatusStamp status={c.status} />
            <span className="ledger-meta">{formatDateTime(c.created_at)}</span>
            <span style={{ color: 'var(--muted)' }}>›</span>
          </div>
        ))}
      </div>
    </AppShell>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div className={`stat-card ${accent ? `accent-${accent}` : ''}`}>
      <div className="stat-value">{value ?? '—'}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
