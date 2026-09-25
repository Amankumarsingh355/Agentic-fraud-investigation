import React, { useEffect, useState } from 'react';
import { AlertTriangle } from 'lucide-react';

export const ThreatGauge = ({ riskScore = 0.94 }) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1200; // ms
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = riskScore / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= riskScore) {
        setAnimatedScore(riskScore);
        clearInterval(timer);
      } else {
        setAnimatedScore(Number(start.toFixed(2)));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [riskScore]);

  // SVG Gauge calculations
  // Arc angle from 140 deg to 400 deg (260 degree total span)
  const radius = 68;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  // We use a 240-degree arc (around 66.6% of full circle)
  const arcLength = circumference * (240 / 360);
  const strokeDashoffset = arcLength - (arcLength * (animatedScore / 1.0));

  return (
    <div className="flex flex-col border border-cyber-border bg-cyber-panel/85 rounded-lg p-3.5 shadow-[0_0_18px_rgba(0,0,0,0.8)] relative overflow-hidden">
      {/* Top Header */}
      <div className="flex items-center gap-2 pb-2 mb-2 border-b border-cyber-border/60">
        <AlertTriangle className="w-4 h-4 text-cyber-crimson stroke-[2.5]" />
        <h3 className="text-xs font-mono font-extrabold tracking-wider text-cyber-crimson uppercase">
          THREAT LEVEL
        </h3>
      </div>

      {/* Speedometer Gauge Visual */}
      <div className="relative flex flex-col items-center justify-center my-1">
        <svg width="190" height="150" viewBox="0 0 200 160" className="overflow-visible">
          <defs>
            {/* Red Glow Filter */}
            <filter id="gauge-glow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            {/* Linear gradient for stroke */}
            <linearGradient id="crimson-grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#EF4444" />
              <stop offset="100%" stopColor="#FF334B" />
            </linearGradient>
          </defs>

          {/* Background Track Arc */}
          <path
            d="M 35 130 A 68 68 0 1 1 165 130"
            fill="none"
            stroke="#121D2C"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Cyan outer reference tick marks */}
          <path
            d="M 31 133 A 75 75 0 1 1 169 133"
            fill="none"
            stroke="#00E5FF"
            strokeWidth="1.5"
            strokeDasharray="2 10"
            strokeOpacity="0.4"
          />

          {/* Active Red Progress Arc */}
          <path
            d="M 35 130 A 68 68 0 1 1 165 130"
            fill="none"
            stroke="url(#crimson-grad)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            filter="url(#gauge-glow)"
            className="transition-all duration-300"
          />
        </svg>

        {/* Center Numbers Readout */}
        <div className="absolute top-[52px] flex flex-col items-center select-none">
          <div className="flex items-baseline">
            <span className="text-3xl font-mono font-extrabold text-cyber-crimson tracking-tight shadow-sm" style={{ filter: "drop-shadow(0 0 8px rgba(255,51,75,0.6))" }}>
              {animatedScore.toFixed(2)}
            </span>
            <span className="text-sm font-mono font-semibold text-red-400/60 ml-0.5">
              /1
            </span>
          </div>
          <span className="text-[9.5px] font-mono font-bold tracking-widest text-cyan-400/80 uppercase mt-0.5">
            RISK SCORE
          </span>
        </div>

        {/* CRITICAL Badge */}
        <div className="mt-1 px-5 py-1 rounded-md border border-cyber-crimson bg-red-950/60 text-cyber-crimson text-xs font-mono font-extrabold tracking-widest uppercase shadow-[0_0_15px_rgba(255,51,75,0.45)]">
          CRITICAL
        </div>
      </div>
    </div>
  );
};
