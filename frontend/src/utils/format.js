export const LEVEL_LABELS = {
  hod: 'Department Authority (HOD)',
  dean: 'Dean',
  final_authority: 'Final Authority',
  student: 'Student',
};

export const ROLE_NEXT_ACTION = {
  hod: 'Escalate to Dean',
  dean: 'Escalate to Final Authority',
  final_authority: null,
};

export function formatDateTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function timeAgo(iso) {
  if (!iso) return '';
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}
