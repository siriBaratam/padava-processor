import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, Lock, Mail, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('officer@petroleum.gov.in');
  const [password, setPassword] = useState('••••••••••••');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#F7F7F4] flex flex-col justify-center items-center px-4 relative overflow-hidden">
      <div className="w-full max-w-md glass-card p-8 relative z-10 shadow-sm border-[#E6E5E0]">
        {/* Header Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-4 group">
            <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/30 group-hover:border-orange-500/60 transition-colors">
              <Shield className="w-6 h-6 text-[#F54E00]" />
            </div>
            <span className="text-xl font-bold text-[#26251E]">
              EnergyGuard <span className="text-[#F54E00] font-mono text-sm">AI</span>
            </span>
          </Link>
          <h2 className="text-2xl font-normal tracking-tight-title text-[#26251E]">Welcome back</h2>
          <p className="text-xs text-[#807D72] mt-1 font-mono">
            SECURE ACCESS · SOVEREIGN ENERGY CORE
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-5">
          {/* Email */}
          <div>
            <label className="block text-xs font-medium text-[#26251E] mb-1.5 font-mono">
              OFFICIAL EMAIL ADDRESS
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-3 py-2.5 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00] transition-colors font-sans"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-medium text-[#26251E] font-mono">
                SECURITY PASSWORD
              </label>
              <a href="#" className="text-xs text-[#F54E00] hover:underline">
                Forgot password?
              </a>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#807D72] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-[#FFFFFF] border border-[#E6E5E0] rounded-md pl-9 pr-10 py-2.5 text-sm text-[#26251E] focus:outline-none focus:border-[#F54E00] transition-colors font-sans"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#807D72] hover:text-[#26251E]"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember me */}
          <div className="flex items-center justify-between text-xs text-[#5A5852]">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                defaultChecked
                className="rounded border-[#E6E5E0] bg-[#FFFFFF] text-[#F54E00] focus:ring-orange-500/20"
              />
              <span>Remember authentication token</span>
            </label>
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="w-full py-3 bg-[#F54E00] hover:bg-[#D04200] text-white font-semibold rounded-md transition-all shadow-sm flex items-center justify-center space-x-2"
          >
            <span>Access Command Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Footer Link */}
        <div className="mt-8 text-center text-xs text-[#807D72] border-t border-[#E6E5E0] pt-6">
          <span>Don't have clearance yet? </span>
          <Link to="/register" className="text-[#F54E00] font-semibold hover:underline">
            Register Account
          </Link>
        </div>
      </div>
    </div>
  );
}
