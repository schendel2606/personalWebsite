import { useState } from 'react';
import ChatSheet from './ChatSheet';

const WORKER_URL = import.meta.env.PUBLIC_CHAT_WORKER_URL ?? 'https://chat.niv.schendel.me/';

export default function ChatPill() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        className="chat-pill"
        onClick={() => setOpen(true)}
        aria-label="Open chat"
        style={{ display: open ? 'none' : 'block' }}
      >
        ▸ Skeptical? Talk to my AI
      </button>
      {open && <ChatSheet workerUrl={WORKER_URL} onClose={() => setOpen(false)} />}
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
      `}</style>
    </>
  );
}
