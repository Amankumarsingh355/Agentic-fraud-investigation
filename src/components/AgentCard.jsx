import React from 'react';
import { 
  Database, 
  Network, 
  Cpu, 
  FileText, 
  Brain, 
  ShieldAlert, 
  Zap, 
  ShieldCheck, 
  Crosshair, 
  FileCode, 
  Terminal 
} from 'lucide-react';
import { StatusBadge } from './StatusBadge';

const iconMap = {
  Database,
  Network,
  Cpu,
  FileText,
  Brain,
  ShieldAlert,
  Zap,
  ShieldCheck,
  Crosshair,
  FileCode,
  Terminal
};

export const AgentCard = ({ agent, onClick }) => {
  const IconComponent = iconMap[agent.icon] || Cpu;

  // Custom border/glow depending on status
  let containerStyle = "border-cyber-border/70 bg-[#080E17]/60 hover:border-cyber-cyan/50 hover:bg-[#0A1320]";
  let iconContainerStyle = "border-cyber-border bg-[#0B1522] text-cyber-cyan";

  if (agent.status === 'ACTIVE') {
    containerStyle = "border-cyber-cyan bg-cyan-950/30 shadow-[0_0_15px_rgba(0,229,255,0.35)]";
    iconContainerStyle = "border-cyber-cyan bg-cyan-900/40 text-cyber-cyan";
  } else if (agent.status === 'TRIGGERED') {
    containerStyle = "border-red-500/80 bg-red-950/30 shadow-[0_0_14px_rgba(255,51,75,0.35)]";
    iconContainerStyle = "border-red-500/60 bg-red-900/40 text-cyber-crimson";
  } else if (agent.status === 'BYPASSED') {
    containerStyle = "border-slate-800/80 bg-slate-900/30 opacity-70";
    iconContainerStyle = "border-slate-800 bg-slate-900 text-slate-400";
  }

  return (
    <div
      onClick={() => onClick(agent)}
      className={`
        relative group flex items-center justify-between p-2 px-3 rounded-md border transition-all duration-200 cursor-pointer mb-1.5
        ${containerStyle}
      `}
    >
      {/* Left: Icon + Index + Name & Description */}
      <div className="flex items-center gap-2.5 min-w-0">
        {/* Rounded square icon */}
        <div className={`w-7 h-7 rounded border flex items-center justify-center shrink-0 ${iconContainerStyle}`}>
          <IconComponent className="w-3.5 h-3.5" />
        </div>

        <div className="flex items-center gap-1.5 truncate">
          <span className="text-[11px] font-mono text-cyan-400/80 font-bold shrink-0">
            [{agent.id}]
          </span>
          <div className="flex flex-col truncate">
            <span className="text-[11px] font-mono font-bold text-slate-100 tracking-wider truncate group-hover:text-cyber-cyan transition-colors">
              {agent.name}
            </span>
            <span className="text-[10px] font-mono text-slate-400 truncate">
              {agent.desc}
            </span>
          </div>
        </div>
      </div>

      {/* Right: Status Badge */}
      <div className="shrink-0 ml-2">
        <StatusBadge status={agent.status} />
      </div>
    </div>
  );
};
