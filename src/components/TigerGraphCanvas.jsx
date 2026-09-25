import React, { useState, useRef } from 'react';
import { 
  Plus, 
  Minus, 
  Crosshair, 
  Maximize2, 
  LayoutGrid, 
  Code2, 
  Laptop, 
  User, 
  Wallet, 
  Receipt,
  ShieldAlert
} from 'lucide-react';
import { GraphNode } from './GraphNode';
import { GraphEdge } from './GraphEdge';
import { JsonPayload } from './JsonPayload';
import { graphNodes, graphEdges, circularLoopBadge } from '../data/graphData';
import { goldStandardPayload } from '../data/caseData';

export const TigerGraphCanvas = ({ 
  onSelectNode, 
  selectedNode, 
  activeTab, 
  setActiveTab 
}) => {
  const [zoom, setZoom] = useState(1);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  // Canvas coordinate system (reference 800 x 480)
  const viewBoxWidth = 800;
  const viewBoxHeight = 480;

  // Convert percentage coordinates to pixel coordinates
  const nodesWithPixels = graphNodes.map(node => ({
    ...node,
    pixelX: (node.x / 100) * viewBoxWidth,
    pixelY: (node.y / 100) * viewBoxHeight
  }));

  const nodeMap = nodesWithPixels.reduce((acc, node) => {
    acc[node.id] = node;
    return acc;
  }, {});

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.15, 1.6));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.15, 0.7));
  const handleResetZoom = () => setZoom(1);

  const handleMouseEnter = (node, e) => {
    setHoveredNode(node);
    const rect = e.currentTarget.getBoundingClientRect();
    setTooltipPos({ x: rect.left, y: rect.top - 8 });
  };

  const handleMouseLeave = () => {
    setHoveredNode(null);
  };

  return (
    <div className="flex flex-col h-full border border-cyber-border bg-cyber-panel/85 rounded-lg shadow-[0_0_20px_rgba(0,0,0,0.8)] overflow-hidden">
      {/* Top Tab Bar: CANVAS VIEW vs JSON PAYLOAD */}
      <div className="flex items-center justify-between border-b border-cyber-border px-3 py-2 bg-cyber-dark/80">
        <div className="flex items-center gap-2">
          {/* Tab 1: CANVAS VIEW */}
          <button
            onClick={() => setActiveTab('canvas')}
            className={`
              flex items-center gap-2 px-3 py-1.5 rounded-md font-mono text-xs font-bold tracking-wider transition-all
              ${activeTab === 'canvas'
                ? 'border border-cyber-cyan bg-cyan-950/40 text-cyber-cyan shadow-[0_0_12px_rgba(0,229,255,0.4)]'
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
              }
            `}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            <span>CANVAS VIEW</span>
          </button>

          {/* Tab 2: JSON PAYLOAD */}
          <button
            onClick={() => setActiveTab('json')}
            className={`
              flex items-center gap-2 px-3 py-1.5 rounded-md font-mono text-xs font-bold tracking-wider transition-all
              ${activeTab === 'json'
                ? 'border border-cyber-cyan bg-cyan-950/40 text-cyber-cyan shadow-[0_0_12px_rgba(0,229,255,0.4)]'
                : 'border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/50'
              }
            `}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>JSON PAYLOAD</span>
          </button>
        </div>

        {/* Right side metadata */}
        <div className="hidden sm:flex items-center gap-2 text-[10px] font-mono text-slate-400">
          <span className="text-cyan-400/80">GRAPH_NAME:</span>
          <span className="font-bold text-slate-200">FraudInvestigationGraph</span>
        </div>
      </div>

      {/* Main Canvas Body or JSON Tab View */}
      <div className="relative flex-1 bg-[#050B14] overflow-hidden min-h-[360px] flex items-center justify-center">
        {activeTab === 'json' ? (
          <JsonPayload payload={goldStandardPayload} />
        ) : (
          <>
            {/* Top-Left: TigerGraph Logo & Subtitle */}
            <div className="absolute top-3 left-4 z-10 flex items-center gap-2.5 pointer-events-none select-none">
              <div className="w-8 h-8 rounded border border-cyan-400/50 bg-[#091522]/90 flex items-center justify-center text-cyber-cyan shadow-[0_0_10px_rgba(0,229,255,0.3)]">
                {/* Stylized Tiger Icon */}
                <svg className="w-5 h-5 fill-cyber-cyan" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v4h-2zm0 6h2v2h-2z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-mono font-extrabold tracking-widest text-white">
                  TIGERGRAPH
                </span>
                <span className="text-[9px] font-mono text-cyan-400/70 tracking-wider">
                  GRAPH ANALYTICS
                </span>
              </div>
            </div>

            {/* Top-Right: Legend */}
            <div className="absolute top-3 right-4 z-10 hidden sm:flex flex-col gap-1.5 p-2 px-3 rounded border border-cyber-border bg-[#080F1B]/90 backdrop-blur-sm pointer-events-none text-[9.5px] font-mono">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#FF334B]" />
                  <span className="text-slate-300">User</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#00E5FF]" />
                  <span className="text-slate-300">Device</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#FF9900]" />
                  <span className="text-slate-300">Wallet</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#A855F7]" />
                  <span className="text-slate-300">Transaction</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 border-t border-dashed border-cyan-400" />
                  <span className="text-slate-400">Connection</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 border-t border-dashed border-red-500" />
                  <span className="text-slate-400">Transfer</span>
                </div>
              </div>
            </div>

            {/* Interactive SVG Network Graph */}
            <svg
              viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
              className="w-full h-full select-none"
              style={{
                transform: `scale(${zoom})`,
                transition: 'transform 0.3s ease-out'
              }}
            >
              {/* Definitions: Arrowhead markers */}
              <defs>
                <marker id="arrow-00E5FF" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#00E5FF" />
                </marker>
                <marker id="arrow-FF9900" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#FF9900" />
                </marker>
                <marker id="arrow-A855F7" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#A855F7" />
                </marker>
                <marker id="arrow-FF334B" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#FF334B" />
                </marker>
                {/* Background grid pattern */}
                <pattern id="canvas-grid" width="30" height="30" patternUnits="userSpaceOnUse">
                  <circle cx="15" cy="15" r="0.8" fill="rgba(0, 229, 255, 0.15)" />
                  <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(14, 42, 58, 0.3)" strokeWidth="0.5" />
                </pattern>
              </defs>

              {/* Background Grid */}
              <rect width="100%" height="100%" fill="url(#canvas-grid)" />

              {/* Faint ambient constellation connections */}
              <g opacity="0.18">
                <line x1="280" y1="200" x2="380" y2="120" stroke="#00E5FF" strokeWidth="0.8" />
                <line x1="380" y1="120" x2="480" y2="160" stroke="#00E5FF" strokeWidth="0.8" />
                <line x1="480" y1="160" x2="620" y2="130" stroke="#00E5FF" strokeWidth="0.8" />
                <line x1="200" y1="360" x2="280" y2="200" stroke="#00E5FF" strokeWidth="0.8" />
                <line x1="620" y1="130" x2="720" y2="240" stroke="#00E5FF" strokeWidth="0.8" />
                <line x1="720" y1="240" x2="660" y2="380" stroke="#00E5FF" strokeWidth="0.8" />
                <circle cx="380" cy="120" r="1.5" fill="#00E5FF" />
                <circle cx="480" cy="160" r="1.5" fill="#00E5FF" />
                <circle cx="620" cy="130" r="1.5" fill="#00E5FF" />
                <circle cx="720" cy="240" r="1.5" fill="#00E5FF" />
              </g>

              {/* Standard Graph Edges */}
              {graphEdges.map((edge) => (
                <GraphEdge
                  key={edge.id}
                  edge={edge}
                  fromNode={nodeMap[edge.from]}
                  toNode={nodeMap[edge.to]}
                />
              ))}

              {/* Large 3-Hop Red Circular Transfer Loop */}
              {/* Loop starts at USER_101 (512, 259), sweeps right to 3-Hop Loop badge, up and left through DEVICE_99 to USER_882 */}
              <g className="cursor-pointer" onClick={() => onSelectNode(nodeMap["USER_882"])}>
                {/* Outer Red Glow Stroke */}
                <path
                  d="M 510 260 C 580 250, 600 180, 540 150 C 490 120, 400 150, 310 190"
                  fill="none"
                  stroke="#FF334B"
                  strokeWidth={3}
                  strokeOpacity={0.2}
                />

                {/* Animated Red Dashed Path */}
                <path
                  d="M 510 260 C 580 250, 600 180, 540 150 C 490 120, 400 150, 310 190"
                  fill="none"
                  stroke="#FF334B"
                  strokeWidth={2}
                  strokeDasharray="6 4"
                  markerEnd="url(#arrow-FF334B)"
                  style={{
                    filter: "drop-shadow(0 0 8px rgba(255,51,75,0.7))"
                  }}
                >
                  <animate
                    attributeName="stroke-dashoffset"
                    from="0"
                    to="-20"
                    dur="1.5s"
                    repeatCount="indefinite"
                  />
                </path>

                {/* 3-HOP LOOP ($15k) Badge */}
                <g transform="translate(535, 192)">
                  <rect
                    x={-42}
                    y={-18}
                    width={84}
                    height={36}
                    rx={6}
                    fill="#3B0707"
                    stroke="#FF334B"
                    strokeWidth={1.5}
                    style={{
                      filter: "drop-shadow(0 0 12px rgba(255,51,75,0.7))"
                    }}
                  />
                  <text
                    y={-2}
                    textAnchor="middle"
                    className="text-[9.5px] font-mono font-extrabold fill-cyber-crimson tracking-wider pointer-events-none select-none"
                  >
                    3-HOP LOOP
                  </text>
                  <text
                    y={11}
                    textAnchor="middle"
                    className="text-[9px] font-mono font-bold fill-cyber-crimson tracking-wider pointer-events-none select-none"
                  >
                    ($15k)
                  </text>
                </g>
              </g>

              {/* Render Graph Nodes */}
              {nodesWithPixels.map((node) => (
                <GraphNode
                  key={node.id}
                  node={node}
                  isSelected={selectedNode?.id === node.id}
                  onClick={onSelectNode}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                />
              ))}
            </svg>

            {/* Zoom & Canvas Controls (Right Side) */}
            <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-1 p-1 rounded-md border border-cyber-border bg-[#080F1B]/90 backdrop-blur-sm shadow-[0_0_12px_rgba(0,0,0,0.8)]">
              <button
                onClick={handleZoomIn}
                className="w-7 h-7 rounded flex items-center justify-center text-slate-300 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
                title="Zoom In"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                onClick={handleZoomOut}
                className="w-7 h-7 rounded flex items-center justify-center text-slate-300 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
                title="Zoom Out"
              >
                <Minus className="w-4 h-4" />
              </button>
              <button
                onClick={handleResetZoom}
                className="w-7 h-7 rounded flex items-center justify-center text-slate-300 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
                title="Recenter"
              >
                <Crosshair className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoom(1.2)}
                className="w-7 h-7 rounded flex items-center justify-center text-slate-300 hover:text-cyber-cyan hover:bg-cyan-950/40 transition-colors"
                title="Fullscreen Focus"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Bottom-Right Mini-Map Radar HUD */}
            <div className="absolute bottom-3 right-4 z-10 w-24 h-16 rounded border border-cyber-border bg-[#060C17]/90 p-1 hidden sm:flex flex-col justify-between overflow-hidden shadow-[0_0_10px_rgba(0,0,0,0.7)]">
              {/* Radar sweep effect */}
              <div className="relative w-full h-full border border-cyan-900/40 rounded flex items-center justify-center overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(0,229,255,0.1)_0%,transparent_70%)]" />
                <div className="w-10 h-10 rounded-full border border-cyan-500/20 absolute" />
                <div className="w-5 h-5 rounded-full border border-cyan-500/30 absolute" />
                {/* Node micro-dots */}
                <div className="w-1.5 h-1.5 rounded-full bg-[#FF334B] absolute top-5 left-7" />
                <div className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] absolute top-3 left-12" />
                <div className="w-1.5 h-1.5 rounded-full bg-[#00FF88] absolute top-8 left-14" />
                <div className="w-1 h-1 rounded-full bg-[#FF9900] absolute top-9 left-4" />
                <div className="w-1 h-1 rounded-full bg-[#A855F7] absolute top-10 left-9" />
              </div>
            </div>

            {/* Hover Tooltip */}
            {hoveredNode && (
              <div
                className="fixed z-50 pointer-events-none transform -translate-x-1/2 -translate-y-full px-2.5 py-1.5 rounded border border-cyber-cyan/60 bg-[#091322]/95 backdrop-blur-md shadow-[0_0_15px_rgba(0,229,255,0.3)] text-left"
                style={{ left: `${tooltipPos.x}px`, top: `${tooltipPos.y}px` }}
              >
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-mono font-bold text-white">
                    {hoveredNode.label}
                  </span>
                  <span className="text-[9px] font-mono text-cyan-300">
                    [{hoveredNode.type}]
                  </span>
                </div>
                <div className="text-[9px] font-mono text-slate-300">
                  Risk: <span className="text-cyber-crimson font-bold">{(hoveredNode.risk * 100).toFixed(0)}%</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
