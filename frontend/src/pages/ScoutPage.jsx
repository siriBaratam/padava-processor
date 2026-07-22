import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { mockScoutAlerts } from '../data/mockData';
import { Radar, Search, ExternalLink } from 'lucide-react';

export default function ScoutPage() {
  const [filterType, setFilterType] = useState('ALL');

  const filteredNews = mockScoutAlerts.filter((item) => {
    if (filterType !== 'ALL' && item.type !== filterType) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex font-sans">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Scout Agent — Global Intelligence Radar" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-4 overflow-y-auto max-w-6xl mx-auto w-full">
          {/* HEADER */}
          <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3.5 flex items-center justify-between font-mono text-xs">
            <div className="flex items-center space-x-3">
              <Radar className="w-5 h-5 text-[#276A4E] animate-pulse" />
              <div>
                <span className="font-bold text-[#10201E] font-sans">Scout Agent Intelligence Radar</span>
                <span className="ml-2 px-1.5 py-0.5 rounded bg-[#E4EEE8] text-[#276A4E] text-[10px] font-bold">RUNNING</span>
              </div>
            </div>
            <div className="text-[11px] text-[#4B5A57]">
              Scan rate: <span className="text-[#276A4E] font-bold">5,000 feeds/sec</span>
            </div>
          </div>

          {/* FILTER BAR */}
          <div className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-2.5 flex items-center space-x-2 font-mono text-xs">
            {['ALL', 'BAD', 'GOOD', 'NEUTRAL'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                  filterType === t
                    ? 'bg-[#0E6E6A] text-white'
                    : 'bg-[#F2F4F3] text-[#4B5A57] hover:text-[#10201E]'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* TIMELINE FEED ITEM LIST */}
          <div className="space-y-2 font-mono text-xs">
            {filteredNews.map((item) => (
              <div
                key={item.id}
                className="bg-[#FAFBFA] border border-[#DCE1DF] rounded-md p-3 flex items-center justify-between gap-3 hover:border-[#0E6E6A] transition-colors"
              >
                <div className="flex items-center space-x-3 truncate">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold flex-shrink-0 ${item.type === 'BAD' ? 'bg-[#F7E9E6] text-[#B23A2E]' : 'bg-[#E4EEE8] text-[#276A4E]'}`}>
                    {item.RiskScore}/10
                  </span>

                  <span className="font-sans font-semibold text-[#10201E] truncate">{item.Headline}</span>
                </div>

                <div className="flex items-center space-x-3 text-[11px] text-[#4B5A57] flex-shrink-0">
                  <span className="px-1.5 py-0.5 rounded bg-[#F2F4F3] border border-[#DCE1DF] text-[#0E6E6A]">
                    {item.corridor}
                  </span>
                  <span>{item.source}</span>
                  <span className="text-[#10201E]">{item.timeAgo}</span>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
