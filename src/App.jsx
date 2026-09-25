import React, { useState, useEffect, useRef } from 'react';
import { Bot, MessageSquare, Target, Activity, CheckCircle, ShieldAlert, FileText, Database, User, Search, Loader2, Send, Mic, Paperclip, Plus, Moon, Sun } from 'lucide-react';
import { PegaGraphCanvas } from './components/PegaGraphCanvas';
import { CaseTimeline } from './components/CaseTimeline';
import { AgentActivity } from './components/AgentActivity';
import { NextBestAction } from './components/NextBestAction';
import { EvidenceDrawer } from './components/EvidenceDrawer';
import { PolicyModal } from './components/PolicyModal';
import { ChatMessage } from './components/ChatMessage';

export function App() {
  const [activeCaseId, setActiveCaseId] = useState(null);
  const [cases, setCases] = useState([]);
  const [caseData, setCaseData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Right Panel Tabs: 'graph', 'agents', 'timeline', 'actions'
  const [rightPanelTab, setRightPanelTab] = useState('graph');
  
  // Chat
  const [chatMessages, setChatMessages] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [theme, setTheme] = useState('dark');
  const [showTemplates, setShowTemplates] = useState(false);
  
  useEffect(() => {
    // Load chat sessions from localStorage
    const sessions = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('chat_history_')) {
        const id = key.replace('chat_history_', '');
        const customTitle = localStorage.getItem('chat_title_' + id); sessions.push({ id, title: customTitle || 'Investigation: ' + id });
      }
    }
    setChatSessions(sessions);
  }, [activeCaseId]);

  
  const handleRenameSession = (id, newTitle) => {
    localStorage.setItem('chat_title_' + id, newTitle);
    setChatSessions(prev => prev.map(s => s.id === id ? { ...s, title: newTitle } : s));
  };

  const handleDeleteSession = (id) => {
    localStorage.removeItem('chat_history_' + id);
    setChatSessions(prev => prev.filter(s => s.id !== id));
    if (activeCaseId === id) {
      setChatMessages([]);
    }
  };

  const handleNewChat = () => {
    const newId = 'CASE-NEW-' + Math.floor(Math.random() * 1000);
    setActiveCaseId(newId);
    
    // Initialize empty ad-hoc chat
    const initial = [
      {
        id: 'init-ai',
        sender: 'ai',
        time: new Date().toLocaleTimeString(),
        text: '## New Ad-Hoc Investigation: ' + newId + '\n\n' +
          'No specific TigerGraph case selected. You can ask me general fraud analysis questions, or I can help you investigate specific entities.'
      }
    ];
    setChatMessages(initial);
    localStorage.setItem('chat_history_' + newId, JSON.stringify(initial));
    localStorage.setItem('chat_title_' + newId, 'New Investigation');
    
    // Update Sidebar state manually so we don't depend entirely on the useEffect
    setChatSessions(prev => {
       const exists = prev.find(p => p.id === newId);
       if (!exists) return [...prev, { id: newId, title: 'New Investigation' }];
       return prev;
    });
  };

  
  const fileInputRef = useRef(null);

  const handleStopGeneration = () => {
    // If we had an AbortController for streaming, we would abort it here.
    // Since we don't have the explicit global abort controller setup here, we just mock the stop.
    setIsAnalyzing(false);
  };

  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputMsg(prev => prev + (prev ? ' ' : '') + transcript);
    };
    recognition.start();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setInputMsg(prev => prev + (prev ? '\n' : '') + '[Attached File: ' + file.name + ']');
    }
  };

  const [inputMsg, setInputMsg] = useState('');
  const chatEndRef = useRef(null);

  // Modals / Evidence
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [isPolicyModalOpen, setIsPolicyModalOpen] = useState(false);

  // Fetch initial case list
  useEffect(() => {
    fetch('/api/cases')
      .then(res => res.json())
      .then(data => {
        if (data && data.cases) {
          setCases(data.cases);
          if (data.cases.length > 0 && !activeCaseId) {
            setActiveCaseId(data.cases[0].case_id);
          }
        }
      })
      .catch(err => console.error("Error loading cases:", err));
  }, []);

  // Fetch Case Detail
  useEffect(() => {
    if (!activeCaseId) return;
    setIsAnalyzing(true);
    fetch(`/api/case?id=${activeCaseId}`)
      .then(res => res.json())
      .then(data => {
        setCaseData(data);
        setIsAnalyzing(false);
        loadChatHistory(activeCaseId, data);
      })
      .catch(err => {
        console.error("Error loading case detail:", err);
        setIsAnalyzing(false);
      });
  }, [activeCaseId]);

  const loadChatHistory = (cid, data) => {
    const key = `chat_history_${cid}`;
    const saved = localStorage.getItem(key);
    if (saved) {
      setChatMessages(JSON.parse(saved));
    } else {
      const c = data?.case || {};
      const initial = [
        {
          id: 'init-ai',
          sender: 'ai',
          time: new Date().toLocaleTimeString(),
          text: `## Investigation Initialized: ${cid}\n\n` +
            `TigerGraph Agentic Forensics active. Case triggered by **${c.trigger_type || 'Unknown'}**.\n\n` +
            `� **Primary Entity**: ${c.customer_id || 'Unknown'}\n` +
            `� **Exposure**: $${Number(c.exposure_usd || 0).toLocaleString()}\n` +
            `� **Pattern**: ${c.pattern || 'Unknown'}\n\n` +
            `How would you like to proceed with this investigation? You can ask me to run an agent pipeline, query the graph, or analyze relationships.`
        }
      ];
      setChatMessages(initial);
      localStorage.setItem(key, JSON.stringify(initial));
    }
  };

  const saveChatHistory = (cid, msgs) => {
    localStorage.setItem(`chat_history_${cid}`, JSON.stringify(msgs));
  };

  
  const handleRegenerate = (msgId) => {
    const index = chatMessages.findIndex(m => m.id === msgId);
    if (index === -1) return;
    const targetMsg = chatMessages[index];
    let promptText = '';
    if (targetMsg.sender === 'ai') {
       if (index > 0 && chatMessages[index - 1].sender === 'user') {
           promptText = chatMessages[index - 1].text;
           setChatMessages(prev => prev.slice(0, index));
       } else {
           promptText = 'Please elaborate further on your previous response.';
           setChatMessages(prev => prev.slice(0, index));
       }
    } else {
       promptText = targetMsg.text;
       setChatMessages(prev => prev.slice(0, index));
    }
    handleSendMessage(null, promptText);
  };

  const handleEditMessage = (msgId, newText) => {
    const index = chatMessages.findIndex(m => m.id === msgId);
    if (index === -1) return;
    setChatMessages(prev => prev.slice(0, index));
    handleSendMessage(null, newText);
  };

  const handleSendMessage = async (e, textOverride = null) => {
    if (e) e.preventDefault();
    if (!inputMsg.trim() || !activeCaseId) return;

    const userText = textOverride || inputMsg;
    setInputMsg('');
    
    const newMsgs = [...chatMessages, {
      id: Date.now().toString(),
      sender: 'user',
      time: new Date().toLocaleTimeString(),
      text: userText
    }];
    setChatMessages(newMsgs);
    saveChatHistory(activeCaseId, newMsgs);
    setIsAnalyzing(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: activeCaseId,
          message: userText,
          history: newMsgs.map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
        })
      });
      const resData = await response.json();
      
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        time: new Date().toLocaleTimeString(),
        text: resData.reply || "No response received.",
        agent: "Chief Orchestrator"
      };
      
      const finalMsgs = [...newMsgs, aiResponse];
      setChatMessages(finalMsgs);
      saveChatHistory(activeCaseId, finalMsgs);
    } catch (error) {
      console.error(error);
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        time: new Date().toLocaleTimeString(),
        text: "Error connecting to AI backend. Ensure Ollama and serve.py are running.",
        isError: true
      };
      const finalMsgs = [...newMsgs, errorMsg];
      setChatMessages(finalMsgs);
      saveChatHistory(activeCaseId, finalMsgs);
    }
    
    setIsAnalyzing(false);
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isAnalyzing]);

  const c = caseData?.case || {};
  const risk = c.fraud_probability ? Math.round(c.fraud_probability * 100) : 0;
  const conf = c.confidence_score ? Math.round(c.confidence_score * 100) : 0;

  return (
    <div className="flex h-screen bg-[#0E1015] text-[#D1D5DB] font-sans overflow-hidden">
      
      {/* LEFT COLUMN: CASE EXPLORER */}
      <aside className={`w-64 flex-shrink-0 flex flex-col border-r transition-colors ${theme === 'dark' ? 'border-[#1C1E24] bg-[#12141A]' : 'border-slate-300 bg-slate-50'}`}>
          <div className={`p-4 border-b ${theme === 'dark' ? 'border-[#1C1E24]' : 'border-slate-300'}`}>
            <div className={`flex items-center gap-2 font-bold tracking-tight ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
              <div className="w-7 h-7 rounded overflow-hidden flex items-center justify-center flex-shrink-0">
                  <img src="/savanna-logo.png" alt="Logo" className="w-full h-full object-cover" />
                </div>
              <span>Savanna X Aegis</span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <div className="text-[10px] text-[#6B7280] uppercase tracking-wider font-semibold">
                Agentic Workspace
              </div>
              <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} className="p-1 text-slate-400 hover:text-[#10B981]">
                {theme === 'dark' ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
          
          <div className="p-3">
            <button onClick={handleNewChat} className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-[#10B981] hover:bg-[#34D399] text-black font-bold text-xs cursor-pointer transition-all shadow-md">
              <Plus className="w-3.5 h-3.5" />
              <span>New Investigation</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <div className="text-[10px] font-bold text-slate-500 uppercase px-2 mb-2 mt-2">Active Cases</div>
            {cases.map((c) => {
              const isActive = activeCaseId === c.case_id;
              return (
                <button
                  key={c.case_id}
                  onClick={() => setActiveCaseId(c.case_id)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg flex flex-col gap-1 transition-all ${isActive ? 'bg-[#1C1E24] border border-[#2A2D35] shadow-sm' : 'hover:bg-[#1C1E24]/50 border border-transparent'}`}
                >
                  <div className={`text-xs font-bold font-mono flex items-center gap-2 ${isActive ? 'text-[#10B981]' : 'text-slate-300'}`}>
                    <Activity className="w-3 h-3" />
                    {c.case_id}
                  </div>
                  <div className="text-[10px] text-[#9CA3AF] truncate">
                    {c.pattern || c.status}
                  </div>
                </button>
              )
            })}
            
            <div className="text-[10px] font-bold text-slate-500 uppercase px-2 mb-2 mt-4">Chat History</div>
            {chatSessions.map((session) => (
               <div key={session.id} className="group flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#1C1E24]/50 transition-all cursor-pointer" onClick={() => setActiveCaseId(session.id)}>
                 <div className="flex items-center gap-2 overflow-hidden">
                   <MessageSquare className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                   <span className="text-xs text-slate-300 truncate">{session.title}</span>
                 </div>
                 <button onClick={(e) => { e.stopPropagation(); handleDeleteSession(session.id); }} className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition-opacity">
                   <ShieldAlert className="w-3 h-3" />
                 </button>
               </div>
            ))}
          </div>
        </aside>

      {/* CENTER COLUMN: CHATGPT-STYLE WORKSPACE */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#0A0C10]">
        
        {/* Compact Header Summary */}
        <header className="h-14 flex-shrink-0 border-b border-[#1C1E24] px-6 flex items-center justify-between bg-[#0A0C10]/80 backdrop-blur">
          <div className="flex items-center gap-6">
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="text-[#10B981]">?</span> {activeCaseId || 'No Case'}
            </h1>
            <div className="flex gap-4 text-xs font-mono text-[#9CA3AF]">
              <span className="flex items-center gap-1">
                Risk: <strong className={risk >= 75 ? 'text-red-400' : 'text-white'}>{risk}%</strong>
              </span>
              <span className="flex items-center gap-1">
                Conf: <strong className="text-white">{conf}%</strong>
              </span>
              <span className="flex items-center gap-1">
                Status: <strong className="text-[#10B981] uppercase">{c.status || 'OPEN'}</strong>
              </span>
              {isAnalyzing && (
                <span className="flex items-center gap-1 text-[#10B981] ml-4 bg-[#10B981]/10 px-2 py-0.5 rounded">
                  <Activity className="w-3 h-3 animate-pulse" /> Investigating...
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Scrollable Conversation */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-10 space-y-8 scroll-smooth">
            {chatMessages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto opacity-70">
                <img src="/savanna-logo.png" className="w-16 h-16 mb-6 opacity-50 grayscale" alt="Logo" />
                <h2 className="text-2xl font-bold text-white mb-2">How can I help you investigate today?</h2>
                <p className="text-slate-400 text-sm mb-8">Select an active case from the sidebar or choose a prompt below to begin.</p>
                
                <div className="grid grid-cols-2 gap-4 w-full">
                  {[
                    "Summarize the evidence for this case.",
                    "Why was this transaction flagged?",
                    "Show me all connected devices.",
                    "Find suspicious relationships in the graph."
                  ].map((prompt, i) => (
                    <button 
                      key={i} 
                      onClick={() => handleSendMessage(null, prompt)}
                      className="p-4 bg-[#1C1E24] hover:bg-[#2A2D35] border border-[#2A2D35] hover:border-[#10B981]/50 rounded-xl text-left text-sm text-slate-300 transition-all shadow-sm"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            )}
                    {chatMessages.map((msg) => (
            <ChatMessage 
              key={msg.id} 
              message={msg} 
              onOpenEvidence={setSelectedEntity}
              onViewGraph={() => setRightPanelTab('graph')}
              onViewPolicy={() => setRightPanelTab('actions')}
              onViewSimilar={() => setRightPanelTab('timeline')}
              onReviewAction={() => setRightPanelTab('actions')}
              onRegenerate={handleRegenerate}
              onEdit={handleEditMessage}
            />
          ))}
          {isAnalyzing && (
            <div className="flex gap-4 max-w-4xl mx-auto">
              <div className="w-8 h-8 rounded-full bg-[#10B981]/10 border border-[#10B981]/30 flex items-center justify-center flex-shrink-0">
                <Loader2 className="w-4 h-4 text-[#10B981] animate-spin" />
              </div>
              <div className="text-sm text-[#9CA3AF] p-4 flex items-center">
                Agents actively investigating...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* ChatGPT-style Input Box */}
        <div className="p-4 sm:p-6 bg-gradient-to-t from-[#0A0C10] via-[#0A0C10] to-transparent">
          
          {isAnalyzing && (
            <div className="flex justify-center mb-2">
              <button onClick={handleStopGeneration} className="flex items-center gap-2 bg-[#1C1E24] hover:bg-[#2A2D35] border border-red-500/30 text-red-400 px-4 py-2 rounded-full text-xs font-medium transition-colors shadow-lg">
                <span className="w-2 h-2 bg-red-500 rounded-sm animate-pulse"></span>
                Stop generating
              </button>
            </div>
          )}
          <form onSubmit={(e) => handleSendMessage(e)} className="max-w-4xl mx-auto relative flex flex-col bg-[#1C1E24] border border-[#2A2D35] rounded-2xl focus-within:border-[#10B981] focus-within:shadow-[0_0_15px_rgba(16,185,129,0.1)] transition-all">
            <textarea
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(e);
                } else if (e.key === 'Escape') {
                  handleStopGeneration();
                }
              }}
              placeholder="Ask anything about this investigation... (e.g. 'Show me all connected devices')"
              className="w-full bg-transparent p-4 text-sm text-white placeholder-[#6B7280] outline-none resize-none"
              rows={1}
              style={{ minHeight: '56px', maxHeight: '200px' }}
            />
            <div className="flex items-center justify-between px-3 pb-3">
              <div className="flex items-center gap-2 text-slate-400">
                <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" /><button type="button" onClick={() => fileInputRef.current?.click()} className="p-2 hover:bg-[#2A2D35] hover:text-white rounded-lg transition-colors" title="Attach file">
                  <Paperclip className="w-4 h-4" />
                </button>
                <button type="button" onClick={() => handleVoiceInput()} className="p-2 hover:bg-[#2A2D35] hover:text-white rounded-lg transition-colors" title="Voice input">
                  <Mic className="w-4 h-4" />
                </button>
              </div>
              <button
                type="submit"
                disabled={!inputMsg.trim() || isAnalyzing}
                className="w-8 h-8 bg-[#10B981] hover:bg-[#34D399] disabled:bg-[#2A2D35] disabled:text-[#6B7280] text-black rounded-xl flex items-center justify-center transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>

          <div className="text-center text-[10px] text-[#4B5563] mt-3 font-mono">
            Responses driven by TigerGraph analytics and Ollama local reasoning engine.
          </div>
        </div>
      </main>

      {/* RIGHT COLUMN: CONTEXTUAL VIEWS */}
      <aside className="w-[450px] flex-shrink-0 flex flex-col border-l border-[#1C1E24] bg-[#12141A]">
        {/* Tabs */}
        <div className="flex border-b border-[#1C1E24] px-2 pt-2 bg-[#0E1015]">
          <button onClick={() => setRightPanelTab('graph')} className={`px-4 py-2 text-xs font-bold font-mono border-b-2 transition-colors ${rightPanelTab === 'graph' ? 'border-[#10B981] text-[#10B981]' : 'border-transparent text-[#6B7280] hover:text-white'}`}>Graph</button>
          <button onClick={() => setRightPanelTab('agents')} className={`px-4 py-2 text-xs font-bold font-mono border-b-2 transition-colors ${rightPanelTab === 'agents' ? 'border-[#10B981] text-[#10B981]' : 'border-transparent text-[#6B7280] hover:text-white'}`}>Agents</button>
          <button onClick={() => setRightPanelTab('timeline')} className={`px-4 py-2 text-xs font-bold font-mono border-b-2 transition-colors ${rightPanelTab === 'timeline' ? 'border-[#10B981] text-[#10B981]' : 'border-transparent text-[#6B7280] hover:text-white'}`}>Timeline</button>
          <button onClick={() => setRightPanelTab('actions')} className={`px-4 py-2 text-xs font-bold font-mono border-b-2 transition-colors ${rightPanelTab === 'actions' ? 'border-[#10B981] text-[#10B981]' : 'border-transparent text-[#6B7280] hover:text-white'}`}>Actions</button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden relative bg-[#0A0C10]">
          {rightPanelTab === 'graph' && (
            <div className="absolute inset-0">
              <PegaGraphCanvas 
                caseId={activeCaseId}
                caseData={caseData} 
                onSelectNode={(node) => setSelectedEntity(node)} 
              />
            </div>
          )}
          
          {rightPanelTab === 'agents' && (
            <div className="absolute inset-0 overflow-y-auto p-4 bg-[#12141A]">
              <AgentActivity caseData={caseData} isAnalyzing={isAnalyzing} />
            </div>
          )}

          {rightPanelTab === 'timeline' && (
            <div className="absolute inset-0 overflow-y-auto p-4 bg-[#12141A]">
              <CaseTimeline caseId={activeCaseId} />
            </div>
          )}

          {rightPanelTab === 'actions' && (
            <div className="absolute inset-0 overflow-y-auto p-4 bg-[#12141A]">
              <NextBestAction 
                caseData={caseData} 
                onApprove={() => alert("Action Approved")} 
                onReject={() => alert("Action Rejected")} 
                onRequestEvidence={() => alert("Requesting Evidence")}
                onEscalate={() => alert("Escalated to L2")}
                isProcessing={isAnalyzing} 
              />
            </div>
          )}
        </div>
      </aside>

      {/* Entity Drawer Overlay */}
      {selectedEntity && (
        <EvidenceDrawer
          entity={selectedEntity}
          onClose={() => setSelectedEntity(null)}
          onInvestigateEntity={(ent) => {
            setSelectedEntity(null);
            setInputMsg(`Investigate relationships for entity ${ent.label || ent.id}`);
            // Focus input or trigger send automatically?
          }}
        />
      )}
      
      {/* Policy Modal Overlay */}
      <PolicyModal
        isOpen={isPolicyModalOpen}
        onClose={() => setIsPolicyModalOpen(false)}
      />
    </div>
  );
}

export default App;


