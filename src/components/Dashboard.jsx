import React from 'react';
import { AgentPipeline } from './AgentPipeline';
import { TigerGraphCanvas } from './TigerGraphCanvas';
import { ConsoleLogs } from './ConsoleLogs';
import { ThreatMetrics } from './ThreatMetrics';

export const Dashboard = ({
  agents,
  logs,
  riskScore,
  onSelectAgent,
  onSelectNode,
  selectedNode,
  activeTab,
  setActiveTab,
  onAutoFreeze,
  onEscalate,
  onSelectInsight
}) => {
  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-3 flex-1 items-start">
      {/* LEFT COLUMN: Agent Pipeline (27%) */}
      <div className="lg:col-span-3 h-full flex flex-col min-w-0">
        <AgentPipeline
          agents={agents}
          onSelectAgent={onSelectAgent}
        />
      </div>

      {/* CENTER COLUMN: TigerGraph Canvas + Console Logs (48%) */}
      <div className="lg:col-span-6 h-full flex flex-col min-w-0">
        <div className="flex-1 min-h-[380px]">
          <TigerGraphCanvas
            onSelectNode={onSelectNode}
            selectedNode={selectedNode}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        </div>
        <ConsoleLogs logs={logs} />
      </div>

      {/* RIGHT COLUMN: Threat Metrics, Actions & Insights (25%) */}
      <div className="lg:col-span-3 h-full flex flex-col min-w-0">
        <ThreatMetrics
          riskScore={riskScore}
          onAutoFreeze={onAutoFreeze}
          onEscalate={onEscalate}
          onSelectInsight={onSelectInsight}
        />
      </div>
    </div>
  );
};
