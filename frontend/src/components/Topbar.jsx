import React from 'react';
import { Search, Bell, ChevronDown } from 'lucide-react';

export default function Topbar({ title = "Dashboard" }) {
  return (
    <header className="fixed top-0 right-0 left-14 lg:left-60 z-30 h-16 bg-[#F2F4F3]/95 backdrop-blur-md border-b border-[#DCE1DF] px-4 md:px-6 flex items-center justify-between transition-all duration-200">
      <div className="flex items-center space-x-3">
        <h1 className="text-lg md:text-xl font-semibold text-[#10201E] tracking-tight">
          {title}
        </h1>
        <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30 font-bold">
          <span className="w-1.5 h-1.5 rounded-full bg-[#B23A2E] animate-pulse mr-1.5"></span>
          CRITICAL MODE
        </span>
      </div>

      <div className="flex items-center space-x-3 md:space-x-4">
        {/* Search Bar */}
        <div className="relative hidden sm:block">
          <Search className="w-4 h-4 text-[#4B5A57] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search vessels, refineries, corridors..."
            className="w-48 lg:w-64 bg-[#FAFBFA] border border-[#DCE1DF] rounded-md pl-9 pr-3 py-1.5 text-xs text-[#10201E] focus:outline-none focus:border-[#0E6E6A] placeholder:text-[#4B5A57] font-sans"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 rounded-md bg-[#FAFBFA] border border-[#DCE1DF] text-[#4B5A57] hover:text-[#10201E] transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#B23A2E] animate-pulse"></span>
        </button>

        {/* User Pill */}
        <div className="flex items-center space-x-2 pl-2 border-l border-[#DCE1DF]">
          <div className="w-7 h-7 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 flex items-center justify-center text-[#0E6E6A] font-bold text-xs">
            RN
          </div>
          <span className="hidden lg:inline text-xs font-medium text-[#10201E]">Min. Petroleum</span>
          <ChevronDown className="w-3.5 h-3.5 text-[#4B5A57] hidden sm:inline" />
        </div>
      </div>
    </header>
  );
}
