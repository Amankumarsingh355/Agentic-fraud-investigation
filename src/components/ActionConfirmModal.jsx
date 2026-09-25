import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, Snowflake, Upload, CheckCircle2, Lock } from 'lucide-react';

export const ActionConfirmModal = ({ actionType, onClose, onConfirm }) => {
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const isFreeze = actionType === 'FREEZE';

  const handleExecute = () => {
    setConfirmed(true);
    setTimeout(() => {
      onConfirm && onConfirm();
      onClose();
    }, 1800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-md border border-red-500/70 bg-[#080811] rounded-lg p-5 shadow-[0_0_35px_rgba(255,51,75,0.4)] overflow-hidden font-mono"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top danger line */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyber-crimson to-transparent" />

        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-cyber-border">
          <div className="flex items-center gap-2.5">
            <div className={`w-8 h-8 rounded border flex items-center justify-center ${
              isFreeze ? 'border-red-500/70 bg-red-950/40 text-cyber-crimson' : 'border-cyber-cyan bg-cyan-950/40 text-cyber-cyan'
            }`}>
              {isFreeze ? <Snowflake className="w-4 h-4" /> : <Upload className="w-4 h-4" />}
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wider">
                {isFreeze ? 'MANDATORY ACCOUNT FREEZE' : 'ESCALATE INVESTIGATION'}
              </h3>
              <span className="text-[10px] text-red-400">
                GOVERNANCE PROTOCOL // BANK FRAUD POLICY v1.0 (RULE R6)
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {confirmed ? (
          <div className="py-6 flex flex-col items-center justify-center text-center gap-3">
            <CheckCircle2 className="w-12 h-12 text-cyber-emerald animate-bounce" />
            <h4 className="text-base font-bold text-white tracking-wider">
              {isFreeze ? 'ACCOUNTS FROZEN SUCCESSFULLY' : 'CASE ESCALATED TO L2 QUEUE'}
            </h4>
            <p className="text-xs text-slate-300">
              Cryptographic lock applied to USER_101 & USER_882. FinCEN audit docket updated.
            </p>
          </div>
        ) : (
          <>
            {/* Modal Body */}
            <div className="space-y-3 text-xs mb-5">
              <div className="p-3 rounded bg-red-950/20 border border-red-500/40 text-slate-200">
                <div className="flex items-center gap-1.5 text-cyber-crimson font-bold text-xs mb-1">
                  <ShieldAlert className="w-4 h-4 shrink-0" />
                  <span>SIMULATED DEFENSIVE ACTION:</span>
                </div>
                <p className="text-[11px] leading-relaxed">
                  {isFreeze 
                    ? "Target transaction $15,000 will be permanently stopped. Debit/Credit cards attached to USER_101 and USER_882 will be suspended. All outbound wires locked."
                    : "Case #TG-CASE-2026-8819 will be expedited to Tier-3 human forensic fraud team with full TigerGraph graph trace dossier attached."
                  }
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="p-2 rounded bg-[#0D1522] border border-cyber-border">
                  <span className="text-slate-400 block">PRIMARY TARGET:</span>
                  <span className="text-white font-bold">USER_101 (Victim)</span>
                </div>
                <div className="p-2 rounded bg-[#0D1522] border border-cyber-border">
                  <span className="text-slate-400 block">SYNDICATE MULE:</span>
                  <span className="text-cyber-crimson font-bold">USER_882 (Flagged)</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-2 pt-2 border-t border-cyber-border">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded border border-cyber-border bg-slate-900 text-xs text-slate-300 hover:text-white transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={handleExecute}
                className={`px-5 py-2 rounded text-xs font-bold tracking-wider uppercase transition-all shadow-md active:scale-95 flex items-center gap-2 ${
                  isFreeze 
                    ? 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)]'
                    : 'bg-cyan-600 hover:bg-cyan-500 text-black font-extrabold shadow-[0_0_15px_rgba(0,229,255,0.4)]'
                }`}
              >
                <Lock className="w-3.5 h-3.5" />
                <span>CONFIRM {isFreeze ? 'FREEZE' : 'ESCALATION'}</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
