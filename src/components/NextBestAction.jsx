import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, ArrowUpRight, HelpCircle, Check } from 'lucide-react';

export function NextBestAction({ 
  caseData, 
  onApprove, 
  onReject, 
  onRequestEvidence, 
  onEscalate,
  isProcessing
}) {
  const [confirmedAction, setConfirmedAction] = useState(null);

  const c = caseData?.case || {};
  const nba = caseData?.next_best_actions || {};
  const finals = nba.final || [];
  const topAction = finals[0] || { action: "ESCALATE_TO_ANALYST", route: "L1", reason: "Graph anomaly detected" };

  const actionName = topAction.action || "ESCALATE_TO_ANALYST";
  const route = topAction.route || "L1";
  const requiredRole = route === "L2" ? "Senior Fraud Manager" : route === "L1" ? "Lead Fraud Analyst" : "Autonomous (Auto)";
  const reason = topAction.reason || nba.what_changed || "Corroborated multi-hop fraud network requires operational containment.";

  const isApproved = c.approval_status === "APPROVED" || confirmedAction === "APPROVED";
  const isRejected = c.approval_status === "REJECTED" || confirmedAction === "REJECTED";

  const handleApprove = () => {
    setConfirmedAction("APPROVED");
    onApprove && onApprove(actionName, route);
  };

  const handleReject = () => {
    setConfirmedAction("REJECTED");
    onReject && onReject(actionName, "Analyst rejected recommendation after forensic review");
  };

  return (
    <div className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl p-3.5 space-y-3">
      <div className="flex items-center justify-between text-xs font-semibold text-white">
        <span className="uppercase tracking-wider text-[11px] text-slate-400">Next Best Action</span>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${
          route === 'L2' 
            ? 'text-red-400 bg-red-950/40 border-red-800/40' 
            : route === 'L1' 
            ? 'text-amber-400 bg-amber-950/40 border-amber-800/40' 
            : 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40'
        }`}>
          Route: {route}
        </span>
      </div>

      <div>
        <div className="text-sm font-bold text-white flex items-center gap-1.5 font-mono">
          <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
          {actionName.replace(/_/g, ' ')}
        </div>
        <div className="text-[10px] text-slate-400 mt-1 font-mono">
          Authorization: <span className="text-slate-200">{requiredRole}</span>
        </div>
      </div>

      <p className="text-[11px] text-slate-300 leading-relaxed bg-workspace-surface/60 p-2.5 rounded border border-workspace-border/40">
        {reason}
      </p>

      {/* Decision Status if already adjudicated */}
      {isApproved ? (
        <div className="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/50 flex items-center gap-2 text-emerald-400 text-xs">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <div>
            <div className="font-semibold">ACTION APPROVED</div>
            <div className="text-[10px] text-slate-400">Dispatched to core banking ledger.</div>
          </div>
        </div>
      ) : isRejected ? (
        <div className="p-2.5 rounded-lg bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-red-400 text-xs">
          <XCircle className="w-4 h-4 flex-shrink-0" />
          <div>
            <div className="font-semibold">ACTION REJECTED</div>
            <div className="text-[10px] text-slate-400">Recorded in compliance audit ledger.</div>
          </div>
        </div>
      ) : (
        <div className="space-y-1.5 pt-1">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleApprove}
              disabled={isProcessing}
              className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-sm transition-colors"
            >
              <Check className="w-3.5 h-3.5" />
              <span>APPROVE</span>
            </button>

            <button
              onClick={handleReject}
              disabled={isProcessing}
              className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-workspace-surface hover:bg-red-950/40 text-slate-300 hover:text-red-400 border border-workspace-border text-xs transition-colors"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>REJECT</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={onRequestEvidence}
              className="py-1.5 px-2 rounded-lg bg-workspace-cardHover hover:bg-workspace-cardActive text-slate-300 hover:text-white border border-workspace-border text-[11px] transition-colors"
            >
              Request Evidence
            </button>

            <button
              onClick={onEscalate}
              className="flex items-center justify-center gap-1 py-1.5 px-2 rounded-lg bg-workspace-cardHover hover:bg-workspace-cardActive text-slate-300 hover:text-white border border-workspace-border text-[11px] transition-colors"
            >
              <span>Escalate L2</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
export default NextBestAction;
