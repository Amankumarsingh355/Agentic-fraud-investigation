import React from 'react';

export const GraphEdge = ({ edge, fromNode, toNode }) => {
  if (!fromNode || !toNode) return null;

  const x1 = fromNode.pixelX;
  const y1 = fromNode.pixelY;
  const x2 = toNode.pixelX;
  const y2 = toNode.pixelY;

  // Calculate slight offset so the arrow doesn't overlap the node circle
  const dx = x2 - x1;
  const dy = y2 - y1;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist === 0) return null;

  const nodeRadius = 24;
  const startX = x1 + (dx / dist) * nodeRadius;
  const startY = y1 + (dy / dist) * nodeRadius;
  const endX = x2 - (dx / dist) * (nodeRadius + 4);
  const endY = y2 - (dy / dist) * (nodeRadius + 4);

  const markerId = `arrow-${edge.color.replace('#', '')}`;

  return (
    <g className="transition-opacity duration-300">
      {/* Background glow stroke */}
      <line
        x1={startX}
        y1={startY}
        x2={endX}
        y2={endY}
        stroke={edge.color}
        strokeWidth={3}
        strokeOpacity={0.25}
        className="pointer-events-none"
      />

      {/* Primary dashed animated edge */}
      <line
        x1={startX}
        y1={startY}
        x2={endX}
        y2={endY}
        stroke={edge.color}
        strokeWidth={1.5}
        strokeDasharray="5 4"
        markerEnd={`url(#${markerId})`}
        className="pointer-events-none"
        style={{
          filter: `drop-shadow(0 0 5px ${edge.color})`
        }}
      >
        <animate
          attributeName="stroke-dashoffset"
          from="0"
          to="-18"
          dur="1.8s"
          repeatCount="indefinite"
        />
      </line>
    </g>
  );
};
