import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import SupplyChainMap from '../components/SupplyChainMap';
import { mockVessels } from '../data/mockData';
import { Compass, Anchor } from 'lucide-react';

export default function NavigatorPage() {
  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Navigator Agent — Maritime Route Optimisation" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#0E6E6A]">
                <Compass className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-base font-semibold text-[#10201E]">Navigator Agent Routing System</h2>
                  <span className="px-2 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                    RUNNING
                  </span>
                </div>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  SATELLITE AIS VESSEL TELEMETRY · AUTOMATED CHOKEPOINT RISK CALCULATIONS
                </p>
              </div>
            </div>
          </div>

          {/* ROUTE STATUS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4 border-t-2 border-t-[#276A4E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Safe Corridors</span>
              <p className="text-3xl font-bold font-mono text-[#276A4E] mt-2">2</p>
              <p className="text-[11px] font-mono text-[#276A4E] mt-1">Persian Gulf & Cape of Good Hope</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#B23A2E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Blocked Corridors</span>
              <p className="text-3xl font-bold font-mono text-[#B23A2E] mt-2">1</p>
              <p className="text-[11px] font-mono text-[#B23A2E] mt-1">Suez / Red Sea Passage Blocked</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#B07A2C]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Rerouted Vessels</span>
              <p className="text-3xl font-bold font-mono text-[#B07A2C] mt-2">2</p>
              <p className="text-[11px] font-mono text-[#4B5A57] mt-1">MT Kaveri & MT Sindhu Detoured</p>
            </div>
          </div>

          {/* ROUTE TABLE */}
          <div className="glass-card p-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#DCE1DF] mb-4">
              <h3 className="text-sm font-semibold text-[#10201E]">
                Active Vessel Maritime Status Telemetry
              </h3>
              <span className="text-xs font-mono text-[#0E6E6A] font-bold">REAL-TIME AIS STREAM</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[10px] font-mono text-[#4B5A57] uppercase bg-[#EAEDEC] border-b border-[#DCE1DF]">
                  <tr>
                    <th className="p-3">Vessel Name</th>
                    <th className="p-3">Supplier</th>
                    <th className="p-3">Origin</th>
                    <th className="p-3">Destination</th>
                    <th className="p-3">Original Route</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Alternate Route</th>
                    <th className="p-3">ETA</th>
                    <th className="p-3">Distance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE1DF]">
                  {mockVessels.map((v) => (
                    <tr key={v.vessel} className="hover:bg-[#EAEDEC] transition-colors">
                      <td className="p-3 font-bold text-[#10201E] flex items-center space-x-2">
                        <Anchor className="w-4 h-4 text-[#0E6E6A]" />
                        <span>{v.vessel}</span>
                      </td>
                      <td className="p-3 text-[#4B5A57]">{v.supplier}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{v.origin}</td>
                      <td className="p-3 font-mono text-[#10201E] font-bold">{v.destination}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{v.originalRoute}</td>
                      <td className="p-3">
                        <span
                          className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                            v.status === 'BLOCKED'
                              ? 'bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30'
                              : 'bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30'
                          }`}
                        >
                          {v.status}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-[#B07A2C] font-semibold">{v.alternateRoute}</td>
                      <td className="p-3 font-mono text-[#10201E] font-bold">{v.eta}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{v.distance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* MAP VISUAL */}
          <SupplyChainMap />
        </main>
      </div>
    </div>
  );
}
