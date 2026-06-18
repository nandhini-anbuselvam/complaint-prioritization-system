import { useEffect, useRef, useState } from 'react';
import { notifications as notifApi } from '../api/client';
import { timeAgo } from '../utils/format';

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const ref = useRef(null);

  async function load() {
    try {
      const { data } = await notifApi.list();
      setItems(data.results || data);
      setUnread((data.results || data).filter((n) => !n.is_read).length);
    } catch {
      /* ignore */
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 20000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  async function markAll() {
    await notifApi.markAllRead();
    load();
  }

  return (
    <div className="notif-wrap" ref={ref}>
      <button className="notif-bell" onClick={() => setOpen((o) => !o)} aria-label="Notifications">
        🔔
        {unread > 0 && <span className="notif-dot" />}
      </button>
      {open && (
        <div className="notif-panel">
          <div className="notif-panel-head">
            <h4>Notifications</h4>
            {unread > 0 && <button onClick={markAll}>Mark all read</button>}
          </div>
          {items.length === 0 && <div className="notif-empty">Nothing here yet.</div>}
          {items.map((n) => (
            <div key={n.id} className={`notif-item ${n.is_read ? '' : 'unread'}`}>
              <div>{n.message}</div>
              <div className="notif-time">{timeAgo(n.created_at)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
