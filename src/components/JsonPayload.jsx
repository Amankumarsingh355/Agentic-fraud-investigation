import React, { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';

export const JsonPayload = ({ payload }) => {
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(payload, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Syntax highlight helper for JSON
  const renderHighlightedJson = (str) => {
    // Escape HTML chars
    const safeStr = str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Regex syntax highlighting
    const highlighted = safeStr.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = 'text-cyan-300'; // number / default
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = 'text-cyber-cyan font-bold'; // key
          } else {
            cls = 'text-emerald-300'; // string value
          }
        } else if (/true|false/.test(match)) {
          cls = 'text-amber-400 font-bold'; // boolean
        } else if (/null/.test(match)) {
          cls = 'text-slate-500'; // null
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );

    return <pre className="font-mono text-xs leading-relaxed" dangerouslySetInnerHTML={{ __html: highlighted }} />;
  };

  return (
    <div className="relative w-full h-full flex flex-col bg-[#050911] p-4 overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-cyber-border/80">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyber-cyan" />
          <span className="text-xs font-mono font-bold text-white tracking-wider">
            PRODUCTION_PAYLOAD // FrontendReportSchema
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1 rounded border border-cyber-cyan/50 bg-cyan-950/40 text-cyber-cyan text-[11px] font-mono hover:bg-cyan-900/50 transition-colors shadow-[0_0_8px_rgba(0,229,255,0.25)]"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-cyber-emerald" />
              <span className="text-cyber-emerald font-bold">COPIED</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>COPY JSON</span>
            </>
          )}
        </button>
      </div>

      {/* Code Viewer Body */}
      <div className="flex-1 overflow-auto rounded bg-[#03060C] p-3 border border-cyber-border/50 selection:bg-cyan-900">
        {renderHighlightedJson(jsonString)}
      </div>
    </div>
  );
};
