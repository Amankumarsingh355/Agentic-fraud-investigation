import React from 'react';
import { Terminal, Crosshair, Play, RotateCcw, ShieldCheck } from 'lucide-react';

export const Header = ({ onExecuteScan, isScanning, scanProgress, confidence = "98.4%" }) => {
  return (
    <header className="relative w-full border border-cyber-border bg-cyber-panel/90 backdrop-blur-md rounded-lg p-3 px-4 shadow-[0_0_20px_rgba(0,0,0,0.8)] mb-3 overflow-hidden">
      {/* Top micro cyan accent line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyber-cyan via-cyber-cyan/50 to-transparent" />

      <div className="flex flex-col lg:flex-row items-center justify-between gap-4">
        {/* Left: Terminal Icon + Title + Subtitle */}
        <div className="flex items-center gap-3.5 w-full lg:w-auto">
          {/* Terminal Icon Box */}
          <div className="w-10 h-10 rounded-md border border-cyber-cyan/60 bg-cyber-dark/80 flex items-center justify-center text-cyber-cyan shadow-[0_0_12px_rgba(0,229,255,0.35)] shrink-0">
            <span className="font-mono font-bold text-lg select-none text-cyber-cyan">&gt;_</span>
          </div>

          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <h1 className="text-lg md:text-xl font-mono font-extrabold tracking-wider text-white flex items-center">
                AGENTIC_NEURAL_SHIELD
                <span className="text-cyber-cyan ml-2 text-base font-semibold">// v2.6</span>
              </h1>
            </div>
            <p className="text-[11px] font-mono text-cyan-400/70 tracking-widest uppercase font-medium">
              TIGERGRAPH + OLLAMA MULTI-AGENT FRAUD ENGINE
            </p>
          </div>
        </div>

        {/* Center / Stats: Accuracy & Online Status */}
        <div className="flex items-center gap-4 text-xs font-mono">
          {/* Accuracy Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-cyan-500/40 bg-cyber-dark/70 text-cyan-300 shadow-[0_0_10px_rgba(0,229,255,0.15)]">
            <Crosshair className="w-3.5 h-3.5 text-cyber-cyan stroke-[2.5]" />
            <span className="text-slate-400">ACCURACY:</span>
            <span className="font-bold text-cyber-cyan">{confidence}</span>
          </div>

          {/* Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-500/30 bg-cyber-dark/70 text-cyber-emerald shadow-[0_0_10px_rgba(0,255,136,0.15)]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-emerald opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-emerald"></span>
            </span>
            <span className="text-slate-400">STATUS:</span>
            <span className="font-bold text-cyber-emerald">ONLINE</span>
          </div>
        </div>

        {/* Right: EXECUTE SCAN Button */}
        <div className="w-full lg:w-auto flex justify-end">
          <button
            onClick={onExecuteScan}
            disabled={isScanning}
            className={`
              relative group flex items-center justify-center gap-2.5 px-6 py-2 rounded-md font-mono text-xs font-bold tracking-wider uppercase transition-all duration-300
              ${isScanning
                ? 'bg-cyan-950/80 border border-cyber-cyan text-cyber-cyan cursor-wait shadow-[0_0_18px_rgba(0,229,255,0.5)]'
                : 'bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyber-cyan text-white hover:text-cyber-cyan shadow-[0_0_15px_rgba(0,229,255,0.35)] hover:shadow-[0_0_25px_rgba(0,229,255,0.6)] active:scale-[0.98]'
              }
            `}
          >
            {isScanning ? (
              <>
                <RotateCcw className="w-4 h-4 animate-spin text-cyber-cyan" />
                <span>SCANNING... ({scanProgress}%)</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-cyber-cyan text-cyber-cyan group-hover:scale-110 transition-transform" />
                <span className="text-cyber-cyan font-extrabold">EXECUTE SCAN</span>
              </>
            )}
            
            {/* Cyber corner marks */}
            <span className="absolute top-0 right-0 w-1.5 h-1.5 border-t border-r border-cyber-cyan" />
            <span className="absolute bottom-0 left-0 w-1.5 h-1.5 border-b border-l border-cyber-cyan" />
          </button>
        </div>
      </div>
    </header>
  );
};
