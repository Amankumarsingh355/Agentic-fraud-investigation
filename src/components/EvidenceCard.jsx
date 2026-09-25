import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, Share2, Shield, Hash, CheckCircle2 } from 'lucide-react';

export function EvidenceCard({ evidence, onSelectEntity }) {
  const [expanded, setExpanded] = useState(false);

  const id = evidence.id || 'E-001';
  const claim = evidence.claim || evidence.description || 'Evidentiary graph signal detected';
  const source = evidence.source || 'TigerGraph Subgraph';
  const type = evidence.type || 'Shared Entity';
  const entity = evidence.entity || evidence.target_entity || 'Device_99';
  const confidence = evidence.confidence !== undefined ? evidence.confidence : 0.94;
  const connected = evidence.connected_accounts || ['ACC-101', 'ACC-882'];

  return (
    <div className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl overflow-hidden transition-all">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-start justify-between text-left hover:bg-workspace-cardHover/40 transition-colors"
      >
        <div className="flex items-start gap-2.5">
          <div className="p-1.5 rounded-lg bg-blue-950/40 border border-blue-800/40 text-blue-400 mt-0.5">
            <Share2 className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-mono text-xs font-bold text-white">[{id}]</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-workspace-surface border border-workspace-border text-slate-300">
                {source}
              </span>
            </div>
            <div className="text-xs text-slate-200 font-medium leading-snug">
              {claim}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-400 text-xs">
          <span className="font-mono text-[11px] text-emerald-400">
            {Math.round(confidence * 100)}% Conf
          </span>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {expanded && (
        <div className="px-3.5 pb-3.5 pt-1 border-t border-workspace-border/50 text-xs font-mono space-y-2 bg-workspace-surface/40">
          <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
            <div>
              <span className="text-slate-400 block text-[10px]">Entity:</span>
              <button 
                onClick={() => onSelectEntity && onSelectEntity(entity)}
                className="text-blue-400 hover:underline font-bold text-left"
              >
                {entity}
              </button>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Relationship Type:</span>
              <span className="text-slate-200">{type}</span>
            </div>
          </div>

          {connected && connected.length > 0 && (
            <div>
              <span className="text-slate-400 block text-[10px] mb-1">Connected Entities:</span>
              <div className="flex flex-wrap gap-1">
                {connected.map((acc, i) => (
                  <span key={i} className="px-1.5 py-0.5 rounded bg-workspace-card border border-workspace-border text-slate-300 text-[10px]">
                    {acc}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => onSelectEntity && onSelectEntity(entity)}
              className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 font-sans"
            >
              Investigate in Graph →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
export default EvidenceCard;
