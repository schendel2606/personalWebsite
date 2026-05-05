import { useEffect, useRef, useState } from 'react';
import type { ChatMessage, ChatResponse, RateLimitResponse } from './chat-types';

const STORAGE_KEY = 'niv-chat-history';
const MAX_TURNS = 20;
const WORKER_URL = import.meta.env.PUBLIC_CHAT_WORKER_URL ?? 'https://chat.niv.schendel.me/';

const SUGGESTED_PROMPTS = [
  "What's his most interesting technical project?",
  'How does he handle messy legacy systems?',
  'What kind of role would actually fit him?',
];

export default function ChatPanel() {
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

  async function sendText(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;
    const userMsg: ChatMessage = { role: 'user', content: trimmed };
    const next = [...messages, userMsg].slice(-MAX_TURNS);
    setMessages(next);
    setInput('');
    setBusy(true);
    setError(null);

    try {
      const res = await fetch(WORKER_URL, {
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
        setError("That didn't work. Try again?");
        return;
      }
      const data = await res.json() as ChatResponse;
      setMessages([...next, { role: 'assistant', content: data.reply }]);
    } catch {
      setError('Network hiccup. Try again?');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat-panel" aria-label="Chat with Niv's AI">
      <header className="chat-head">
        <span className="chat-dot" aria-hidden="true" />
        <h2 className="chat-title">Talk to my AI</h2>
        <span className="chat-meta">Convince me to interview Niv.</span>
      </header>

      <div ref={scrollRef} className="chat-body">
        {rateLimited ? (
          <RateLimitedView data={rateLimited} />
        ) : messages.length === 0 ? (
          <EmptyState onPick={sendText} disabled={busy} />
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`} dir="auto" style={{ unicodeBidi: 'plaintext' }}>
              {m.content}
            </div>
          ))
        )}
        {busy && <div className="bubble assistant typing">. . .</div>}
      </div>

      {error && !rateLimited && <p className="chat-error">{error}</p>}

      <form
        className="chat-input"
        onSubmit={(e) => { e.preventDefault(); sendText(input); }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={rateLimited ? 'Quota reached' : 'Ask anything about Niv...'}
          disabled={busy || !!rateLimited}
          maxLength={500}
          aria-label="Message"
        />
        <button type="submit" disabled={busy || !input.trim() || !!rateLimited}>
          send
        </button>
      </form>

      <ChatStyles />
    </section>
  );
}

function EmptyState({ onPick, disabled }: { onPick: (t: string) => void; disabled: boolean }) {
  return (
    <div className="chat-empty">
      <p className="chat-empty-hint">
        I'm an AI agent built by Niv to argue for hiring him. I'll only answer
        questions related to that, and I'll be honest about what I don't know.
      </p>
      <p className="chat-empty-label">Try one of these:</p>
      <ul className="chat-suggestions">
        {SUGGESTED_PROMPTS.map((p) => (
          <li key={p}>
            <button type="button" onClick={() => onPick(p)} disabled={disabled}>
              {p}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RateLimitedView({ data }: { data: RateLimitResponse }) {
  const minutes = Math.ceil(data.retryAfterSeconds / 60);
  return (
    <div className="rate-limited">
      <h3 className="rate-limited-title">You've reached the hourly limit.</h3>
      <p>
        Which probably means we talked enough for now
        {minutes > 0 ? ` (resets in ${minutes} minute${minutes === 1 ? '' : 's'})` : ''}.
      </p>
      <p>
        If you still have questions, the better version of this conversation is
        with the actual Niv. You can reach him by email or LinkedIn.
      </p>
      <p className="rate-limited-meta">
        He'll be more flexible than the rate limiter. Probably also slightly
        more caffeinated.
      </p>
      <div className="rate-limited-cta">
        <a href={`mailto:${data.fallbackContacts.email}?subject=Following%20up%20from%20your%20site`}
           className="cta">Email →</a>
        <a href={data.fallbackContacts.linkedin} className="cta" target="_blank" rel="noopener">
          LinkedIn ↗
        </a>
      </div>
    </div>
  );
}

function ChatStyles() {
  return (
    <style>{`
      .chat-panel {
        display: flex;
        flex-direction: column;
        background: var(--bg-elev);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        overflow: hidden;
        height: 100%;
        min-height: 480px;
      }
      .chat-head {
        display: flex;
        align-items: baseline;
        gap: var(--space-sm);
        padding: var(--space-md) var(--space-lg);
        border-bottom: 1px solid var(--border);
      }
      .chat-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 12px var(--accent-glow);
        align-self: center;
      }
      .chat-title {
        font-family: var(--font-mono);
        font-size: 14px;
        font-weight: 600;
        margin: 0;
      }
      .chat-meta {
        color: var(--fg-muted);
        font-size: 12px;
        margin-left: auto;
      }
      .chat-body {
        flex: 1;
        overflow-y: auto;
        padding: var(--space-lg);
        display: flex;
        flex-direction: column;
        gap: var(--space-md);
      }
      .chat-empty {
        display: flex;
        flex-direction: column;
        gap: var(--space-md);
      }
      .chat-empty-hint {
        color: var(--fg);
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
      }
      .chat-empty-label {
        color: var(--fg-muted);
        font-family: var(--font-mono);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: var(--space-md) 0 0;
      }
      .chat-suggestions {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: var(--space-xs);
      }
      .chat-suggestions button {
        width: 100%;
        text-align: left;
        padding: 10px 14px;
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        color: var(--fg);
        font: inherit;
        font-size: 13px;
        cursor: pointer;
        transition: border-color 120ms, background 120ms;
      }
      .chat-suggestions button:hover:not(:disabled) {
        border-color: var(--accent);
        background: rgba(94,106,210,0.06);
      }
      .chat-suggestions button:disabled { opacity: 0.5; cursor: wait; }
      .bubble {
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 88%;
        font-size: 14px;
        line-height: 1.55;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
      .bubble.user {
        align-self: flex-end;
        background: var(--accent);
        color: white;
      }
      .bubble.assistant {
        align-self: flex-start;
        background: rgba(255,255,255,0.05);
        color: var(--fg);
      }
      .bubble.typing { opacity: 0.6; font-family: var(--font-mono); letter-spacing: 0.2em; }
      .chat-error {
        color: #ff8181;
        font-size: 13px;
        padding: var(--space-sm) var(--space-lg);
        margin: 0;
        border-top: 1px solid var(--border);
      }
      .chat-input {
        display: flex;
        gap: var(--space-sm);
        padding: var(--space-md) var(--space-lg);
        border-top: 1px solid var(--border);
        background: var(--bg);
      }
      .chat-input input {
        flex: 1;
        padding: 10px 12px;
        background: var(--bg-elev);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        color: var(--fg);
        font: inherit;
        font-size: 14px;
      }
      .chat-input input:focus { outline: none; border-color: var(--accent); }
      .chat-input button {
        padding: 10px 18px;
        background: var(--accent);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 120ms;
      }
      .chat-input button:disabled { opacity: 0.4; cursor: not-allowed; }
      .rate-limited { display: flex; flex-direction: column; gap: var(--space-md); font-size: 14px; line-height: 1.6; }
      .rate-limited-title { font-family: var(--font-mono); font-size: 15px; margin: 0; }
      .rate-limited p { margin: 0; }
      .rate-limited-meta { color: var(--fg-muted); }
      .rate-limited-cta { display: flex; gap: var(--space-sm); margin-top: var(--space-sm); }
      .cta {
        padding: 8px 14px;
        background: var(--accent);
        color: white;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 12px;
        text-decoration: none;
      }
      .cta:hover { opacity: 0.9; text-decoration: none; }
    `}</style>
  );
}
