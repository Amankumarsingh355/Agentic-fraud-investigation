import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Check, 
  X, 
  AlertTriangle, 
  Clock, 
  UserCheck, 
  CheckCircle2, 
  XCircle,
  FileText
} from 'lucide-react';

export function ApprovalCenter({ onSelectCase }) {
  const [approvalsData, setApprovalsData] = useState({ pending: [], history: [] });
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState(null);

  const fetchApprovals = () => {
    setLoading(true);
    fetch('/api/approvals')
      .then(res => res.json())
      .then(data => {
        setApprovalsData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading approvals:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleAction = (caseId, action, decision) => {
    setSubmittingId(caseId);
    const endpoint = decision === 'approve' 
      ? `/api/investigations/${caseId}/approve` 
      : `/api/investigations/${caseId}/reject`;

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonBodyHelper(caseId, action, decision)
    })
      .then(res => res.json())
      .then(() => {
        fetchApprovals();
        setSubmittingId(null);
      })
      .catch(() => setSubmittingId(null));
  };

  const jsonBodyHelper = (caseId, action, decision) => {
    return JSON.stringify({
      case_id: caseId,
      action: action,
      analyst: "Senior Fraud Analyst L2",
      route: "L1",
      reason: decision === 'approve' ? "Approved by analyst" : "Rejected by analyst"
    });
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-workspace-bg overflow-y-auto p-4 max-w-4xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-workspace-border/70 pb-3">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-amber-400" />
            Human-in-the-Loop Governance & Approval Center
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Adjudicate high-consequence operational restrictions (L1 Team Lead / L2 Fraud Manager).
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          className="text-xs font-mono px-3 py-1.5 rounded-lg bg-workspace-card hover:bg-workspace-cardHover border border-workspace-border text-slate-300 transition-colors"
        >
          Refresh Queue
        </button>
      </div>

      {/* Pending Approvals */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
          <span>Pending Analyst Decisions ({approvalsData.pending.length})</span>
          <span className="text-[10px] text-amber-400 font-mono">Requires L1/L2 Authorization</span>
        </div>

        {approvalsData.pending.length === 0 ? (
          <div className="bg-workspace-card/50 rounded-xl p-8 border border-workspace-border/60 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <div className="text-sm font-semibold text-white">Queue Cleared</div>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              No pending L1/L2 actions currently requiring human sign-off. All active cases are either autonomous or adjudicated.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {approvalsData.pending.map((item) => (
              <div 
                key={item.case_id}
                className="bg-workspace-card/80 border border-workspace-border rounded-xl p-4 space-y-3 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onSelectCase && onSelectCase(item.case_id)}
                      className="font-mono text-sm font-bold text-blue-400 hover:underline"
                    >
                      {item.case_id}
                    </button>
                    <span className="text-slate-500">•</span>
                    <span className="text-xs font-semibold text-white">
                      Recommended: {item.action.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <span className="text-xs font-mono px-2 py-0.5 rounded border border-amber-800/50 bg-amber-950/40 text-amber-400">
                    Route: {item.route}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                  <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
                    <span className="text-slate-400 text-[10px] block">Risk Score:</span>
                    <span className="text-red-400 font-bold">{Math.round(item.risk_score * 100)}%</span>
                  </div>
                  <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
                    <span className="text-slate-400 text-[10px] block">Confidence:</span>
                    <span className="text-slate-200">{Math.round(item.confidence * 100)}%</span>
                  </div>
                  <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
                    <span className="text-slate-400 text-[10px] block">Evidence Sufficiency:</span>
                    <span className="text-indigo-400">{Math.round(item.evidence_completeness * 100)}%</span>
                  </div>
                  <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
                    <span className="text-slate-400 text-[10px] block">Required Role:</span>
                    <span className="text-slate-200 truncate">{item.required_role}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 bg-workspace-surface/50 p-2.5 rounded border border-workspace-border/40">
                  {item.reason}
                </p>

                <div className="flex items-center justify-between pt-1">
                  <div className="text-[11px] text-slate-400 font-mono">
                    Policy Grounding: <span className="text-purple-300 font-semibold">{item.policy_rule}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleAction(item.case_id, item.action, 'approve')}
                      disabled={submittingId === item.case_id}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-sm transition-colors"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>APPROVE</span>
                    </button>

                    <button
                      onClick={() => handleAction(item.case_id, item.action, 'reject')}
                      disabled={submittingId === item.case_id}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-workspace-surface hover:bg-red-950/40 text-slate-300 hover:text-red-400 border border-workspace-border text-xs transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                      <span>REJECT</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* History */}
      <div className="space-y-3 pt-2">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Adjudication History & Audit Ledger ({approvalsData.history.length})
        </div>

        <div className="bg-workspace-card/70 border border-workspace-border rounded-xl divide-y divide-workspace-border/50 overflow-hidden">
          {approvalsData.history.map((rec, i) => (
            <div key={i} className="p-3 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${rec.status === 'APPROVED' ? 'bg-emerald-400' : 'bg-red-400'}`} />
                <button
                  onClick={() => onSelectCase && onSelectCase(rec.case_id)}
                  className="font-bold text-slate-200 hover:text-blue-400"
                >
                  {rec.case_id}
                </button>
                <span className="text-slate-400">•</span>
                <span className="text-slate-300">{rec.action}</span>
              </div>

              <div className="flex items-center gap-3 text-slate-400 text-[11px]">
                <span>{rec.analyst}</span>
                <span className="text-slate-600">|</span>
                <span className="text-slate-400">{rec.timestamp?.split('T')[1]?.split('.')[0] || '19:42:31'}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  rec.status === 'APPROVED' ? 'text-emerald-400 bg-emerald-950/40' : 'text-red-400 bg-red-950/40'
                }`}>
                  {rec.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
export default ApprovalCenter;
