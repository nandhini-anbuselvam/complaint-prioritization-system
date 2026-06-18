import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { complaints as complaintApi } from '../api/client';
import { AppShell } from '../components/AppShell';
import { PriorityPill, CategoryPill } from '../components/Pills';
import { StatusStamp } from '../components/StatusStamp';
import { useAuth } from '../context/AuthContext';
import { LEVEL_LABELS, ROLE_NEXT_ACTION, formatDateTime, timeAgo } from '../utils/format';

export default function ComplaintDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const [notes, setNotes] = useState('');
  const [banner, setBanner] = useState('');

  async function load() {
    setLoading(true);
    const { data } = await complaintApi.detail(id);
    setComplaint(data);
    setLoading(false);
  }

  useEffect(() => { load(); }, [id]);

  const canAct = user && complaint && user.role !== 'student' && user.role === complaint.current_level
    && complaint.status !== 'Resolved';

  async function runAction(fn, label) {
    setActionLoading(label);
    setBanner('');
    try {
      const { data } = await fn();
      setComplaint(data);
      setBanner(`${label} successful.`);
      setNotes('');
    } catch (err) {
      setBanner(err.response?.data?.detail || `Could not ${label.toLowerCase()}.`);
    } finally {
      setActionLoading('');
    }
  }

  if (loading || !complaint) {
    return (
      <AppShell title="Complaint">
        <div className="center-page"><div className="spinner" /></div>
      </AppShell>
    );
  }

  const nextLevelAction = ROLE_NEXT_ACTION[user.role];

  return (
    <AppShell title={complaint.ticket_number}>
      <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)} style={{ marginBottom: 16 }}>
        ← Back
      </button>

      <div className="detail-header">
        <div>
          <h2 style={{ fontSize: 24 }}>{complaint.title}</h2>
          <div className="detail-pills">
            <CategoryPill category={complaint.category} />
            <PriorityPill priority={complaint.priority} />
            <StatusStamp status={complaint.status} size="lg" />
          </div>
        </div>
      </div>

      {banner && <div className="form-success">{banner}</div>}

      <div className="detail-grid">
        <div className="card card-pad">
          <div className="section-label">Description</div>
          <p style={{ fontSize: 14.5, lineHeight: 1.7, marginBottom: 24 }}>{complaint.description}</p>

          <div className="section-label">Case History</div>
          <div className="timeline">
            {complaint.history.map((h) => (
              <div className="timeline-item" key={h.id}>
                <div className="timeline-dot" />
                <div className="timeline-action">{h.action}</div>
                <div className="timeline-meta">
                  {h.performed_by_name ? `by ${h.performed_by_name} · ` : ''}{formatDateTime(h.timestamp)}
                </div>
                {h.notes && <div className="timeline-notes">{h.notes}</div>}
              </div>
            ))}
          </div>

          {canAct && (
            <div className="action-row" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
              <div className="field" style={{ marginBottom: 12 }}>
                <label htmlFor="notes">Notes (optional)</label>
                <textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add context for the student or the next authority…" />
              </div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {(complaint.status === 'Pending' || complaint.status === 'Escalated') && (
                  <button className="btn btn-primary" disabled={!!actionLoading}
                    onClick={() => runAction(() => complaintApi.updateStatus(id, 'In Progress', notes), 'Mark In Progress')}>
                    {actionLoading === 'Mark In Progress' ? 'Updating…' : 'Mark In Progress'}
                  </button>
                )}
                <button className="btn btn-success" disabled={!!actionLoading}
                  onClick={() => runAction(() => complaintApi.resolve(id, notes), 'Resolve')}>
                  {actionLoading === 'Resolve' ? 'Resolving…' : 'Mark Resolved'}
                </button>
                {nextLevelAction && (
                  <button className="btn btn-gold" disabled={!!actionLoading}
                    onClick={() => runAction(() => complaintApi.escalate(id, notes || 'Manually escalated'), 'Escalate')}>
                    {actionLoading === 'Escalate' ? 'Escalating…' : nextLevelAction}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="card card-pad">
          <div className="section-label">Case Details</div>
          <dl className="kv-list">
            <div className="kv-row"><dt>Ticket</dt><dd className="mono">{complaint.ticket_number}</dd></div>
            <div className="kv-row"><dt>Filed by</dt><dd>{complaint.created_by_detail?.first_name} {complaint.created_by_detail?.last_name}</dd></div>
            <div className="kv-row"><dt>Current level</dt><dd>{LEVEL_LABELS[complaint.current_level]}</dd></div>
            <div className="kv-row"><dt>Assigned to</dt><dd>{complaint.assigned_to_detail ? `${complaint.assigned_to_detail.first_name} ${complaint.assigned_to_detail.last_name}` : '—'}</dd></div>
            <div className="kv-row"><dt>Filed on</dt><dd>{formatDateTime(complaint.created_at)}</dd></div>
            <div className="kv-row"><dt>SLA deadline</dt><dd style={{ color: complaint.is_overdue ? 'var(--high)' : undefined }}>
              {formatDateTime(complaint.escalation_deadline)}
            </dd></div>
            <div className="kv-row"><dt>Classification confidence</dt><dd>{(complaint.classification_confidence * 100).toFixed(0)}%</dd></div>
            {complaint.resolved_at && (
              <div className="kv-row"><dt>Resolved on</dt><dd>{formatDateTime(complaint.resolved_at)}</dd></div>
            )}
          </dl>

          {complaint.is_overdue && complaint.status !== 'Resolved' && (
            <div className="form-error" style={{ marginTop: 16 }}>
              Past its SLA deadline ({timeAgo(complaint.escalation_deadline)}) — eligible for escalation.
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
