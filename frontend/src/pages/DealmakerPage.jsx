import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { mockSuppliers, crudePriceData } from '../data/mockData';
import { Handshake, Award } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function DealmakerPage() {
  const [selectedSupplier, setSelectedSupplier] = useState('ADNOC');

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Dealmaker Agent — Spot Market Procurement" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#B07A2C]">
                <Handshake className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-base font-semibold text-[#10201E]">Dealmaker Agent Procurement Engine</h2>
                  <span className="px-2 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                    RUNNING
                  </span>
                </div>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  GLOBAL CRUDE SPOT MARKET REAL-TIME NEGOTIATION & CONTRACT MATCHING
                </p>
              </div>
            </div>
          </div>

          {/* TOP CARDS ROW */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-4 border-t-2 border-t-[#B23A2E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Emergency Volume Needed</span>
              <p className="text-3xl font-bold font-mono text-[#B23A2E] mt-2">410 kbd</p>
              <p className="text-[11px] font-mono text-[#4B5A57] mt-1">To bridge Red Sea diversion gap</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#276A4E]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Best Price Found</span>
              <div className="flex items-center justify-between mt-2">
                <p className="text-3xl font-bold font-mono text-[#276A4E]">$84.50<span className="text-xs text-[#4B5A57]">/bbl</span></p>
                <span className="px-2 py-1 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                  -$2.70 vs Spot Avg
                </span>
              </div>
              <p className="text-[11px] font-mono text-[#276A4E] mt-1">ADNOC UAE Official Tender Proposal</p>
            </div>

            <div className="glass-card p-4 border-t-2 border-t-[#0E6E6A]">
              <span className="text-xs font-mono text-[#4B5A57] uppercase">Est. Total Landed Outlay</span>
              <p className="text-3xl font-bold font-mono text-[#0E6E6A] mt-2">₹1,840 Cr</p>
              <p className="text-[11px] font-mono text-[#4B5A57] mt-1">3-Month Term Accord Coverage</p>
            </div>
          </div>

          {/* SUPPLIER COMPARISON TABLE */}
          <div className="glass-card p-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#DCE1DF] mb-4">
              <h3 className="text-sm font-semibold text-[#10201E]">
                Recommended Spot Procurement Options
              </h3>
              <span className="text-xs font-mono text-[#0E6E6A] font-bold">RANKED BY LANDED ETA & PRICE</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[10px] font-mono text-[#4B5A57] uppercase bg-[#EAEDEC] border-b border-[#DCE1DF]">
                  <tr>
                    <th className="p-3">Rank</th>
                    <th className="p-3">Supplier</th>
                    <th className="p-3">Country</th>
                    <th className="p-3">Corridor</th>
                    <th className="p-3">Volume</th>
                    <th className="p-3">Price / bbl</th>
                    <th className="p-3">Delivery</th>
                    <th className="p-3">Contract</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE1DF]">
                  {mockSuppliers.map((s) => (
                    <tr
                      key={s.name}
                      className={`transition-colors ${
                        s.isBest
                          ? 'bg-[#E4EEE8]/60 border-l-4 border-l-[#276A4E]'
                          : 'hover:bg-[#EAEDEC]'
                      }`}
                    >
                      <td className="p-3 font-mono font-bold text-[#10201E]">
                        {s.isBest ? (
                          <span className="inline-flex items-center space-x-1 text-[#276A4E]">
                            <Award className="w-4 h-4" />
                            <span>#{s.rank}</span>
                          </span>
                        ) : (
                          `#${s.rank}`
                        )}
                      </td>
                      <td className="p-3 font-bold text-[#10201E] flex items-center space-x-2">
                        <span>{s.name}</span>
                        {s.isBest && (
                          <span className="px-1.5 py-0.5 rounded bg-[#276A4E] text-white font-bold text-[9px] font-mono">
                            BEST DEAL
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-[#4B5A57]">{s.country}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{s.corridor}</td>
                      <td className="p-3 font-mono text-[#0E6E6A] font-bold">{s.volume}</td>
                      <td className="p-3 font-mono text-[#276A4E] font-bold">{s.price}</td>
                      <td className="p-3 font-mono text-[#10201E]">{s.delivery}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{s.contract}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => setSelectedSupplier(s.name)}
                          className={`px-3 py-1 rounded text-xs font-mono font-bold transition-all ${
                            selectedSupplier === s.name
                              ? 'bg-[#276A4E] text-white'
                              : 'bg-[#FAFBFA] border border-[#DCE1DF] text-[#10201E] hover:border-[#0E6E6A]'
                          }`}
                        >
                          {selectedSupplier === s.name ? 'Selected' : 'Select'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* PRICE COMPARISON CHART */}
          <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-[#10201E]">
                Brent Crude Spot Price Benchmark (Last 30 Days)
              </h3>
              <span className="text-xs font-mono text-[#276A4E] font-bold">Current Accord Lock: $84.50/bbl</span>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={crudePriceData}>
                  <XAxis dataKey="day" stroke="#4B5A57" fontSize={11} />
                  <YAxis domain={[75, 95]} stroke="#4B5A57" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: '#FAFBFA', borderColor: '#DCE1DF', color: '#10201E' }} />
                  <ReferenceLine y={84.5} label={{ value: 'ADNOC Accord ($84.50)', fill: '#276A4E', fontSize: 11 }} stroke="#276A4E" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="price" stroke="#0E6E6A" strokeWidth={3} dot={{ r: 5, fill: '#0E6E6A' }} name="Brent Spot Price ($/bbl)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
