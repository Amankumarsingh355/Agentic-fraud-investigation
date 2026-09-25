import React from 'react';
import { Cpu } from 'lucide-react';
import { AgentCard } from './AgentCard';
import { OllamaIcon } from './OllamaIcon';

export const AgentPipeline = ({ agents, onSelectAgent }) => {
  return (
    <div className="flex flex-col h-full border border-cyber-border bg-cyber-panel/80 rounded-lg p-3 shadow-[0_0_15px_rgba(0,0,0,0.7)]">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-cyber-border/60">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded border border-cyber-cyan/40 bg-cyber-dark/60 flex items-center justify-center text-cyber-cyan">
            <Cpu className="w-3.5 h-3.5" />
          </div>
          <h2 className="text-xs font-mono font-extrabold tracking-wider text-cyber-cyan uppercase">
            AGENT PIPELINE [11/11]
          </h2>
        </div>

        {/* Llama-3 LOCAL Badge with Ollama Icon */}
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-cyan-500/40 bg-cyber-dark/80 text-[10px] font-mono text-cyan-300 shadow-[0_0_8px_rgba(0,229,255,0.25)]">
          <OllamaIcon className="w-3.5 h-3.5 text-cyber-cyan drop-shadow-[0_0_4px_rgba(0,229,255,0.6)]" />
          <span className="font-semibold tracking-wider">Llama-3 LOCAL</span>
        </div>
      </div>

      {/* 11 Agent Rows */}
      <div className="flex-1 overflow-y-auto pr-0.5 space-y-1">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onClick={onSelectAgent}
          />
        ))}
      </div>
    </div>
  );
};
