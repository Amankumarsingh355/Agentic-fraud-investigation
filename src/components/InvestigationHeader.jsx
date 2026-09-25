import React, { useState } from 'react';
import { Search, Bell, Shield, ChevronDown, Check, Copy, RefreshCw, Download } from 'lucide-react';
import aegisLogo from '../assets/aegis-logo.png';

export function InvestigationHeader({ 
  caseData, 
  onSearch, 
  onRerun, 
  isRerunning,
  onExportJson 
}) {
  const [searchTerm, setSearchTerm] = useState('');

  const c = caseData?.case || {};
  const caseId = c.case_id || 'No Case Selected';

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch(searchTerm);
    }
  };

  return (
    <header className="h-14 border-b border-[#1C1E24] bg-[#0E1015] px-4 flex items-center justify-between flex-shrink-0 z-30 select-none font-sans">
      {/* 1. Left: Aegis Logo & Text */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <img src={aegisLogo} alt="Aegis" className="h-8 object-contain" />
          <div className="flex items-center gap-1.5 font-bold tracking-tight">
            <span className="text-white text-sm tracking-tight font-sans">TigerGraph Savanna</span>
            <span className="text-[#10B981] text-sm font-sans font-bold">X</span>
            <span className="text-white text-sm font-sans font-medium">Taskforce Aegis Ai</span>
          </div>
        </div>

        <span className="text-[#646A7E] text-xs font-sans pl-2 border-l border-[#242834] hidden sm:inline">
          Fraud Investigation
        </span>
      </div>

      {/* 2. Center: Global Search Bar */}
      <div className="flex-1 max-w-xl mx-6 lg:mx-10 relative">
        <Search className="w-4 h-4 text-[#646A7E] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleSearchSubmit}
          placeholder="Search by user, card, transaction, device..."
          className="w-full bg-[#15171F] border border-[#232733] hover:border-[#353A4D] focus:border-[#10B981] rounded-lg pl-10 pr-4 py-2 text-xs text-white placeholder-[#585E72] outline-none transition-colors font-sans"
        />
        {searchTerm && (
          <button 
            onClick={() => { setSearchTerm(''); if (onSearch) onSearch(''); }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[#646A7E] hover:text-white"
          >
            ✕
          </button>
        )}
      </div>

      {/* 3. Right: Notification Bell & Aman Singh Profile */}
      <div className="flex items-center gap-3">
        {/* Re-run button subtle */}
        {onRerun && (
          <button
            onClick={onRerun}
            disabled={isRerunning}
            className="p-2 rounded-lg bg-[#15171F] hover:bg-[#1E222D] border border-[#232733] text-[#8E93A6] hover:text-white transition-colors"
            title="Re-run TigerGraph Investigation"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRerunning ? 'animate-spin text-[#10B981]' : ''}`} />
          </button>
        )}

        {/* Notification Bell with Badge 4 */}
        <div className="relative p-2 rounded-lg hover:bg-[#1A1D27] cursor-pointer text-[#8E93A6] hover:text-white transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-3.5 h-3.5 bg-[#10B981] text-black text-[9px] font-bold rounded-full flex items-center justify-center">
            4
          </span>
        </div>

        {/* Avatar & Profile Details */}
        <div className="flex items-center gap-2.5 pl-2.5 border-l border-[#242834]">
          <div className="w-8 h-8 rounded-full bg-[#202430] border border-[#303648] flex items-center justify-center text-xs font-bold text-slate-200">
            AK
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-semibold text-white leading-tight">Aman Singh</span>
            <span className="text-[10px] text-[#646A7E] leading-tight font-medium">Investigator</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default InvestigationHeader;
