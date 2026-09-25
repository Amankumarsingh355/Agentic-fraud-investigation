import React, { useState, useEffect } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  ChevronRight, 
  CheckCircle2, 
  Clock, 
  Brain, 
  Database, 
  ShieldAlert, 
  Terminal, 
  FileText, 
  Sparkles, 
  Activity, 
  Share2, 
  Scale, 
  Check, 
  ExternalLink 
} from 'lucide-react';

export function ChainOfThought({ 
  title = "Drafting forensic investigation report with TigerGraph & 11 Agents", 
  steps = [], 
  duration = "1.8s", 
  isLive = false,
  defaultExpanded = false,
  caseId = "HHG-001"
}) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded || isLive);
  const [expandedStepId, setExpandedStepId] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Live timer tick during active analysis
  useEffect(() => {
    let timer;
    if (isLive) {
      setIsExpanded(true);
      const start = Date.now();
      timer = setInterval(() => {
        setElapsedTime(((Date.now() - start) / 1000).toFixed(1));
      }, 100);
    }
    return () => clearInterval(timer);
  }, [isLive]);

  // Base steps fallback if none provided
  const baseSteps = steps.length > 0 ? steps : [
    {
      id: 'step_1',
      title: 'Recalled 2 precedent cases from ChromaDB Vector Store',
      status: 'completed',
      duration: '0.2s',
      type: 'memory',
      detail: 'Case #CC-0001 (94% similarity, Syndicate Ring) and Case #CC-0141 (87% similarity, Card Testing).',
      codeSnippet: `similar_engine.find_similar_cases(pattern="syndicate_ring", exposure=77.07, top_k=2)`
    },
    {
      id: 'step_2',
      title: 'Executing TigerGraph Cloud query (findSharedDevices)',
      status: 'completed',
      duration: '0.4s',
      type: 'gsql',
      detail: 'Traversed 2-hop edges (USED_DEVICE, OWNED_BY). Discovered 2 linked accounts sharing hardware fingerprint.',
      codeSnippet: `conn.runInstalledQuery("findSharedDevices", {"input_user": ("User_101",)})`
    },
    {
      id: 'step_3',
      title: 'Analyzing 72h transaction velocity & burst frequency',
      status: 'completed',
      duration: '0.3s',
      type: 'velocity',
      detail: 'Window scanned: 4 transactions in 72 hours. Micro-authorization velocity spike detected (>340% over baseline).',
      codeSnippet: `velocity_agent.analyze(window_hours=72, threshold_mult=3.0)`
    },
    {
      id: 'step_4',
      title: 'Scanning device telemetry and proxy exit nodes',
      status: 'completed',
      duration: '0.2s',
      type: 'identity',
      detail: 'Device: POS Terminal | Browser: Headless Chrome / App | Proxy: Direct (Clean) | Region: 444.0 vs Home: 204.0.',
      codeSnippet: `identity_agent.evaluate_fingerprint(device_profile="Device_99 | POS", ip="192.168.1.45")`
    },
    {
      id: 'step_5',
      title: 'Assessing uncertainty & decoupling risk from confidence',
      status: 'completed',
      duration: '0.2s',
      type: 'uncertainty',
      detail: 'Fraud Probability: 0.85 (HIGH) | Confidence: 0.87 (HIGH) | Uncertainty: LOW | Completeness: 82%.',
      codeSnippet: `uncertainty_engine.assess(risk_score=0.85, evidence_completeness=0.82)`
    },
    {
      id: 'step_6',
      title: 'Evaluating Bank Fraud Policy v1.0 governance (Rules R1-R10)',
      status: 'completed',
      duration: '0.2s',
      type: 'policy',
      detail: 'Rule R6 (Syndicate Detection) triggered; Rule R1 (Restraint on premature block) satisfied by multi-signal corroboration.',
      codeSnippet: `policy_engine.evaluate_actions(rules=["R1", "R5", "R6"], exposure=77.07)`
    },
    {
      id: 'step_7',
      title: 'Formulating Next-Best-Action with Human-In-The-Loop route',
      status: 'completed',
      duration: '0.2s',
      type: 'action',
      detail: 'Prescribed Final Action: BLOCK_CARD + CREATE_CASE. Assigned Approval Route: L1 (Senior Fraud Specialist sign-off required).',
      codeSnippet: `action_engine.assign_route(action="BLOCK_CARD", route="L1", requires_hitl=True)`
    },
    {
      id: 'step_8',
      title: 'Enforcing FinCEN 31 CFR § 1020.320 SAR regulatory rules',
      status: 'completed',
      duration: '0.1s',
      type: 'sar',
      detail: 'SAR Filing Determination: EXEMPT (Total exposure $77.07 is below $1,000 threshold and no insider participation).',
      codeSnippet: `sar_generator.evaluate(exposure=77.07, threshold=1000.0, syndicate=False)`
    },
    {
      id: 'step_9',
      title: 'Master Decision Validator 4-Step CoT audit verified',
      status: 'completed',
      duration: '0.3s',
      type: 'validator',
      detail: 'Step A (Graph Proof): PASS | Step B (Policy Route): APPROVED | Step C (Memory Precedent): 94% MATCH | Step D (Gate): PASSED.',
      codeSnippet: `validator.audit(forensics=PASS, policy=APPROVED, precedent=0.94, gate=OPEN)`
    }
  ];

  // Dynamic live step progression during active investigation
  const effectiveSteps = isLive ? baseSteps.map((step, idx) => {
    const elapsed = parseFloat(elapsedTime);
    const stepThreshold = (idx + 1) * 0.22;
    const isPast = elapsed >= stepThreshold;
    const isCurrent = elapsed < stepThreshold && (idx === 0 || elapsed >= (idx * 0.22));
    return {
      ...step,
      status: isPast ? 'completed' : isCurrent ? 'running' : 'pending',
      duration: isPast ? (step.duration || '0.2s') : isCurrent ? 'executing...' : 'queued'
    };
  }) : baseSteps;

  const getStepIcon = (type, status) => {
    if (status === 'running') {
      return (
        <span className="relative flex h-3 w-3 mr-0.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
        </span>
      );
    }
    if (status === 'pending') {
      return <span className="inline-block w-2.5 h-2.5 rounded-full border border-slate-700 mx-0.5" />;
    }

    switch (type) {
      case 'memory': return <Brain className="w-3.5 h-3.5 text-indigo-400" />;
      case 'gsql': return <Terminal className="w-3.5 h-3.5 text-cyan-400" />;
      case 'velocity': return <Activity className="w-3.5 h-3.5 text-amber-400" />;
      case 'identity': return <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />;
      case 'uncertainty': return <Scale className="w-3.5 h-3.5 text-blue-400" />;
      case 'policy': return <FileText className="w-3.5 h-3.5 text-emerald-400" />;
      case 'action': return <Check className="w-3.5 h-3.5 text-rose-400" />;
      case 'sar': return <Database className="w-3.5 h-3.5 text-amber-400" />;
      case 'validator': return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
      default: return <Sparkles className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const toggleStep = (stepId) => {
    setExpandedStepId(expandedStepId === stepId ? null : stepId);
  };

  const displayTime = isLive ? `${elapsedTime}s` : duration;

  return (
    <div className="w-full my-2 font-sans transition-all duration-200">
      {/* Accordion Header - Matches ChatGPT / Claude / Antigravity Style */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="group flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-workspace-cardHover/60 cursor-pointer select-none transition-colors border border-transparent hover:border-workspace-border/50 text-slate-400 hover:text-slate-200"
      >
        <div className="flex items-center gap-2 min-w-0">
          {/* Animated dot indicator */}
          <div className="relative flex items-center justify-center flex-shrink-0">
            {isLive ? (
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
              </span>
            ) : (
              <span className="inline-block w-2 h-2 rounded-full bg-slate-500 group-hover:bg-slate-400 transition-colors" />
            )}
          </div>

          {/* Title */}
          <span className="text-xs font-normal truncate text-slate-300 group-hover:text-white transition-colors">
            {title}
          </span>
        </div>

        {/* Right side: Duration + Chevron */}
        <div className="flex items-center gap-1.5 flex-shrink-0 ml-3">
          <span className="text-[11px] font-mono text-slate-400 group-hover:text-slate-300">
            {displayTime}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-200" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-200" />
          )}
        </div>
      </div>

      {/* Expanded Chain of Thought Dropdown Container */}
      {isExpanded && (
        <div className="mt-1.5 ml-2.5 pl-3 border-l-2 border-slate-700/60 space-y-1 py-1">
          {effectiveSteps.map((step, idx) => {
            const isStepOpen = expandedStepId === step.id;
            const hasExtra = step.detail || step.codeSnippet;

            return (
              <div 
                key={step.id || idx}
                className="group/item rounded-md transition-colors"
              >
                {/* Step Row */}
                <div 
                  onClick={() => hasExtra && toggleStep(step.id)}
                  className={`flex items-center justify-between py-1 px-2 rounded cursor-pointer select-none text-xs transition-colors ${
                    isStepOpen 
                      ? 'bg-workspace-card/80 text-white' 
                      : 'hover:bg-workspace-card/40 text-slate-300 hover:text-slate-100'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0 pr-2">
                    <span className="flex-shrink-0 opacity-80 group-hover/item:opacity-100">
                      {getStepIcon(step.type, step.status)}
                    </span>
                    <span className={`truncate text-[12px] font-normal tracking-tight ${
                      step.status === 'running' ? 'text-cyan-300 font-medium' : step.status === 'pending' ? 'text-slate-500' : 'text-slate-300'
                    }`}>
                      {step.title}
                    </span>
                  </div>

                  <div className="flex items-center gap-1 flex-shrink-0 text-slate-400">
                    {step.duration && (
                      <span className={`text-[10px] font-mono hidden sm:inline ${
                        step.status === 'running' ? 'text-cyan-400 animate-pulse font-semibold' : 'text-slate-400'
                      }`}>
                        {step.duration}
                      </span>
                    )}
                    {hasExtra && (
                      <ChevronRight className={`w-3 h-3 text-slate-400 transition-transform duration-200 ${
                        isStepOpen ? 'rotate-90 text-blue-400' : 'group-hover/item:text-slate-200'
                      }`} />
                    )}
                  </div>
                </div>

                {/* Step Nested Detail / Telemetry */}
                {isStepOpen && (
                  <div className="mt-1 mb-2 ml-6 mr-1 p-2.5 rounded-lg bg-[#0e131b] border border-workspace-border/70 text-[11px] font-sans space-y-2 shadow-inner">
                    {step.detail && (
                      <div className="text-slate-300 leading-relaxed">
                        <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block mb-0.5">
                          Evidence Telemetry
                        </span>
                        {step.detail}
                      </div>
                    )}

                    {step.codeSnippet && (
                      <div className="space-y-1">
                        <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider block">
                          Execution / Tool Call
                        </span>
                        <div className="bg-[#080b10] p-2 rounded border border-slate-800 text-cyan-300 font-mono text-[10.5px] overflow-x-auto whitespace-pre">
                          {step.codeSnippet}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
