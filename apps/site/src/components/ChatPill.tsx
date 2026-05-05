import { useState } from 'react';

export default function ChatPill() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        className="chat-pill"
        onClick={() => setOpen((o) => !o)}
        aria-label="Open chat"
      >
        ▸ Skeptical? Talk to my AI
      </button>
      {open && (
        <div className="chat-stub" role="dialog">
          Chat coming online soon.
          <button onClick={() => setOpen(false)} aria-label="Close">×</button>
        </div>
      )}
      <style>{`
        .chat-pill {
          position: fixed;
          bottom: 24px;
          right: 24px;
          padding: 10px 16px;
          background: var(--accent);
          color: white;
          font-family: var(--font-mono);
          font-size: 12px;
          font-weight: 500;
          border: none;
          border-radius: var(--radius-pill);
          cursor: pointer;
          box-shadow: 0 0 32px var(--accent-glow);
          z-index: 100;
        }
        .chat-stub {
          position: fixed;
          bottom: 80px;
          right: 24px;
          background: var(--bg-elev);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          padding: var(--space-md);
          color: var(--fg);
          z-index: 100;
        }
        .chat-stub button {
          margin-left: var(--space-md);
          background: none;
          border: none;
          color: var(--fg-muted);
          cursor: pointer;
        }
      `}</style>
    </>
  );
}
