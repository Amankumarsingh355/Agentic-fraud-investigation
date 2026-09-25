import React, { useState } from 'react';
import { 
  X, 
  ShieldAlert, 
  Lock, 
  Send, 
  PlusCircle, 
  CheckCircle2, 
  AlertTriangle,
  FileCheck,
  Building2
} from 'lucide-react';

export function PegaActionModal({ 
  isOpen, 
  actionType, 
  caseData, 
  selectedEntity, 
  onClose, 
  onConfirm 
}) {
  const [confirmed, setConfirmed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const c = caseData?.case || {};
  const sar = caseData?.sar || {};
  const caseId = c.case_id || 'HHG-001';
  const entityLabel = selectedEntity?.label || selectedEntity?.id || `Case ${caseId}`;
  const amount = Number(c.exposure_usd || 77.07).toFixed(2);

  const handleExecute = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setConfirmed(true);
      setTimeout(() => {
        onConfirm && onConfirm(actionType, selectedEntity);
        setConfirmed(false);
        onClose();
      }, 1500);
    }, 800);
  };

  const getModalConfig = () => {
    switch (actionType) {
      case 'SAR':
        return {
          title: 'SUBMIT FINCEN SAR REGULATORY FILING',
          subtitle: 'Bank Secrecy Act / FinCEN Form 111 Regulatory Transmission',
          icon: Send,
          iconColor: 'text-[#10B981]',
          borderColor: 'border-[#10B981]/60',
          badgeText: 'REGULATORY COMPLIANCE',
          buttonText: 'Authorize & Transmit SAR',
          description: `You are filing an official Suspicious Activity Report (SAR) for Case ${caseId}. Total exposure of $${amount} USD and multi-hop forensic graph findings will be submitted to the FinCEN regulatory docket under Bank Fraud Policy v1.0 [Rule R6].`
        };
      case 'BLOCK':
        return {
          title: 'INSTITUTIONAL SANDBOX CARD/USER SUSPENSION',
          subtitle: 'Payment Rail Defense & Authorization Halt Protocol',
          icon: Lock,
          iconColor: 'text-red-400',
          borderColor: 'border-red-600/60',
          badgeText: 'DEFENSIVE ACTION',
          buttonText: 'Execute Sandbox Block',
          description: `Initiating defensive block for entity "${entityLabel}". Payment card authorizations will be halted and the card state will transition from ACTIVE to BLOCKED in the institutional payment gateway.`
        };
      case 'NEW_CASE':
      default:
        return {
          title: 'INITIALIZE NEW INVESTIGATION CASE',
          subtitle: 'Autonomous Agent Investigation Docket Creation',
          icon: PlusCircle,
          iconColor: 'text-emerald-400',
          borderColor: 'border-emerald-600/60',
          badgeText: 'CASE LIFECYCLE',
          buttonText: 'Create Case Docket',
          description: `Create a dedicated investigation record for target entity "${entityLabel}". Graph traversal and 11-agent forensic synthesis will be scheduled immediately.`
        };
    }
  };

  const config = getModalConfig();
  const Icon = config.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div 
        className={`relative w-full max-w-lg bg-[#181818] border ${config.borderColor} rounded-lg p-5 shadow-2xl font-mono text-xs`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#2A2A2A]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded bg-[#121212] border border-[#2A2A2A] flex items-center justify-center shrink-0">
              <Icon className={`w-4 h-4 ${config.iconColor}`} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                {config.title}
              </h3>
              <span className="text-[10px] text-[#A0A0A0]">
                {config.subtitle}
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded text-[#A0A0A0] hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {confirmed ? (
          <div className="py-6 flex flex-col items-center justify-center text-center gap-2">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 animate-bounce" />
            <h4 className="text-sm font-bold text-white">ACTION EXECUTED IN SANDBOX</h4>
            <p className="text-xs text-[#A0A0A0]">
              Audit trail logged with immutable cryptographic nonce.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Description Card */}
            <div className="p-3 rounded bg-[#121212] border border-[#2A2A2A] space-y-2">
              <div className="flex items-center gap-1.5 text-white font-bold text-xs">
                <AlertTriangle className="w-4 h-4 text-[#10B981] shrink-0" />
                <span>CONFIRMATION REQUIRED</span>
              </div>
              <p className="text-[11px] text-[#A0A0A0] leading-relaxed">
                {config.description}
              </p>
            </div>

            {/* Entity Key/Values */}
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-[#121212] border border-[#2A2A2A]">
                <span className="text-[#666666] block text-[10px] uppercase">Target Entity:</span>
                <span className="text-white font-bold truncate block">{entityLabel}</span>
              </div>
              <div className="p-2 rounded bg-[#121212] border border-[#2A2A2A]">
                <span className="text-[#666666] block text-[10px] uppercase">Associated Exposure:</span>
                <span className="text-[#10B981] font-bold block">${amount} USD</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-2 pt-3 border-t border-[#2A2A2A]">
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="px-3 py-1.5 rounded bg-[#2A2A2A] hover:bg-[#333333] text-slate-300 font-mono text-xs transition-colors"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleExecute}
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-[#10B981] hover:bg-[#34D399] text-black font-mono font-bold text-xs shadow-[0_0_12px_rgba(16,185,129,0.35)] transition-all"
              >
                {isSubmitting ? (
                  <>
                    <span className="w-3 h-3 border-2 border-black border-t-transparent rounded-full animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>{config.buttonText}</span>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PegaActionModal;
