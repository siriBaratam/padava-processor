import React from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { mockStations } from '../data/mockData';
import { Calculator } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function AccountantPage() {
  const chartData = mockStations.map((s) => ({
    name: s.name.replace(' Refinery', '').replace(' Port', ''),
    stockDays: s.stockDays,
    gapDays: parseInt(s.daysGap),
  }));

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex font-sans">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Accountant Agent — Financial Impact Engine" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-4 overflow-y-auto max-w-6xl mx-auto w-full">
          {/* HEADER */}
          <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 flex items-center justify-between font-mono text-xs">
            <div className="flex items-center space-x-3">
              <Calculator className="w-5 h-5 text-[#2B4C6F]" />
              <div>
                <span className="font-bold text-[#10201E] font-sans">Accountant Financial Model</span>
                <span className="ml-2 px-1.5 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] text-[10px] font-bold">ACTIVE</span>
              </div>
            </div>
            <div className="text-[#0E6E6A] font-bold">
              Daily Impact: ₹420 Cr/day
            </div>
          </div>

          {/* TOP METRIC CARDS */}
          <div className="grid grid-cols-3 gap-3 font-mono text-xs">
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3">
              <span className="text-[10px] text-[#4B5A57] uppercase">Stockout Risk</span>
              <p className="text-lg font-bold text-[#B23A2E] mt-1">3 Refineries</p>
            </div>
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3">
              <span className="text-[10px] text-[#4B5A57] uppercase">Freight Surcharge</span>
              <p className="text-lg font-bold text-[#0E6E6A] mt-1">+12.4% Spot</p>
            </div>
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3">
              <span className="text-[10px] text-[#4B5A57] uppercase">Average Gap</span>
              <p className="text-lg font-bold text-[#B23A2E] mt-1">19 Days</p>
            </div>
          </div>

          {/* TABLE & BAR CHART */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Table */}
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-4 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[#EAEDEC] font-mono text-xs font-bold text-[#10201E]">
                <span>Refinery Inventory Gap</span>
                <span className="text-[#4B5A57] font-normal">5 Stations</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="text-[9px] text-[#4B5A57] uppercase border-b border-[#EAEDEC]">
                    <tr>
                      <th className="pb-1.5 px-1">Station</th>
                      <th className="pb-1.5 px-1">Stock</th>
                      <th className="pb-1.5 px-1">Delay</th>
                      <th className="pb-1.5 px-1 text-right">Risk</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#EAEDEC]">
                    {mockStations.map((s) => (
                      <tr key={s.name} className="hover:bg-[#F2F4F3]/60">
                        <td className="py-2 px-1 font-sans font-semibold text-[#10201E]">{s.name}</td>
                        <td className="py-2 px-1 text-[#0E6E6A] font-bold">{s.stockDays}d</td>
                        <td className="py-2 px-1 text-[#B23A2E]">{s.delay}</td>
                        <td className="py-2 px-1 text-right">
                          <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${s.risk === 'CRITICAL' ? 'bg-[#F7E9E6] text-[#B23A2E]' : 'bg-[#F5EDDF] text-[#B07A2C]'}`}>
                            {s.risk}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-4">
              <h3 className="text-xs font-mono font-bold text-[#10201E] mb-3">Stock Days vs Supply Gap</h3>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" stroke="#4B5A57" fontSize={10} />
                    <YAxis stroke="#4B5A57" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#FAFBFA', borderColor: '#DCE1DF', color: '#10201E', fontSize: '11px' }} />
                    <Bar dataKey="stockDays" fill="#0E6E6A" name="Stock Days" />
                    <Bar dataKey="gapDays" fill="#B23A2E" name="Gap Days" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
