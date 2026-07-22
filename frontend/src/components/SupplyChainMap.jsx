import React, { useState } from 'react';
import { Navigation } from 'lucide-react';

export default function SupplyChainMap() {
  const [selectedRoute, setSelectedRoute] = useState(null);

  return (
    <div className="glass-card p-4 relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-3 border-b border-[#DCE1DF]">
        <div>
          <h3 className="text-sm font-semibold text-[#10201E] flex items-center space-x-2">
            <Navigation className="w-4 h-4 text-[#0E6E6A]" />
            <span>Sovereign Maritime Import Corridors & Real-Time Vessel Telemetry</span>
          </h3>
          <p className="text-xs text-[#4B5A57] font-mono mt-0.5">
            LIVE MONITORING · SUEZ / RED SEA / HORMUZ / CAPE DETOUR
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-0.5 bg-[#B23A2E] rounded"></span>
            <span className="text-[#4B5A57]">Blocked / High Risk</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-0.5 bg-[#B07A2C] rounded"></span>
            <span className="text-[#4B5A57]">Rerouted</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-0.5 bg-[#276A4E] rounded"></span>
            <span className="text-[#4B5A57]">Clear</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas Map Visual */}
      <div className="relative w-full h-[380px] bg-[#EAEDEC] rounded-md border border-[#DCE1DF] p-2 overflow-hidden">
        <svg className="w-full h-full" viewBox="0 0 1000 500" fill="none">
          {/* Grid Lines */}
          <pattern id="grid-ops" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#DCE1DF" strokeWidth="0.8" strokeDasharray="2,2" />
          </pattern>
          <rect width="1000" height="500" fill="url(#grid-ops)" />

          {/* Landmass Outlines */}
          {/* Africa & Middle East */}
          <path
            d="M 50 150 Q 150 120 280 180 Q 240 280 200 450 Q 120 420 50 300 Z"
            fill="#D5DBD8"
            stroke="#C1C8C5"
            strokeWidth="1"
          />
          {/* Arabian Peninsula */}
          <path
            d="M 280 180 Q 360 160 440 200 Q 420 280 340 300 Q 300 240 280 180 Z"
            fill="#C9D3CF"
            stroke="#C1C8C5"
            strokeWidth="1"
          />
          {/* India Subcontinent */}
          <path
            d="M 580 160 Q 680 140 760 180 Q 720 340 680 440 Q 620 360 580 160 Z"
            fill="#E4EFEE"
            stroke="#0E6E6A"
            strokeWidth="1.5"
          />

          {/* CORRIDOR ROUTE LINES */}
          {/* 1. Red Sea Corridor (BLOCKED - Dashed Brick Red) */}
          <g className="cursor-pointer" onClick={() => setSelectedRoute('red-sea')}>
            <path
              d="M 250 160 Q 300 220 360 280 T 450 320"
              stroke="#B23A2E"
              strokeWidth="3"
              strokeDasharray="6,4"
              className="animate-pulse"
            />
            <text x="310" y="230" fill="#B23A2E" fontSize="11" fontFamily="JetBrains Mono" fontWeight="bold">
              ⛔ Red Sea Corridor (BLOCKED)
            </text>
          </g>

          {/* 2. Strait of Hormuz Corridor (HIGH RISK - Solid Amber) */}
          <g className="cursor-pointer" onClick={() => setSelectedRoute('hormuz')}>
            <path
              d="M 440 200 Q 480 230 520 250 T 630 260"
              stroke="#B07A2C"
              strokeWidth="2.5"
            />
            <text x="450" y="210" fill="#B07A2C" fontSize="11" fontFamily="JetBrains Mono" fontWeight="bold">
              ⚠️ Strait of Hormuz (HIGH RISK)
            </text>
          </g>

          {/* 3. Persian Gulf Emergency Supply (CLEAR - Solid Sea Green) */}
          <g className="cursor-pointer" onClick={() => setSelectedRoute('persian-gulf')}>
            <path
              d="M 410 210 Q 520 280 640 290"
              stroke="#276A4E"
              strokeWidth="3"
            />
            <text x="470" y="300" fill="#276A4E" fontSize="11" fontFamily="JetBrains Mono" fontWeight="bold">
              ✅ UAE Direct Persian Gulf Route
            </text>
          </g>

          {/* 4. Cape of Good Hope Alternate Route (REROUTED - Muted Amber) */}
          <g className="cursor-pointer" onClick={() => setSelectedRoute('cape')}>
            <path
              d="M 180 430 Q 350 490 550 440 T 670 340"
              stroke="#B07A2C"
              strokeWidth="3"
              strokeDasharray="8,4"
            />
            <text x="320" y="470" fill="#B07A2C" fontSize="11" fontFamily="JetBrains Mono" fontWeight="bold">
              🔄 Cape of Good Hope Reroute (+15 Days)
            </text>
          </g>

          {/* INDIAN REFINERY PORT MARKERS */}
          {/* Kochi Refinery */}
          <g transform="translate(660, 360)">
            <circle r="7" fill="#B23A2E" className="animate-ping opacity-75" />
            <circle r="5" fill="#B23A2E" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="12" y="4" fill="#10201E" fontSize="11" fontWeight="bold" fontFamily="Inter">
              Kochi (10d Stock)
            </text>
          </g>

          {/* Paradip Refinery */}
          <g transform="translate(730, 260)">
            <circle r="7" fill="#B23A2E" className="animate-ping opacity-75" />
            <circle r="5" fill="#B23A2E" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="12" y="4" fill="#10201E" fontSize="11" fontWeight="bold" fontFamily="Inter">
              Paradip (8d Stock)
            </text>
          </g>

          {/* Haldia Port */}
          <g transform="translate(740, 220)">
            <circle r="5" fill="#B23A2E" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="12" y="4" fill="#10201E" fontSize="11" fontWeight="bold" fontFamily="Inter">
              Haldia (6d Stock)
            </text>
          </g>

          {/* Jamnagar Refinery */}
          <g transform="translate(620, 210)">
            <circle r="5" fill="#B07A2C" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="-95" y="4" fill="#10201E" fontSize="11" fontWeight="bold" fontFamily="Inter">
              Jamnagar (7d)
            </text>
          </g>

          {/* HPCL Vizag */}
          <g transform="translate(710, 290)">
            <circle r="5" fill="#B07A2C" stroke="#FFFFFF" strokeWidth="1.5" />
            <text x="12" y="4" fill="#10201E" fontSize="11" fontWeight="bold" fontFamily="Inter">
              Vizag (8d)
            </text>
          </g>

          {/* VESSEL MARKERS */}
          <g transform="translate(380, 460) rotate(45)">
            <polygon points="0,-8 6,8 -6,8" fill="#B07A2C" stroke="#000" strokeWidth="0.5" />
            <text x="10" y="4" fill="#B07A2C" fontSize="10" fontFamily="JetBrains Mono" fontWeight="bold" transform="rotate(-45)">
              🚢 MT Kaveri (Rerouted)
            </text>
          </g>

          <g transform="translate(540, 275) rotate(15)">
            <polygon points="0,-8 6,8 -6,8" fill="#276A4E" stroke="#000" strokeWidth="0.5" />
            <text x="10" y="4" fill="#276A4E" fontSize="10" fontFamily="JetBrains Mono" fontWeight="bold" transform="rotate(-15)">
              🚢 MT Charter 1 (ETA 10d)
            </text>
          </g>
        </svg>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-[#FAFBFA]/95 backdrop-blur border border-[#DCE1DF] p-2.5 rounded-md text-[11px] font-mono space-y-1 text-[#10201E] shadow-sm">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#B23A2E]"></span>
            <span>Critical Disruption: Red Sea Corridor</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#B07A2C]"></span>
            <span>Cape Detour (+15d delay / +$2.1M freight)</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#276A4E]"></span>
            <span>ADNOC Spot Supply Accord Active</span>
          </div>
        </div>
      </div>
    </div>
  );
}
