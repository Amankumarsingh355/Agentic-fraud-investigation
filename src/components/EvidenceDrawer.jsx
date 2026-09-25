import React from 'react';
import { X, Share2, ShieldAlert, CreditCard, Hash, ExternalLink, ArrowRight } from 'lucide-react';

export function EvidenceDrawer({ entity, onClose, onInvestigateEntity }) {
  if (!entity) return null;

  const title = entity.label || entity.id || 'Entity Details';
  const type = entity.type || 'Device';
  const details = entity.details || {};
  const risk = entity.risk_level || 'MEDIUM';

  const riskColor = risk === 'CRITICAL' || risk === 'HIGH'
    ? 'text-red-400 bg-red-950/40 border-red-800/40'
    : risk === 'MEDIUM'
    ? 'text-amber-400 bg-amber-950/40 border-amber-800/40'
    : 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-workspace-surface border-l border-workspace-border shadow-subtle-elevated z-50 flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-workspace-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-950/40 border border-blue-800/40 text-blue-400">
            <Share2 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-mono uppercase tracking-wider">Entity Forensics</div>
            <div className="text-sm font-bold text-white font-mono truncate max-w-[200px]">{title}</div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-workspace-card transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs font-mono">
        {/* Risk Badge */}
        <div className="flex items-center justify-between bg-workspace-card p-3 rounded-xl border border-workspace-border">
          <span className="text-slate-400 text-xs font-sans">Entity Threat Assessment:</span>
          <span className={`px-2 py-0.5 rounded border text-xs font-bold ${riskColor}`}>
            {risk} RISK
          </span>
        </div>

        {/* Detailed Metrics */}
        <div className="bg-workspace-card/60 rounded-xl p-3.5 border border-workspace-border space-y-3">
          <div className="text-[11px] font-semibold text-white uppercase tracking-wider border-b border-workspace-border/50 pb-1.5 font-sans">
            Topological Attributes
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <span className="text-slate-400 block text-[10px]">Entity Type:</span>
              <span className="text-slate-200 font-semibold uppercase">{type}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Connected Accounts:</span>
              <span className="text-slate-200">{details.connected_accounts || 1}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Transactions:</span>
              <span className="text-slate-200">{details.transactions || (details.amount ? 1 : 4)}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Risk Relationships:</span>
              <span className="text-slate-200">{details.risk_relationships || 2}</span>
            </div>
          </div>

          {details.amount && (
            <div className="pt-2 border-t border-workspace-border/40">
              <span className="text-slate-400 block text-[10px]">Amount:</span>
              <span className="text-white text-sm font-bold">${Number(details.amount).toFixed(2)}</span>
            </div>
          )}

          {details.full_profile && (
            <div className="pt-2 border-t border-workspace-border/40">
              <span className="text-slate-400 block text-[10px]">Full Hardware Profile:</span>
              <span className="text-slate-300 text-[10px] break-all">{details.full_profile}</span>
            </div>
          )}
        </div>

        {/* Shared With List */}
        {details.shared_with && details.shared_with.length > 0 && (
          <div className="bg-workspace-card/60 rounded-xl p-3.5 border border-workspace-border space-y-2">
            <div className="text-[11px] font-semibold text-white uppercase tracking-wider font-sans">
              Shared Cardholder Entities
            </div>
            <div className="space-y-1">
              {details.shared_with.map((acc, i) => (
                <div key={i} className="flex items-center justify-between bg-workspace-surface/60 p-2 rounded border border-workspace-border/40 text-[11px]">
                  <span className="text-slate-200">{acc}</span>
                  <span className="text-[10px] text-red-400 bg-red-950/40 px-1.5 py-0.5 rounded border border-red-800/40">
                    Syndicate Link
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-workspace-border bg-workspace-surface/80">
        <button
          onClick={() => {
            onInvestigateEntity && onInvestigateEntity(entity);
            onClose();
          }}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-sm transition-colors"
        >
          <span>Investigate Entity in Chat</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
export default EvidenceDrawer;
