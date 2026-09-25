import React from 'react';
import { Shield, Snowflake, ArrowUpRight, Upload } from 'lucide-react';

export const RecommendedActions = ({ onAutoFreeze, onEscalate }) => {
  return (
    <div className="flex flex-col border border-cyber-border bg-cyber-panel/85 rounded-lg p-3.5 mt-3 shadow-[0_0_18px_rgba(0,0,0,0.8)]">
      {/* Header */}
      <div className="flex items-center gap-2 pb-2 mb-2.5 border-b border-cyber-border/60">
        <Shield className="w-4 h-4 text-cyber-cyan stroke-[2.5]" />
        <h3 className="text-xs font-mono font-extrabold tracking-wider text-cyber-cyan uppercase">
          RECOMMENDED ACTION
        </h3>
      </div>

      {/* Banner / Recommendation Box */}
      <div className="flex items-center justify-center gap-2.5 py-2.5 px-3 rounded-md border border-red-500/70 bg-red-950/30 text-cyber-crimson font-mono text-xs font-bold tracking-wider mb-3 shadow-[0_0_12px_rgba(255,51,75,0.25)]">
        <Snowflake className="w-4 h-4 text-cyber-crimson animate-pulse" />
        <span className="uppercase">FREEZE ACCOUNT</span>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-2 font-mono text-xs font-bold">
        {/* AUTO FREEZE (Primary Red Button) */}
        <button
          onClick={onAutoFreeze}
          className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-md bg-[#DC2626] hover:bg-[#EF4444] text-white tracking-wider uppercase transition-all duration-200 shadow-[0_0_18px_rgba(239,68,68,0.5)] hover:shadow-[0_0_25px_rgba(239,68,68,0.7)] active:scale-[0.98]"
        >
          <Snowflake className="w-4 h-4" />
          <span>AUTO FREEZE</span>
        </button>

        {/* ESCALATE (Secondary Cyan Button) */}
        <button
          onClick={onEscalate}
          className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-md border border-cyber-cyan bg-cyan-950/30 hover:bg-cyan-900/40 text-cyber-cyan tracking-wider uppercase transition-all duration-200 shadow-[0_0_12px_rgba(0,229,255,0.25)] hover:shadow-[0_0_18px_rgba(0,229,255,0.45)] active:scale-[0.98]"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>ESCALATE</span>
        </button>
      </div>
    </div>
  );
};
