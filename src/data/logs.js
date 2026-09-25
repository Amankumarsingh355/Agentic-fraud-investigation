export const initialConsoleLogs = [
  { id: 1, time: "12:42:17", sender: "AGENT_2", color: "cyan", text: "Shared IP matched (192.168.1.23)" },
  { id: 2, time: "12:42:19", sender: "AGENT_8", color: "crimson", text: "Rule R6 Triggered (Shared device/IP fraud syndicate)" },
  { id: 3, time: "12:42:22", sender: "AGENT_3", color: "cyan", text: "Ring detection completed (3-hop loop found)" },
  { id: 4, time: "12:42:26", sender: "AGENT_9", color: "amber", text: "Early stop condition met (confidence > 0.9)" },
  { id: 5, time: "12:42:28", sender: "AGENT_11", color: "cyan", text: "Preparing JSON payload for response..." },
  { id: 6, time: "12:42:30", sender: "SYS", color: "purple", text: "Analysis completed. Awaiting action." }
];

export const scanSimulationLogs = [
  { step: 1, time: "12:43:01", sender: "AGENT_1", color: "emerald", text: "Signal ingested: Webhook trigger TXN #3514030 ($15,000.00)" },
  { step: 2, time: "12:43:02", sender: "AGENT_2", color: "cyan", text: "Executing pyTigerGraph GSQL multi-hop query: trace_fraud_ring(user_id='User_101', max_hops=3)" },
  { step: 2, time: "12:43:03", sender: "AGENT_2", color: "cyan", text: "Shared node discovered: DEVICE_99 links USER_101 with known fraudster USER_882" },
  { step: 3, time: "12:43:04", sender: "AGENT_3", color: "cyan", text: "Ring detection algorithm completed: 3-hop circular loop ($15k) confirmed" },
  { step: 4, time: "12:43:05", sender: "AGENT_4", color: "emerald", text: "Case TG-CASE-2026-8819 opened. Immutable audit trail instantiated" },
  { step: 5, time: "12:43:06", sender: "AGENT_5", color: "cyan", text: "Memory RAG: 94% vector match with precedent Case #HHG-001 (Syndicate Mule Ring)" },
  { step: 6, time: "12:43:07", sender: "AGENT_6", color: "muted", text: "Step-up validation: Bypassed due to critical risk score (0.94 >= 0.90)" },
  { step: 7, time: "12:43:08", sender: "AGENT_7", color: "emerald", text: "Action Engine: Recommendation generated -> 'Block Transaction & Freeze Account'" },
  { step: 8, time: "12:43:09", sender: "AGENT_8", color: "crimson", text: "Policy Rule R6 verified. FinCEN SAR threshold ($1k bank loss) triggered" },
  { step: 9, time: "12:43:10", sender: "AGENT_9", color: "amber", text: "Early stop efficiency gate: Halting further hops due to high evidence density (>0.90)" },
  { step: 10, time: "12:43:11", sender: "AGENT_10", color: "cyan", text: "Explainability narrative formulated for regulatory and forensic audit" },
  { step: 11, time: "12:43:12", sender: "AGENT_11", color: "cyan", text: "Strict 4-Step Chain-of-Thought (CoT) audit passed. Emitting production FrontendReportSchema JSON" },
  { step: 12, time: "12:43:13", sender: "SYS", color: "emerald", text: "SCAN COMPLETE // 98.4% Confidence // Case Status: RESOLVED // Action: FREEZE ACCOUNT" }
];
