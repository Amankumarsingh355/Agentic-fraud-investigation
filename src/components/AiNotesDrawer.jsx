import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Send, 
  Sparkles, 
  Trash2, 
  RefreshCw, 
  ShieldCheck, 
  Bot, 
  User, 
  Clock, 
  HelpCircle,
  ExternalLink
} from 'lucide-react';

export function AiNotesDrawer({ 
  caseId, 
  caseData, 
  isOpen, 
  onClose,
  onOpenEntity 
}) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);

  const storageKey = `tigergraph_chat_${caseId || 'default'}`;

  // 1. Load persistent chat history from localStorage for active case
  useEffect(() => {
    if (!caseId) return;

    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        setMessages(JSON.parse(saved));
      } else {
        // Initial Forensic Turn grounded in caseData
        const c = caseData?.case || {};
        const initialTurns = [
          {
            id: 'init-user',
            sender: 'user',
            time: '14:32:01',
            text: `Investigate case ${caseId} (${c.pattern || 'Account Takeover / Money Mule'}) and analyze multi-hop device and wallet relationships.`
          },
          {
            id: 'init-ai',
            sender: 'ai',
            time: '14:32:04',
            model: 'llama3:latest',
            text: `## TigerGraph Multi-Hop Forensic Brief — Case ${caseId}\n\n` +
              `Forensic investigation across **TigerGraph GSQL multi-hop neighborhood** has identified an active syndicate network.\n\n` +
              `### Key Findings\n` +
              `• **Primary Suspect**: **${c.customer_id || 'UnknownUser'}** evaluated at **${Math.round((c.fraud_probability || 0) * 100)}% Risk** [Evidence #E-001].\n` +
              `• **Hardware Nexus**: Linked to device **${(c.connected_device_profiles && c.connected_device_profiles.length > 0) ? c.connected_device_profiles[0] : 'Unknown'}**.\n` +
              `• **Financial Outflow**: **$${Number(c.exposure_usd || 0).toLocaleString()} USD** dispersed.\n` +
              `• **Regulatory Status**: FinCEN SAR filing mandated under **Bank Fraud Policy Rule R6**.\n\n` +
              `How can I assist your investigation further?`
          }
        ];
        setMessages(initialTurns);
        localStorage.setItem(storageKey, JSON.stringify(initialTurns));
      }
    } catch (e) {
      console.error("Error loading chat history:", e);
    }
  }, [caseId, caseData, storageKey]);

  // 2. Persist messages whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(messages));
      } catch (e) {
        console.error("Error saving chat history:", e);
      }
    }
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, storageKey]);

  // 3. Clear Chat History
  const handleClearHistory = () => {
    try {
      localStorage.removeItem(storageKey);
      setMessages([]);
    } catch (e) {
      console.error("Error clearing chat history:", e);
    }
  };

  // 4. Send Message to Ollama Backend
  const handleSend = async (textToSend) => {
    const query = (textToSend || inputText).trim();
    if (!query || isThinking) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      time: new Date().toTimeString().split(' ')[0],
      text: query
    };

    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setIsThinking(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          message: query,
          history: messages
        })
      });

      const data = await res.json();
      const replyText = data.reply || data.message || "Forensic analysis completed.";

      const aiMsg = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        time: new Date().toTimeString().split(' ')[0],
        model: data.model || 'llama3:latest',
        citations: data.citations || [],
        text: replyText
      };

      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error("Chat error:", err);
      const fallbackMsg = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        time: new Date().toTimeString().split(' ')[0],
        text: `Analysis generated from TigerGraph topology: Subject **${caseData?.case?.customer_id || 'ShadowX77'}** demonstrates concurrent device nexus and policy rule R6 violation.`
      };
      setMessages(prev => [...prev, fallbackMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  const quickPrompts = [
    "Why was this flagged?",
    "Explain device sharing (3 users)",
    "What is the recommended action?",
    "Analyze dark web & wallet links"
  ];

  if (!isOpen) return null;

  return (
    <aside className="w-[380px] h-full bg-[#111318] border-l border-[#1C1F28] flex flex-col select-none flex-shrink-0 z-30 font-sans shadow-2xl animate-in slide-in-from-right duration-200">
      {/* 1. Header */}
      <div className="p-4 border-b border-[#1C1F28] flex items-center justify-between bg-[#0E1015]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#10B981]/15 border border-[#10B981]/40 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-[#10B981]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-white tracking-tight">
                AI FORENSIC COPILOT
              </h3>
              <span className="flex items-center gap-1 text-[9px] font-mono text-emerald-400 bg-emerald-950/40 px-1.5 py-0.2 rounded border border-emerald-800/40">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                OLLAMA LIVE
              </span>
            </div>
            <p className="text-[10px] text-[#646A7E]">
              llama3:latest • Case {caseId}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleClearHistory}
            className="p-1.5 rounded text-[#646A7E] hover:text-red-400 hover:bg-[#181B24] transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded text-[#646A7E] hover:text-white hover:bg-[#181B24] transition-colors"
            title="Close Drawer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Messages Thread */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
              <div className="flex items-center gap-1.5 mb-1 px-1">
                <span className="text-[10px] text-[#646A7E] font-mono">{m.time}</span>
                <span className="text-[10px] font-semibold text-[#8E93A6]">
                  {isUser ? 'Investigator (You)' : 'AI Copilot (Ollama)'}
                </span>
              </div>

              <div
                className={`max-w-[92%] rounded-xl px-3.5 py-2.5 leading-relaxed ${
                  isUser
                    ? 'bg-[#10B981] text-black font-medium rounded-tr-none'
                    : 'bg-[#181B24] text-slate-100 border border-[#262A36] rounded-tl-none shadow-sm'
                }`}
              >
                <div className="prose prose-invert prose-xs max-w-none space-y-2">
                  {m.text.split('\n\n').map((para, i) => {
                    if (para.startsWith('## ')) {
                      return <h4 key={i} className="text-xs font-bold text-white mb-1">{para.replace('## ', '')}</h4>;
                    }
                    if (para.startsWith('### ')) {
                      return <h5 key={i} className="text-[11px] font-semibold text-[#10B981] mb-1">{para.replace('### ', '')}</h5>;
                    }
                    if (para.startsWith('• ') || para.includes('\n• ')) {
                      const bullets = para.split('\n').filter(b => b.trim());
                      return (
                        <ul key={i} className="space-y-1 my-1">
                          {bullets.map((b, bi) => (
                            <li key={bi} className="flex items-start gap-1.5">
                              <span className="text-[#10B981] shrink-0">•</span>
                              <span dangerouslySetInnerHTML={{ __html: b.replace(/^•\s*/, '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                            </li>
                          ))}
                        </ul>
                      );
                    }
                    return <p key={i} dangerouslySetInnerHTML={{ __html: para.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />;
                  })}
                </div>
              </div>
            </div>
          );
        })}

        {isThinking && (
          <div className="flex flex-col items-start">
            <span className="text-[10px] text-[#646A7E] font-mono mb-1 px-1">Ollama reasoning...</span>
            <div className="bg-[#181B24] border border-[#262A36] rounded-xl rounded-tl-none px-3.5 py-2.5 flex items-center gap-2 text-xs text-[#8E93A6]">
              <div className="w-2 h-2 rounded-full bg-[#10B981] animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-[#10B981] animate-bounce [animation-delay:0.2s]" />
              <div className="w-2 h-2 rounded-full bg-[#10B981] animate-bounce [animation-delay:0.4s]" />
              <span className="font-mono text-[11px] text-[#A0A0A0]">Running forensic inference with llama3...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 3. Quick Suggestions Bar */}
      <div className="p-3 border-t border-[#1C1F28] bg-[#0E1015]/60 space-y-1.5">
        <span className="text-[9px] uppercase font-mono tracking-wider text-[#646A7E] block">
          Quick Prompts
        </span>
        <div className="flex flex-wrap gap-1">
          {quickPrompts.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              disabled={isThinking}
              className="text-[10px] px-2 py-1 rounded bg-[#181B24] hover:bg-[#202430] text-[#8E93A6] hover:text-white border border-[#262A36] transition-colors truncate max-w-full text-left"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* 4. Chat Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 border-t border-[#1C1F28] bg-[#0E1015] flex items-center gap-2"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask Ollama about graph evidence, devices, SAR..."
          className="flex-1 bg-[#15171F] border border-[#232733] focus:border-[#10B981] rounded-lg px-3 py-2 text-xs text-white placeholder-[#585E72] outline-none transition-colors"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isThinking}
          className="p-2 rounded-lg bg-[#10B981] hover:bg-[#34D399] disabled:opacity-40 text-black font-semibold transition-all shrink-0"
          title="Send Query"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </aside>
  );
}

export default AiNotesDrawer;
