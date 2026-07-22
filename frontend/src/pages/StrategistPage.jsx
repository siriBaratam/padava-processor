import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { BrainCircuit } from 'lucide-react';

export default function StrategistPage() {
  const [actions, setActions] = useState([
    { id: 1, text: "Issue maritime mandate to reroute MT Kaveri & MT Sindhu via Cape of Good Hope", urgency: "IMMEDIATE", status: "Done" },
    { id: 2, text: "Authorize 5-day Indian Strategic Petroleum Reserve (ISPRL) drawdown for Kochi & Paradip", urgency: "IMMEDIATE", status: "In Progress" },
    { id: 3, text: "Activate spot market procurement protocol with ADNOC UAE for 410,000 bpd gap", urgency: "48HR", status: "Pending" },
  ]);

  const toggleStatus = (id) => {
    setActions(actions.map(a => {
      if (a.id === id) {
        const nextStatus = a.status === 'Pending' ? 'In Progress' : a.status === 'In Progress' ? 'Done' : 'Pending';
        return { ...a, status: nextStatus };
      }
      return a;
    }));
  };

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Strategist Agent — Sovereign Response Engine" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#0E6E6A]">
                <BrainCircuit className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-base font-semibold text-[#10201E]">Strategist Agent Response Engine</h2>
                  <span className="px-2 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                    RUNNING
                  </span>
                </div>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  MATCHING THREAT SCENARIOS TO NATIONAL DEFENSE ENERGY PLAYBOOKS
                </p>
              </div>
            </div>

            <div className="text-xs font-mono text-[#4B5A57]">
              Generated: <span className="text-[#0E6E6A] font-bold">6 minutes ago</span>
            </div>
          </div>

          {/* LARGE STRATEGY RECOMMENDATION CARD */}
          <div className="glass-card p-6 border-[#0E6E6A]/40 bg-[#FAFBFA]">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#DCE1DF]">
              <div className="flex items-center space-x-3">
                <span className="px-3 py-1 rounded bg-[#B23A2E] text-white font-bold text-xs font-mono animate-pulse">
                  IMMEDIATE ACTION MANDATED
                </span>
                <span className="text-xs text-[#4B5A57] font-mono">STRATEGY CODE: SG-2026-REDSEA-ALPHA</span>
              </div>
              <span className="text-xs text-[#0E6E6A] font-mono font-semibold">Confidence: 98.4%</span>
            </div>

            <h2 className="text-2xl font-semibold tracking-tight-title text-[#10201E] mb-4">
              Emergency Reroute + Strategic Petroleum Reserve (SPR) Drawdown
            </h2>

            <div className="space-y-3 mb-6">
              <div className="flex items-start space-x-3 text-sm text-[#10201E]">
                <span className="w-6 h-6 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 text-[#0E6E6A] font-mono font-bold flex items-center justify-center text-xs flex-shrink-0">
                  1
                </span>
                <p className="mt-0.5">
                  Reroute <strong className="text-[#0E6E6A] font-mono">MT Kaveri</strong> and <strong className="text-[#0E6E6A] font-mono">MT Sindhu</strong> via Cape of Good Hope immediately to bypass Red Sea hostilities.
                </p>
              </div>
              <div className="flex items-start space-x-3 text-sm text-[#10201E]">
                <span className="w-6 h-6 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 text-[#0E6E6A] font-mono font-bold flex items-center justify-center text-xs flex-shrink-0">
                  2
                </span>
                <p className="mt-0.5">
                  Authorise 5-day Strategic Petroleum Reserve (SPR) drawdown for <strong className="text-[#B23A2E]">Kochi</strong> and <strong className="text-[#B23A2E]">Paradip</strong> refineries to prevent stockout.
                </p>
              </div>
              <div className="flex items-start space-x-3 text-sm text-[#10201E]">
                <span className="w-6 h-6 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 text-[#0E6E6A] font-mono font-bold flex items-center justify-center text-xs flex-shrink-0">
                  3
                </span>
                <p className="mt-0.5">
                  Activate spot market emergency crude procurement from UAE (<strong className="text-[#276A4E] font-mono">ADNOC</strong>) for <strong className="text-[#0E6E6A] font-mono">410,000 bpd</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* TWO COLUMN */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Response Playbook Card */}
            <div className="glass-card p-4 space-y-4">
              <div className="pb-3 border-b border-[#DCE1DF]">
                <h3 className="text-sm font-semibold text-[#10201E]">
                  National Response Playbook Engine
                </h3>
                <p className="text-xs text-[#4B5A57] font-mono">MATCHED PROTOCOL DATA</p>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <span className="text-[#4B5A57] font-mono">Event Type Detected:</span>
                  <span className="font-mono text-[#B23A2E] font-bold">military_attack</span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <span className="text-[#4B5A57] font-mono">Matched Strategy:</span>
                  <span className="font-semibold text-[#0E6E6A]">Emergency reroute + reserve activation</span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <span className="text-[#4B5A57] font-mono">SPR Action:</span>
                  <span className="px-2 py-0.5 rounded bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 font-mono font-bold">
                    DRAWDOWN (REQUIRED)
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <span className="text-[#4B5A57] font-mono">Reroute Needed:</span>
                  <span className="px-2 py-0.5 rounded bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 font-mono font-bold">
                    YES (CAPE DETOUR)
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <span className="text-[#4B5A57] font-mono">Emergency Procurement:</span>
                  <span className="px-2 py-0.5 rounded bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 font-mono font-bold">
                    YES (ADNOC SPOT)
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Priority Actions Card */}
            <div className="glass-card p-4 space-y-4">
              <div className="pb-3 border-b border-[#DCE1DF] flex items-center justify-between">
                <h3 className="text-sm font-semibold text-[#10201E]">
                  Priority Action Execution Items
                </h3>
                <span className="text-[10px] font-mono text-[#4B5A57]">Click badge to toggle status</span>
              </div>

              <div className="space-y-3">
                {actions.map((act) => (
                  <div key={act.id} className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] flex items-start justify-between gap-3">
                    <div className="flex items-start space-x-3">
                      <span className="w-5 h-5 rounded-full bg-[#E4EFEE] text-[#0E6E6A] font-mono font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                        #{act.id}
                      </span>
                      <div>
                        <p className="text-xs text-[#10201E] font-medium">{act.text}</p>
                        <span className="inline-block mt-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#E4EFEE] text-[#0E6E6A] border border-[#0E6E6A]/20">
                          Urgency: {act.urgency}
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleStatus(act.id)}
                      className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all flex-shrink-0 ${
                        act.status === 'Done'
                          ? 'bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30'
                          : act.status === 'In Progress'
                          ? 'bg-[#F5EDDF] text-[#B07A2C] border border-[#B07A2C]/30'
                          : 'bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30'
                      }`}
                    >
                      {act.status}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
