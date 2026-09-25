import React from 'react';
import { Lightbulb, ChevronRight } from 'lucide-react';
import { keyInsights } from '../data/insights';

export const KeyInsights = ({ onSelectInsight }) => {
  return (
    <div className="flex flex-col border border-cyber-border bg-cyber-panel/85 rounded-lg p-3.5 mt-3 shadow-[0_0_18px_rgba(0,0,0,0.8)]">
      {/* Header */}
      <div className="flex items-center gap-2 pb-2 mb-2 border-b border-cyber-border/60">
        <Lightbulb className="w-4 h-4 text-cyber-cyan stroke-[2.5]" />
        <h3 className="text-xs font-mono font-extrabold tracking-wider text-cyber-cyan uppercase">
          KEY INSIGHTS
        </h3>
      </div>

      {/* Insights List */}
      <div className="flex flex-col gap-2 font-mono text-[10.5px]">
        {keyInsights.map((insight) => (
          <div
            key={insight.id}
            onClick={() => onSelectInsight && onSelectInsight(insight)}
            className="flex items-start gap-2 p-1.5 rounded hover:bg-cyan-950/20 transition-colors cursor-pointer group"
          >
            <ChevronRight className="w-3.5 h-3.5 text-cyber-emerald mt-0.5 shrink-0 group-hover:translate-x-0.5 transition-transform" />
            <div className="flex flex-col">
              <span className="font-bold text-cyber-emerald tracking-wide group-hover:text-cyber-cyan transition-colors">
                {insight.title}
              </span>
              <span className="text-[9.5px] text-slate-400 leading-tight mt-0.5">
                {insight.detail}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
