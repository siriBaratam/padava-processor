import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { FileText, Download, RefreshCw, Shield } from 'lucide-react';

export default function ReportsPage() {
  const [reportType, setReportType] = useState('Full Report');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="Executive Intelligence Reports" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto">
          {/* HEADER */}
          <div className="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#0E6E6A]">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-[#10201E]">National Energy Resilience Reports</h2>
                <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                  AUTOMATED EXECUTIVE SUMMARY & SOVEREIGN AUDIT COMPLIANCE MODULE
                </p>
              </div>
            </div>
          </div>

          {/* CONTROLS BAR */}
          <div className="glass-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
              <div>
                <label className="block text-[10px] font-mono text-[#4B5A57] mb-1">DATE RANGE</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="date"
                    defaultValue="2026-07-01"
                    className="bg-[#FAFBFA] border border-[#DCE1DF] text-xs text-[#10201E] rounded px-2.5 py-1.5 font-mono"
                  />
                  <span className="text-xs text-[#4B5A57]">to</span>
                  <input
                    type="date"
                    defaultValue="2026-07-21"
                    className="bg-[#FAFBFA] border border-[#DCE1DF] text-xs text-[#10201E] rounded px-2.5 py-1.5 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-mono text-[#4B5A57] mb-1">REPORT TYPE</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="bg-[#FAFBFA] border border-[#DCE1DF] text-xs text-[#10201E] rounded px-3 py-1.5 font-mono"
                >
                  <option value="Full Report">Full Sovereign Resilience Audit</option>
                  <option value="Scout Only">Scout Intelligence Summary</option>
                  <option value="Accountant Only">Refinery Financial Impact</option>
                  <option value="Strategist Only">Response Playbook Assessment</option>
                  <option value="Navigator Only">Maritime Route Telemetry</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="px-4 py-2 bg-[#0E6E6A] hover:bg-[#0A5653] text-white font-semibold text-xs rounded transition-all flex items-center space-x-2 shadow-sm"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
                <span>{isGenerating ? 'Generating...' : 'Generate Report'}</span>
              </button>

              <button className="px-4 py-2 border border-[#DCE1DF] hover:bg-[#EAEDEC] text-[#10201E] bg-[#FAFBFA] text-xs rounded transition-all flex items-center space-x-2">
                <Download className="w-3.5 h-3.5 text-[#0E6E6A]" />
                <span>Download PDF</span>
              </button>
            </div>
          </div>

          {/* REPORT PREVIEW CARD */}
          <div className="glass-card p-8 border-[#DCE1DF] bg-[#FAFBFA]">
            <div className="flex items-center justify-between pb-6 border-b border-[#DCE1DF] mb-6">
              <div className="flex items-center space-x-3">
                <Shield className="w-8 h-8 text-[#0E6E6A]" />
                <div>
                  <h3 className="text-xl font-semibold tracking-tight text-[#10201E]">
                    EnergyGuard AI — Sovereign Executive Briefing
                  </h3>
                  <p className="text-xs text-[#4B5A57] font-mono">
                    CLASSIFICATION: SECRET / FOR MINISTRY EYES ONLY · REF: EG-2026-REPORT-0721
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-xs font-mono font-bold">
                AUDITED & VERIFIED
              </span>
            </div>

            <div className="space-y-6 text-sm text-[#4B5A57]">
              <div>
                <h4 className="text-xs font-mono uppercase text-[#0E6E6A] font-bold mb-2">
                  1. EXECUTIVE SUMMARY & SHOCK ANALYSIS
                </h4>
                <p className="leading-relaxed text-xs">
                  Following anti-ship ballistic missile strikes in the southern Red Sea, Suez Transit through Bab-el-Mandeb has been classified at maximum disruption risk (8.7/10). Indian state refineries at Kochi (10 days stock) and Paradip (8 days stock) faced immediate shutdown risks.
                </p>
              </div>

              <div>
                <h4 className="text-xs font-mono uppercase text-[#0E6E6A] font-bold mb-2">
                  2. MULTI-AGENT RECOVERY TIMELINE
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                  <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                    <span className="text-[#4B5A57]">Scout Detection:</span>
                    <p className="text-[#10201E] font-bold mt-1">4 minutes post-event</p>
                  </div>
                  <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                    <span className="text-[#4B5A57]">Playbook Execution:</span>
                    <p className="text-[#0E6E6A] font-bold mt-1">6 minutes total time</p>
                  </div>
                  <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                    <span className="text-[#4B5A57]">Est. Total Recovery:</span>
                    <p className="text-[#276A4E] font-bold mt-1">6 days (vs 47d baseline)</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-mono uppercase text-[#0E6E6A] font-bold mb-2">
                  3. STRATEGIC PETROLEUM RESERVE & SPOT CONTRACT ACTIONS
                </h4>
                <ul className="list-disc list-inside space-y-1 text-xs text-[#4B5A57]">
                  <li>500 kbd SPR release authorized from Padur underground caverns.</li>
                  <li>$2.4B emergency spot crude agreement concluded with ADNOC UAE @ $84.50/bbl.</li>
                  <li>MT Kaveri & MT Sindhu rerouted via Cape of Good Hope with +15 day ETA adjustment.</li>
                </ul>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
