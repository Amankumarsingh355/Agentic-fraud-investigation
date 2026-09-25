import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  RefreshCw, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  HelpCircle,
  Sparkles,
  Bot
} from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChainOfThought } from './ChainOfThought';

export function ChatInterface({ 
  caseData, 
  chatMessages = [], 
  onSendMessage, 
  isAnalyzing, 
  onRerunInvestigation,
  onOpenEvidence,
  onViewGraph,
  onViewPolicy,
  onViewSimilar,
  onReviewAction,
  onAttachEvidence,
  pipelineStatus = []
}) {
  const [inputText, setInputText] = useState('');
  const [progressExpanded, setProgressExpanded] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isAnalyzing]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || isAnalyzing) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const promptSuggestions = [
    "Why was this transaction flagged?",
    "Show me all accounts connected to this device.",
    "What additional evidence do we need?",
    "Explain the recommended action.",
    "Show the policy supporting this recommendation."
  ];

  const c = caseData?.case || {};
  const completedAgents = pipelineStatus.filter(a => a.status === 'Completed').length || 11;
  const totalAgents = 11;

  return (
    <div className="flex-1 flex flex-col h-full bg-workspace-bg relative overflow-hidden">
      {/* Scrollable Message Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {/* Investigation Progress Card (Reflects REAL 11 agents) */}
        {caseData && (
          <div className="max-w-3xl mx-auto bg-workspace-card/70 border border-workspace-border/80 rounded-xl overflow-hidden shadow-subtle-card">
            <button
              onClick={() => setProgressExpanded(!progressExpanded)}
              className="w-full px-4 py-2.5 flex items-center justify-between bg-workspace-surface/60 hover:bg-workspace-surface text-slate-300 text-xs font-medium border-b border-workspace-border/50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white">Investigation Progress</span>
                <span className="text-slate-400 font-mono text-[11px]">
                  ({completedAgents} / {totalAgents} agents completed)
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-400">
                <span className="text-[11px] font-mono">
                  {isAnalyzing ? 'Executing...' : 'Verified by Master Decision Validator'}
                </span>
                {progressExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {progressExpanded && (
              <div className="p-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono bg-workspace-card/40">
                {pipelineStatus.map((agent) => {
                  const isDone = agent.status === 'Completed';
                  const isRunning = agent.status === 'Running';

                  return (
                    <div 
                      key={agent.id}
                      className="flex items-center justify-between px-2.5 py-1.5 rounded bg-workspace-surface/50 border border-workspace-border/40"
                    >
                      <div className="flex items-center gap-2 truncate">
                        {isDone ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        ) : isRunning ? (
                          <span className="w-3.5 h-3.5 flex items-center justify-center flex-shrink-0">
                            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                          </span>
                        ) : (
                          <span className="w-3.5 h-3.5 rounded-full border border-slate-600 flex-shrink-0" />
                        )}
                        <span className={`truncate ${isDone ? 'text-slate-200' : isRunning ? 'text-blue-300 font-semibold' : 'text-slate-500'}`}>
                          {agent.name}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 flex-shrink-0 ml-2">
                        {agent.latency || '0.2s'}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Chat Messages */}
        <div className="max-w-3xl mx-auto space-y-3">
          {chatMessages.map((msg, index) => (
            <ChatMessage
              key={index}
              message={msg}
              onOpenEvidence={onOpenEvidence}
              onViewGraph={onViewGraph}
              onViewPolicy={onViewPolicy}
              onViewSimilar={onViewSimilar}
              onReviewAction={onReviewAction}
            />
          ))}

          {/* Live Multi-Agent Chain of Thought Reasoning Trail */}
          {isAnalyzing && (
            <div className="flex gap-3 py-3 px-4">
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 flex-shrink-0 mt-0.5">
                <Bot className="w-4 h-4 animate-pulse" />
              </div>
              <div className="flex-1 max-w-[85%] bg-workspace-card/60 p-3 rounded-xl border border-workspace-border/70 space-y-2">
                <ChainOfThought 
                  title="Drafting forensic investigation report with TigerGraph & 11 Agents"
                  isLive={true}
                  caseId={c.case_id || "HHG-001"}
                />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggested Prompt Pills */}
      <div className="px-4 py-1.5 max-w-3xl mx-auto w-full">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] scrollbar-none">
          <span className="text-slate-500 text-[10px] flex items-center gap-1 uppercase tracking-wider font-semibold mr-1">
            <Sparkles className="w-3 h-3 text-blue-400" /> Prompts:
          </span>
          {promptSuggestions.map((prompt, i) => (
            <button
              key={i}
              onClick={() => onSendMessage(prompt)}
              disabled={isAnalyzing}
              className="px-2.5 py-1 rounded-full bg-workspace-card hover:bg-workspace-cardHover text-slate-300 hover:text-white border border-workspace-border whitespace-nowrap transition-colors flex-shrink-0"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom ChatGPT-Style Docked Input Box */}
      <div className="p-4 border-t border-workspace-border/70 bg-workspace-surface/50">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative flex items-center bg-workspace-card border border-workspace-border rounded-xl focus-within:border-blue-500/60 shadow-subtle-card transition-all">
            <button
              type="button"
              onClick={onAttachEvidence}
              className="p-2.5 text-slate-400 hover:text-white transition-colors"
              title="Attach out-of-band Evidence / Re-investigate"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            <textarea
              ref={inputRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask the investigation agent anything about this case..."
              className="flex-1 bg-transparent py-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none resize-none font-sans"
            />

            <button
              type="submit"
              disabled={!inputText.trim() || isAnalyzing}
              className={`p-2 mr-2 rounded-lg transition-colors ${
                inputText.trim() && !isAnalyzing
                  ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-sm'
                  : 'bg-workspace-surface text-slate-600 cursor-not-allowed'
              }`}
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1.5 px-1 font-mono">
            <span>Press Enter to send • Shift + Enter for new line</span>
            <span>Grounded in TigerGraph & Bank Fraud Policy v1.0</span>
          </div>
        </form>
      </div>
    </div>
  );
}
export default ChatInterface;
