export function PriorityPill({ priority }) {
  const cls = { High: 'pill-high', Medium: 'pill-medium', Low: 'pill-low' }[priority] || 'pill-medium';
  return <span className={`pill ${cls}`}>{priority}</span>;
}

export function CategoryPill({ category }) {
  return <span className="pill pill-category">{category}</span>;
}
