import React, { useState } from 'react';
import { 
  X, 
  Send, 
  Ban, 
  Download, 
  MapPin, 
  AlertTriangle, 
  ArrowUpRight, 
  Smartphone, 
  CreditCard, 
  Users, 
  User,
  ShieldAlert,
  Copy,
  Check
} from 'lucide-react';

export function PegaEntityDrawer({ 
  selectedEntity, 
  caseData, 
  onClose,
  onTriggerAction,
  onExportSubgraph
}) {
  const [activeTab, setActiveTab] = useState('Summary');
  const [copied, setCopied] = useState(false);

  const c = caseData?.case || {};
  const entityInfo = c.entity_info || {};
  const riskIndicators = c.risk_indicators || [
    { title: "Linked to dark web marketplace", severity: "High" },
    { title: "Multiple wallet activity", severity: "High" },
    { title: "Device sharing (3 users)", severity: "Medium" },
    { title: "Unusual transaction pattern", severity: "High" }
  ];
  const relatedCounts = c.related_counts || {
    transactions: 12,
    devices: 3,
    cards: 2,
    related_users: 3
  };

  // If no node selected, default to primary user entity
  const node = selectedEntity || {
    id: c.customer_id || "UnknownUser",
    label: c.customer_id || "Unknown User",
    title: "User",
    type: "user",
    risk_score: 0,
    risk_level: "Medium Risk",
    details: entityInfo
  };

  const isUser = (node.type || '').toLowerCase() === 'user' || node.is_central;
  const displayName = node.label || node.id;
  const score = node.risk_score || 87;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(String(text));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const tabs = ['Summary', 'Details', 'Risk Scores', 'Financials'];

  return (
    <aside className="w-[340px] h-full bg-[#111318] border-l border-[#1C1F28] flex flex-col select-none flex-shrink-0 z-20 font-sans overflow-hidden">
      {/* 1. Entity Profile Header */}
      <div className="p-4 border-b border-[#1C1F28] flex items-start justify-between">
        <div className="flex items-center gap-3">
          {/* Avatar Icon */}
          <div className="w-12 h-12 rounded-full bg-[#181B24] border border-[#262A36] flex items-center justify-center text-slate-200 shrink-0">
            <User className="w-6 h-6 text-[#8E93A6]" />
          </div>

          <div className="flex flex-col">
            <span className="text-[11px] text-[#646A7E] font-medium leading-none">
              User Entity
            </span>
            <div className="flex items-center gap-2 mt-1">
              <h3 className="text-base font-bold text-white tracking-tight">
                {displayName}
              </h3>
              <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-950/60 text-red-400 border border-red-800/60 shadow-[0_0_8px_rgba(239,68,68,0.2)]">
                <AlertTriangle className="w-3 h-3 text-red-400" />
                High Risk
              </span>
            </div>
            <span className="text-xs text-[#8E93A6] mt-0.5">
              Risk Score <strong className="text-white font-mono">{score}/100</strong>
            </span>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded text-[#646A7E] hover:text-white hover:bg-[#181B24] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 2. Navigation Tabs */}
      <div className="flex border-b border-[#1C1F28] bg-[#0E1015] px-4">
        {tabs.map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2.5 text-xs font-medium transition-colors relative mr-5 ${
                isActive ? 'text-[#10B981] font-semibold' : 'text-[#8E93A6] hover:text-white'
              }`}
            >
              {tab}
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#10B981] rounded-full" />
              )}
            </button>
          );
        })}
      </div>

      {/* 3. Tab Contents */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
        {/* SUMMARY TAB */}
        {activeTab === 'Summary' && (
          <>
            {/* Section: Entity Information */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-white tracking-tight">
                Entity Information
              </h4>
              <div className="space-y-1.5 text-[#8E93A6] text-xs">
                <div className="flex justify-between items-center py-0.5">
                  <span>Type</span>
                  <span className="text-white font-medium">User</span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>User ID</span>
                  <span className="text-white font-medium flex items-center gap-1">
                    {entityInfo.user_id || 'ShadowX77'}
                    <button onClick={() => handleCopy(entityInfo.user_id || 'ShadowX77')} className="text-[#646A7E] hover:text-white">
                      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Aliases</span>
                  <span className="text-white font-medium">
                    {entityInfo.aliases_count || 4} <span className="text-[#10B981] hover:underline cursor-pointer">(View All)</span>
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Associated Wallets</span>
                  <span className="text-white font-medium">
                    {entityInfo.wallets_count || 3} <span className="text-[#10B981] hover:underline cursor-pointer">(View All)</span>
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Email</span>
                  <span className="text-white font-mono text-[11px] truncate max-w-[170px]">
                    {entityInfo.email || 'shadowx77@proton.me'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Created At</span>
                  <span className="text-white font-mono text-[11px]">
                    {entityInfo.created_at || '2025-11-14 08:32:17'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Last Activity</span>
                  <span className="text-white font-mono text-[11px]">
                    {entityInfo.last_activity || '2026-09-21 16:45:32'}
                  </span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span>Location</span>
                  <span className="text-white font-medium flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-[#10B981]" />
                    {entityInfo.location || 'Eastern Europe'}
                  </span>
                </div>
              </div>
            </div>

            {/* Section: Risk Indicators */}
            <div className="space-y-2 pt-2 border-t border-[#1C1F28]">
              <h4 className="text-xs font-semibold text-white tracking-tight flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-[#10B981]" />
                Risk Indicators
              </h4>
              <div className="space-y-1.5">
                {riskIndicators.map((ind, i) => {
                  const isHigh = ind.severity === 'High';
                  return (
                    <div key={i} className="flex items-center justify-between text-xs py-0.5">
                      <div className="flex items-center gap-2 text-[#8E93A6]">
                        <AlertTriangle className={`w-3 h-3 ${isHigh ? 'text-[#10B981]' : 'text-amber-500'}`} />
                        <span className="text-slate-200">{ind.title}</span>
                      </div>
                      <span className={`text-[10px] font-semibold px-2 py-0.2 rounded-full ${
                        isHigh ? 'bg-red-950/60 text-red-400' : 'bg-amber-950/60 text-amber-400'
                      }`}>
                        {ind.severity}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Section: Related Entities */}
            <div className="space-y-2 pt-2 border-t border-[#1C1F28]">
              <h4 className="text-xs font-semibold text-white tracking-tight flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-[#10B981]" />
                Related Entities
              </h4>
              <div className="space-y-1.5 text-xs text-[#8E93A6]">
                <div className="flex items-center justify-between py-0.5">
                  <div className="flex items-center gap-2">
                    <ArrowUpRight className="w-3.5 h-3.5 text-[#585E72]" />
                    <span>Transactions</span>
                  </div>
                  <span className="text-white font-mono font-bold">{relatedCounts.transactions}</span>
                </div>
                <div className="flex items-center justify-between py-0.5">
                  <div className="flex items-center gap-2">
                    <Smartphone className="w-3.5 h-3.5 text-[#585E72]" />
                    <span>Devices</span>
                  </div>
                  <span className="text-white font-mono font-bold">{relatedCounts.devices}</span>
                </div>
                <div className="flex items-center justify-between py-0.5">
                  <div className="flex items-center gap-2">
                    <CreditCard className="w-3.5 h-3.5 text-[#585E72]" />
                    <span>Cards</span>
                  </div>
                  <span className="text-white font-mono font-bold">{relatedCounts.cards}</span>
                </div>
                <div className="flex items-center justify-between py-0.5">
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5 text-[#585E72]" />
                    <span>Related Users</span>
                  </div>
                  <span className="text-white font-mono font-bold">{relatedCounts.related_users}</span>
                </div>
              </div>
            </div>
          </>
        )}

        {/* DETAILS TAB */}
        {activeTab === 'Details' && (
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white tracking-tight">TigerGraph Node Telemetry</h4>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded bg-[#181B24] border border-[#262A36]">
                <span className="text-[10px] text-[#646A7E] block uppercase">GSQL Vertex Class</span>
                <span className="text-white font-mono">{node.type || 'User'}</span>
              </div>
              <div className="p-2.5 rounded bg-[#181B24] border border-[#262A36]">
                <span className="text-[10px] text-[#646A7E] block uppercase">Vertex Primary ID</span>
                <span className="text-[#10B981] font-mono">{node.id}</span>
              </div>
              <div className="p-2.5 rounded bg-[#181B24] border border-[#262A36]">
                <span className="text-[10px] text-[#646A7E] block uppercase">Topological Neighborhood</span>
                <span className="text-slate-200">8 First-Hop Edges, 3 Shared Devices</span>
              </div>
            </div>
          </div>
        )}

        {/* RISK SCORES TAB */}
        {activeTab === 'Risk Scores' && (
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white tracking-tight">Mathematical Risk Assessment</h4>
            <div className="p-3 rounded-lg bg-[#181B24] border border-[#262A36] space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-[#8E93A6]">Assessed Risk:</span>
                <span className="text-[#10B981] font-bold text-sm font-mono">{score}%</span>
              </div>
              <div className="w-full h-2 bg-[#202430] rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-amber-500 to-[#10B981]" style={{ width: `${score}%` }} />
              </div>
            </div>
            <div className="space-y-1.5 text-xs text-[#8E93A6]">
              <div className="flex justify-between">
                <span>Confidence Level:</span>
                <span className="text-white font-mono">91%</span>
              </div>
              <div className="flex justify-between">
                <span>Uncertainty Metric:</span>
                <span className="text-emerald-400 font-mono">LOW (Decoupled)</span>
              </div>
              <div className="flex justify-between">
                <span>Regulatory Threshold:</span>
                <span className="text-red-400 font-mono">Rule R6 Triggered</span>
              </div>
            </div>
          </div>
        )}

        {/* FINANCIALS TAB */}
        {activeTab === 'Financials' && (
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-white tracking-tight">Financial Exposure & SAR</h4>
            <div className="p-3 rounded-lg bg-[#181B24] border border-[#262A36] space-y-1">
              <span className="text-[10px] text-[#646A7E] uppercase block">Total Flagged Exposure</span>
              <div className="text-xl font-bold text-[#10B981] font-mono">
                ${Number(c.exposure_usd || 4850.00).toLocaleString('en-US', { minimumFractionDigits: 2 })} USD
              </div>
              <span className="text-[10px] text-[#8E93A6]">FinCEN $1,000 threshold exceeded</span>
            </div>
            <div className="space-y-1.5 text-xs text-[#8E93A6]">
              <div className="flex justify-between">
                <span>FinCEN SAR Status:</span>
                <span className="text-red-400 font-semibold font-mono">MANDATORY FILING</span>
              </div>
              <div className="flex justify-between">
                <span>31 CFR § 1020.320:</span>
                <span className="text-white font-mono">Section 4 Satisfied</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 4. Bottom Action Buttons */}
      <div className="p-4 border-t border-[#1C1F28] space-y-2">
        {/* Full-Width Orange Primary Button: Submit SAR */}
        <button
          onClick={() => onTriggerAction && onTriggerAction('SAR', node)}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-[#10B981] hover:bg-[#34D399] text-black font-semibold text-xs shadow-[0_0_15px_rgba(16,185,129,0.35)] transition-all font-sans"
        >
          <Send className="w-4 h-4 fill-current" />
          <span>Submit SAR</span>
        </button>

        {/* Row of Two Secondary Buttons: Block User & Export Subgraph */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onTriggerAction && onTriggerAction('BLOCK', node)}
            className="flex items-center justify-center gap-1.5 py-2 rounded-lg bg-[#15171F] hover:bg-red-950/40 text-slate-200 hover:text-red-400 border border-[#232733] hover:border-red-800 text-xs transition-colors font-sans"
          >
            <Ban className="w-3.5 h-3.5 text-amber-500" />
            <span>Block User</span>
          </button>

          <button
            onClick={() => onExportSubgraph && onExportSubgraph()}
            className="flex items-center justify-center gap-1.5 py-2 rounded-lg bg-[#15171F] hover:bg-[#1E222D] text-slate-200 hover:text-white border border-[#232733] text-xs transition-colors font-sans"
          >
            <Download className="w-3.5 h-3.5 text-[#8E93A6]" />
            <span>Export Subgraph</span>
          </button>
        </div>
      </div>
    </aside>
  );
}

export default PegaEntityDrawer;
