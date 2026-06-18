const STAMP_CLASS = {
  Pending: 'stamp-pending',
  'In Progress': 'stamp-progress',
  Escalated: 'stamp-escalated',
  Resolved: 'stamp-resolved',
};

export function StatusStamp({ status, size }) {
  const cls = STAMP_CLASS[status] || 'stamp-pending';
  return <span className={`stamp ${cls} ${size === 'lg' ? 'stamp-lg' : ''}`}>{status}</span>;
}
