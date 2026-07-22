import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {Title} from "../components/ui/Title.jsx";
import {
  Shield, Eye, EyeOff, Lock, Mail, User, Building,
  ArrowRight, Anchor, CheckCircle2, AlertCircle, ChevronDown
} from 'lucide-react';

/* ── tiny shared helpers ───────────────────────────── */
function InputField({ id, label, type = 'text', icon: Icon, value, onChange, placeholder, required, rightSlot }) {
  const [focused, setFocused] = useState(false);
  const hasValue = value && value.length > 0;

  return (
    <div className="auth-field-group">
      <label htmlFor={id} className="auth-label">{label}</label>
      <div className={`auth-input-wrap ${focused ? 'auth-input-wrap--focused' : ''} ${hasValue && !focused ? 'auth-input-wrap--filled' : ''}`}>
        <span className="auth-input-icon">
          <Icon size={15} />
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
    </div>
  );
}

function SelectField({ id, label, value, onChange, options }) {
  const [focused, setFocused] = useState(false);
  return (
    <div className="auth-field-group">
      <label htmlFor={id} className="auth-label">{label}</label>
      <div className={`auth-input-wrap auth-select-wrap ${focused ? 'auth-input-wrap--focused' : ''}`}>
        <select
          id={id}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="auth-select"
          required
        >
          {options.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <span className="auth-select-chevron">
          <ChevronDown size={14} />
        </span>
      </div>
    </div>
  );
}

const ROLE_OPTIONS = [
  { value: 'Viewer', label: 'Viewer — Read Only' },
  { value: 'Analyst', label: 'Analyst — Intelligence' },
  { value: 'Manager', label: 'Manager — Tactical Ops' },
  { value: 'Admin', label: 'Admin — Sovereign Executive' },
];

const PARTICLES = Array.from({ length: 18 }, (_, i) => ({
  id: i,
  style: {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    width: `${2 + Math.random() * 4}px`,
    height: `${2 + Math.random() * 4}px`,
    animationDelay: `${Math.random() * 6}s`,
    animationDuration: `${6 + Math.random() * 8}s`,
    opacity: 0.15 + Math.random() * 0.25,
  },
}));

/* ====================================================================
   REGISTER PAGE
   ==================================================================== */
export default function RegisterPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    organisation: '',
    role: 'Analyst',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const update = (key) => (e) => setFormData((f) => ({ ...f, [key]: e.target.value }));

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match. Please re-enter.');
      return;
    }
    if (!agreed) {
      setError('You must accept the security data disclosure policy.');
      return;
    }

    setLoading(true);
    await new Promise((r) => setTimeout(r, 1400));
    navigate('/dashboard');
  };

  const passwordStrength = (() => {
    const p = formData.password;
    if (!p) return 0;
    let s = 0;
    if (p.length >= 8) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/[0-9]/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    return s;
  })();

  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong'][passwordStrength];
  const strengthColor = ['', '#ef4444', '#f97316', '#eab308', '#22c55e'][passwordStrength];

  return (
    <div className="auth-root">
      {/* ── Background ───────────────────────────────────── */}
      <div className="auth-bg">
        <img
          src="/cargo-ship.jpg"
          alt="Cargo ships at sea"
          className="auth-bg-img"
          draggable="false"
        />
        <div className="auth-bg-vignette" />
        <div className="auth-bg-gradient" />
        <div className="auth-scanline" />
      </div>

      {/* Particles */}
      <div className="auth-particles" aria-hidden>
        {PARTICLES.map((p) => (
          <div key={p.id} className="auth-particle" style={p.style} />
        ))}
      </div>

      {/* ── Left branding panel ─────────────────────────── */}
      <aside className="auth-brand-panel">
        <div className="auth-brand-inner">
          <div className="auth-brand-logo">
            <Anchor size={28} className="text-[#F54E00]" />
          </div>
          <h1 className="auth-brand-title">
            Join the<br />
            <span className="text-[#F54E00]">Mission</span>
          </h1>
          <p className="auth-brand-sub">
            Request clearance to access India's premier maritime energy intelligence platform.
          </p>

          <div className="auth-brand-steps">
            {[
              { step: '01', text: 'Register your credentials' },
              { step: '02', text: 'Verify official email' },
              { step: '03', text: 'Access cleared' },
            ].map((s) => (
              <div key={s.step} className="auth-step-item">
                <span className="auth-step-num">{s.step}</span>
                <span className="auth-step-text">{s.text}</span>
              </div>
            ))}
          </div>

          <div className="auth-brand-badge">
            <Shield size={12} />
            <span>Government-Grade Encryption</span>
          </div>
        </div>
      </aside>

      {/* ── Card panel ───────────────────────────────────── */}
      <main className="auth-card-panel auth-card-panel--register">
        <div className="auth-card auth-card--wide" role="main" aria-label="Registration form">
          <div className="auth-card-glow" />

          {/* Header */}
          <header className="auth-card-header">
            <Title/>
            <h2 className="auth-card-title">Request Platform Access</h2>
            <p className="auth-card-subtitle">Create your sovereign energy intelligence account</p>
          </header>

          {/* Error banner */}
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleRegister} className="auth-form" noValidate>
            {/* Row 1 */}
            <div className="auth-grid-2">
              <InputField
                id="reg-name"
                label="Full Name"
                icon={User}
                value={formData.fullName}
                onChange={update('fullName')}
                placeholder="Dr. Rajesh Nair"
                required
              />
              <InputField
                id="reg-email"
                label="Official Email"
                type="email"
                icon={Mail}
                value={formData.email}
                onChange={update('email')}
                placeholder="nair.r@petroleum.gov.in"
                required
              />
            </div>

            {/* Row 2 */}
            <div className="auth-grid-2">
              <InputField
                id="reg-org"
                label="Organisation"
                icon={Building}
                value={formData.organisation}
                onChange={update('organisation')}
                placeholder="Ministry of Petroleum"
                required
              />
              <SelectField
                id="reg-role"
                label="Role Clearance"
                value={formData.role}
                onChange={update('role')}
                options={ROLE_OPTIONS}
              />
            </div>

            {/* Password Row */}
            <div className="auth-grid-2">
              <div>
                <InputField
                  id="reg-password"
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  icon={Lock}
                  value={formData.password}
                  onChange={update('password')}
                  placeholder="••••••••"
                  required
                  rightSlot={
                    <button
                      type="button"
                      tabIndex={-1}
                      onClick={() => setShowPassword((v) => !v)}
                      className="auth-input-btn"
                    >
                      {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  }
                />
                {/* Password strength bar */}
                {formData.password && (
                  <div className="auth-strength-bar-wrap">
                    <div className="auth-strength-track">
                      {[1, 2, 3, 4].map((n) => (
                        <div
                          key={n}
                          className="auth-strength-segment"
                          style={{
                            backgroundColor:
                              passwordStrength >= n ? strengthColor : 'rgba(255,255,255,0.1)',
                          }}
                        />
                      ))}
                    </div>
                    <span className="auth-strength-label" style={{ color: strengthColor }}>
                      {strengthLabel}
                    </span>
                  </div>
                )}
              </div>

              <InputField
                id="reg-confirm"
                label="Confirm Password"
                type={showConfirm ? 'text' : 'password'}
                icon={Lock}
                value={formData.confirmPassword}
                onChange={update('confirmPassword')}
                placeholder="••••••••"
                required
                rightSlot={
                  <button
                    type="button"
                    tabIndex={-1}
                    onClick={() => setShowConfirm((v) => !v)}
                    className="auth-input-btn"
                  >
                    {showConfirm ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                }
              />
            </div>

            {/* Terms */}
            <label className="auth-terms-label">
              <span
                className={`auth-terms-box ${agreed ? 'auth-terms-box--checked' : ''}`}
                onClick={() => setAgreed((v) => !v)}
                role="checkbox"
                aria-checked={agreed}
                tabIndex={0}
                onKeyDown={(e) => e.key === ' ' && setAgreed((v) => !v)}
              >
                {agreed && <CheckCircle2 size={12} className="text-[#F54E00]" />}
              </span>
              <span>
                I accept government security{' '}
                <a href="#" className="auth-link">data disclosure policies</a>{' '}
                and the platform terms of service.
              </span>
            </label>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className={`auth-submit-btn ${loading ? 'auth-submit-btn--loading' : ''}`}
            >
              {loading ? (
                <>
                  <span className="auth-spinner" />
                  <span>Registering credentials…</span>
                </>
              ) : (
                <>
                  <span>Register Credentials</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <p className="auth-footer" style={{ marginTop: '1.25rem' }}>
            Already have registered credentials?{' '}
            <Link to="/login" className="auth-footer-link">
              Sign In
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
