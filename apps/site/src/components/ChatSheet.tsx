import { useEffect, useRef, useState } from 'react';
import type { ChatMessage, ChatResponse, RateLimitResponse } from './chat-types';

const STORAGE_KEY = 'niv-chat-history';
const MAX_TURNS = 20;

interface Props {
  workerUrl: string;
  onClose: () => void;
}

export default function ChatSheet({ workerUrl, onClose }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    if (typeof sessionStorage === 'undefined') return [];
    try { return JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? '[]'); }
    catch { return []; }
  });
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [rateLimited, setRateLimited] = useState<RateLimitResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_TURNS)));
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  async function send() {
    if (!input.trim() || busy) return;
    const userMsg: ChatMessage = { role: 'user', content: input.trim() };
    const next = [...messages, userMsg].slice(-MAX_TURNS);
    setMessages(next);
    setInput('');
    setBusy(true);
    setError(null);

    try {
      const res = await fetch(workerUrl, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next }),
      });
      if (res.status === 429) {
        setRateLimited(await res.json() as RateLimitResponse);
        return;
      }
      if (!res.ok) {
        setError('Something went wrong. Please try again.');
        return;
      }
      const data = await res.json() as ChatResponse;
      setMessages([...next, { role: 'assistant', content: data.reply }]);
    } catch {
      setError('Network error. Try again?');
    } finally {
      setBusy(false);
    }
  }

  if (rateLimited) {
    const minutes = Math.ceil(rateLimited.retryAfterSeconds / 60);
    return (
      <Sheet onClose={onClose}>
        <h3 style={{ fontFamily: 'var(--font-mono)', marginBottom: 16 }}>That was a good chat.</h3>
        <p style={{ marginBottom: 16, fontSize: 14 }}>
          We've talked enough for now (resets in {minutes} minute{minutes === 1 ? '' : 's'}).
          If you'd like to keep going, the conversation is better continued at one of these:
        </p>
        <div style={{ display: 'flex', gap: 12 }}>
          <a href={`mailto:${rateLimited.fallbackContacts.email}?subject=Following%20up%20from%20your%20site`}
             className="chat-cta">Email →</a>
          <a href={rateLimited.fallbackContacts.linkedin} className="chat-cta">LinkedIn →</a>
        </div>
      </Sheet>
    );
  }

  return (
    <Sheet onClose={onClose}>
      <div ref={scrollRef} className="chat-history">
        {messages.length === 0 && (
          <p className="chat-empty">
            Ask me anything about why Niv would be a fit for your role. I'll try to be useful.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`} dir="auto" style={{ unicodeBidi: 'plaintext' }}>
            {m.content}
          </div>
        ))}
        {busy && <div className="bubble assistant typing">…</div>}
      </div>
      {error && <p className="chat-error">{error}</p>}
      <form
        className="chat-input"
        onSubmit={(e) => { e.preventDefault(); send(); }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Convince me…"
          disabled={busy}
          maxLength={500}
        />
        <button type="submit" disabled={busy || !input.trim()}>send</button>
      </form>
      <ChatStyles />
    </Sheet>
  );
}

function Sheet({ children, onClose }: { children: React.ReactNode; onClose: () => void }) {
  return (
    <>
      <div className="chat-backdrop" onClick={onClose} />
      <div className="chat-sheet" role="dialog" aria-label="Chat with Niv's AI">
        <button className="chat-close" onClick={onClose} aria-label="Close">×</button>
        {children}
      </div>
    </>
  );
}

function ChatStyles() {
  return (
    <style>{`
      .chat-backdrop {
        position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 99;
      }
      .chat-sheet {
        position: fixed; bottom: 0; right: 0; left: auto;
        width: 420px; max-width: 100vw;
        height: 75vh; max-height: 600px;
        background: var(--bg-elev);
        border: 1px solid var(--border);
        border-radius: 12px 12px 0 0;
        padding: 24px;
        z-index: 100;
        display: flex; flex-direction: column;
      }
      @media (max-width: 540px) {
        .chat-sheet { width: 100%; height: 75vh; border-radius: 12px 12px 0 0; }
      }
      .chat-close {
        position: absolute; top: 12px; right: 12px;
        background: none; border: none; color: var(--fg-muted);
        font-size: 20px; cursor: pointer;
      }
      .chat-history {
        flex: 1; overflow-y: auto;
        display: flex; flex-direction: column; gap: 12px;
        margin-bottom: 16px;
      }
      .chat-empty { color: var(--fg-muted); font-size: 14px; }
      .bubble {
        padding: 8px 12px;
        border-radius: 12px;
        max-width: 80%;
        font-size: 14px;
        line-height: 1.5;
      }
      .bubble.user {
        align-self: flex-end;
        background: var(--accent);
        color: white;
      }
      .bubble.assistant {
        align-self: flex-start;
        background: rgba(255,255,255,0.06);
        color: var(--fg);
      }
      .bubble.typing { opacity: 0.6; }
      .chat-error { color: #ff6b6b; font-size: 13px; margin-bottom: 8px; }
      .chat-input { display: flex; gap: 8px; }
      .chat-input input {
        flex: 1;
        padding: 10px 12px;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--fg);
        font: inherit;
      }
      .chat-input input:focus { outline: none; border-color: var(--accent); }
      .chat-input button {
        padding: 10px 16px;
        background: var(--accent);
        color: white;
        border: none;
        border-radius: 6px;
        font-family: var(--font-mono);
        font-size: 12px;
        cursor: pointer;
      }
      .chat-input button:disabled { opacity: 0.5; cursor: not-allowed; }
      .chat-cta {
        padding: 8px 14px;
        background: var(--accent);
        color: white;
        border-radius: 6px;
        font-family: var(--font-mono);
        font-size: 12px;
        text-decoration: none;
      }
    `}</style>
  );
}
