import React from 'react';
import { AlertCircle, HelpCircle, CheckCircle2, ArrowRight } from 'lucide-react';

export function UncertaintyPanel({ caseData, onRequestEvidence }) {
  const c = caseData?.case || {};
  const evidenceRequests = caseData?.evidence_requests || [];

  const confidence = c.confidence_score !== undefined ? c.confidence_score : 0.87;
  const completeness = c.evidence_completeness !== undefined ? c.evidence_completeness : 0.82;
  const uncertainty = c.uncertainty_level || (confidence > 0.8 ? 'LOW' : confidence > 0.5 ? 'MEDIUM' : 'HIGH');
  const isHighUncertainty = uncertainty === 'HIGH' || completeness < 0.60;

  const defaultMissingEvidence = [
    { title: "Customer SMS Transaction Validation", desc: "Out-of-band inquiry via SMS/app push" },
    { title: "Hardware Device Ownership Confirmation", desc: "Verification of Android device IMEI / profile" }
  ];

  const items = evidenceRequests.length > 0 
    ? evidenceRequests.map(r => ({ title: r.type || "Evidence Ingestion", desc: r.description || r.type }))
    : defaultMissingEvidence;

  return (
    <div className={`rounded-xl p-3.5 space-y-3 border transition-colors ${
      isHighUncertainty 
        ? 'bg-amber-950/20 border-amber-800/50' 
        : 'bg-workspace-card/70 border-workspace-border/70'
    }`}>
      <div className="flex items-center justify-between text-xs font-semibold text-white">
        <span className="uppercase tracking-wider text-[11px] text-slate-400">Uncertainty & Evidence</span>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${
          uncertainty === 'LOW' 
            ? 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40' 
            : 'text-amber-400 bg-amber-950/40 border-amber-800/40'
        }`}>
          {uncertainty}
        </span>
      </div>

      {isHighUncertainty ? (
        <div className="space-y-2">
          <div className="flex items-start gap-2 text-amber-400 text-xs">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div className="font-semibold">ADDITIONAL EVIDENCE REQUIRED</div>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            The investigation currently has insufficient evidence to execute irreversible account restrictions under Policy Rule R1.
          </p>

          <div className="space-y-1.5 pt-1">
            <div className="text-[10px] uppercase font-semibold text-slate-400">Missing Evidence:</div>
            {items.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1.5 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                <span>{item.title}</span>
              </div>
            ))}
          </div>

          <button
            onClick={onRequestEvidence}
            className="w-full mt-2 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs shadow-sm transition-colors"
          >
            <span>Request Additional Evidence</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-[11px] text-slate-300 leading-relaxed">
            Evidence sufficiency is established at <strong className="text-white">{Math.round(completeness * 100)}%</strong>. 
            Multi-hop graph evidence corroborates fraud signal without requiring blocking deferrals.
          </p>
          <div className="space-y-1">
            {items.slice(0, 2).map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 text-[11px] text-slate-400">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="truncate">{item.title}</span>
              </div>
            ))}
          </div>

          <button
            onClick={onRequestEvidence}
            className="w-full mt-1 py-1.5 px-3 rounded-lg bg-workspace-cardHover hover:bg-workspace-cardActive text-slate-300 hover:text-white border border-workspace-border text-xs transition-colors"
          >
            Attach Supplementary Evidence
          </button>
        </div>
      )}
    </div>
  );
}
export default UncertaintyPanel;
