import React, { useState } from 'react';
import { Search, Bell, LogOut, Settings, User, ChevronDown, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
} from './ui/DropdownMenu';

export default function Topbar({ title = 'Dashboard' }) {
  const navigate = useNavigate();
  const [notifCount] = useState(3);

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <header className="topbar">
      {/* Left — title */}
      <div className="topbar-left">
        <h1 className="topbar-title">{title}</h1>
        <span className="topbar-badge">
          <span className="topbar-badge-dot" />
          CRITICAL MODE
        </span>
      </div>

      {/* Right — actions */}
      <div className="topbar-right">
        {/* Search */}
        <div className="topbar-search-wrap">
          <Search className="topbar-search-icon" size={14} />
          <input
            type="text"
            placeholder="Search vessels, refineries…"
            className="topbar-search"
          />
        </div>

        {/* Notifications */}
        <button className="topbar-icon-btn" aria-label="Notifications">
          <Bell size={16} />
          {notifCount > 0 && (
            <span className="topbar-notif-badge">{notifCount}</span>
          )}
        </button>

        {/* Divider */}
        <div className="topbar-divider" aria-hidden />

        {/* User Profile Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="topbar-user-btn" aria-label="User menu">
              <div className="topbar-avatar">
                <span>RN</span>
              </div>
              <div className="topbar-user-info">
                <span className="topbar-user-name">Rajesh Nair</span>
                <span className="topbar-user-role">Min. Petroleum</span>
              </div>
              <ChevronDown size={13} className="topbar-user-chevron" />
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end">
            {/* User meta header */}
            <div className="topbar-dd-header">
              <div className="topbar-dd-avatar">
                <span>RN</span>
              </div>
              <div>
                <p className="topbar-dd-name">Rajesh Nair</p>
                <p className="topbar-dd-email">nair.r@petroleum.gov.in</p>
              </div>
            </div>

            <DropdownMenuSeparator />
            <DropdownMenuLabel>Account</DropdownMenuLabel>

            <DropdownMenuItem onClick={() => navigate('/settings')}>
              <User size={14} />
              Profile Settings
            </DropdownMenuItem>

            <DropdownMenuItem onClick={() => navigate('/settings')}>
              <Settings size={14} />
              Preferences
            </DropdownMenuItem>

            <DropdownMenuItem onClick={() => {}}>
              <Shield size={14} />
              Security & Access
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem variant="destructive" onClick={handleLogout}>
              <LogOut size={14} />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
