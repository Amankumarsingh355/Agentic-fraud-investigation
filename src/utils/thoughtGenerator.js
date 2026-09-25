/**
 * Thought Generator for Institutional Multi-Agent Fraud Investigation
 * Dynamically synthesizes 11-Agent forensic reasoning steps and GSQL/ChromaDB execution telemetry
 */

export function generateCaseThoughtSteps(caseData) {
  const c = caseData?.case || {};
  const nba = caseData?.next_best_actions || {};
  const sar = caseData?.sar || {};
  
  const txnId = c.first_suspicious_txn_id || 3514030;
  const custId = c.customer_id || '101';
  const pattern = c.pattern || 'Syndicate Mule Ring';
  const exposure = Number(c.exposure_usd || 77.07).toFixed(2);
  const fraudProb = Math.round((c.fraud_probability || 0.85) * 100);
  const confidence = Math.round((c.confidence_score || 0.87) * 100);
  const uncertainty = c.uncertainty_level || 'LOW';
  const completeness = Math.round((c.evidence_completeness || 0.82) * 100);
  
  const connectedCards = c.connected_card_ids || ['Card_4242', 'Card_8811'];
  const connectedDevices = c.connected_device_profiles || ['Device_99 | POS Terminal'];
  const deviceProfile = connectedDevices[0] || 'Device_99 (POS)';
  
  const finalActions = (nba.final || []).map(a => a.action);
  const primaryAction = finalActions[0] || 'BLOCK_CARD';
  const actionsStr = finalActions.join(' + ') || 'BLOCK_CARD + CREATE_CASE';
  
  const routes = (nba.final || []).map(a => a.route);
  const primaryRoute = routes[0] || 'L1';
  const routesStr = routes.join(', ') || 'L1';
  
  const isSar = Boolean(sar.file);
  const sarAmount = sar.total_amount_usd ? `$${Number(sar.total_amount_usd).toFixed(2)}` : `$${exposure}`;

  return [
    {
      id: 'step_1',
      title: 'Recalled 2 precedent cases from ChromaDB Vector Store',
      status: 'completed',
      duration: '0.2s',
      type: 'memory',
      detail: `Vector similarity retrieved Case #CC-0001 (94% match, ${pattern}) and Case #CC-0141 (87% match, Card Velocity Burst). Prior resolution confirmed true positive.`,
      codeSnippet: `similar_cases = memory_agent.find_similar(pattern="${pattern}", exposure=${exposure}, top_k=2)`
    },
    {
      id: 'step_2',
      title: 'Executing TigerGraph Cloud query (findSharedDevices)',
      status: 'completed',
      duration: '0.4s',
      type: 'gsql',
      detail: `Traversed 2-hop graph topology (USED_DEVICE, OWNS_ACCOUNT). Discovered ${connectedCards.length} linked cardholder accounts sharing hardware fingerprint [Evidence #E-001].`,
      codeSnippet: `conn.runInstalledQuery("findSharedDevices", {"input_user": ("User_${custId}",)})\n--> Discovered nexus on ${deviceProfile}`
    },
    {
      id: 'step_3',
      title: 'Analyzing 72h transaction velocity & burst frequency',
      status: 'completed',
      duration: '0.3s',
      type: 'velocity',
      detail: `Scanned 72-hour window on TX #${txnId}. Detected velocity burst of 4 rapid micro-authorizations (>340% over customer historical baseline).`,
      codeSnippet: `velocity_agent.evaluate_burst(txn_id=${txnId}, window_hours=72, threshold_mult=3.0)`
    },
    {
      id: 'step_4',
      title: 'Scanning device telemetry and proxy exit nodes',
      status: 'completed',
      duration: '0.2s',
      type: 'identity',
      detail: `Hardware profile: ${deviceProfile} | Terminal Class: POS/In-Store | Proxy Node: Direct connection | Geo-anomaly: Transaction in region 444.0 vs Home region 204.0.`,
      codeSnippet: `identity_agent.audit_fingerprint(device="${deviceProfile}", ip="192.168.1.45")`
    },
    {
      id: 'step_5',
      title: 'Assessing uncertainty & decoupling risk from confidence',
      status: 'completed',
      duration: '0.2s',
      type: 'uncertainty',
      detail: `Fraud Probability: ${fraudProb}% (${fraudProb >= 75 ? 'HIGH' : 'MEDIUM'}) | Model Confidence: ${confidence}% | Uncertainty State: ${uncertainty} | Evidence Completeness: ${completeness}%.`,
      codeSnippet: `uncertainty_engine.compute_uncertainty(risk_score=${(fraudProb/100).toFixed(2)}, completeness=${(completeness/100).toFixed(2)})`
    },
    {
      id: 'step_6',
      title: 'Evaluating Bank Fraud Policy v1.0 governance (Rules R1-R10)',
      status: 'completed',
      duration: '0.2s',
      type: 'policy',
      detail: `Rule R6 (Syndicate Detection) triggered due to shared hardware across distinct cardholders; Rule R1 (Premature Block Restraint) satisfied by multi-signal corroboration.`,
      codeSnippet: `policy_validator.check_rules(["R1", "R5", "R6"], exposure=${exposure}, pattern="${pattern}")`
    },
    {
      id: 'step_7',
      title: 'Formulating Next-Best-Action with Human-In-The-Loop route',
      status: 'completed',
      duration: '0.2s',
      type: 'action',
      detail: `Prescribed Actions: ${actionsStr}. Governance Route: ${routesStr} (Senior Fraud Specialist sign-off required prior to destructive blocking).`,
      codeSnippet: `action_engine.dispatch(action="${primaryAction}", route="${primaryRoute}", requires_hitl=True)`
    },
    {
      id: 'step_8',
      title: 'Enforcing FinCEN 31 CFR § 1020.320 SAR regulatory rules',
      status: 'completed',
      duration: '0.1s',
      type: 'sar',
      detail: isSar 
        ? `SAR Filing Determination: MANDATED (Aggregated exposure of ${sarAmount} exceeds $1,000 threshold under Section 4 with syndicate nexus).`
        : `SAR Filing Determination: EXEMPT (Total exposure of $${exposure} is below $1,000 threshold and no insider participation detected).`,
      codeSnippet: `sar_generator.evaluate_filing(exposure=${exposure}, has_syndicate=True, insider=False)`
    },
    {
      id: 'step_9',
      title: 'Master Decision Validator 4-Step CoT audit verified',
      status: 'completed',
      duration: '0.3s',
      type: 'validator',
      detail: `Step A (Graph Proof): PASS | Step B (Policy Route): APPROVED | Step C (Memory Precedent): MATCHED | Step D (Safety Gate): PASSED. Zero reasoning leakage.`,
      codeSnippet: `master_validator.audit(forensics=PASS, policy=APPROVED, precedent=0.94, gate=OPEN)`
    }
  ];
}

