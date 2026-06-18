import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { complaints as complaintApi } from '../api/client';
import { AppShell } from '../components/AppShell';
import { PriorityPill, CategoryPill } from '../components/Pills';

export default function RaiseComplaintPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [department, setDepartment] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const { data } = await complaintApi.create({ title, description, department });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit the complaint. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell title="Raise a Complaint">
      <div className="page-head">
        <p>Describe the issue in your own words — category and priority are assigned automatically.</p>
      </div>

      <div className="detail-grid">
        <div className="card card-pad">
          {!result ? (
            <form onSubmit={handleSubmit}>
              {error && <div className="form-error">{error}</div>}
              <div className="field">
                <label htmlFor="title">Title</label>
                <input
                  id="title" value={title} onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Restroom not cleaned in Block A" required maxLength={200}
                />
              </div>
              <div className="field">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description" value={description} onChange={(e) => setDescription(e.target.value)}
                  placeholder="Give as much detail as you can — what happened, where, and when."
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="department">Department (optional)</label>
                <input
                  id="department" value={department} onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. CSE — leave blank if not sure"
                />
                <div className="field-hint">If known, this routes your complaint to the right HOD directly.</div>
              </div>
              <button className="btn btn-primary" type="submit" disabled={submitting}>
                {submitting ? 'Classifying…' : 'Submit Complaint'}
              </button>
            </form>
          ) : (
            <div>
              <div className="form-success">Complaint filed and routed to {result.assigned_to_name || 'the HOD'}.</div>
              <div className="section-label">Predicted classification</div>
              <div className="detail-pills" style={{ marginBottom: 18 }}>
                <CategoryPill category={result.category} />
                <PriorityPill priority={result.priority} />
              </div>
              <div className="confidence-bar">
                <div className="confidence-bar-fill" style={{ width: `${result.classification_confidence * 100}%` }} />
              </div>
              <div className="field-hint">Model confidence: {(result.classification_confidence * 100).toFixed(0)}%</div>

              <div className="action-row">
                <button className="btn btn-primary" onClick={() => navigate(`/complaint/${result.id}`)}>
                  View Complaint
                </button>
                <button className="btn btn-ghost" onClick={() => { setResult(null); setTitle(''); setDescription(''); setDepartment(''); }}>
                  File Another
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="card card-pad">
          <div className="section-label">How classification works</div>
          <p style={{ fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.7 }}>
            Your description is passed through a TF-IDF vectorizer and a logistic regression
            model trained on past complaints to predict both the <strong>category</strong>
            (e.g. Infrastructure, Safety, Academic) and the <strong>priority</strong>
            (High, Medium, Low). Complaints mentioning safety-critical terms — fire, threats,
            harassment — are always routed as High priority regardless of model confidence.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
