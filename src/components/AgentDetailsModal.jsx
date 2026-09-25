import React, { useEffect } from 'react';
import { X, Bot, Clock, ShieldCheck, Cpu, Terminal } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { OllamaIcon } from './OllamaIcon';

export const AgentDetailsModal = ({ agent, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!agent) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-lg border border-cyber-cyan/60 bg-[#070D18] rounded-lg p-5 shadow-[0_0_30px_rgba(0,229,255,0.35)] overflow-hidden font-mono"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top cyan accent line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyber-cyan to-transparent" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-cyber-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded border border-cyber-cyan/60 bg-cyan-950/40 flex items-center justify-center text-cyber-cyan shadow-[0_0_10px_rgba(0,229,255,0.3)]">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-cyber-cyan font-bold">[{agent.id}]</span>
                <h3 className="text-sm font-bold text-white tracking-wider">
                  {agent.name} AGENT
                </h3>
              </div>
              <span className="text-[10px] text-slate-400">
                {agent.role}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <StatusBadge status={agent.status} />
            <button
              onClick={onClose}
              className="p-1 rounded text-slate-400 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Meta Grid */}
        <div className="grid grid-cols-2 gap-2 mb-4 text-[11px]">
          <div className="p-2 rounded bg-[#0A1422] border border-cyber-border">
            <span className="text-slate-400 text-[10px] block">LLM / ORCHESTRATOR:</span>
            <span className="text-cyber-cyan font-bold flex items-center gap-1.5 mt-0.5">
              <OllamaIcon className="w-3.5 h-3.5 text-cyber-cyan drop-shadow-[0_0_4px_rgba(0,229,255,0.6)]" />
              {agent.model || 'Ollama Llama-3 (Local)'}
            </span>
          </div>

          <div className="p-2 rounded bg-[#0A1422] border border-cyber-border">
            <span className="text-slate-400 text-[10px] block">EXECUTION LATENCY:</span>
            <span className="text-cyber-emerald font-bold flex items-center gap-1.5 mt-0.5">
              <Clock className="w-3.5 h-3.5" />
              {agent.latency}
            </span>
          </div>
        </div>

        {/* Forensic Input / Output */}
        <div className="space-y-3 text-xs mb-4">
          <div className="p-2.5 rounded bg-[#040811] border border-slate-800">
            <span className="text-[10px] text-cyan-400 font-bold block mb-1 uppercase tracking-wider">
              INPUT PARAMETERS:
            </span>
            <p className="text-slate-300 text-[11px] leading-relaxed">
              {agent.input}
            </p>
          </div>

          <div className="p-2.5 rounded bg-[#040811] border border-slate-800">
            <span className="text-[10px] text-cyber-emerald font-bold block mb-1 uppercase tracking-wider">
              OUTPUT FINDINGS:
            </span>
            <p className="text-slate-200 text-[11px] leading-relaxed">
              {agent.output}
            </p>
          </div>

          <div className="p-2.5 rounded bg-[#06101F] border border-cyber-border/70">
            <span className="text-[10px] text-cyber-amber font-bold block mb-1 uppercase tracking-wider flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-cyber-amber" />
              CHAIN-OF-THOUGHT (CoT) AUDIT:
            </span>
            <p className="text-slate-300 text-[11px] leading-relaxed italic">
              "{agent.cot}"
            </p>
          </div>
        </div>

        {/* Action Footer */}
        <div className="flex justify-end gap-2 pt-2 border-t border-cyber-border">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-cyber-cyan bg-cyan-950/40 text-xs text-cyber-cyan hover:bg-cyan-900/50 transition-colors shadow-[0_0_10px_rgba(0,229,255,0.3)]"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
};
