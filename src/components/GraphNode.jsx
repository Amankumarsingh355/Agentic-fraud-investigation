import React from 'react';
import { User, Laptop, Wallet, Receipt, Shield } from 'lucide-react';

const iconMap = {
  User,
  Laptop,
  Wallet,
  Receipt,
  Shield
};

export const GraphNode = ({ node, isSelected, onClick, onMouseEnter, onMouseLeave }) => {
  const IconComponent = iconMap[node.icon] || User;

  return (
    <g
      transform={`translate(${node.pixelX}, ${node.pixelY})`}
      className="cursor-pointer group"
      onClick={() => onClick(node)}
      onMouseEnter={(e) => onMouseEnter(node, e)}
      onMouseLeave={onMouseLeave}
    >
      {/* Outer Halo / Pulsing Glow */}
      <circle
        r={isSelected ? 32 : 28}
        fill="transparent"
        stroke={node.color}
        strokeWidth={isSelected ? 2 : 1}
        strokeDasharray={isSelected ? "4 2" : "none"}
        className="transition-all duration-300 opacity-40 group-hover:opacity-100 group-hover:scale-110"
        style={{
          filter: `drop-shadow(0 0 10px ${node.glowColor})`
        }}
      />

      {/* Main Node Background Circle */}
      <circle
        r={22}
        fill="#080E17"
        stroke={node.color}
        strokeWidth={2}
        className="transition-transform duration-200 group-hover:scale-105"
        style={{
          filter: `drop-shadow(0 0 8px ${node.glowColor})`
        }}
      />

      {/* Icon Centered */}
      <foreignObject x={-12} y={-12} width={24} height={24} className="pointer-events-none">
        <div className="w-full h-full flex items-center justify-center" style={{ color: node.color }}>
          <IconComponent className="w-4 h-4 stroke-[2.2]" />
        </div>
      </foreignObject>

      {/* Primary Label */}
      <text
        y={36}
        textAnchor="middle"
        className="text-[11px] font-mono font-bold fill-white tracking-wider pointer-events-none select-none"
      >
        {node.label}
      </text>

      {/* Sublabel or Badge */}
      {node.badge ? (
        <g transform="translate(0, 44)">
          <rect
            x={-24}
            y={0}
            width={48}
            height={14}
            rx={3}
            fill={node.badgeColor === 'crimson' ? '#450A0A' : '#064E3B'}
            stroke={node.badgeColor === 'crimson' ? '#FF334B' : '#00FF88'}
            strokeWidth={1}
            style={{
              filter: `drop-shadow(0 0 6px ${node.badgeColor === 'crimson' ? 'rgba(255,51,75,0.4)' : 'rgba(0,255,136,0.4)'})`
            }}
          />
          <text
            y={10}
            textAnchor="middle"
            className={`text-[8.5px] font-mono font-bold tracking-wider uppercase pointer-events-none select-none ${
              node.badgeColor === 'crimson' ? 'fill-cyber-crimson' : 'fill-cyber-emerald'
            }`}
          >
            {node.badge}
          </text>
        </g>
      ) : node.sublabel ? (
        <text
          y={48}
          textAnchor="middle"
          className="text-[9.5px] font-mono font-medium fill-cyan-400/80 pointer-events-none select-none"
        >
          {node.sublabel}
        </text>
      ) : null}
    </g>
  );
};
