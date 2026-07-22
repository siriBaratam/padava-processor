import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import AgentStatusCard from '../components/AgentStatusCard';
import SupplyChainMap from '../components/SupplyChainMap';
import { mockScoutAlerts, mockStations } from '../data/mockData';
import { ArrowUpRight, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const latestAlerts = mockScoutAlerts.slice(0, 4);
  const criticalStations = mockStations.filter(s => s.risk === 'CRITICAL');

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex font-sans">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Command Dashboard" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto max-w-7xl mx-auto w-full">
          
          {/* CURSOR-INSPIRED MINIMAL ALERT BAR */}
          <div className="bg-[#F7E9E6] border border-[#B23A2E]/20 rounded-md px-4 py-2.5 text-[#B23A2E] flex items-center justify-between gap-3 font-mono text-xs">
            <div className="flex items-center space-x-2.5 truncate">
              <span className="w-2 h-2 rounded-full bg-[#B23A2E] animate-ping flex-shrink-0"></span>
              <span className="font-bold uppercase tracking-wider">CRITICAL:</span>
              <span className="text-[#10201E] font-sans truncate">Red Sea corridor blocked · Kochi & Paradip at risk</span>
              <span className="px-1.5 py-0.5 rounded bg-[#B23A2E] text-white text-[10px] font-bold">8.7/10</span>
            </div>

            <button className="px-2.5 py-1 bg-[#B23A2E] hover:bg-[#8F2E24] text-white text-[11px] font-bold rounded transition-all flex items-center space-x-1 flex-shrink-0">
              <span>PLAYBOOK</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          {/* CURSOR METRIC CARDS GRID */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] font-mono text-[#4B5A57] uppercase tracking-wider">Active Alerts</span>
              <p className="text-2xl font-bold font-mono text-[#10201E]">7 <span className="text-xs font-normal text-[#B23A2E]">(3 Critical)</span></p>
            </div>

            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] font-mono text-[#4B5A57] uppercase tracking-wider">Stations at Risk</span>
              <p className="text-2xl font-bold font-mono text-[#B07A2C]">3 <span className="text-xs font-normal text-[#4B5A57]">(Kochi, Paradip)</span></p>
            </div>

            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] font-mono text-[#4B5A57] uppercase tracking-wider">Severity Tier</span>
              <p className="text-2xl font-bold font-mono text-[#B23A2E]">CRITICAL</p>
            </div>

            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] font-mono text-[#4B5A57] uppercase tracking-wider">Cost Surcharge</span>
              <p className="text-2xl font-bold font-mono text-[#0E6E6A]">₹420 Cr<span className="text-xs font-normal text-[#4B5A57]">/day</span></p>
            </div>
          </div>

          {/* FLEET STATUS GRID */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-[#4B5A57] uppercase tracking-wider">
              <span>Agent Fleet Telemetry</span>
              <span className="text-[#276A4E] font-semibold">● 6 ACTIVE</span>
            </div>
            <AgentStatusCard />
          </div>

          {/* TWO COLUMN MINIMAL CONTENT */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            {/* Left: Intelligence Stream */}
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-4 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[#EAEDEC]">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#10201E]">Scout Intel Stream</h3>
                <span className="text-[10px] font-mono text-[#0E6E6A]">REALTIME</span>
              </div>

              <div className="space-y-2">
                {latestAlerts.map((alert) => (
                  <div key={alert.id} className="p-2 rounded bg-[#F2F4F3]/80 border border-[#DCE1DF]/60 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2 truncate">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${alert.type === 'BAD' ? 'bg-[#F7E9E6] text-[#B23A2E]' : 'bg-[#E4EEE8] text-[#276A4E]'}`}>
                        {alert.type}
                      </span>
                      <span className="text-[#10201E] font-sans truncate">{alert.headline}</span>
                    </div>
                    <span className="text-[10px] text-[#4B5A57] flex-shrink-0 ml-2">{alert.timeAgo}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Vulnerability Matrix */}
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-4 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[#EAEDEC]">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#10201E]">Refinery Vulnerability</h3>
                <span className="text-[10px] font-mono text-[#B23A2E] font-bold">3 CRITICAL</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="text-[9px] text-[#4B5A57] uppercase border-b border-[#EAEDEC]">
                    <tr>
                      <th className="pb-1.5 px-1">Station</th>
                      <th className="pb-1.5 px-1">Corridor</th>
                      <th className="pb-1.5 px-1">Stock</th>
                      <th className="pb-1.5 px-1">Gap</th>
                      <th className="pb-1.5 px-1 text-right">Risk</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#EAEDEC]">
                    {criticalStations.map((s) => (
                      <tr key={s.name} className="hover:bg-[#F2F4F3]/60">
                        <td className="py-2 px-1 font-sans font-semibold text-[#10201E]">{s.name}</td>
                        <td className="py-2 px-1 text-[#4B5A57]">{s.corridor}</td>
                        <td className="py-2 px-1 text-[#10201E]">{s.stockDays}d</td>
                        <td className="py-2 px-1 text-[#B23A2E] font-bold">{s.daysGap}</td>
                        <td className="py-2 px-1 text-right">
                          <span className="px-1.5 py-0.5 rounded bg-[#F7E9E6] text-[#B23A2E] text-[9px] font-bold">CRITICAL</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* MAP VISUAL */}
          <SupplyChainMap />

        </main>
      </div>
    </div>
  );
}
