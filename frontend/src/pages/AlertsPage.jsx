import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { mockAlertsHistory } from '../data/mockData';
import { Bell, Search } from 'lucide-react';

export default function AlertsPage() {
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [alerts, setAlerts] = useState(mockAlertsHistory);

  const toggleAlertStatus = (id) => {
    setAlerts(alerts.map(a => {
      if (a.id === id) {
        return { ...a, status: a.status === 'New' ? 'Acknowledged' : 'New' };
      }
      return a;
    }));
  };

  const filteredAlerts = alerts.filter(a => {
    if (severityFilter !== 'ALL' && a.severity !== severityFilter) return false;
    if (search && !a.message.toLowerCase().includes(search.toLowerCase()) && !a.agent.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="System Alerts History" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#F7E9E6] border border-[#B23A2E]/30 text-[#B23A2E]">
                <Bell className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-[#10201E]">National Sovereign Alert History</h2>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  AUDITED LOG OF ALL MULTI-AGENT THREAT ALERTS & DECISION TRIGGERS
                </p>
              </div>
            </div>
          </div>

          {/* FILTER BAR */}
          <div className="glass-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-3 py-1.5 rounded text-xs font-mono font-bold transition-all ${
                    severityFilter === sev
                      ? 'bg-[#0E6E6A] text-white'
                      : 'bg-[#FAFBFA] border border-[#DCE1DF] text-[#4B5A57] hover:border-[#0E6E6A]'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>

            <div className="flex items-center space-x-3 w-full md:w-auto">
              <input
                type="date"
                defaultValue="2026-07-21"
                className="bg-[#FAFBFA] border border-[#DCE1DF] text-xs text-[#10201E] rounded px-3 py-1.5 focus:outline-none focus:border-[#0E6E6A] font-mono"
              />
              <div className="relative flex-1 md:w-56">
                <Search className="w-3.5 h-3.5 text-[#4B5A57] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search alerts..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-[#FAFBFA] border border-[#DCE1DF] rounded pl-8 pr-3 py-1.5 text-xs text-[#10201E] focus:outline-none focus:border-[#0E6E6A]"
                />
              </div>
            </div>
          </div>

          {/* ALERTS TABLE */}
          <div className="glass-card p-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-[10px] font-mono text-[#4B5A57] uppercase bg-[#EAEDEC] border-b border-[#DCE1DF]">
                  <tr>
                    <th className="p-3">Alert ID</th>
                    <th className="p-3">Severity</th>
                    <th className="p-3">Alert Message</th>
                    <th className="p-3">Originating Agent</th>
                    <th className="p-3">Affected Corridor / Station</th>
                    <th className="p-3">Timestamp</th>
                    <th className="p-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE1DF]">
                  {filteredAlerts.map((alt) => (
                    <tr key={alt.id} className="hover:bg-[#EAEDEC] transition-colors">
                      <td className="p-3 font-mono font-bold text-[#4B5A57]">{alt.id}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            alt.severity === 'CRITICAL'
                              ? 'bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30'
                              : alt.severity === 'HIGH'
                              ? 'bg-[#F5EDDF] text-[#B07A2C] border border-[#B07A2C]/30'
                              : alt.severity === 'MEDIUM'
                              ? 'bg-[#F5EDDF] text-[#B07A2C] border border-[#B07A2C]/30'
                              : 'bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30'
                          }`}
                        >
                          {alt.severity}
                        </span>
                      </td>
                      <td className="p-3 font-semibold text-[#10201E]">{alt.message}</td>
                      <td className="p-3 font-mono text-[#0E6E6A]">{alt.agent}</td>
                      <td className="p-3 font-mono text-[#4B5A57]">{alt.corridor}</td>
                      <td className="p-3 font-mono text-[#4B5A57] text-[11px]">{alt.timestamp}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => toggleAlertStatus(alt.id)}
                          className={`px-2.5 py-1 rounded text-[10px] font-mono font-bold transition-all ${
                            alt.status === 'New'
                              ? 'bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 animate-pulse'
                              : 'bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30'
                          }`}
                        >
                          {alt.status}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
