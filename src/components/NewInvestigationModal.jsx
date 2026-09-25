import React, { useState } from 'react';
import { X, Search, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

export function NewInvestigationModal({ isOpen, onClose, onStartInvestigation, benchmarkCases = [] }) {
  const [txnId, setTxnId] = useState('');
  const [triggerType, setTriggerType] = useState('risk_score');
  const [triggerText, setTriggerText] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!txnId.trim()) return;
    onStartInvestigation({
      flagged_txn_id: parseInt(txnId.trim(), 10),
      trigger_type: triggerType,
      trigger_text: triggerText || `Ad-hoc investigation on TXN #${txnId}`
    });
    onClose();
  };

  const handleSelectBenchmark = (b) => {
    onStartInvestigation({
      case_id: b.case_id,
      flagged_txn_id: parseInt(b.flagged_txn_id, 10),
      trigger_type: b.trigger_type,
      trigger_text: b.trigger_text
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-lg bg-workspace-surface border border-workspace-border rounded-2xl shadow-subtle-elevated overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-workspace-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Start New Fraud Investigation</h3>
              <p className="text-[11px] text-slate-400">Launch the 11-agent pipeline across TigerGraph & Case Memory</p>
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
              Flagged Transaction ID
            </label>
            <input
              type="number"
              placeholder="e.g. 3514030"
              value={txnId}
              onChange={(e) => setTxnId(e.target.value)}
              className="w-full bg-workspace-card border border-workspace-border rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Trigger Type
              </label>
              <select
                value={triggerType}
                onChange={(e) => setTriggerType(e.target.value)}
                className="w-full bg-workspace-card border border-workspace-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-sans"
              >
                <option value="risk_score">High Model Score (ML)</option>
                <option value="velocity_spike">Velocity Anomaly Spike</option>
                <option value="customer_report">Customer Dispute / Denial</option>
                <option value="hardware_ring">Hardware Ring Nexus</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Trigger Context (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Out of region POS swipe"
                value={triggerText}
                onChange={(e) => setTriggerText(e.target.value)}
                className="w-full bg-workspace-card border border-workspace-border rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={!txnId.trim()}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Launch 11-Agent Investigation</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Benchmark Selectors */}
        <div className="px-4 pb-4 border-t border-workspace-border/50 pt-3">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Or Select an Official Benchmark Case:
          </div>

          <div className="grid grid-cols-2 gap-1.5 max-h-36 overflow-y-auto pr-1">
            {benchmarkCases.slice(0, 8).map((b) => (
              <button
                key={b.case_id}
                onClick={() => handleSelectBenchmark(b)}
                className="text-left p-1.5 rounded bg-workspace-card hover:bg-workspace-cardHover border border-workspace-border/60 text-xs transition-colors flex items-center justify-between"
              >
                <span className="font-mono font-semibold text-blue-400">{b.case_id}</span>
                <span className="text-[10px] text-slate-400 truncate max-w-[120px]">{b.trigger_text}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
export default NewInvestigationModal;
