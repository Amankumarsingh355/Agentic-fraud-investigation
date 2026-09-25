import React, { useState, useEffect } from 'react';
import { History, CheckCircle2, Clock, Shield, AlertTriangle, ArrowRight } from 'lucide-react';

export function CaseTimeline({ caseId }) {
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    fetch(`/api/investigations/${caseId}/timeline`)
      .then(res => res.json())
      .then(data => {
        if (data && data.timeline) {
          setTimelineEvents(data.timeline);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading timeline:", err);
        setLoading(false);
      });
  }, [caseId]);

  const defaultEvents = [
    { time: "19:41:02", title: "Investigation Started", stage: "INGESTION", desc: "Flagged transaction ingested following anomaly detection trigger." },
    { time: "19:41:04", title: "Transaction Catalog Retrieved", stage: "CATALOG", desc: "Transaction metadata, customer history, and billing region extracted." },
    { time: "19:41:06", title: "TigerGraph Multi-Hop Investigation Completed", stage: "EVIDENCE", desc: "2-hop and 3-hop traversal identified connected entities." },
    { time: "19:41:09", title: "Shared Device Nexus Discovered", stage: "EVIDENCE", desc: "Device_99 linked across multiple cardholder accounts." },
    { time: "19:41:12", title: "Historical Case Vector Matched", stage: "MEMORY", desc: "Precedent match with Case #HHG-001 (Syndicate Mule Ring) with 94% similarity." },
    { time: "19:41:15", title: "Risk & Uncertainty Decoupled", stage: "EVALUATION", desc: "Fraud probability 0.94, Confidence 0.87, Uncertainty LOW." },
    { time: "19:41:18", title: "Policy Rule Verification", stage: "GOVERNANCE", desc: "Grounded under Bank Fraud Policy v1.0 (Rule R6). FinCEN SAR threshold verified." },
    { time: "19:41:22", title: "Decision Formulated & Audited", stage: "DECISION", desc: "4-step CoT audit passed. Next-best-action: BLOCK_CARD (Route: L1)." }
  ];

  const events = timelineEvents.length > 0 ? timelineEvents.map((e, idx) => ({
    time: e.time || `19:41:${String(idx * 3 + 2).padStart(2, '0')}`,
    title: e.title || e.stage || `Stage ${e.step}`,
    stage: e.stage || "EVIDENCE",
    desc: e.detail || e.claim || (e.actions ? `Actions: ${e.actions.join(', ')}` : "Event logged in immutable audit ledger.")
  })) : defaultEvents;

  return (
    <div className="flex-1 flex flex-col h-full bg-workspace-bg overflow-y-auto p-4 max-w-4xl mx-auto w-full space-y-4">
      <div className="flex items-center justify-between border-b border-workspace-border/70 pb-3">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-emerald-400" />
            Immutable Audit Trail & Investigation Timeline
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Chronological audit events recorded during autonomous investigation of {caseId}.
          </p>
        </div>

        <span className="text-xs font-mono px-2.5 py-1 rounded bg-workspace-card border border-workspace-border text-slate-300">
          {events.length} Events Logged
        </span>
      </div>

      {/* Timeline Steps */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-workspace-border">
        {events.map((ev, i) => (
          <div key={i} className="relative flex items-start gap-4">
            {/* Timeline Dot */}
            <div className="absolute -left-6 top-1 w-3.5 h-3.5 rounded-full bg-workspace-surface border-2 border-emerald-400 flex items-center justify-center">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </div>

            {/* Event Box */}
            <div className="flex-1 bg-workspace-card/70 border border-workspace-border rounded-xl p-3.5 shadow-sm space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold text-white">{ev.title}</span>
                <span className="font-mono text-[10px] text-slate-400 bg-workspace-surface px-1.5 py-0.5 rounded border border-workspace-border/50">
                  {ev.time}
                </span>
              </div>

              <div className="text-xs text-slate-300 font-sans leading-relaxed">
                {ev.desc}
              </div>

              <div className="pt-1 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                Stage: <span className="text-blue-400">{ev.stage}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
export default CaseTimeline;
