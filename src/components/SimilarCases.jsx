import React from 'react';
import { Database, ExternalLink, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

export function SimilarCases({ caseData, onSelectCase }) {
  const c = caseData?.case || {};
  const currentPattern = c.pattern || "Syndicate Mule Ring";

  // Precedents from case memory
  const precedents = [
    {
      id: "HHG-001",
      similarity: 94,
      verdict: "fraud",
      pattern: "Syndicate Mule Ring",
      exposure: 77.07,
      matchReason: "Identical shared hardware fingerprint and out-of-region card swipe pattern."
    },
    {
      id: "HHG-005",
      similarity: 88,
      verdict: "fraud",
      pattern: "Hardware Ring 112",
      exposure: 100.07,
      matchReason: "Shared device profile linked across 5+ distinct cardholders in 24h window."
    },
    {
      id: "HHG-012",
      similarity: 62,
      verdict: "legitimate",
      pattern: "Authorized Travel Spend",
      exposure: 30.91,
      matchReason: "Out-of-region swipe confirmed authorized via SMS verification (False Positive)."
    }
  ];

  return (
    <div className="flex-1 flex flex-col h-full bg-workspace-bg overflow-y-auto p-4 max-w-4xl mx-auto w-full space-y-4">
      <div className="flex items-center justify-between border-b border-workspace-border/70 pb-3">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-400" />
            Case Memory & Precedent Retrieval (ChromaDB + TigerGraph)
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Vector similarity matching against closed institutional fraud cases.
          </p>
        </div>

        <span className="text-xs font-mono px-2.5 py-1 rounded bg-workspace-card border border-workspace-border text-slate-300">
          ChromaDB Live
        </span>
      </div>

      <div className="space-y-3">
        {precedents.map((p) => {
          const isFraud = p.verdict === 'fraud';

          return (
            <div 
              key={p.id}
              className="bg-workspace-card/70 border border-workspace-border rounded-xl p-4 space-y-2 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-sm font-bold text-blue-400">{p.id}</span>
                  <span className="text-slate-500">•</span>
                  <span className="text-xs font-semibold text-white">{p.pattern}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-950/40 border border-indigo-800/40 text-indigo-400 font-semibold">
                    {p.similarity}% Vector Match
                  </span>
                  <span className={`font-mono text-[10px] px-2 py-0.5 rounded border font-semibold ${
                    isFraud 
                      ? 'text-red-400 bg-red-950/40 border-red-800/40' 
                      : 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40'
                  }`}>
                    {p.verdict.toUpperCase()}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                {p.matchReason}
              </p>

              <div className="flex items-center justify-between pt-2 border-t border-workspace-border/40 text-[11px] font-mono">
                <span className="text-slate-400">
                  Exposure: <strong className="text-white">${p.exposure.toFixed(2)} USD</strong>
                </span>

                <button
                  onClick={() => onSelectCase && onSelectCase(p.id)}
                  className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <span>Load Case Context</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
export default SimilarCases;
