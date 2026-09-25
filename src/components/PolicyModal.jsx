import React from 'react';
import { X, Shield, BookOpen, CheckCircle2 } from 'lucide-react';

export function PolicyModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const policyRules = [
    { rule: "Rule R1", title: "Verify Before You Block on a Weak Signal", text: "If an investigation rests on a single signal and assessed fraud probability is below 0.70, recommend VERIFY_WITH_CUSTOMER or STEP_UP_AUTH prior to any card block." },
    { rule: "Rule R2", title: "Customer Denies the Transaction", text: "When a cardholder denies authorizing the transaction, recommend BLOCK_CARD and CREATE_CASE. Recommend FILE_REPORT if exposure exceeds $1,000 or links to shared hardware/syndicate." },
    { rule: "Rule R3", title: "Customer Confirms the Transaction", text: "When a cardholder confirms authorizing the transaction, recommend CLOSE_NO_FRAUD and record confirmation." },
    { rule: "Rule R4", title: "Unresponsive Cardholder (No Reply in 24h)", text: "If no response within 24h, recommend MONITOR_CARD and DECLINE_TRANSACTION. If exposure > $500, recommend ESCALATE_TO_ANALYST." },
    { rule: "Rule R5", title: "Card Testing Sequence", text: "Three or more small online authorizations under $5.00 followed by a larger transaction: recommend DECLINE_TRANSACTION and STEP_UP_AUTH. If > $100 cleared, recommend BLOCK_CARD." },
    { rule: "Rule R6", title: "Shared Origin & Syndicate Detection", text: "When multiple cards exhibit unauthorized activity from same device profile or IP: identify shared entity, recommend CREATE_CASE, FILE_REPORT, and MONITOR_CONNECTED_CARDS." },
    { rule: "Rule R7", title: "Disputed Established Recurring Activity", text: "When a cardholder disputes a recurring subscription: recommend CREATE_CASE, VERIFY_WITH_CUSTOMER, and WARN_CUSTOMER. Do not block the card." },
    { rule: "Rule R8", title: "Escalation Under Ambiguity", text: "If assessed verdict is uncertain and exposure exceeds $500, or evidence has contradictions: recommend ESCALATE_TO_ANALYST." },
    { rule: "Rule R9", title: "Undocumented Coordinated Patterns", text: "When activity deviates from known typologies but graph evidence indicates coordinated exploitation: recommend CREATE_CASE, FILE_REPORT, and ESCALATE_TO_ANALYST." },
    { rule: "Rule R10", title: "Restraint on Total Account Blocking", text: "Never recommend BLOCK_ALL_CARDS unless at least two distinct cards belonging to customer show confirmed fraud or digital credentials confirmed compromised." }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-workspace-surface border border-workspace-border rounded-2xl shadow-subtle-elevated overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-4 border-b border-workspace-border flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-purple-600/20 text-purple-400 border border-purple-500/30">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Bank Fraud Policy v1.0</h3>
              <p className="text-[11px] text-slate-400">Institutional Governance & Decision Authority Matrix</p>
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
        <div className="p-4 overflow-y-auto space-y-3 font-sans text-xs">
          <div className="bg-purple-950/30 border border-purple-800/40 p-3 rounded-xl text-purple-200 text-xs">
            <strong>Section 4 — FinCEN SAR Statutory Reporting:</strong> Mandatory filing for transactions involving at least $1,000 in potential fraud loss to the institution or associated with multi-account syndicate hardware networks.
          </div>

          <div className="space-y-2">
            {policyRules.map((r, i) => (
              <div key={i} className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl p-3 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-purple-400">{r.rule}</span>
                  <span className="text-white font-semibold text-xs">{r.title}</span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {r.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default PolicyModal;
