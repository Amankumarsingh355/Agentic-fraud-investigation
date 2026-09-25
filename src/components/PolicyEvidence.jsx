import React from 'react';
import { BookOpen, Shield, ExternalLink } from 'lucide-react';

export function PolicyEvidence({ caseData, onOpenPolicyModal }) {
  const c = caseData?.case || {};
  const sar = caseData?.sar || {};
  const citations = sar.regulatory_citations || [
    "Bank Fraud Policy v1.0 Section 3 (Rule R6)",
    "FinCEN 31 CFR § 1020.320 (BSA/AML SAR)"
  ];

  return (
    <div className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl p-3.5 space-y-3">
      <div className="flex items-center justify-between text-xs font-semibold text-white">
        <span className="uppercase tracking-wider text-[11px] text-slate-400">Policy & Governance</span>
        <Shield className="w-3.5 h-3.5 text-purple-400" />
      </div>

      <div className="space-y-2">
        <div className="text-[11px] text-slate-300">
          Governing Institutional Directives:
        </div>

        <div className="space-y-1.5">
          {citations.map((cite, idx) => (
            <div 
              key={idx} 
              className="flex items-start gap-2 bg-workspace-surface/60 p-2 rounded border border-workspace-border/40 text-[11px] font-mono text-purple-300"
            >
              <BookOpen className="w-3.5 h-3.5 text-purple-400 flex-shrink-0 mt-0.5" />
              <span className="leading-snug">{cite}</span>
            </div>
          ))}
        </div>

        <button
          onClick={onOpenPolicyModal}
          className="w-full mt-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-workspace-cardHover hover:bg-workspace-cardActive text-slate-300 hover:text-white border border-workspace-border text-xs transition-colors"
        >
          <span>View Bank Fraud Policy v1.0</span>
          <ExternalLink className="w-3 h-3 text-slate-400" />
        </button>
      </div>
    </div>
  );
}
export default PolicyEvidence;
