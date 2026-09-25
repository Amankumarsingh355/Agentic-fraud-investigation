import React from 'react';
import { Check, X, AlertTriangle } from 'lucide-react';

export const StatusBadge = ({ status }) => {
  switch (status) {
    case 'COMPLETED':
      return (
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/40 border border-emerald-500/40 text-cyber-emerald text-[10px] font-mono font-semibold tracking-wider shadow-[0_0_8px_rgba(0,255,136,0.25)]">
          <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 flex items-center justify-center text-cyber-emerald">
            <Check className="w-2.5 h-2.5 stroke-[3]" />
          </div>
          <span>COMPLETED</span>
        </div>
      );

    case 'BYPASSED':
      return (
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-900/60 border border-slate-700/60 text-slate-400 text-[10px] font-mono font-semibold tracking-wider">
          <div className="w-3.5 h-3.5 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
            <X className="w-2.5 h-2.5 stroke-[3]" />
          </div>
          <span>BYPASSED</span>
        </div>
      );

    case 'TRIGGERED':
      return (
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-950/60 border border-red-500 text-cyber-crimson text-[10px] font-mono font-semibold tracking-wider shadow-[0_0_12px_rgba(255,51,75,0.4)] animate-pulse">
          <div className="w-3.5 h-3.5 rounded-full bg-red-500/20 flex items-center justify-center text-cyber-crimson">
            <AlertTriangle className="w-2.5 h-2.5 stroke-[3]" />
          </div>
          <span>TRIGGERED</span>
        </div>
      );

    case 'ACTIVE':
      return (
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/70 border border-cyber-cyan text-cyber-cyan text-[10px] font-mono font-semibold tracking-wider shadow-[0_0_14px_rgba(0,229,255,0.5)]">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-cyan opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-cyan"></span>
          </span>
          <span>ACTIVE</span>
        </div>
      );

    case 'SCANNING':
      return (
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950/50 border border-cyan-400/50 text-cyan-300 text-[10px] font-mono font-semibold tracking-wider">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>PROBING</span>
        </div>
      );

    default:
      return (
        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-mono">
          <span>{status}</span>
        </div>
      );
  }
};
