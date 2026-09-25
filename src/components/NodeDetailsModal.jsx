import React, { useEffect } from 'react';
import { X, Network, Shield, AlertTriangle, Cpu, ArrowRight } from 'lucide-react';

export const NodeDetailsModal = ({ node, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!node) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-lg border border-cyber-cyan/60 bg-[#070D18] rounded-lg p-5 shadow-[0_0_30px_rgba(0,229,255,0.35)] overflow-hidden font-mono"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top cyan scan accent */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyber-cyan to-transparent" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-cyber-border">
          <div className="flex items-center gap-2.5">
            <div 
              className="w-8 h-8 rounded border flex items-center justify-center"
              style={{ borderColor: node.color, backgroundColor: `${node.color}15`, color: node.color }}
            >
              <Network className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-wider">
                  NODE_INSPECTOR // {node.id}
                </h3>
                {node.badge && (
                  <span className={`text-[9px] px-2 py-0.5 rounded font-bold uppercase ${
                    node.badgeColor === 'crimson' 
                      ? 'bg-red-950/80 text-cyber-crimson border border-red-500/60' 
                      : 'bg-emerald-950/80 text-cyber-emerald border border-emerald-500/60'
                  }`}>
                    {node.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] text-cyan-400/80">
                TYPE: {node.type.toUpperCase()} | STATUS: {node.status}
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Risk Level Banner */}
        <div className="flex items-center justify-between p-2.5 rounded bg-[#0A1422] border border-cyber-border mb-4 text-xs">
          <span className="text-slate-400">Calculated Topology Risk:</span>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 rounded bg-slate-800 overflow-hidden">
              <div 
                className="h-full rounded"
                style={{ 
                  width: `${node.risk * 100}%`,
                  backgroundColor: node.color
                }} 
              />
            </div>
            <span className="font-bold" style={{ color: node.color }}>
              {(node.risk * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Detailed Attributes */}
        <div className="space-y-2 text-xs mb-4">
          {Object.entries(node.details || {}).map(([key, val]) => (
            <div key={key} className="flex justify-between items-start gap-4 py-1 border-b border-slate-800/60">
              <span className="text-slate-400 capitalize shrink-0 text-[11px]">
                {key.replace(/([A-Z])/g, ' $1').toLowerCase()}:
              </span>
              <span className="font-semibold text-slate-200 text-right text-[11px] break-all">
                {String(val)}
              </span>
            </div>
          ))}
        </div>

        {/* Action Footer */}
        <div className="flex justify-end gap-2 pt-2 border-t border-cyber-border">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-cyber-border bg-slate-900 text-xs text-slate-300 hover:text-white transition-colors"
          >
            DISMISS
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-cyber-cyan bg-cyan-950/40 text-xs text-cyber-cyan hover:bg-cyan-900/50 transition-colors shadow-[0_0_10px_rgba(0,229,255,0.3)]"
          >
            TRACE SUBGRAPH
          </button>
        </div>
      </div>
    </div>
  );
};