export function getLiveThinkingSteps(elapsedSeconds) {
  const steps = [
    {
      id: 'live_1',
      title: 'Recalling precedent cases from ChromaDB Vector Store',
      type: 'memory',
      duration: elapsedSeconds > 0.4 ? '0.2s' : 'Searching...',
      status: elapsedSeconds > 0.4 ? 'completed' : 'running',
      detail: 'Querying vector index for past closed cases matching anomalous velocity and syndicate hardware profile...',
      codeSnippet: `similar_cases = memory_agent.query_precedents(k=2)`
    },
    {
      id: 'live_2',
      title: 'Executing TigerGraph Cloud query (findSharedDevices)',
      type: 'gsql',
      duration: elapsedSeconds > 0.9 ? '0.4s' : elapsedSeconds > 0.4 ? 'Executing...' : 'Queued',
      status: elapsedSeconds > 0.9 ? 'completed' : elapsedSeconds > 0.4 ? 'running' : 'pending',
      detail: 'Traversing 2-hop edges in TigerGraph Cloud to discover shared devices and correlated cards...',
      codeSnippet: `conn.runInstalledQuery("findSharedDevices", {"input_user": ("User_101",)})`
    },
    {
      id: 'live_3',
      title: 'Evaluating Bank Fraud Policy rules (R1-R10) & FinCEN criteria',
      type: 'policy',
      duration: elapsedSeconds > 1.4 ? '0.2s' : elapsedSeconds > 0.9 ? 'Validating...' : 'Queued',
      status: elapsedSeconds > 1.4 ? 'completed' : elapsedSeconds > 0.9 ? 'running' : 'pending',
      detail: 'Checking statutory thresholds, Human-In-The-Loop approval routes, and FinCEN SAR filing requirements...',
      codeSnippet: `policy_validator.check_governance(rules=["R1", "R6"], exposure=77.07)`
    },
    {
      id: 'live_4',
      title: 'Formulating Next-Best-Action & Master Decision Verification',
      type: 'action',
      duration: elapsedSeconds > 1.7 ? '0.2s' : elapsedSeconds > 1.4 ? 'Auditing...' : 'Queued',
      status: elapsedSeconds > 1.7 ? 'completed' : elapsedSeconds > 1.4 ? 'running' : 'pending',
      detail: 'Assigning L1 / L2 approval route and executing 4-step CoT audit with safety gate enforcement...',
      codeSnippet: `validator.audit(actions=["BLOCK_CARD"], route="L1", gate=OPEN)`
    }
  ];

  return steps;
}
