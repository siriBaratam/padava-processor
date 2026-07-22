import React from 'react';
import { Link } from 'react-router-dom';
import OceanBreezeLogo from './OceanBreezeLogo';

export default function Footer() {
  return (
    <footer className="bg-[#FAFBFA] border-t border-[#DCE1DF] py-12 text-[#4B5A57]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <Link to="/" className="flex items-center space-x-2.5 group">
              <div className="p-1 rounded bg-[#E4EFEE] border border-[#0E6E6A]/30">
                <OceanBreezeLogo className="w-5 h-5" />
              </div>
              <span className="text-base font-semibold text-[#10201E]">
                EnergyGuard <span className="text-[#0E6E6A] font-mono text-xs font-bold">AI</span>
              </span>
            </Link>
            <p className="text-xs leading-relaxed">
              Sovereign AI-powered crude oil supply chain resilience platform for the Ministry of Petroleum & Natural Gas, Government of India.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-mono uppercase text-[#10201E] font-bold mb-3">AI Agents</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/scout" className="hover:text-[#0E6E6A] transition-colors">Scout Agent</Link></li>
              <li><Link to="/accountant" className="hover:text-[#0E6E6A] transition-colors">Accountant Agent</Link></li>
              <li><Link to="/strategist" className="hover:text-[#0E6E6A] transition-colors">Strategist Agent</Link></li>
              <li><Link to="/allocator" className="hover:text-[#0E6E6A] transition-colors">Allocator Agent</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-mono uppercase text-[#10201E] font-bold mb-3">Refinery Telemetry</h4>
            <ul className="space-y-2 text-xs font-mono">
              <li>Kochi Refinery (10 days cover)</li>
              <li>Paradip Refinery (8 days cover)</li>
              <li>Haldia Port (6 days cover)</li>
              <li>Jamnagar Refinery (7 days cover)</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-mono uppercase text-[#10201E] font-bold mb-3">Sovereign Compliance</h4>
            <p className="text-xs leading-relaxed mb-3">
              Audited according to National Defense Energy Protocol 2026-ALPHA.
            </p>
            <span className="inline-block px-2 py-1 rounded bg-[#E4EEE8] text-[#276A4E] border border-[#276A4E]/30 text-[10px] font-mono font-bold">
              CLASSIFICATION: OFFICIAL / RESTRICTED
            </span>
          </div>
        </div>

        <div className="pt-8 border-t border-[#DCE1DF] flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-[#4B5A57] gap-4">
          <p>© 2026 EnergyGuard AI — Ministry of Petroleum & Natural Gas, Govt of India</p>
          <div className="flex space-x-4">
            <a href="#" className="hover:text-[#10201E]">Privacy Policy</a>
            <span>·</span>
            <a href="#" className="hover:text-[#10201E]">Security Audit</a>
            <span>·</span>
            <a href="#" className="hover:text-[#10201E]">API Governance</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
