import React from 'react';
import { Radar, Calculator, BrainCircuit, Boxes, Handshake, Compass } from 'lucide-react';

const agentConfig = [
  { name: 'Scout', role: 'Global Radar', activity: 'Scanning 40+ maritime & geopolitical feeds', icon: Radar },
  { name: 'Accountant', role: 'Cost & Stock', activity: 'Calculating inventory drawdown & landed costs', icon: Calculator },
  { name: 'Strategist', role: 'Playbook', activity: 'Synthesizing national emergency defense plan', icon: BrainCircuit },
  { name: 'Allocator', role: 'Reserves', activity: 'Balancing stock ratio between Kochi & Paradip', icon: Boxes },
  { name: 'Dealmaker', role: 'Procurement', activity: 'Evaluating ADNOC & Aramco spot offers', icon: Handshake },
  { name: 'Navigator', role: 'Maritime AIS', activity: 'Tracking Cape of Good Hope detour telemetry', icon: Compass },
];

export default function AgentStatusCard() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {agentConfig.map((agent) => {
        const Icon = agent.icon;
        return (
          <div
            key={agent.name}
            className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-lg p-3 flex flex-col justify-between space-y-2 group relative transition-all duration-150 hover:border-[#0E6E6A] hover:shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="p-1.5 rounded bg-[#F2F4F3] text-[#0E6E6A]">
                <Icon className="w-3.5 h-3.5 text-[#0E6E6A]" />
              </div>
              <span className="flex items-center space-x-1 text-[10px] font-mono text-[#276A4E] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-[#276A4E] animate-breathe"></span>
                <span>Active</span>
              </span>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-[#10201E] group-hover:text-[#0E6E6A] transition-colors leading-snug">
                {agent.name}
              </h4>
              <p className="text-[10px] text-[#4B5A57] truncate font-mono">{agent.role}</p>
            </div>

            <div className="pt-1.5 border-t border-[#EAEDEC] flex items-center justify-between text-[10px] font-mono text-[#4B5A57]">
              <span>Scan:</span>
              <span className="text-[#10201E] font-medium">2m ago</span>
            </div>

            {/* Linear Style Tooltip */}
            <div className="absolute left-1/2 -bottom-9 -translate-x-1/2 hidden group-hover:block z-50 bg-[#10201E] text-white text-[10px] font-mono px-2.5 py-1 rounded shadow-lg whitespace-nowrap pointer-events-none border border-white/10">
              {agent.activity}
            </div>
          </div>
        );
      })}
    </div>
  );
}
