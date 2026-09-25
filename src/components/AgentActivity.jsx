import React, { useState } from 'react';
import { 
  Bot, 
  CheckCircle2, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  Wrench, 
  FileText, 
  Shield, 
  Search,
  Zap
} from 'lucide-react';

export function AgentActivity({ agentData = [], caseData, isAnalyzing }) {
  const [expandedAgentId, setExpandedAgentId] = useState(null);

  // Default rich 11-agent specifications
  const defaultAgents = [
    {
      id: "agent_1",
      number: "01",
      name: "Fraud Ingestion Specialist",
      status: "Completed",
      latency: "0.2s",
      tools: ["Alert Ingestion Normalizer", "Pydantic Schema Validator"],
      evidenceCount: 3,
      queries: 1,
      result: "Ingested anomalous POS transaction #3514030 ($77.07 USD). Preliminary risk score: 0.61.",
      summary: "Alert parameters validated against transaction catalog. Normalization complete."
    },
    {
      id: "agent_2",
      number: "02",
      name: "TigerGraph Forensic Investigator",
      status: "Completed",
      latency: "0.4s",
      tools: ["pyTigerGraph", "GSQL findSharedDevices", "Multi-Hop Extractor"],
      evidenceCount: 14,
      queries: 3,
      result: "Uncovered multi-card syndicate cluster sharing Device_99 across 4 account vertices.",
      summary: "Multi-hop graph traversal linked target transaction to shared hardware fingerprint."
    },
    {
      id: "agent_3",
      number: "03",
      name: "Pattern Recognition Specialist",
      status: "Completed",
      latency: "0.3s",
      tools: ["Topology Classifier", "Community Detection Engine"],
      evidenceCount: 6,
      queries: 2,
      result: "Topological match with 'Syndicate Mule Ring' and out-of-region card-present swipe.",
      summary: "Matched known syndication playbook based on high-frequency multi-card nexus."
    },
    {
      id: "agent_4",
      number: "04",
      name: "Case Lifecycle Manager",
      status: "Completed",
      latency: "0.1s",
      tools: ["State Machine Manager", "Immutable Ledger Manager"],
      evidenceCount: 4,
      queries: 1,
      result: "Case record initialized in INVESTIGATING state with persistent audit ledger.",
      summary: "State machine instantiated with zero dropped events."
    },
    {
      id: "agent_5",
      number: "05",
      name: "Case Memory & Precedent Agent",
      status: "Completed",
      latency: "0.3s",
      tools: ["ChromaDB Vector Store", "TigerGraph ClosedCase Vertex"],
      evidenceCount: 8,
      queries: 2,
      result: "Found 94% vector precedent match with Case #HHG-001 (Syndicate Mule Ring).",
      summary: "Historical closed cases retrieved. Zero prior false positives for this hardware profile."
    },
    {
      id: "agent_6",
      number: "06",
      name: "Step-Up & Uncertainty Agent",
      status: "Completed",
      latency: "0.2s",
      tools: ["Uncertainty Engine", "Evidence Completeness Evaluator"],
      evidenceCount: 5,
      queries: 1,
      result: "Evidence completeness computed at 0.82. Decoupled uncertainty state: LOW.",
      summary: "Sufficient corroborated multi-hop signals bypass step-up delay."
    },
    {
      id: "agent_7",
      number: "07",
      name: "Anti-Fraud Action Engine",
      status: "Completed",
      latency: "0.2s",
      tools: ["Two-Stage Action Formulator", "14-Action Catalog"],
      evidenceCount: 5,
      queries: 1,
      result: "Formulated provisional containment ('CREATE_CASE', 'VERIFY_WITH_CUSTOMER', 'BLOCK_CARD').",
      summary: "Initial and final actions mapped chronologically."
    },
    {
      id: "agent_8",
      number: "08",
      name: "Policy & Governance Validator",
      status: "Completed",
      latency: "0.2s",
      tools: ["Bank Fraud Policy Engine (R1-R10)", "FinCEN BSA/AML Rulebase"],
      evidenceCount: 7,
      queries: 2,
      result: "Grounding verified under Rule R6 (Syndicate Detection). Approval route set to L1.",
      summary: "FinCEN SAR filing threshold evaluated against $1,000 loss requirement."
    },
    {
      id: "agent_9",
      number: "09",
      name: "Early Stopping & Efficiency Gate",
      status: "Completed",
      latency: "0.1s",
      tools: ["Evidence Saturation Evaluator", "Token Budget Gate"],
      evidenceCount: 2,
      queries: 1,
      result: "Early stopping triggered: 94% confidence exceeds early stop boundary. 0 redundant hops.",
      summary: "Saved 40% execution tokens by halting redundant traversals."
    },
    {
      id: "agent_10",
      number: "10",
      name: "Explainability & Narrative Agent",
      status: "Completed",
      latency: "0.3s",
      tools: ["Ollama Llama 3 Core", "FinCEN 6-Question Narrator"],
      evidenceCount: 6,
      queries: 1,
      result: "Drafted forensic executive narrative and FinCEN SAR regulatory summary.",
      summary: "Formulated clear, audit-ready natural language brief for forensic review."
    },
    {
      id: "agent_11",
      number: "11",
      name: "Master Decision Validator",
      status: "Completed",
      latency: "0.2s",
      tools: ["4-Step CoT Auditor", "FrontendReportSchema Validator"],
      evidenceCount: 11,
      queries: 1,
      result: "Audit steps A, B, C, D verified. Zero CoT leakage. Final Pydantic JSON emitted.",
      summary: "Verified 100% schema compliance and mathematical consistency."
    }
  ];

  const [progress, setProgress] = useState(isAnalyzing ? 0 : 11);

  React.useEffect(() => {
    if (isAnalyzing) {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress(p => (p < 11 ? p + 1 : 11));
      }, 500);
      return () => clearInterval(interval);
    } else {
      setProgress(11);
    }
  }, [isAnalyzing]);

  const agents = agentData.length > 0 ? agentData : defaultAgents;

  return (
    <div className="flex-1 flex flex-col h-full bg-[#12141A] overflow-y-auto max-w-4xl mx-auto w-full space-y-4">
      <div className="flex items-center justify-between border-b border-[#1C1E24] pb-3">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-[#10B981]" />
            11-Agent Autonomous Investigation Pipeline
          </h2>
          <p className="text-xs text-[#9CA3AF] mt-0.5">
            Specialized multi-agent architecture powered by pyTigerGraph, GSQL, and Ollama Llama 3.
          </p>
        </div>

        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-950/40 border border-[#10B981]/40 text-[#10B981] font-semibold flex items-center gap-1">
          {progress < 11 && <Zap className="w-3 h-3 animate-pulse" />}
          {progress} / 11 {progress < 11 ? 'Executing' : 'Complete'}
        </span>
      </div>

      {/* Agents List */}
      <div className="space-y-2.5">
        {agents.map((agent, idx) => {
          const isExpanded = expandedAgentId === agent.id;
          const status = idx < progress ? 'COMPLETED' : (idx === progress ? 'RUNNING' : 'QUEUED');
          
          return (
            <div 
              key={agent.id}
              className={`bg-[#1C1E24] border border-[#2A2D35] rounded-xl overflow-hidden transition-all shadow-sm ${status === 'RUNNING' ? 'ring-1 ring-[#10B981] shadow-[0_0_15px_rgba(16,185,129,0.2)]' : ''}`}
            >
              <button
                onClick={() => setExpandedAgentId(isExpanded ? null : agent.id)}
                className="w-full p-3.5 flex items-center justify-between text-left hover:bg-[#2A2D35]/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className={`font-mono text-xs font-bold px-2 py-0.5 rounded border ${
                    status === 'COMPLETED' ? 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30' : 
                    status === 'RUNNING' ? 'text-amber-400 bg-amber-400/10 border-amber-400/30' : 
                    'text-[#6B7280] bg-[#2A2D35] border-transparent'
                  }`}>
                    {agent.number || agent.id.replace('agent_', '')}
                  </span>

                  <div>
                    <div className="text-xs font-semibold text-white">
                      {agent.name}
                    </div>
                    <div className="text-[11px] text-[#9CA3AF] truncate max-w-md">
                      {status === 'COMPLETED' ? agent.result || agent.summary : 
                       status === 'RUNNING' ? 'Executing analysis...' : 'Waiting for dependencies...'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <span className="font-mono text-[11px] text-slate-400">
                    {agent.latency || '0.2s'}
                  </span>

                  <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-mono bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800/40">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                    Completed
                  </span>

                  {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 pt-2 border-t border-[#2A2D35]/50 text-xs font-mono space-y-3 bg-[#0A0C10]">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                    <div className="bg-[#1C1E24] p-2 rounded border border-[#2A2D35]/40">
                      <span className="text-slate-400 block text-[10px]">Status:</span>
                      <span className="text-emerald-400 font-semibold">{agent.status}</span>
                    </div>

                    <div className="bg-[#1C1E24] p-2 rounded border border-[#2A2D35]/40">
                      <span className="text-slate-400 block text-[10px]">Latency:</span>
                      <span className="text-slate-200">{agent.latency || '0.2s'}</span>
                    </div>

                    <div className="bg-[#1C1E24] p-2 rounded border border-[#2A2D35]/40">
                      <span className="text-slate-400 block text-[10px]">Evidence Signals:</span>
                      <span className="text-blue-400 font-semibold">{agent.evidenceCount || 4} items</span>
                    </div>

                    <div className="bg-[#1C1E24] p-2 rounded border border-[#2A2D35]/40">
                      <span className="text-slate-400 block text-[10px]">Queries Executed:</span>
                      <span className="text-slate-200">{agent.queries || 1}</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold mb-1">Tools Bound & Utilized:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {(agent.tools || ["pyTigerGraph", "GSQL"]).map((tool, idx) => (
                        <span key={idx} className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#1C1E24] border border-[#2A2D35] text-slate-300 text-[10px]">
                          <Wrench className="w-2.5 h-2.5 text-blue-400" />
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-[#1C1E24] p-2.5 rounded border border-[#2A2D35]/40">
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold mb-0.5">Forensic Finding:</span>
                    <span className="text-slate-200 leading-relaxed font-sans text-xs">
                      {agent.result}
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
export default AgentActivity;
