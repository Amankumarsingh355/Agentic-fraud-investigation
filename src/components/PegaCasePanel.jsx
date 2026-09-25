import React, { useState } from 'react';
import { 
  ArrowLeft,
  ChevronDown,
  Bell,
  CreditCard,
  Users,
  Bot,
  Layers,
  Sparkles,
  AlertTriangle,
  Target,
  Share2,
  Clock,
  UserCheck,
  ShieldAlert,
  FolderOpen
} from 'lucide-react';

export function PegaCasePanel({ 
  caseData, 
  cases = [], 
  activeCaseId, 
  onSelectCase, 
  activeNav, 
  onSelectNav,
  onOpenAiNotes,
  onTagClick
}) {
  const [caseListOpen, setCaseListOpen] = useState(false);

  const c = caseData?.case || {};
  const caseId = activeCaseId || c.case_id || 'Unknown';
  const title = caseData?.title || c.pattern_description || 'Unknown Fraud Pattern';
  const category = caseData?.category || 'Financial Fraud';
  const pattern = c.pattern || 'Unknown';
  const assignedTo = c.assigned_to || 'System';
  const createdDate = c.opened_at || 'Unknown';
  const updatedDate = c.updated_at || 'Unknown';

  const riskScore = c.fraud_probability !== undefined ? Math.round(c.fraud_probability * 100) : 0;
  const confidenceScore = c.confidence_score !== undefined ? Math.round(c.confidence_score * 100) : 0;
  const criticalAlerts = c.critical_alerts_count || 0;
  const relatedEntities = c.related_entities_count || 0;

  const quickTags = c.quick_tags || [];

  const navItems = [
    { id: 'overview', label: 'Overview', icon: FolderOpen, count: null },
    { id: 'alerts', label: 'Alerts', icon: Bell, count: 6 },
    { id: 'accounts', label: 'Accounts', icon: CreditCard, count: 3 },
    { id: 'related', label: 'Related Subjects', icon: Users, count: 12 },
    { id: 'ai_notes', label: 'AI Notes', icon: Sparkles, count: 4 }
  ];

  // Circular gauge calculations (r = 34, circum = 2 * PI * 34 ≈ 213.6)
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (riskScore / 100) * circumference;

  return (
    <aside className="w-[280px] h-full bg-[#111318] border-r border-[#1C1F28] flex flex-col select-none flex-shrink-0 z-20 font-sans overflow-y-auto">
      {/* 1. All Cases Back Button & Switcher Dropdown */}
      <div className="p-3 border-b border-[#1C1F28] relative">
        <button
          onClick={() => setCaseListOpen(!caseListOpen)}
          className="flex items-center gap-1.5 text-xs text-[#8E93A6] hover:text-white transition-colors py-1 group w-full justify-between"
        >
          <div className="flex items-center gap-1.5">
            <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
            <span className="font-medium">All Cases</span>
          </div>
          <ChevronDown className={`w-3.5 h-3.5 text-[#646A7E] transition-transform ${caseListOpen ? 'rotate-180' : ''}`} />
        </button>

        {caseListOpen && (
          <div className="absolute top-full left-3 right-3 mt-1 bg-[#181B24] border border-[#262A36] rounded-lg shadow-2xl z-50 max-h-60 overflow-y-auto py-1">
            <div className="px-3 py-1.5 text-[10px] uppercase font-mono tracking-wider text-[#646A7E] border-b border-[#242834]">
              Switch Benchmark Case
            </div>
            {cases.map((cs) => (
              <button
                key={cs.case_id}
                onClick={() => {
                  onSelectCase(cs.case_id);
                  setCaseListOpen(false);
                }}
                className={`w-full px-3 py-2 flex items-center justify-between text-xs text-left transition-colors ${
                  cs.case_id === caseId 
                    ? 'bg-[#10B981]/15 text-[#10B981] font-bold' 
                    : 'text-slate-300 hover:bg-[#202430]'
                }`}
              >
                <span className="font-mono">{cs.case_id}</span>
                <span className="text-[10px] text-[#8E93A6]">
                  ${Number(cs.exposure_usd || 0).toLocaleString()}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 2. Case Header */}
      <div className="p-4 border-b border-[#1C1F28] space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-white font-mono tracking-wide">
            {caseId}
          </span>
          <span className="text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded bg-red-950/40 text-red-400 border border-red-800/50">
            HIGH PRIORITY
          </span>
        </div>

        <div>
          <h2 className="text-base font-bold text-white leading-tight">
            {title}
          </h2>
          <p className="text-xs text-[#7B8296] mt-0.5">
            {category}
          </p>
        </div>

        {/* Metadata Key/Values with Icons */}
        <div className="pt-2 space-y-2 text-xs">
          <div className="flex items-center gap-2 text-[#7B8296]">
            <FolderOpen className="w-3.5 h-3.5 text-[#585E72] shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="text-[10px] text-[#585E72] uppercase leading-none">Case Type</span>
              <span className="text-slate-200 font-medium truncate">{pattern}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[#7B8296]">
            <UserCheck className="w-3.5 h-3.5 text-[#585E72] shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="text-[10px] text-[#585E72] uppercase leading-none">Assigned To</span>
              <span className="text-slate-200 font-medium truncate">{assignedTo}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[#7B8296]">
            <Clock className="w-3.5 h-3.5 text-[#585E72] shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="text-[10px] text-[#585E72] uppercase leading-none">Created</span>
              <span className="text-slate-200 font-medium">{createdDate}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-[#7B8296]">
            <Clock className="w-3.5 h-3.5 text-[#585E72] shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="text-[10px] text-[#585E72] uppercase leading-none">Last Updated</span>
              <span className="text-slate-200 font-medium">{updatedDate}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Navigation Menu Items */}
      <div className="p-3 border-b border-[#1C1F28] space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = (activeNav || 'overview') === item.id;

          return (
            <button
              key={item.id}
              onClick={() => {
                if (item.id === 'ai_notes' && onOpenAiNotes) {
                  onOpenAiNotes();
                } else if (onSelectNav) {
                  onSelectNav(item.id);
                }
              }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs transition-colors duration-150 group ${
                isActive
                  ? 'bg-[#10B981]/15 text-[#10B981] font-semibold border-l-2 border-[#10B981]'
                  : 'text-[#8E93A6] hover:text-white hover:bg-[#181B24]'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-[#10B981]' : 'text-[#646A7E] group-hover:text-slate-300'}`} />
                <span>{item.label}</span>
              </div>

              {item.count !== null && (
                <span className="w-4 h-4 rounded-full bg-red-600/90 text-white text-[10px] font-bold flex items-center justify-center">
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 4. Risk Summary Gauge & Metrics */}
      <div className="p-4 border-b border-[#1C1F28] space-y-3">
        <h3 className="text-xs font-semibold text-white tracking-tight">
          Risk Summary
        </h3>

        <div className="flex items-center gap-4">
          {/* Radial Ring Gauge */}
          <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
            <svg className="w-20 h-20 -rotate-90">
              <circle
                cx="40"
                cy="40"
                r={radius}
                className="text-[#202430]"
                strokeWidth="6"
                stroke="currentColor"
                fill="transparent"
              />
              <circle
                cx="40"
                cy="40"
                r={radius}
                className="text-[#10B981]"
                strokeWidth="6"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                style={{
                  filter: 'drop-shadow(0 0 6px rgba(16, 185, 129, 0.5))'
                }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-sm font-bold text-white leading-none font-mono">
                {riskScore}<span className="text-[10px] text-[#7B8296] font-normal">/100</span>
              </span>
              <span className="text-[9px] font-semibold text-[#10B981] mt-0.5">
                High Risk
              </span>
            </div>
          </div>

          {/* Metric Details to the Right */}
          <div className="space-y-1.5 text-xs flex-1">
            <div className="flex items-center justify-between text-[#8E93A6]">
              <span className="flex items-center gap-1.5 text-[11px]">
                <Target className="w-3.5 h-3.5 text-[#585E72]" />
                Confidence
              </span>
              <span className="font-bold text-white font-mono">{confidenceScore}%</span>
            </div>

            <div className="flex items-center justify-between text-[#8E93A6]">
              <span className="flex items-center gap-1.5 text-[11px]">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                Critical Alerts
              </span>
              <span className="font-bold text-white font-mono">{criticalAlerts}</span>
            </div>

            <div className="flex items-center justify-between text-[#8E93A6]">
              <span className="flex items-center gap-1.5 text-[11px]">
                <Share2 className="w-3.5 h-3.5 text-[#585E72]" />
                Related Entities
              </span>
              <span className="font-bold text-white font-mono">{relatedEntities}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Quick Tags */}
      <div className="p-4 space-y-2">
        <h3 className="text-xs font-semibold text-[#7B8296] tracking-tight uppercase text-[10px]">
          Quick Tags
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {quickTags.map((tag) => {
            const isHighRisk = tag.toLowerCase().includes('highrisk') || tag.toLowerCase().includes('darkweb');
            return (
              <button
                key={tag}
                onClick={() => onTagClick && onTagClick(tag)}
                className={`text-[11px] px-2.5 py-1 rounded-md transition-colors border ${
                  isHighRisk
                    ? 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/40 hover:bg-[#10B981]/25'
                    : 'bg-[#181B24] text-[#8E93A6] border-[#242834] hover:text-white hover:border-[#353A4D]'
                }`}
              >
                {tag}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

export default PegaCasePanel;
