import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

export const ConsoleLogs = ({ logs }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getColorClass = (color) => {
    switch (color) {
      case 'cyan':
        return 'text-cyber-cyan';
      case 'emerald':
        return 'text-cyber-emerald';
      case 'crimson':
        return 'text-cyber-crimson';
      case 'amber':
        return 'text-cyber-amber';
      case 'purple':
        return 'text-cyber-purpleNeon';
      case 'muted':
        return 'text-slate-400';
      default:
        return 'text-slate-300';
    }
  };

  return (
    <div className="flex flex-col border border-cyber-border bg-[#050912]/90 rounded-lg p-2.5 px-3 mt-3 shadow-[0_0_15px_rgba(0,0,0,0.8)]">
      {/* Header */}
      <div className="flex items-center gap-2 pb-1.5 mb-1.5 border-b border-cyber-border/60">
        <div className="w-4 h-4 rounded border border-cyan-500/40 bg-cyber-dark/80 flex items-center justify-center text-cyber-cyan">
          <Terminal className="w-2.5 h-2.5" />
        </div>
        <span className="text-[11px] font-mono font-extrabold tracking-wider text-cyber-cyan uppercase">
          CONSOLE LOGS
        </span>
      </div>

      {/* Terminal Output */}
      <div
        ref={scrollRef}
        className="max-h-[125px] overflow-y-auto space-y-1 font-mono text-[11px] leading-relaxed pr-1"
      >
        {logs.map((log) => (
          <div key={log.id || `${log.time}-${log.sender}`} className="flex items-start gap-1.5">
            <span className="text-slate-500 shrink-0">&gt;</span>
            <span className="text-cyan-400/80 shrink-0">[{log.time}]</span>
            <span className={`font-bold shrink-0 ${getColorClass(log.color)}`}>
              {log.sender}:
            </span>
            <span className="text-slate-300 break-all">
              {log.text}
            </span>
          </div>
        ))}

        {/* Blinking prompt line */}
        <div className="flex items-center gap-1.5 pt-0.5">
          <span className="text-slate-500">&gt;</span>
          <span className="inline-block w-2 h-3.5 bg-cyber-cyan animate-pulse" />
        </div>
      </div>
    </div>
  );
};
