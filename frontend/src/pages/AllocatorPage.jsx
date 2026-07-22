import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { allocationVsReqData } from '../data/mockData';
import { Boxes, CheckCircle2, Zap, Truck, Factory, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function AllocatorPage() {
  const allocationTable = [
    { station: "Kochi Refinery", priority: "CRITICAL", volume: "310 kbd", covers: "14 days", status: "Allocated" },
    { station: "Paradip Refinery", priority: "CRITICAL", volume: "190 kbd", covers: "10 days", status: "Allocated" },
    { station: "Haldia Port", priority: "CRITICAL", volume: "150 kbd", covers: "8 days", status: "Allocated" },
  ];

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Allocator Agent — Reserve & Fuel Allocation" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#2B4C6F]">
                <Boxes className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-base font-semibold text-[#10201E]">Allocator Agent Engine</h2>
                  <span className="px-2 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                    RUNNING
                  </span>
                </div>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  NATIONAL EMERGENCY FUEL ALLOCATION & ESSENTIAL SECTOR RATIONING
                </p>
              </div>
            </div>
          </div>

          {/* TOP CARDS ROW */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4 border-t-2 border-t-[#0E6E6A]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">SPR Release Approved</span>
              <p className="text-3xl font-bold font-mono text-[#0E6E6A] mt-2">500 kbd</p>
              <p className="text-[11px] font-mono text-[#4B5A57] mt-1">ISPRL Padur & Visakhapatnam Reserves</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#B23A2E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Total Gap Remaining</span>
              <p className="text-3xl font-bold font-mono text-[#B23A2E] mt-2">410 kbd</p>
              <p className="text-[11px] font-mono text-[#B23A2E] mt-1">Covered via UAE Spot Contract</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#276A4E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Stations Covered</span>
              <p className="text-3xl font-bold font-mono text-[#276A4E] mt-2">3 of 3</p>
              <p className="text-[11px] font-mono text-[#276A4E] mt-1">Kochi, Paradip, Haldia Fully Allocated</p>
            </div>
          </div>

          {/* ALLOCATION TABLE */}
          <div className="glass-card p-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#DCE1DF] mb-4">
              <h3 className="text-sm font-semibold text-[#10201E]">
                Refinery Reserve Allocation Breakdown
              </h3>
              <span className="text-xs font-mono text-[#276A4E] font-bold">100% DISPATCHED</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[10px] font-mono text-[#4B5A57] uppercase bg-[#EAEDEC] border-b border-[#DCE1DF]">
                  <tr>
                    <th className="p-3">Station</th>
                    <th className="p-3">Priority</th>
                    <th className="p-3">Allocated Volume</th>
                    <th className="p-3">Covers Days</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE1DF]">
                  {allocationTable.map((row) => (
                    <tr key={row.station} className="hover:bg-[#EAEDEC] transition-colors border-l-2 border-l-[#276A4E]">
                      <td className="p-3 font-semibold text-[#10201E]">{row.station}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 text-[10px] font-mono font-bold">
                          {row.priority}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-[#0E6E6A] font-bold">{row.volume}</td>
                      <td className="p-3 font-mono text-[#276A4E] font-bold">{row.covers}</td>
                      <td className="p-3">
                        <span className="px-2.5 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-[10px] font-mono font-bold flex items-center space-x-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>{row.status}</span>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* TWO COLUMN */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Bar Chart (2 Cols) */}
            <div className="glass-card p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-[#10201E] mb-4">
                Allocation vs Requirement per Station (kbd)
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart layout="vertical" data={allocationVsReqData}>
                    <XAxis type="number" stroke="#4B5A57" fontSize={11} />
                    <YAxis dataKey="station" type="category" stroke="#4B5A57" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: '#FAFBFA', borderColor: '#DCE1DF', color: '#10201E' }} />
                    <Legend />
                    <Bar dataKey="required" fill="#B23A2E" name="Required Volume (kbd)" />
                    <Bar dataKey="allocated" fill="#276A4E" name="Allocated Volume (kbd)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Sector Priority Card (1 Col) */}
            <div className="glass-card p-4 space-y-3">
              <div className="pb-3 border-b border-[#DCE1DF]">
                <h3 className="text-sm font-semibold text-[#10201E]">
                  Essential Sector Priority Order
                </h3>
                <p className="text-xs text-[#4B5A57] font-mono">NATIONAL RATIONING HIERARCHY</p>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-3 rounded bg-[#EAEDEC] border border-[#0E6E6A]/30 flex items-start space-x-3">
                  <Zap className="w-4 h-4 text-[#0E6E6A] mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-[#10201E]">1. Power Generation Facilities</h4>
                    <p className="text-[10px] text-[#4B5A57] mt-0.5">Highest priority · Grid protection</p>
                  </div>
                </div>

                <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] flex items-start space-x-3">
                  <Truck className="w-4 h-4 text-[#2B4C6F] mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-[#10201E]">2. Transport Fuel Distribution</h4>
                    <p className="text-[10px] text-[#4B5A57] mt-0.5">Railways, defense & public logistics</p>
                  </div>
                </div>

                <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] flex items-start space-x-3">
                  <Factory className="w-4 h-4 text-purple-700 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-[#10201E]">3. Industrial Refineries</h4>
                    <p className="text-[10px] text-[#4B5A57] mt-0.5">Petrochemical & manufacturing feed</p>
                  </div>
                </div>

                <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] flex items-start space-x-3">
                  <RefreshCw className="w-4 h-4 text-[#4B5A57] mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-[#10201E]">4. Reserve Replenishment</h4>
                    <p className="text-[10px] text-[#4B5A57] mt-0.5">Strategic cavern refilling</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
