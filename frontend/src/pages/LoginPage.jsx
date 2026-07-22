import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {Title} from "../components/ui/Title.jsx"
import {
  Shield, Eye, EyeOff, Lock, Mail, ArrowRight,
  Anchor, Waves, AlertCircle, CheckCircle2
} from 'lucide-react';

/* ---------- tiny helpers ---------- */
function InputField({ id, label, type = 'text', icon: Icon, value, onChange, placeholder, required, rightSlot, hint }) {
  const [focused, setFocused] = useState(false);
  const hasValue = value && value.length > 0;

  return (
    <div className="auth-field-group">
      <label htmlFor={id} className="auth-label">{label}</label>
      <div className={`auth-input-wrap ${focused ? 'auth-input-wrap--focused' : ''} ${hasValue && !focused ? 'auth-input-wrap--filled' : ''}`}>
        <span className="auth-input-icon">
          <Icon size={16} />
        </span>
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          required={required}
          className="auth-input"
          autoComplete="off"
        />
        {rightSlot}
      </div>
      {hint && <p className="auth-hint">{hint}</p>}
    </div>
  );
}

/* ---------- animated floating particles ---------- */
function Particle({ style }) {
  return <div className="auth-particle" style={style} />;
}

const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  id: i,
  style: {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    width: `${2 + Math.random() * 3}px`,
    height: `${2 + Math.random() * 3}px`,
    animationDelay: `${Math.random() * 6}s`,
    animationDuration: `${8 + Math.random() * 10}s`,
    '--op': 0.08 + Math.random() * 0.12,
  },
}));

/* ====================================================================
   LOGIN PAGE
   ==================================================================== */
export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    /* Simulate auth delay */
    await new Promise((r) => setTimeout(r, 1200));

    if (email && password) {
      navigate('/dashboard');
    } else {
      setError('Invalid credentials. Please check your email and password.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-root">
      {/* ── Background Image + overlays ─────────────────── */}
      <div className="auth-bg">
        <img
          src="/flung-ship.jpg"
          alt="Goods ships at sea"
          className="auth-bg-img"
          draggable="false"
        />
        {/* dark vignette */}
        <div className="auth-bg-vignette" />
        {/* teal accent gradient */}
        <div className="auth-bg-gradient" />
        {/* animated scan-line */}
        <div className="auth-scanline" />
      </div>

      {/* ── Floating particles ───────────────────────────── */}
      <div className="auth-particles" aria-hidden>
        {PARTICLES.map((p) => (
          <Particle key={p.id} style={p.style} />
        ))}
      </div>

      {/* ── Left branding panel ─────────────────────────── */}
      <aside className="auth-brand-panel">
        <div className="auth-brand-inner">
          <div className="auth-brand-logo">
            <Anchor size={28} className="text-[#0E6E6A]" />
          </div>
          <h1 className="auth-brand-title">
            Padava<br />
            {/* Teal accent — matches Landing page primary brand color */}
            <span className="text-[#0E6E6A]">Processor</span>
          </h1>
          <p className="auth-brand-sub">
            Sovereign-grade maritime intelligence for India's critical energy supply chain.
          </p>

          <div className="auth-brand-stats">
            {[
              { label: 'Vessels Tracked', value: '2,400+' },
              { label: 'Ports Monitored', value: '180+' },
              { label: 'Uptime SLA', value: '99.9%' },
            ].map((s) => (
              <div key={s.label} className="auth-stat-item">
                <span className="auth-stat-value">{s.value}</span>
                <span className="auth-stat-label">{s.label}</span>
              </div>
            ))}
          </div>

          <div className="auth-brand-badge">
            <Waves size={12} className="animate-pulse" />
            <span>Live Mission Ops Active</span>
          </div>
        </div>
      </aside>

      {/* ── Auth card ────────────────────────────────────── */}
      <main className="auth-card-panel">
        <div className="auth-card" role="main" aria-label="Login form">

          {/* Card glow border top */}
          <div className="auth-card-glow" />

          {/* Header */}
          <header className="auth-card-header">
            <Title/>
            <h2 className="auth-card-title">Welcome back</h2>
            <p className="auth-card-subtitle">Sign in to your command dashboard</p>
          </header>

          {/* Error banner */}
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="auth-form" noValidate>
            <InputField
              id="login-email"
              label="Official Email Address"
              type="email"
              icon={Mail}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="officer@petroleum.gov.in"
              required
            />

            <InputField
              id="login-password"
              label="Security Password"
              type={showPassword ? 'text' : 'password'}
              icon={Lock}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              rightSlot={
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  className="auth-input-btn"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              }
            />

            {/* Remember + Forgot */}
            <div className="auth-row">
              <label className="auth-checkbox-label">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="auth-checkbox"
                />
                <span className="auth-checkbox-custom" aria-hidden>
                  {remember && <CheckCircle2 size={10} className="text-[#0E6E6A]" />}
                </span>
                <span>Remember me</span>
              </label>
              <a href="#" className="auth-link">Forgot password?</a>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className={`auth-submit-btn ${loading ? 'auth-submit-btn--loading' : ''}`}
            >
              {loading ? (
                <>
                  <span className="auth-spinner" />
                  <span>Authenticating…</span>
                </>
              ) : (
                <>
                  <span>Access Command Dashboard</span>
                  <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="auth-divider">
            <span className="auth-divider-line" />
            <span className="auth-divider-text">OR</span>
            <span className="auth-divider-line" />
          </div>

          {/* Footer */}
          <p className="auth-footer">
            Don't have clearance yet?{' '}
            <Link to="/register" className="auth-footer-link">
              Register Account
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
