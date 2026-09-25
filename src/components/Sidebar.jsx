import React from 'react';
import { 
  Plus, 
  MessageSquare, 
  LayoutDashboard, 
  Share2, 
  Bot, 
  ShieldCheck, 
  History, 
  Award, 
  Database,
  FileCheck2,
  AlertCircle
} from 'lucide-react';
import { SystemStatus } from './SystemStatus';

export function Sidebar({ 
  cases = [], 
  activeCaseId, 
  onSelectCase, 
  onNewInvestigation, 
  activeNav, 
  onSelectNav,
  systemStatus
}) {
  return (
    <aside className="w-[250px] h-screen bg-[#1E1E1E] flex flex-col border-r border-[#2A2A2A] select-none flex-shrink-0 font-mono text-xs">
      {/* Top New Investigation Button (Orange #10B981) */}
      <div className="p-3 space-y-2">
        <button
          onClick={onNewInvestigation}
          className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded bg-[#10B981] hover:bg-[#34D399] text-black font-bold text-xs shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all duration-150"
        >
          <Plus className="w-4 h-4 stroke-[2.5]" />
          <span>New Investigation</span>
        </button>
        <label className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded border border-[#10B981] text-[#10B981] hover:bg-[#10B981]/10 font-bold text-xs cursor-pointer transition-all">
          <Database className="w-4 h-4" />
          <span>Upload Dataset</span>
          <input 
            type="file" 
            className="hidden" 
            accept=".json,.csv"
            onChange={(e) => {
              if (e.target.files.length > 0) {
                const formData = new FormData();
                formData.append('dataset', e.target.files[0]);
                fetch('/api/upload_dataset', { method: 'POST', body: formData })
                  .then(r => r.json())
                  .then(data => {
                    // Trigger refresh of cases
                    window.location.reload();
                  })
                  .catch(console.error);
              }
            }}
          />
        </label>
      </div>

      {/* Main Navigation Items */}
      <div className="px-3 py-1 space-y-0.5 border-b border-[#2A2A2A]">
        <button
          onClick={() => onSelectNav('graph')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'graph' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <Share2 className={`w-3.5 h-3.5 ${activeNav === 'graph' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>Graph Cockpit</span>
        </button>

        <button
          onClick={() => onSelectNav('chat')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'chat' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <MessageSquare className={`w-3.5 h-3.5 ${activeNav === 'chat' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>Analyst Chat</span>
        </button>

        <button
          onClick={() => onSelectNav('agents')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'agents' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <Bot className={`w-3.5 h-3.5 ${activeNav === 'agents' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>11-Agent Activity</span>
        </button>

        <button
          onClick={() => onSelectNav('approvals')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'approvals' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <ShieldCheck className={`w-3.5 h-3.5 ${activeNav === 'approvals' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>Approvals Center</span>
        </button>

        <button
          onClick={() => onSelectNav('timeline')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'timeline' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <History className={`w-3.5 h-3.5 ${activeNav === 'timeline' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>Case Timeline</span>
        </button>

        <button
          onClick={() => onSelectNav('benchmark')}
          className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors ${
            activeNav === 'benchmark' 
              ? 'bg-[#10B981]/15 text-white font-bold border-l-2 border-[#10B981]' 
              : 'text-[#A0A0A0] hover:text-white hover:bg-[#252525]'
          }`}
        >
          <Award className={`w-3.5 h-3.5 ${activeNav === 'benchmark' ? 'text-[#10B981]' : 'text-[#A0A0A0]'}`} />
          <span>Benchmark Suite</span>
        </button>
      </div>

      {/* Case Feed List (Scrollable) */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        <div className="flex items-center justify-between px-1 py-1 text-[9px] uppercase tracking-wider text-[#666666]">
          <span>Active Cases ({cases.length})</span>
          <span>IEEE-CIS</span>
        </div>
        
        <button
          onClick={() => onSelectNav && onSelectNav('batch_process')}
          className="w-full mb-2 flex items-center justify-center gap-1.5 px-2 py-1.5 rounded bg-[#10B981]/20 hover:bg-[#10B981]/40 border border-[#10B981]/50 text-[#10B981] font-bold text-[10px] transition-all"
        >
          <Database className="w-3 h-3" />
          <span>Select All Cases & Process</span>
        </button>

        {cases.map((cs) => {
          const isSelected = cs.case_id === activeCaseId;
          const isFraud = cs.verdict === 'fraud';

          return (
            <button
              key={cs.case_id}
              onClick={() => onSelectCase(cs.case_id)}
              className={`w-full text-left p-2 rounded transition-all text-xs flex flex-col gap-1 border ${
                isSelected
                  ? 'bg-[#121212] border-[#10B981]/80 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
                  : 'bg-[#181818] border-[#2A2A2A] hover:border-[#3A3A3A] hover:bg-[#202020]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`font-bold ${isSelected ? 'text-[#10B981]' : 'text-white'}`}>
                  {cs.case_id}
                </span>
                <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold uppercase ${
                  isFraud ? 'bg-red-950/60 text-red-400' : 'bg-emerald-950/60 text-emerald-400'
                }`}>
                  {cs.verdict || 'review'}
                </span>
              </div>

              <div className="flex items-center justify-between text-[10px] text-[#A0A0A0]">
                <span className="truncate max-w-[120px]">{cs.pattern?.replace(/_/g, ' ') || 'fraud'}</span>
                <span className="font-bold text-slate-300">
                  ${Number(cs.exposure_usd || 0).toFixed(0)}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* System Status Widget at Bottom */}
      <div className="p-2 border-t border-[#2A2A2A] bg-[#141414]">
        <SystemStatus status={systemStatus} />
      </div>
    </aside>
  );
}

export default Sidebar;
