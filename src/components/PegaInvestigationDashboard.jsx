import React, { useState, useEffect } from 'react';
import { PegaCasePanel } from './PegaCasePanel';
import { PegaGraphCanvas } from './PegaGraphCanvas';
import { PegaEntityDrawer } from './PegaEntityDrawer';
import { PegaActionModal } from './PegaActionModal';
import { AiNotesDrawer } from './AiNotesDrawer';

export function PegaInvestigationDashboard({
  caseId,
  caseData,
  cases = [],
  onSelectCase,
  activeNav,
  onSelectNav,
  onNewInvestigation
}) {
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [actionModal, setActionModal] = useState({ isOpen: false, type: null, entity: null });
  const [aiNotesOpen, setAiNotesOpen] = useState(false);

  // Load graph data for counts and export
  useEffect(() => {
    if (!caseId) return;
    fetch(`/api/investigations/${caseId}/graph`)
      .then(res => res.json())
      .then(data => {
        if (data && data.nodes) {
          setGraphData(data);
          // Auto-select central node
          const central = data.nodes.find(n => n.is_central) || data.nodes[0];
          if (central) {
            setSelectedEntity(central);
          }
        }
      })
      .catch(err => console.error("Error loading graph for dashboard:", err));
  }, [caseId]);

  // Handle Export Subgraph as JSON
  const handleExportSubgraph = (dataToExport) => {
    const data = dataToExport || graphData;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${caseId}_subgraph.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Handle Action Trigger (opens modal)
  const handleTriggerAction = (actionType, entity) => {
    setActionModal({
      isOpen: true,
      type: actionType,
      entity: entity || selectedEntity
    });
  };

  // Handle Confirmed Action from Modal
  const handleConfirmAction = (actionType, entity) => {
    if (actionType === 'BLOCK') {
      fetch(`/api/investigations/${caseId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          action: "BLOCK_CARD",
          route: "L1",
          analyst: "Aman Singh"
        })
      }).catch(err => console.error("Error dispatching block:", err));
    } else if (actionType === 'SAR') {
      fetch(`/api/investigations/${caseId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          action: "FILE_SAR",
          route: "L2",
          analyst: "Aman Singh"
        })
      }).catch(err => console.error("Error dispatching SAR:", err));
    }
  };

  return (
    <div className="flex-1 flex h-full w-full bg-[#0A0C10] overflow-hidden select-none font-sans relative">
      {/* 1. LEFT: Case Panel & Navigation (Exact TigerGraph Savanna style) */}
      <PegaCasePanel
        caseData={caseData}
        cases={cases}
        activeCaseId={caseId}
        onSelectCase={onSelectCase}
        activeNav={activeNav}
        onSelectNav={(navId) => {
          if (navId === 'ai_notes') {
            setAiNotesOpen(true);
          } else {
            if (onSelectNav) onSelectNav(navId);
          }
        }}
        onOpenAiNotes={() => setAiNotesOpen(true)}
      />

      {/* 2. CENTER: Dominant TigerGraph Multi-Hop Radial Canvas */}
      <PegaGraphCanvas
        caseId={caseId}
        caseData={caseData}
        onSelectNode={(node) => {
          setSelectedEntity(node);
        }}
        selectedNodeId={selectedEntity?.id}
        onExportGraph={handleExportSubgraph}
      />

      {/* 3. RIGHT: Entity Details Drawer */}
      <PegaEntityDrawer
        selectedEntity={selectedEntity}
        caseData={caseData}
        onClose={() => setSelectedEntity(null)}
        onTriggerAction={handleTriggerAction}
        onExportSubgraph={() => handleExportSubgraph(graphData)}
      />

      {/* 4. AI Notes & Ollama Copilot Drawer (Slides in on demand) */}
      <AiNotesDrawer
        caseId={caseId}
        caseData={caseData}
        isOpen={aiNotesOpen}
        onClose={() => setAiNotesOpen(false)}
        onOpenEntity={(ent) => setSelectedEntity(ent)}
      />

      {/* 5. Action Confirmation Modal */}
      <PegaActionModal
        isOpen={actionModal.isOpen}
        actionType={actionModal.type}
        caseData={caseData}
        selectedEntity={actionModal.entity}
        onClose={() => setActionModal({ isOpen: false, type: null, entity: null })}
        onConfirm={handleConfirmAction}
      />
    </div>
  );
}

export default PegaInvestigationDashboard;
