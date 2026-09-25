import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  User, 
  CreditCard, 
  ArrowUpRight, 
  Smartphone, 
  MapPin, 
  Mail, 
  Bitcoin,
  Layers, 
  Search, 
  Minus, 
  Plus, 
  SlidersHorizontal,
  Maximize2, 
  ZoomIn, 
  ZoomOut,
  AlertTriangle,
  RotateCcw
} from 'lucide-react';

export function PegaGraphCanvas({ 
  caseId, 
  caseData,
  onSelectNode, 
  selectedNodeId,
  onExportGraph
}) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('All');
  const [searchDepth, setSearchDepth] = useState(2);
  const [hoveredNode, setHoveredNode] = useState(null);

  const containerRef = useRef(null);

  // Fetch real-time graph data from backend
  useEffect(() => {
    if (!caseId) return;
    setLoading(true);

    fetch(`/api/investigations/${caseId}/graph`)
      .then(res => res.json())
      .then(data => {
        if (data && data.nodes && data.nodes.length > 0) {
          setGraphData(data);
          // Auto-select central node or flagged transaction
          const central = data.nodes.find(n => n.is_central) || data.nodes[0];
          if (central && onSelectNode && !selectedNodeId) {
            onSelectNode(central);
          }
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching graph data:", err);
        setLoading(false);
      });
  }, [caseId]);

  // Compute exact coordinates matching reference radial star topology
  const nodePositions = useMemo(() => {
    const coords = {};
    const nodes = graphData.nodes || [];
    if (nodes.length === 0) return coords;

    const centerNode = nodes.find(n => n.is_central) || nodes[0];
    const otherNodes = nodes.filter(n => n.id !== centerNode.id);

    // Center coordinates in SVG space
    const cx = 460;
    const cy = 300;
    coords[centerNode.id] = { x: cx, y: cy };

    // Standard radial orbit positions for 8 types matching media_1790268526500.png:
    // Top (-90 deg): Card
    // Top-Right (-45 deg): Transaction
    // Right (0 deg): Email
    // Bottom-Right (45 deg): Wallet
    // Bottom (90 deg): Alias
    // Bottom-Left (135 deg): Related User
    // Left (180 deg): Location
    // Top-Left (225 deg): Device
    const radiusX = 250;
    const radiusY = 190;

    otherNodes.forEach((node, idx) => {
      let angle = 0;
      const type = (node.type || '').toLowerCase();
      const label = (node.label || '').toLowerCase();

      if (type === 'card') {
        angle = -Math.PI / 2; // -90 deg (Top)
      } else if (type === 'transaction' || label.startsWith('$') || label.startsWith('tx')) {
        angle = -Math.PI / 4; // -45 deg (Top-Right)
      } else if (type === 'email' || label.includes('@')) {
        angle = 0; // 0 deg (Right)
      } else if (type === 'wallet' || label.includes('wallet')) {
        angle = Math.PI / 4; // 45 deg (Bottom-Right)
      } else if (type === 'alias' || label.includes('alias') || label.includes('nightvector')) {
        angle = Math.PI / 2; // 90 deg (Bottom)
      } else if (type === 'user' || label.startsWith('cust')) {
        angle = 3 * Math.PI / 4; // 135 deg (Bottom-Left)
      } else if (type === 'location' || label.includes('europe') || label.includes('region')) {
        angle = Math.PI; // 180 deg (Left)
      } else if (type === 'device' || label.includes('samsung') || label.includes('device')) {
        angle = 5 * Math.PI / 4; // 225 deg (Top-Left)
      } else {
        // Fallback equidistant distribution
        angle = (idx / otherNodes.length) * 2 * Math.PI - Math.PI / 2;
      }

      coords[node.id] = {
        x: cx + radiusX * Math.cos(angle),
        y: cy + radiusY * Math.sin(angle)
      };
    });

    return coords;
  }, [graphData.nodes]);

  // Filter nodes based on active filter button & search query
  const filteredNodes = useMemo(() => {
    return (graphData.nodes || []).filter(node => {
      const type = (node.type || '').toLowerCase();
      const label = (node.label || '').toLowerCase();
      const title = (node.title || '').toLowerCase();

      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!label.includes(q) && !type.includes(q) && !title.includes(q)) {
          return false;
        }
      }

      // Category tab filter
      if (selectedFilter === 'All') return true;
      if (selectedFilter === 'Users') return type === 'user' || type === 'alias';
      if (selectedFilter === 'Devices') return type === 'device';
      if (selectedFilter === 'Cards') return type === 'card';
      if (selectedFilter === 'Transactions') return type === 'transaction';
      return true;
    });
  }, [graphData.nodes, selectedFilter, searchQuery]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  // Node Icons
  const getNodeIcon = (node) => {
    const type = (node.type || '').toLowerCase();
    const label = (node.label || '').toLowerCase();

    if (node.is_central || (type === 'user' && !label.startsWith('cust'))) {
      return <User className="w-5 h-5 text-white" />;
    }
    if (type === 'card') {
      return <CreditCard className="w-4 h-4 text-purple-400" />;
    }
    if (type === 'transaction') {
      return <ArrowUpRight className="w-4 h-4 text-emerald-400" />;
    }
    if (type === 'email') {
      return <Mail className="w-4 h-4 text-cyan-400" />;
    }
    if (type === 'wallet') {
      return <Bitcoin className="w-4 h-4 text-[#10B981]" />;
    }
    if (type === 'alias') {
      return <User className="w-4 h-4 text-[#10B981]" />;
    }
    if (type === 'user') {
      return <User className="w-4 h-4 text-blue-400" />;
    }
    if (type === 'location') {
      return <MapPin className="w-4 h-4 text-slate-300" />;
    }
    if (type === 'device') {
      return <Smartphone className="w-4 h-4 text-sky-400" />;
    }
    return <Layers className="w-4 h-4 text-[#10B981]" />;
  };

  // Node Border & Glow Styling
  const getNodeBorderColor = (node) => {
    if (node.is_central) return '#10B981';
    const type = (node.type || '').toLowerCase();
    if (type === 'card') return '#A855F7';
    if (type === 'transaction') return '#10B981';
    if (type === 'email') return '#0EA5E9';
    if (type === 'wallet') return '#F97316';
    if (type === 'alias') return '#FB923C';
    if (type === 'user') return '#3B82F6';
    if (type === 'location') return '#64748B';
    if (type === 'device') return '#38BDF8';
    return '#10B981';
  };

  // Pan / Drag Handlers
  const handleMouseDown = (e) => {
    if (e.target.tagName === 'svg' || e.target.id === 'canvas-bg') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleFit = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="flex-1 h-full flex flex-col bg-[#0A0C10] relative select-none font-sans overflow-hidden">
      {/* 1. Top Controls Bar */}
      <div className="h-12 border-b border-[#181B24] bg-[#0E1015]/95 px-4 flex items-center justify-between z-10">
        {/* Left: Filter Buttons */}
        <div className="flex items-center gap-1.5">
          {[
            { id: 'All', label: 'All', icon: Layers },
            { id: 'Users', label: 'Users', icon: User },
            { id: 'Devices', label: 'Devices', icon: Smartphone },
            { id: 'Cards', label: 'Cards', icon: CreditCard },
            { id: 'Transactions', label: 'Transactions', icon: ArrowUpRight }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = selectedFilter === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSelectedFilter(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-[#10B981] text-black font-semibold shadow-[0_0_12px_rgba(16,185,129,0.35)]'
                    : 'bg-[#15171F] text-[#8E93A6] hover:text-white hover:bg-[#1E222D] border border-[#232733]'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-black' : 'text-[#646A7E]'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Center/Right: Search Depth, Search Graph & Filter Slider */}
        <div className="flex items-center gap-2">
          {/* Depth Stepper */}
          <div className="flex items-center bg-[#15171F] border border-[#232733] rounded-md px-2 py-1 text-xs">
            <span className="text-[11px] text-[#646A7E] mr-2">Search Depth</span>
            <button
              onClick={() => setSearchDepth(d => Math.max(1, d - 1))}
              className="text-[#8E93A6] hover:text-white p-0.5"
            >
              <Minus className="w-3 h-3" />
            </button>
            <span className="px-2 font-mono font-bold text-white text-xs">{searchDepth}</span>
            <button
              onClick={() => setSearchDepth(d => Math.min(4, d + 1))}
              className="text-[#8E93A6] hover:text-white p-0.5"
            >
              <Plus className="w-3 h-3" />
            </button>
          </div>

          {/* Search Graph Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#646A7E] absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search graph..."
              className="w-36 lg:w-44 pl-8 pr-2.5 py-1 text-xs rounded-md bg-[#15171F] border border-[#232733] text-white placeholder-[#585E72] outline-none focus:border-[#10B981] transition-colors"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-[#646A7E] hover:text-white"
              >
                ✕
              </button>
            )}
          </div>

          {/* Sliders / Filter Options */}
          <button 
            className="p-1.5 rounded-md bg-[#15171F] border border-[#232733] text-[#8E93A6] hover:text-white transition-colors"
            title="Filter Settings"><SlidersHorizontal className="w-3.5 h-3.5" /></button><button onClick={() => {const blob = new Blob([JSON.stringify(graphData, null, 2)], { type: 'application/json' });const url = URL.createObjectURL(blob);const a = document.createElement('a');a.href = url;a.download = `${caseId || 'export'}_graph.json`;document.body.appendChild(a);a.click();document.body.removeChild(a);URL.revokeObjectURL(url);}} className="px-2 py-1.5 rounded-md bg-[#15171F] border border-[#232733] text-[#10B981] font-mono text-[10px] font-bold hover:bg-[#10B981]/10 transition-colors">EXPORT</button></div></div>

      {/* 2. Interactive SVG Canvas Viewport */}
      <div 
        ref={containerRef}
        id="canvas-bg"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={(e) => {
          const delta = e.deltaY > 0 ? -0.1 : 0.1;
          setZoom(z => Math.max(0.4, Math.min(2.5, z + delta)));
        }}
        className="flex-1 w-full h-full relative overflow-hidden cursor-grab active:cursor-grabbing"
      >
        {loading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-[#8E93A6] text-xs font-mono gap-2">
            <div className="w-6 h-6 border-2 border-[#10B981] border-t-transparent rounded-full animate-spin" />
            <span>Traversing TigerGraph multi-hop topological graph...</span>
          </div>
        ) : (
          <svg viewBox="0 0 920 600" className="w-full h-full" style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, transformOrigin: 'center center' }}>
            <defs>
              {/* Subtle Grid Pattern */}
              <pattern id="dot-grid" width="28" height="28" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1" fill="#1C1F28" />
              </pattern>

              {/* Arrow Marker for green Edges */}
              <marker
                id="arrow-green"
                viewBox="0 0 10 10"
                refX="26"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 9 5 L 0 9 z" fill="#10B981" />
              </marker>

              {/* Arrow Marker for Target Inward Edges */}
              <marker
                id="arrow-green-target"
                viewBox="0 0 10 10"
                refX="32"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 9 5 L 0 9 z" fill="#10B981" />
              </marker>

              {/* Risk Glow Filter */}
              <filter id="risk-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Background Grid */}
            <rect width="100%" height="100%" fill="url(#dot-grid)" />

            {/* EDGES LAYER */}
            <g className="edges-layer">
              {(graphData.edges || []).map((edge) => {
                const s = nodePositions[edge.source];
                const t = nodePositions[edge.target];
                if (!s || !t) return null;
                if (!filteredNodeIds.has(edge.source) || !filteredNodeIds.has(edge.target)) return null;

                const isDashed = edge.style === 'dashed';
                const edgeColor = edge.color || (isDashed ? '#475569' : '#10B981');
                const hasArrow = edge.direction === 'to_target' || edge.direction === 'in';
                const markerId = hasArrow ? (edge.target.includes('user') || edge.target.includes('shadow') ? 'url(#arrow-green-target)' : 'url(#arrow-green)') : undefined;

                const midX = (s.x + t.x) / 2;
                const midY = (s.y + t.y) / 2;

                return (
                  <g key={edge.id} className="edge-group">
                    <line
                      x1={s.x}
                      y1={s.y}
                      x2={t.x}
                      y2={t.y}
                      stroke={edgeColor}
                      strokeWidth={isDashed ? 1.5 : 2}
                      strokeDasharray={isDashed ? "4,4" : undefined}
                      markerEnd={markerId}
                      opacity={0.85}
                    />
                    {/* Edge Label */}
                    {edge.label && (
                      <text
                        x={midX}
                        y={midY - 5}
                        fill="#10B981"
                        fontSize="10"
                        textAnchor="middle"
                        fontFamily="monospace"
                        className="pointer-events-none select-none"
                      >
                        {edge.label}
                      </text>
                    )}
                  </g>
                );
              })}
            </g>

            {/* NODES LAYER */}
            <g className="nodes-layer">
              {filteredNodes.map((node) => {
                const pos = nodePositions[node.id];
                if (!pos) return null;

                const isCentral = node.is_central;
                const isSelected = selectedNodeId === node.id;
                const borderColor = getNodeBorderColor(node);
                const radius = isCentral ? 32 : 24;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => onSelectNode && onSelectNode(node)}
                    onMouseEnter={() => setHoveredNode(node)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer group"
                  >
                    {/* Central Glowing Halo */}
                    {isCentral && (
                      <circle
                        r="42"
                        fill="rgba(16, 185, 129, 0.12)"
                        className="animate-pulse pointer-events-none"
                      />
                    )}

                    {/* Outer Circle Node */}
                    <circle
                      r={radius}
                      fill="#12141A"
                      stroke={borderColor}
                      strokeWidth={isSelected ? 3 : 2}
                      filter={isCentral ? "url(#risk-glow)" : undefined}
                      className="transition-all duration-150"
                    />

                    {/* Node Icon */}
                    <foreignObject
                      x={-12}
                      y={-12}
                      width="24"
                      height="24"
                      className="pointer-events-none"
                    >
                      <div className="w-full h-full flex items-center justify-center">
                        {getNodeIcon(node)}
                      </div>
                    </foreignObject>

                    {/* Warning Indicator Dot on Perimeter (High Risk Nodes) */}
                    {node.has_warning && !isCentral && (
                      <circle
                        cx={radius * 0.7}
                        cy={radius * 0.7}
                        r="4"
                        fill="#10B981"
                        stroke="#12141A"
                        strokeWidth="1.5"
                      />
                    )}

                    {/* Central Node Risk Badge (87) */}
                    {isCentral && (
                      <g transform={`translate(${radius * 0.7}, ${-radius * 0.7})`}>
                        <circle r="10" fill="#EF4444" />
                        <text
                          textAnchor="middle"
                          dy="3.5"
                          fill="#FFFFFF"
                          fontSize="10"
                          fontWeight="bold"
                          fontFamily="sans-serif"
                        >
                          {node.risk_score || 87}
                        </text>
                      </g>
                    )}

                    {/* Labels Below Node */}
                    <g transform={`translate(0, ${radius + 14})`}>
                      {/* Node Title / Category */}
                      <text
                        textAnchor="middle"
                        fill="#FFFFFF"
                        fontSize={isCentral ? "13" : "11"}
                        fontWeight={isCentral ? "bold" : "600"}
                        fontFamily="sans-serif"
                        className="select-none"
                      >
                        {node.title || node.label}
                      </text>
                      {/* Node Identifier / Subtitle */}
                      <text
                        y="13"
                        textAnchor="middle"
                        fill="#8E93A6"
                        fontSize="10"
                        fontFamily="sans-serif"
                        className="select-none"
                      >
                        {isCentral ? '(User)' : (node.label !== node.title ? node.label : '')}
                      </text>
                    </g>
                  </g>
                );
              })}
            </g>
          </svg>
        )}

        {/* 3. Bottom Overlay: Legend & Zoom Controls */}
        {/* Bottom-Left Legend */}
        <div className="absolute bottom-4 left-4 bg-[#111318]/90 backdrop-blur-sm border border-[#1C1F28] rounded-lg px-3 py-2 flex items-center gap-4 text-xs font-sans text-[#8E93A6] shadow-lg pointer-events-none">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span>User</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#38BDF8]" />
            <span>Device</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#A855F7]" />
            <span>Card</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span>Transaction</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#64748B]" />
            <span>Other</span>
          </div>
          <div className="h-3 w-px bg-[#262A36]" />
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 bg-[#10B981]" />
            <span>Suspicious Path</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-0.5 border-t border-dashed border-[#64748B]" />
            <span>Related</span>
          </div>
        </div>

        {/* Bottom-Right Zoom & Fit Controls */}
        <div className="absolute bottom-4 right-4 flex flex-col gap-1 z-10">
          <button
            onClick={() => setZoom(z => Math.min(2.5, z + 0.15))}
            className="w-8 h-8 rounded-lg bg-[#15171F] border border-[#232733] hover:bg-[#1E222D] text-[#8E93A6] hover:text-white flex items-center justify-center transition-colors shadow-lg"
            title="Zoom In"
          >
            <Plus className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(z => Math.max(0.4, z - 0.15))}
            className="w-8 h-8 rounded-lg bg-[#15171F] border border-[#232733] hover:bg-[#1E222D] text-[#8E93A6] hover:text-white flex items-center justify-center transition-colors shadow-lg"
            title="Zoom Out"
          >
            <Minus className="w-4 h-4" />
          </button>
          <button
            onClick={handleFit}
            className="w-8 h-8 rounded-lg bg-[#15171F] border border-[#232733] hover:bg-[#1E222D] text-[#8E93A6] hover:text-white flex items-center justify-center transition-colors shadow-lg"
            title="Fit to Screen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default PegaGraphCanvas;


