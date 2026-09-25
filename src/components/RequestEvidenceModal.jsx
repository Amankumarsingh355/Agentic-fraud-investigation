import React, { useState } from 'react';
import { X, HelpCircle, CheckCircle2, ShieldCheck, ArrowRight, RefreshCw } from 'lucide-react';

export function RequestEvidenceModal({ isOpen, onClose, caseId, onSubmitEvidence, isSubmitting }) {
  const [evidenceType, setEvidenceType] = useState('customer_sms');
  const [customerResponse, setCustomerResponse] = useState('denied_fraud');
  const [notes, setNotes] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitEvidence({
      case_id: caseId,
      evidence_type: evidenceType,
      response: customerResponse,
      notes: notes
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-md bg-workspace-surface border border-workspace-border rounded-2xl shadow-subtle-elevated overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-workspace-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-600/20 text-amber-400 border border-amber-500/30">
              <HelpCircle className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Ingest Additional Evidence</h3>
              <p className="text-[11px] text-slate-400">Trigger stateful re-investigation loop for {caseId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-workspace-card transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Evidence Channel / Verification Type
            </label>
            <select
              value={evidenceType}
              onChange={(e) => setEvidenceType(e.target.value)}
              className="w-full bg-workspace-card border border-workspace-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-sans"
            >
              <option value="customer_sms">Out-of-band Customer SMS Validation</option>
              <option value="3ds_verification">3D Secure (3DS) Biometric Step-Up</option>
              <option value="device_telemetry">Hardware Device Ownership Check</option>
              <option value="merchant_inquiry">Merchant Fulfillment Confirmation</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Simulated Customer / Telemetry Outcome
            </label>
            <div className="space-y-1.5 text-xs">
              <label className="flex items-center gap-2 p-2 rounded-lg bg-workspace-card border border-workspace-border cursor-pointer hover:bg-workspace-cardHover">
                <input
                  type="radio"
                  name="response"
                  value="denied_fraud"
                  checked={customerResponse === 'denied_fraud'}
                  onChange={(e) => setCustomerResponse(e.target.value)}
                  className="text-red-500 focus:ring-0"
                />
                <div>
                  <div className="text-red-400 font-medium font-mono">DENIED FRAUD</div>
                  <div className="text-[10px] text-slate-400">Cardholder explicitly denies authorizing charge (Rule R2).</div>
                </div>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg bg-workspace-card border border-workspace-border cursor-pointer hover:bg-workspace-cardHover">
                <input
                  type="radio"
                  name="response"
                  value="confirmed_authorized"
                  checked={customerResponse === 'confirmed_authorized'}
                  onChange={(e) => setCustomerResponse(e.target.value)}
                  className="text-emerald-500 focus:ring-0"
                />
                <div>
                  <div className="text-emerald-400 font-medium font-mono">CONFIRMED AUTHORIZED</div>
                  <div className="text-[10px] text-slate-400">Cardholder confirms legitimate purchase (Rule R3).</div>
                </div>
              </label>

              <label className="flex items-center gap-2 p-2 rounded-lg bg-workspace-card border border-workspace-border cursor-pointer hover:bg-workspace-cardHover">
                <input
                  type="radio"
                  name="response"
                  value="no_reply"
                  checked={customerResponse === 'no_reply'}
                  onChange={(e) => setCustomerResponse(e.target.value)}
                  className="text-amber-500 focus:ring-0"
                />
                <div>
                  <div className="text-amber-400 font-medium font-mono">UNRESPONSIVE / TIMEOUT</div>
                  <div className="text-[10px] text-slate-400">Zero response within 24h window (Rule R4).</div>
                </div>
              </label>
            </div>
          </div>

          <div className="bg-workspace-card p-2.5 rounded-lg border border-workspace-border text-[11px] font-mono text-slate-300">
            <div className="text-slate-400 mb-0.5">Estimated Impact on Uncertainty:</div>
            <div className="text-emerald-400 font-semibold">
              Increases confidence to ~92% • Resolves uncertainty state
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-sm transition-colors"
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Re-evaluating Investigation...</span>
              </>
            ) : (
              <>
                <span>Submit Evidence & Re-investigate</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
export default RequestEvidenceModal;
