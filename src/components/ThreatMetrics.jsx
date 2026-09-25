import React from 'react';
import { ThreatGauge } from './ThreatGauge';
import { RecommendedActions } from './RecommendedActions';
import { KeyInsights } from './KeyInsights';

export const ThreatMetrics = ({ 
  riskScore = 0.94, 
  onAutoFreeze, 
  onEscalate,
  onSelectInsight 
}) => {
  return (
    <div className="flex flex-col h-full">
      {/* 1. Threat Level Gauge */}
      <ThreatGauge riskScore={riskScore} />

      {/* 2. Recommended Action */}
      <RecommendedActions 
        onAutoFreeze={onAutoFreeze} 
        onEscalate={onEscalate} 
      />

      {/* 3. Key Insights */}
      <KeyInsights onSelectInsight={onSelectInsight} />
    </div>
  );
};
