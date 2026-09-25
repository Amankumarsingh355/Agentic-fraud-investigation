import React from 'react';
import { DollarSign, Clock, CreditCard, User, Globe, AlertTriangle, ShieldCheck } from 'lucide-react';

export function CaseSummary({ caseData }) {
  const c = caseData?.case || {};
  const sar = caseData?.sar || {};

  const exposure = c.exposure_usd !== undefined ? c.exposure_usd : 77.07;
  const txnId = c.first_suspicious_txn_id || '3514030';
  const pattern = c.pattern || 'Syndicate Mule Ring';
  const verdict = c.verdict || 'fraud';
  const connectedCards = c.connected_card_ids || ['4242-xxxx'];
  const connectedDevices = c.connected_device_profiles || ['Android 11 | Device_99'];

  return (
    <div className="bg-workspace-card/70 border border-workspace-border/70 rounded-xl p-3.5 space-y-3">
      <div className="flex items-center justify-between text-xs font-semibold text-white">
        <span className="uppercase tracking-wider text-[11px] text-slate-400">Case Overview</span>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/50 border border-blue-800/40 text-blue-400">
          TX #{txnId}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
        <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
          <div className="text-[10px] text-slate-400">Financial Exposure</div>
          <div className="text-sm font-bold text-white mt-0.5">${Number(exposure).toFixed(2)}</div>
        </div>

        <div className="bg-workspace-surface/60 p-2 rounded border border-workspace-border/40">
          <div className="text-[10px] text-slate-400">Detected Pattern</div>
          <div className="text-xs font-semibold text-amber-300 mt-1 truncate" title={pattern}>
            {pattern}
          </div>
        </div>
      </div>

      {/* Connected Entities */}
      <div className="space-y-1.5 text-xs">
        <div className="flex items-center justify-between text-slate-400 text-[11px]">
          <span className="flex items-center gap-1.5">
            <CreditCard className="w-3.5 h-3.5 text-slate-400" /> Connected Cards:
          </span>
          <span className="font-mono text-slate-200">{connectedCards.length}</span>
        </div>

        <div className="flex items-center justify-between text-slate-400 text-[11px]">
          <span className="flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-slate-400" /> Device Profiles:
          </span>
          <span className="font-mono text-slate-200">{connectedDevices.length}</span>
        </div>

        <div className="flex items-center justify-between text-slate-400 text-[11px]">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-400" /> FinCEN SAR:
          </span>
          <span className={`font-mono font-semibold ${sar.file ? 'text-red-400' : 'text-slate-400'}`}>
            {sar.file ? 'MANDATORY' : 'EXEMPT'}
          </span>
        </div>
      </div>
    </div>
  );
}
export default CaseSummary;
