import React from 'react';
import { NavLink } from 'react-router-dom';
import OceanBreezeLogo from './OceanBreezeLogo';
import { 
  LayoutDashboard, 
  Radar, 
  Calculator, 
  BrainCircuit, 
  Boxes, 
  Handshake, 
  Compass, 
  Bell, 
  FileText, 
  Settings
} from 'lucide-react';

export default function Sidebar() {
  const agentNav = [
    { name: 'Scout', path: '/scout', icon: Radar },
    { name: 'Accountant', path: '/accountant', icon: Calculator },
    { name: 'Strategist', path: '/strategist', icon: BrainCircuit },
    { name: 'Allocator', path: '/allocator', icon: Boxes },
    { name: 'Dealmaker', path: '/dealmaker', icon: Handshake },
    { name: 'Navigator', path: '/navigator', icon: Compass },
  ];

  const systemNav = [
    { name: 'Alerts', path: '/alerts', icon: Bell, badge: '7' },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Desktop & Tablet Sidebar */}
      <aside className="fixed left-0 top-0 bottom-0 z-40 bg-[#FAFBFA] border-r border-[#DCE1DF] flex flex-col transition-all duration-200 w-14 lg:w-60">
        {/* Brand Header */}
        <div className="h-16 flex items-center px-3 border-b border-[#DCE1DF]">
          <NavLink to="/" className="flex items-center space-x-3 group w-full">
            <div className="p-1.5 rounded-lg bg-[#E4EFEE] border border-[#0E6E6A]/30 flex-shrink-0 group-hover:border-[#0E6E6A]/60 transition-colors">
              <OceanBreezeLogo className="w-5 h-5" animated={true} />
            </div>
            <div className="hidden lg:flex flex-col min-w-0">
              <span className="text-sm font-semibold text-[#10201E] leading-tight truncate">
                EnergyGuard <span className="text-[#0E6E6A] font-mono text-xs font-bold">AI</span>
              </span>
              <span className="text-[9px] text-[#4B5A57] font-mono tracking-wider uppercase truncate">MARITIME CONSOLE</span>
            </div>
          </NavLink>
        </div>

        {/* Scrollable Navigation */}
        <div className="flex-1 overflow-y-auto py-4 px-2 space-y-6">
          {/* Overview */}
          <div>
            <p className="hidden lg:block px-3 text-[11px] font-mono uppercase tracking-wider text-[#4B5A57] mb-2">
              Overview
            </p>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-[#E4EFEE] text-[#0E6E6A] border-l-2 border-[#0E6E6A] font-semibold'
                    : 'text-[#4B5A57] hover:text-[#10201E] hover:bg-[#EAEDEC]'
                }`
              }
            >
              <LayoutDashboard className="w-4 h-4 flex-shrink-0" />
              <span className="hidden lg:inline">Dashboard</span>
            </NavLink>
          </div>

          {/* AI Agents Fleet */}
          <div>
            <p className="hidden lg:block px-3 text-[11px] font-mono uppercase tracking-wider text-[#4B5A57] mb-2">
              AI Agents Fleet
            </p>
            <div className="space-y-1">
              {agentNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.name}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                        isActive
                          ? 'bg-[#E4EFEE] text-[#0E6E6A] border-l-2 border-[#0E6E6A] font-semibold'
                          : 'text-[#4B5A57] hover:text-[#10201E] hover:bg-[#EAEDEC]'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4 flex-shrink-0 text-[#0E6E6A]" />
                    <span className="hidden lg:inline">{item.name}</span>
                  </NavLink>
                );
              })}
            </div>
          </div>

          {/* System */}
          <div>
            <p className="hidden lg:block px-3 text-[11px] font-mono uppercase tracking-wider text-[#4B5A57] mb-2">
              System
            </p>
            <div className="space-y-1">
              {systemNav.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.name}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                        isActive
                          ? 'bg-[#E4EFEE] text-[#0E6E6A] border-l-2 border-[#0E6E6A] font-semibold'
                          : 'text-[#4B5A57] hover:text-[#10201E] hover:bg-[#EAEDEC]'
                      }`
                    }
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span className="hidden lg:inline">{item.name}</span>
                    </div>
                    {item.badge && (
                      <span className="hidden lg:inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#F7E9E6] text-[#B23A2E] border border-[#B23A2E]/30">
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          </div>
        </div>

        {/* Bottom User Profile */}
        <div className="p-3 border-t border-[#DCE1DF] bg-[#EAEDEC]/50">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 flex items-center justify-center text-[#0E6E6A] font-bold text-xs flex-shrink-0">
              RN
            </div>
            <div className="hidden lg:flex flex-col min-w-0">
              <span className="text-xs font-semibold text-[#10201E] truncate">Rajesh Nair</span>
              <div className="flex items-center space-x-1">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-[#276A4E]"></span>
                <span className="text-[10px] text-[#4B5A57] truncate font-mono">Dep. Sec / Ministry</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Bottom Navigation (<640px) */}
      <div className="sm:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#FAFBFA] border-t border-[#DCE1DF] flex justify-around items-center h-14 px-2">
        <NavLink to="/dashboard" className={({isActive}) => isActive ? 'text-[#0E6E6A]' : 'text-[#4B5A57]'}>
          <LayoutDashboard className="w-5 h-5" />
        </NavLink>
        <NavLink to="/scout" className={({isActive}) => isActive ? 'text-[#0E6E6A]' : 'text-[#4B5A57]'}>
          <Radar className="w-5 h-5" />
        </NavLink>
        <NavLink to="/strategist" className={({isActive}) => isActive ? 'text-[#0E6E6A]' : 'text-[#4B5A57]'}>
          <BrainCircuit className="w-5 h-5" />
        </NavLink>
        <NavLink to="/navigator" className={({isActive}) => isActive ? 'text-[#0E6E6A]' : 'text-[#4B5A57]'}>
          <Compass className="w-5 h-5" />
        </NavLink>
        <NavLink to="/alerts" className={({isActive}) => isActive ? 'text-[#0E6E6A]' : 'text-[#4B5A57]'}>
          <Bell className="w-5 h-5" />
        </NavLink>
      </div>
    </>
  );
}
