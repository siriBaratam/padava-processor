import React from 'react';
import { Link } from 'react-router-dom';
import OceanBreezeLogo from './OceanBreezeLogo';
import { ArrowRight } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#F2F4F3]/95 backdrop-blur-md border-b border-[#DCE1DF] h-16 transition-all duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="p-1.5 rounded-xl bg-[#E4EFEE] border border-[#0E6E6A]/30 group-hover:border-[#0E6E6A] group-hover:bg-[#E4EFEE]/90 transition-all duration-200 shadow-sm flex items-center justify-center">
            <OceanBreezeLogo className="w-7 h-7" animated={true} />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-semibold tracking-tight text-[#10201E] group-hover:text-[#0E6E6A] transition-colors leading-tight">
              EnergyGuard <span className="text-[#0E6E6A] font-mono text-xs font-bold uppercase px-1.5 py-0.5 bg-[#E4EFEE] rounded border border-[#0E6E6A]/30 ml-1">AI</span>
            </span>
            <span className="text-[10px] font-mono text-[#4B5A57] tracking-wider uppercase">OCEANIC CARGO RESILIENCE</span>
          </div>
        </Link>

        <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-[#4B5A57]">
          <a href="#features" className="hover:text-[#10201E] transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-[#10201E] transition-colors">How It Works</a>
          <a href="#testimonials" className="hover:text-[#10201E] transition-colors">Testimonials</a>
          <Link to="/scout" className="hover:text-[#10201E] transition-colors flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-[#0E6E6A] animate-pulse"></span>
            <span className="font-mono text-xs text-[#0E6E6A] font-semibold">Live Radar</span>
          </Link>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/login"
            className="px-4 py-2 text-sm font-medium text-[#10201E] bg-[#FAFBFA] hover:bg-[#EAEDEC] border border-[#DCE1DF] rounded-md transition-all duration-150"
          >
            Login
          </Link>
          <Link
            to="/dashboard"
            className="px-4 py-2 text-sm font-medium bg-[#0E6E6A] hover:bg-[#0A5653] text-white font-semibold rounded-md transition-all duration-150 shadow-sm hover:-translate-y-[1px] hover:shadow-md flex items-center space-x-1.5"
          >
            <span>Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </nav>
  );
}
