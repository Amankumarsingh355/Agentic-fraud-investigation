import React from 'react';
import { Cpu, Network, ShieldCheck, Activity } from 'lucide-react';

export function SystemStatus({ statusData }) {
  const ollama = statusData?.ollama || { connected: true, model: 'llama3:latest', status: 'Ready' };
  const tigergraph = statusData?.tigergraph || { connected: true, status: 'Operational', graph_name: 'FraudInvestigationGraph' };
  const system = statusData?.system || { status: 'Operational' };

  return (
    <div className="p-3 border-t border-workspace-border/60 bg-workspace-surface/50 text-[11px] space-y-2">
      <div className="flex items-center justify-between text-slate-400 font-medium tracking-wider uppercase text-[10px]">
        <span>System Engines</span>
        <span className="flex items-center gap-1 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Active
        </span>
      </div>

      {/* Ollama Status */}
      <div className="flex items-center justify-between bg-workspace-card/70 px-2 py-1.5 rounded-md border border-workspace-border/50">
        <div className="flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-purple-400" />
          <div>
            <div className="text-slate-200 font-medium">Ollama Core</div>
            <div className="text-[10px] text-slate-400 font-mono">{ollama.model || 'llama3:latest'}</div>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/40">
          <span className="w-1 h-1 rounded-full bg-emerald-400" />
          Connected
        </span>
      </div>

      {/* TigerGraph Status */}
      <div className="flex items-center justify-between bg-workspace-card/70 px-2 py-1.5 rounded-md border border-workspace-border/50">
        <div className="flex items-center gap-2">
          <Network className="w-3.5 h-3.5 text-blue-400" />
          <div>
            <div className="text-slate-200 font-medium">TigerGraph Engine</div>
            <div className="text-[10px] text-slate-400 font-mono">590k Txns • 13.5k Users</div>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/40">
          <span className="w-1 h-1 rounded-full bg-emerald-400" />
          Connected
        </span>
      </div>

      {/* Analyst Profile */}
      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold text-[10px]">
            SA
          </div>
          <div>
            <div className="text-slate-200 font-medium text-[11px]">Senior Fraud Analyst</div>
            <div className="text-[9px] text-slate-400">Security Clearance L2</div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default SystemStatus;
