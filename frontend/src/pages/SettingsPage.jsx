import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import { Settings, User, Bell, Key, Copy, RefreshCw, Check } from 'lucide-react';

export default function SettingsPage() {
  const [copiedKey, setCopiedKey] = useState(null);
  const [notifications, setNotifications] = useState({
    emailCritical: true,
    smsCritical: true,
    dashboardAlerts: true,
    dailySummary: false,
  });

  const apiKeys = [
    { name: "NewsAPI Satellite Feed", key: "news_live_************************38a1" },
    { name: "Gemini 1.5 Pro AI Core", key: "gm_prod_************************99f4" },
    { name: "MarineTraffic AIS Stream", key: "mt_ais_************************77b2" },
  ];

  const handleCopy = (name, key) => {
    navigator.clipboard.writeText(key);
    setCopiedKey(name);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex">
      <Sidebar />

      <div className="flex-1 ml-14 lg:ml-60 flex flex-col min-w-0">
        <Topbar title="System Settings & Governance" />

        <main className="flex-1 mt-16 p-4 md:p-6 space-y-6 overflow-y-auto max-w-5xl">
          {/* HEADER */}
          <div className="glass-card p-4 flex items-center space-x-3">
            <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] text-[#0E6E6A]">
              <Settings className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-[#10201E]">Platform Settings & Security Credentials</h2>
              <p className="text-xs text-[#4B5A57] mt-0.5 font-mono">
                USER PROFILE · CRITICAL NOTIFICATIONS · SOVEREIGN API KEY MANAGEMENT
              </p>
            </div>
          </div>

          {/* SECTION 1: PROFILE */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-[#DCE1DF]">
              <User className="w-5 h-5 text-[#0E6E6A]" />
              <h3 className="text-sm font-semibold text-[#10201E]">Executive User Profile</h3>
            </div>

            <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
              <div className="w-20 h-20 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 flex items-center justify-center text-[#0E6E6A] font-bold text-2xl">
                RN
              </div>
              <div className="space-y-1 text-center sm:text-left">
                <h4 className="text-base font-bold text-[#10201E]">Rajesh Nair</h4>
                <p className="text-xs text-[#4B5A57]">nair.r@petroleum.gov.in</p>
                <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-2 text-[10px] font-mono">
                  <span className="px-2 py-0.5 rounded bg-[#E4EFEE] text-[#0E6E6A] border border-[#0E6E6A]/20">
                    Org: Ministry of Petroleum
                  </span>
                  <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                    Role: Sovereign Admin (Read Only)
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* SECTION 2: NOTIFICATIONS */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-[#DCE1DF]">
              <Bell className="w-5 h-5 text-[#0E6E6A]" />
              <h3 className="text-sm font-semibold text-[#10201E]">Critical Threat Notifications</h3>
            </div>

            <div className="space-y-3">
              {[
                { key: 'emailCritical', label: 'Email alerts on CRITICAL risk detection', desc: 'Instant dispatch to ministry priority list' },
                { key: 'smsCritical', label: 'SMS alerts on CRITICAL risk detection', desc: 'Emergency SMS via National Crisis Network' },
                { key: 'dashboardAlerts', label: 'Dashboard real-time audio & banner notifications', desc: 'Pulsing critical alert banners' },
                { key: 'dailySummary', label: 'Daily executive summary report email', desc: 'Sent at 08:00 IST daily' },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                  <div>
                    <h4 className="text-xs font-semibold text-[#10201E]">{item.label}</h4>
                    <p className="text-[10px] text-[#4B5A57]">{item.desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications[item.key]}
                      onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#0E6E6A]"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* SECTION 3: API KEYS */}
          <div className="glass-card p-6 space-y-4">
            <div className="flex items-center space-x-2 pb-3 border-b border-[#DCE1DF]">
              <Key className="w-5 h-5 text-[#0E6E6A]" />
              <h3 className="text-sm font-semibold text-[#10201E]">API Key Credentials Management</h3>
            </div>

            <div className="space-y-3 font-mono text-xs">
              {apiKeys.map((k) => (
                <div key={k.name} className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div>
                    <p className="text-[#10201E] font-bold">{k.name}</p>
                    <p className="text-[#4B5A57] text-[11px] mt-0.5">{k.key}</p>
                  </div>

                  <div className="flex items-center space-x-2 w-full sm:w-auto justify-end">
                    <button
                      onClick={() => handleCopy(k.name, k.key)}
                      className="px-2.5 py-1 rounded bg-[#FAFBFA] hover:bg-[#F2F4F3] text-[#10201E] text-[11px] flex items-center space-x-1 border border-[#DCE1DF]"
                    >
                      {copiedKey === k.name ? <Check className="w-3.5 h-3.5 text-[#276A4E]" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedKey === k.name ? 'Copied' : 'Copy'}</span>
                    </button>
                    <button className="px-2.5 py-1 rounded bg-[#FAFBFA] hover:bg-[#E4EFEE] text-[#4B5A57] hover:text-[#0E6E6A] text-[11px] flex items-center space-x-1 border border-[#DCE1DF]">
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Regenerate</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
