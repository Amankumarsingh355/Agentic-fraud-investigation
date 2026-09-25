import React from 'react';
import { AlertTriangle, ShieldCheck, Gauge } from 'lucide-react';

export function RiskPanel({ caseData }) {
  const c = caseData?.case || {};

  const fraudProb = c.fraud_probability !== undefined ? c.fraud_probability : 0.94;
  const confidence = c.confidence_score !== undefined ? c.confidence_score : 0.87;
  const evidenceComp = c.evidence_completeness !== undefined ? c.evidence_completeness : 0.82;
  const uncertainty = c.uncertainty_level || (confidence > 0.8 ? 'LOW' : confidence > 0.5 ? 'MEDIUM' : 'HIGH');

  const riskPct = Math.round(fraudProb * 100);
  const confPct = Math.round(confidence * 100);
  const evidPct = Math.round(evidenceComp * 100);

  const getRiskColor = (prob) => {
    if (prob >= 0.75) return 'text-red-400 bg-red-950/40 border-red-800/40';
    if (prob >= 0.40) return 'text-amber-400 bg-amber-950/40 border-amber-800/40';
    return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';
  };

  const getUncertaintyColor = (lvl) => {
    if (lvl === 'LOW') return 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40';
    if (lvl === 'MEDIUM') return 'text-amber-400 bg-amber-950/40 border-amber-800/40';
    return 'text-red-400 bg-red-950/40 border-red-800/40';
  };

  return (
    <div className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl p-3.5 space-y-3">
      <div className="flex items-center justify-between text-xs font-semibold text-white">
        <span className="uppercase tracking-wider text-[11px] text-slate-400">Risk & Confidence</span>
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${getRiskColor(fraudProb)} font-bold`}>
          {riskPct}% RISK
        </span>
      </div>

      {/* Progress Bars */}
      <div className="space-y-2.5 text-xs">
        {/* Risk Probability */}
        <div>
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span>Fraud Probability</span>
            <span className="font-mono text-white font-medium">{riskPct}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-workspace-surface overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                riskPct >= 75 ? 'bg-red-500' : riskPct >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${riskPct}%` }}
            />
          </div>
        </div>

        {/* Confidence Score */}
        <div>
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span>Confidence Score</span>
            <span className="font-mono text-white font-medium">{confPct}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-workspace-surface overflow-hidden">
            <div 
              className="h-full rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${confPct}%` }}
            />
          </div>
        </div>

        {/* Evidence Sufficiency */}
        <div>
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span>Evidence Completeness</span>
            <span className="font-mono text-white font-medium">{evidPct}%</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-workspace-surface overflow-hidden">
            <div 
              className="h-full rounded-full bg-indigo-500 transition-all duration-500"
              style={{ width: `${evidPct}%` }}
            />
          </div>
        </div>

        {/* Uncertainty Level */}
        <div className="pt-2 border-t border-workspace-border/50 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">Uncertainty State:</span>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${getUncertaintyColor(uncertainty)}`}>
            {uncertainty} UNCERTAINTY
          </span>
        </div>
      </div>
    </div>
  );
}
export default RiskPanel;
