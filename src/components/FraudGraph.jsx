import React, { useState, useEffect, useRef } from 'react';
import { 
  User, 
  CreditCard, 
  DollarSign, 
  Smartphone, 
  Globe, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Share2, 
  AlertTriangle,
  RotateCcw
} from 'lucide-react';

export function FraudGraph({ caseId, onSelectNode, selectedNodeId }) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  // Fetch real graph data from backend
  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    fetch(`/api/investigations/${caseId}/graph`)
      .then(res => res.json())
      .then(data => {
        if (data && data.nodes && data.nodes.length > 0) {
          setGraphData(data);
        } else {
          // Fallback structure if empty
          setGraphData({
            nodes: [
              { id: "cust_primary", label: "Customer #101", type: "customer", risk_level: "LOW", details: { home_region: "204.0" } },
              { id: "card_primary", label: "Card 101-K1", type: "account", risk_level: "LOW", details: {} },
              { id: "txn_primary", label: "TX #3514030 ($77.07)", type: "transaction", risk_level: "CRITICAL", details: { amount: 77.07, risk_score: 0.94 } },
              { id: "dev_shared", label: "Device: Android 11", type: "device", risk_level: "CRITICAL", details: { connected_accounts: 4 } },
              { id: "ip_shared", label: "IP: 192.168.1.45", type: "ip", risk_level: "MEDIUM", details: {} },
              { id: "other_acc", label: "Account #882", type: "connected_account", risk_level: "HIGH", details: { relationship: "SHARED_DEVICE" } }
            ],
            edges: [
              { id: "e1", source: "cust_primary", target: "card_primary", label: "OWNS_ACCOUNT" },
              { id: "e2", source: "card_primary", target: "txn_primary", label: "INITIATED_TXN" },
              { id: "e3", source: "txn_primary", target: "dev_shared", label: "USED_DEVICE" },
              { id: "e4", source: "dev_shared", target: "ip_shared", label: "USED_IP" },
              { id: "e5", source: "dev_shared", target: "other_acc", label: "SHARED_DEVICE" }
            ]
          });
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching graph data:", err);
        setLoading(false);
      });
  }, [caseId]);

  // Compute hierarchical tree / ring coordinates for SVG rendering
  const getNodeCoordinates = (nodes) => {
    const coords = {};
    const total = nodes.length;
    const width = 800;
    const height = 500;

    // Fixed structured layout matching Section 7:
    // Customer (bottom center) -> Account -> Transaction (center) -> Device (top center) -> IP (top right) -> Other Accounts (top left)
    nodes.forEach((n, idx) => {
      if (n.type === 'customer') {
        coords[n.id] = { x: 400, y: 420 };
      } else if (n.type === 'account') {
        coords[n.id] = { x: 400, y: 320 };
      } else if (n.type === 'transaction') {
        coords[n.id] = { x: 400, y: 220 };
      } else if (n.type === 'device') {
        coords[n.id] = { x: 400, y: 100 };
      } else if (n.type === 'ip') {
        coords[n.id] = { x: 620, y: 100 };
      } else if (n.type === 'connected_account') {
        const offset = (idx % 2 === 0 ? -1 : 1) * (180 + Math.floor(idx / 2) * 80);
        coords[n.id] = { x: 400 + offset, y: 160 };
      } else {
        // Generic circle position
        const angle = (idx / total) * 2 * Math.PI;
        coords[n.id] = {
          x: 400 + Math.cos(angle) * 220,
          y: 250 + Math.sin(angle) * 160
        };
      }
    });

    return coords;
  };

  const coords = getNodeCoordinates(graphData.nodes);

  // Mouse pan handling
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const getNodeColor = (type, risk) => {
    if (risk === 'CRITICAL' || risk === 'HIGH') return '#EF4444';
    if (type === 'device') return '#06B6D4';
    if (type === 'customer') return '#10B981';
    if (type === 'account' || type === 'connected_account') return '#8B5CF6';
    if (type === 'ip') return '#F59E0B';
    return '#3B82F6';
  };

  const getNodeIcon = (type) => {
    if (type === 'customer') return <User className="w-4 h-4 text-emerald-400" />;
    if (type === 'account' || type === 'connected_account') return <CreditCard className="w-4 h-4 text-purple-400" />;
    if (type === 'transaction') return <DollarSign className="w-4 h-4 text-red-400" />;
    if (type === 'device') return <Smartphone className="w-4 h-4 text-cyan-400" />;
    if (type === 'ip') return <Globe className="w-4 h-4 text-amber-400" />;
    return <Share2 className="w-4 h-4 text-blue-400" />;
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-workspace-bg select-none relative overflow-hidden">
      {/* Controls & Legend Bar */}
      <div className="h-12 border-b border-workspace-border/70 bg-workspace-surface/60 px-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-3 text-xs">
          <span className="font-semibold text-white flex items-center gap-1.5 font-mono">
            <Share2 className="w-4 h-4 text-blue-400" />
            TigerGraph Multi-Hop Evidence Graph
          </span>
          <span className="text-[10px] text-slate-400 font-mono bg-workspace-card px-2 py-0.5 rounded border border-workspace-border">
            {graphData.nodes.length} Nodes • {graphData.edges.length} Edges
          </span>
        </div>

        {/* Legend */}
        <div className="hidden md:flex items-center gap-3 text-[10px] font-mono text-slate-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400" /> Customer</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-400" /> Account</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400" /> Transaction</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-400" /> Device</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-400" /> IP</span>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoom(z => Math.min(2, z + 0.15))}
            className="p-1.5 rounded bg-workspace-card hover:bg-workspace-cardHover text-slate-300 hover:text-white border border-workspace-border"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(z => Math.max(0.5, z - 0.15))}
            className="p-1.5 rounded bg-workspace-card hover:bg-workspace-cardHover text-slate-300 hover:text-white border border-workspace-border"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
            className="p-1.5 rounded bg-workspace-card hover:bg-workspace-cardHover text-slate-300 hover:text-white border border-workspace-border"
            title="Reset View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Graph Viewport */}
      <div 
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="flex-1 w-full h-full relative cursor-grab active:cursor-grabbing overflow-hidden"
      >
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs font-mono">
            Loading TigerGraph multi-hop topological evidence...
          </div>
        ) : (
          <svg 
            className="w-full h-full"
            style={{ 
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center'
            }}
          >
            <defs>
              <marker
                id="arrow"
                viewBox="0 0 10 10"
                refX="22"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
              </marker>
              <marker
                id="arrow-red"
                viewBox="0 0 10 10"
                refX="22"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#EF4444" />
              </marker>
            </defs>

            {/* Edges */}
            {graphData.edges.map((e, idx) => {
              const src = coords[e.source];
              const tgt = coords[e.target];
              if (!src || !tgt) return null;

              const isSyndicate = e.type === 'syndicate';
              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g key={e.id || idx}>
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={isSyndicate ? '#EF4444' : '#334155'}
                    strokeWidth={isSyndicate ? "2" : "1.5"}
                    strokeDasharray={isSyndicate ? "4 4" : undefined}
                    markerEnd={isSyndicate ? "url(#arrow-red)" : "url(#arrow)"}
                  />
                  {e.label && (
                    <text
                      x={midX}
                      y={midY - 4}
                      fill="#94A3B8"
                      fontSize="9"
                      fontFamily="JetBrains Mono"
                      textAnchor="middle"
                      className="select-none pointer-events-none"
                    >
                      {e.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {graphData.nodes.map((n) => {
              const c = coords[n.id];
              if (!c) return null;
              const isSelected = selectedNodeId === n.id;
              const color = getNodeColor(n.type, n.risk_level);

              return (
                <g 
                  key={n.id} 
                  transform={`translate(${c.x}, ${c.y})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectNode && onSelectNode(n);
                  }}
                  className="cursor-pointer group"
                >
                  {/* Selection Glow */}
                  {isSelected && (
                    <circle r="28" fill="none" stroke={color} strokeWidth="2.5" opacity="0.6" className="animate-pulse" />
                  )}

                  {/* Outer circle */}
                  <circle
                    r="20"
                    fill="#161F2E"
                    stroke={color}
                    strokeWidth={isSelected ? "2.5" : "1.5"}
                    className="transition-all duration-150 group-hover:scale-110"
                  />

                  {/* Node Label */}
                  <text
                    y="32"
                    fill="#F8FAFC"
                    fontSize="10"
                    fontWeight="500"
                    fontFamily="Inter, sans-serif"
                    textAnchor="middle"
                    className="select-none"
                  >
                    {n.label}
                  </text>

                  {/* Risk Badge on Node */}
                  {n.risk_level === 'CRITICAL' && (
                    <circle cx="14" cy="-14" r="5" fill="#EF4444" />
                  )}
                </g>
              );
            })}
          </svg>
        )}
      </div>
    </div>
  );
}
export default FraudGraph;
