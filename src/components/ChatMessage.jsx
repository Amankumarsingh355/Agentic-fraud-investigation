import React, { useState } from 'react';
import { Bot, User, Shield, Share2, FileText, ExternalLink, ArrowRight, Copy, Check, ThumbsUp, ThumbsDown, RefreshCw, Edit2 } from 'lucide-react';
import { ChainOfThought } from './ChainOfThought';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export function ChatMessage({ 
  message, 
  onOpenEvidence, 
  onViewGraph, 
  onViewPolicy, 
  onViewSimilar,
  onReviewAction,
  onRegenerate,
  onEdit
}) {
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(message.text);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Investigation Response',
        text: message.text,
      }).catch(console.error);
    } else {
      handleCopy();
    }
  };

  const handleSaveEdit = () => {
    setIsEditing(false);
    if (editText.trim() !== message.text && onEdit) {
      onEdit(message.id, editText.trim());
    }
  };

  return (
    <div className={`flex gap-3 py-4 px-4 group ${isUser ? 'bg-workspace-card/30 justify-end' : 'bg-transparent border-b border-workspace-border/30'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg border border-[#10B981]/30 flex items-center justify-center flex-shrink-0 mt-0.5 overflow-hidden">
          <img src="/savanna-logo.png" alt="Chief Orchestrator" className="w-full h-full object-cover" />
        </div>
      )}

      <div className={`max-w-[85%] w-full ${isUser ? 'text-right' : 'text-left'}`}>
        <div className="text-[10px] font-medium text-slate-400 mb-1.5 flex items-center gap-1.5 justify-between">
          <div className="flex flex-wrap items-center gap-1.5">
            {isUser ? (
              <>
                <span>Senior Fraud Analyst</span>
                <span>•</span>
                <span className="font-mono">{message.time || 'Just now'}</span>
              </>
            ) : (
              <>
                <span className="text-[#10B981] font-semibold">{message.agent || 'Chief Orchestrator'}</span>
                <span>•</span>
                <span className="font-mono">{message.time || 'Just now'}</span>
              </>
            )}
          </div>
          
          {/* Top Actions */}
          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
            {isUser ? (
              <button onClick={() => setIsEditing(true)} className="p-1 hover:bg-workspace-card rounded text-slate-400 hover:text-white" title="Edit message">
                <Edit2 className="w-3.5 h-3.5" />
              </button>
            ) : (
              <>
                <button onClick={handleCopy} className="p-1 hover:bg-workspace-card rounded text-slate-400 hover:text-white" title="Copy response">
                  {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
                <button onClick={() => setFeedback('up')} className={`p-1 hover:bg-workspace-card rounded ${feedback === 'up' ? 'text-green-400' : 'text-slate-400 hover:text-white'}`} title="Good response">
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => setFeedback('down')} className={`p-1 hover:bg-workspace-card rounded ${feedback === 'down' ? 'text-red-400' : 'text-slate-400 hover:text-white'}`} title="Bad response">
                  <ThumbsDown className="w-3.5 h-3.5" />
                </button>
                {onRegenerate && (
                  <button onClick={() => onRegenerate(message.id)} className="p-1 hover:bg-workspace-card rounded text-slate-400 hover:text-white" title="Regenerate">
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        <div className={`text-sm leading-relaxed font-sans ${
          isUser 
            ? 'bg-[#1C1E24] text-white p-3.5 rounded-2xl rounded-tr-sm inline-block text-left border border-[#2A2D35]' 
            : message.isError ? 'text-red-400 bg-red-950/20 p-3 rounded-lg border border-red-900/50' : 'text-slate-200'
        }`}>
          {!isUser && message.chainOfThought && (
            <div className="mb-3 pb-3 border-b border-workspace-border/50">
              <ChainOfThought 
                title={message.chainOfThought.title || "Thinking..."}
                steps={message.chainOfThought.steps}
                duration={message.chainOfThought.duration}
                defaultExpanded={message.chainOfThought.defaultExpanded || false}
              />
            </div>
          )}

          {isEditing ? (
            <div className="flex flex-col gap-2">
              <textarea
                value={editText}
                onChange={e => setEditText(e.target.value)}
                className="w-full bg-[#0A0C10] border border-[#2A2D35] rounded p-2 text-white resize-y"
                rows={3}
              />
              <div className="flex justify-end gap-2">
                <button onClick={() => setIsEditing(false)} className="px-3 py-1 text-xs text-slate-400 hover:text-white">Cancel</button>
                <button onClick={handleSaveEdit} className="px-3 py-1 text-xs bg-[#10B981] text-black rounded font-medium hover:bg-[#34D399]">Save & Send</button>
              </div>
            </div>
          ) : (
            <div className={`prose prose-invert max-w-none ${isUser ? 'prose-p:m-0' : 'prose-p:my-2 prose-headings:my-3 prose-pre:my-3 prose-li:my-0.5'}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({node, inline, className, children, ...props}) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <div className="relative group/code rounded-lg overflow-hidden my-4 border border-workspace-border/50">
                        <div className="flex items-center justify-between px-4 py-1.5 bg-[#0A0C10] border-b border-workspace-border/50">
                          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">{match[1]}</span>
                          <button
                            onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                            className="text-slate-400 hover:text-white p-1 rounded transition-colors"
                            title="Copy code"
                          >
                            <Copy className="w-3.5 h-3.5" />
                          </button>
                        </div>
                        <SyntaxHighlighter
                          {...props}
                          children={String(children).replace(/\n$/, '')}
                          style={vscDarkPlus}
                          language={match[1]}
                          PreTag="div"
                          customStyle={{ margin: 0, borderRadius: 0, background: '#12141A', fontSize: '13px' }}
                        />
                      </div>
                    ) : (
                      <code {...props} className={`${className} bg-workspace-card px-1.5 py-0.5 rounded text-blue-300 font-mono text-[13px] border border-workspace-border/50`}>
                        {children}
                      </code>
                    )
                  },
                  a({node, children, href, ...props}) {
                    if (children && typeof children[0] === 'string' && children[0].match(/\[(Evidence|Policy Rule|Device|Node)/)) {
                      return (
                        <button
                          onClick={() => {
                            const type = children[0].split(' ')[0].replace('[', '');
                            if (type === 'Evidence' || type === 'Device' || type === 'Node') onOpenEvidence?.(children[0]);
                            if (type === 'Policy') onViewPolicy?.(children[0]);
                          }}
                          className="inline-flex items-center gap-1 font-mono text-[11px] px-1.5 py-0.5 rounded bg-blue-950/60 border border-blue-800/60 text-blue-400 hover:bg-blue-900/60 transition-colors mx-0.5 no-underline"
                        >
                          <FileText className="w-3 h-3" />
                          {children}
                        </button>
                      );
                    }
                    return <a href={href} className="text-blue-400 hover:underline" {...props}>{children}</a>;
                  }
                }}
              >
                {message.text}
              </ReactMarkdown>
            </div>
          )}

          {message.isError && onRegenerate && (
            <div className="pt-2 mt-2 border-t border-red-900/30">
              <button onClick={() => onRegenerate(message.id)} className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-red-900/40 hover:bg-red-800/60 text-red-300 text-xs transition-colors">
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Request
              </button>
            </div>
          )}
          {/* Quick Action Buttons for AI responses */}
          {!isUser && message.showActions && !isEditing && (
            <div className="pt-3 mt-4 border-t border-workspace-border/60 flex flex-wrap gap-2">
              <button
                onClick={onViewGraph}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1C1E24] hover:bg-[#2A2D35] text-slate-300 hover:text-white border border-[#2A2D35] text-[11px] transition-all"
              >
                <Share2 className="w-3.5 h-3.5 text-cyan-400" />
                View Evidence Graph
              </button>

              <button
                onClick={() => onOpenEvidence && onOpenEvidence('ALL')}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1C1E24] hover:bg-[#2A2D35] text-slate-300 hover:text-white border border-[#2A2D35] text-[11px] transition-all"
              >
                <FileText className="w-3.5 h-3.5 text-blue-400" />
                View Evidence
              </button>

              <button
                onClick={onViewSimilar}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1C1E24] hover:bg-[#2A2D35] text-slate-300 hover:text-white border border-[#2A2D35] text-[11px] transition-all"
              >
                <ExternalLink className="w-3.5 h-3.5 text-indigo-400" />
                View Similar Cases
              </button>

              <button
                onClick={onViewPolicy}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1C1E24] hover:bg-[#2A2D35] text-slate-300 hover:text-white border border-[#2A2D35] text-[11px] transition-all"
              >
                <Shield className="w-3.5 h-3.5 text-purple-400" />
                View Policy
              </button>

              {onReviewAction && (
                <button
                  onClick={onReviewAction}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#10B981] hover:bg-[#34D399] text-black font-medium text-[11px] transition-all ml-auto shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                >
                  Review Next Action
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-slate-700/50 border border-slate-600/50 flex items-center justify-center text-slate-300 flex-shrink-0 mt-0.5">
          <User className="w-5 h-5" />
        </div>
      )}
    </div>
  );
}
export default ChatMessage;
