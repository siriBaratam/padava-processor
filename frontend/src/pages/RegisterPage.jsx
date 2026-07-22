import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, User, Mail, Building, Lock, ArrowRight } from 'lucide-react';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [role, setRole] = useState('Analyst');

  const handleRegister = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F7F4] flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden">
      <div className="w-full max-w-lg glass-card p-8 relative z-10 shadow-sm border-[#E6E5E0]">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-3 group">
            <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/30 group-hover:border-orange-500/60 transition-colors">
              <Shield className="w-6 h-6 text-[#F54E00]" />
            </div>
            <span className="text-xl font-bold text-[#26251E]">
              EnergyGuard <span className="text-[#F54E00] font-mono text-sm">AI</span>
            </span>
          </Link>
          <h2 className="text-2xl font-normal tracking-tight-title text-[#26251E]">Request Platform Access</h2>
          <p className="text-xs text-[#807D72] mt-1 font-mono">
            SOVEREIGN RESILIENCE SYSTEM · USER CREDENTIAL REGISTRATION
          </p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">FULL NAME</label>
            <div className="relative">
              <User className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Dr. Rajesh Nair"
                required
                className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">OFFICIAL EMAIL</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                placeholder="nair.r@petroleum.gov.in"
                required
                className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00]"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">ORGANISATION</label>
              <div className="relative">
                <Building className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Ministry of Petroleum"
                  required
                  className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">ROLE CLEARANCE</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md px-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00] font-sans"
              >
                <option value="Viewer">Viewer (Read Only)</option>
                <option value="Analyst">Analyst (Intelligence)</option>
                <option value="Manager">Manager (Tactical Operations)</option>
                <option value="Admin">Admin (Sovereign Executive)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">PASSWORD</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[#26251E] mb-1 font-mono">CONFIRM PASSWORD</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00]"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs text-[#5A5852] pt-2">
            <input
              type="checkbox"
              required
              defaultChecked
              className="rounded border-[#E6E5E0] bg-[#FFFFFF] text-[#F54E00] focus:ring-orange-500/20"
            />
            <span>I accept government security data disclosure policies.</span>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-[#F54E00] hover:bg-[#D04200] text-white font-semibold rounded-md transition-all shadow-sm flex items-center justify-center space-x-2"
          >
            <span>Register Credentials</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-[#807D72] border-t border-[#E6E5E0] pt-4">
          <span>Already have registered credentials? </span>
          <Link to="/login" className="text-[#F54E00] font-semibold hover:underline">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}
