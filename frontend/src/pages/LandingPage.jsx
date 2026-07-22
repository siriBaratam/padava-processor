import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SpotlightCard from '../components/reactbits/SpotlightCard';
import MagnetButton from '../components/reactbits/MagnetButton';
import ShinyText from '../components/reactbits/ShinyText';
import GridMotionBg from '../components/reactbits/GridMotionBg';
import { 
  Shield, 
  ArrowRight, 
  Play, 
  Radar, 
  Calculator, 
  BrainCircuit, 
  Boxes, 
  Handshake, 
  Compass, 
  Star, 
  Activity, 
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

export default function LandingPage() {
  const heroImageUri = "public/cargo-ship.jpg";

  const agents = [
    {
      name: "Scout Agent",
      role: "Global Intelligence Radar",
      desc: "Watches global news, military alerts, and real-time ship satellite movements.",
      bullets: [
        "Monitors 5,000+ news sources 24/7",
        "Tracks Suez, Hormuz & Malacca AIS data",
        "Scores shock severity from 1.0 to 10.0"
      ],
      icon: Radar,
    },
    {
      name: "Accountant Agent",
      role: "Stock & Financial Impact Engine",
      desc: "Calculates cost surges and station inventory stock-out days.",
      bullets: [
        "Computes exact refinery supply gap days",
        "Models daily freight & demurrage penalties",
        "Forecasts Indian market price impact"
      ],
      icon: Calculator,
    },
    {
      name: "Strategist Agent",
      role: "Sovereign Response Playbook",
      desc: "Decides India's national energy response plan in under 6 minutes.",
      bullets: [
        "Selects emergency reroute pathways",
        "Triggers strategic crude reserve (SPR) drawdown",
        "Matches threat level to defense protocols"
      ],
      icon: BrainCircuit,
    },
    {
      name: "Allocator Agent",
      role: "Strategic Reserve Allocator",
      desc: "Distributes available crude across refineries & critical power stations.",
      bullets: [
        "Prioritizes essential grid & hospital power",
        "Balances stock days between Kochi, Paradip & Haldia",
        "Prevents localized fuel shortages"
      ],
      icon: Boxes,
    },
    {
      name: "Dealmaker Agent",
      role: "Spot Procurement Negotiator",
      desc: "Finds best alternative crude suppliers in emergency markets.",
      bullets: [
        "Scans UAE, Saudi & Kuwait spot offers",
        "Ranks deal proposals by landed cost & ETA",
        "Automates contract term negotiations"
      ],
      icon: Handshake,
    },
    {
      name: "Navigator Agent",
      role: "Maritime Route Planner",
      desc: "Plans safest shipping routes and tracks vessel detours.",
      bullets: [
        "Calculates Cape of Good Hope detour ETAs",
        "Avoids active maritime conflict zones",
        "Provides real-time vessel location telemetry"
      ],
      icon: Compass,
    }
  ];

  const testimonials = [
    {
      quote: "EnergyGuard reduced our disruption response from 47 days to under 6. The Scout agent alone is worth every rupee.",
      name: "Rajesh Nair",
      title: "Deputy Secretary",
      org: "Ministry of Petroleum & Natural Gas",
      initials: "RN"
    },
    {
      quote: "The Strategist agent gave us an actionable plan within minutes of the Red Sea incident. We avoided a 3-day refinery shutdown.",
      name: "Priya Sharma",
      title: "Supply Chain Head",
      org: "Indian Oil Corporation (IOCL)",
      initials: "PS"
    },
    {
      quote: "Finally a system that tells us which stations are at risk before the news reaches the media. True sovereign resilience.",
      name: "Amit Verma",
      title: "Risk Director",
      org: "Hindustan Petroleum (HPCL)",
      initials: "AV"
    }
  ];

  const workflowSteps = [
    { step: "01", name: "News Alert", desc: "Military strike reported near Aden", icon: AlertTriangle },
    { step: "02", name: "Scout Agent", desc: "Parses AIS & flags Red Sea Corridor", icon: Radar },
    { step: "03", name: "Accountant", desc: "Calculates 14-day supply gap", icon: Calculator },
    { step: "04", name: "Strategist", desc: "Recommends SPR drawdown + Reroute", icon: BrainCircuit },
    { step: "05", name: "Allocator", desc: "Allocates 500 kbd across refineries", icon: Boxes },
    { step: "06", name: "Dealmaker", desc: "Secures 250 kbd ADNOC spot deal", icon: Handshake },
    { step: "07", name: "Navigator", desc: "Reroutes MT Kaveri via Cape", icon: Compass },
    { step: "08", name: "Dashboard", desc: "National command center updated", icon: Activity }
  ];

  const tickerItems = [
    "🛰️ Scout Active",
    "🚨 Red Sea Risk: HIGH",
    "📦 Kochi Refinery: 10 days stock",
    "♟️ Strategy: Reroute via Cape",
    "🤝 UAE deal recommended",
    "🧭 2 vessels rerouted",
    "🛡️ National SPR: 9.5 Days Cover",
    "⚡ System Status: OPERATIONAL"
  ];

  return (
    <div className="min-h-screen bg-[#F2F4F3] text-[#10201E] flex flex-col font-sans relative overflow-hidden">
      <Navbar />

      {/* HERO SECTION WITH BRIGHT CARGO SHIP BACKGROUND & REACT BITS GRID MOTION */}
      <section className="relative pt-32 pb-24 overflow-hidden border-b border-[#DCE1DF]">
        {/* React Bits Grid Motion Background Canvas */}
        <GridMotionBg />

        {/* Cargo Ship Background Image */}
        <div 
          className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat opacity-85 transition-opacity duration-700"
          style={{ backgroundImage: `url("${heroImageUri}")` }}
        ></div>

        {/* Vignette Overlay */}
        <div className="absolute inset-0 z-1 bg-gradient-to-b from-[#10201E]/60 via-[#10201E]/40 to-[#F2F4F3]"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Frosted Glass Content Panel */}
          <div className="max-w-4xl mx-auto backdrop-blur-lg bg-[#FAFBFA]/85 border border-white/40 p-8 sm:p-12 rounded-2xl shadow-xl">
            {/* Sovereign Badge */}
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/40 text-[#0E6E6A] text-xs font-mono mb-6 font-semibold">
              <Shield className="w-3.5 h-3.5" />
              <span>SOVEREIGN MARITIME CARGO TELEMETRY CONSOLE</span>
            </div>

            {/* Main Headline with React Bits ShinyText */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight-display text-[#10201E] max-w-4xl mx-auto leading-none mb-6">
              AI-Powered Energy Supply Chain Resilience for <ShinyText text="India" className="font-bold" />
            </h1>

            {/* Subtext */}
            <p className="text-base sm:text-lg text-[#4B5A57] max-w-2xl mx-auto mb-10 font-normal leading-relaxed">
              India imports <strong className="text-[#10201E] font-mono">88%</strong> of its crude oil. <strong className="text-[#10201E] font-mono">40%</strong> transits through the Strait of Hormuz. One incident. <strong className="text-[#10201E] font-mono">9.5 days</strong> of reserve cover. EnergyGuard gives you <strong className="text-[#0E6E6A] font-mono font-bold">47 days back</strong>.
            </p>

            {/* Interactive React Bits Magnetic Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
              <MagnetButton magnetStrength={0.2}>
                <Link
                  to="/dashboard"
                  className="px-8 py-3.5 bg-[#0E6E6A] hover:bg-[#0A5653] text-white font-semibold rounded-md transition-all duration-150 shadow-sm hover:shadow-md flex items-center justify-center space-x-2"
                >
                  <span>See the Dashboard</span>
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </MagnetButton>

              <MagnetButton magnetStrength={0.2}>
                <a
                  href="#how-it-works"
                  className="px-8 py-3.5 border border-[#DCE1DF] hover:bg-[#EAEDEC] text-[#10201E] bg-[#FAFBFA] rounded-md transition-all duration-150 flex items-center justify-center space-x-2"
                >
                  <Play className="w-4 h-4 fill-current text-[#0E6E6A]" />
                  <span>Watch Operational Demo</span>
                </a>
              </MagnetButton>
            </div>

            {/* React Bits Spotlight Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <SpotlightCard className="p-4 text-center bg-[#FAFBFA]/90">
                <p className="text-2xl lg:text-3xl font-bold font-mono text-[#10201E]">88%</p>
                <p className="text-xs font-mono text-[#4B5A57] mt-1">Import Dependent</p>
              </SpotlightCard>
              <SpotlightCard className="p-4 text-center bg-[#FAFBFA]/90">
                <p className="text-2xl lg:text-3xl font-bold font-mono text-[#B23A2E]">9.5 Days</p>
                <p className="text-xs font-mono text-[#4B5A57] mt-1">SPR Reserve Cover</p>
              </SpotlightCard>
              <SpotlightCard className="p-4 text-center bg-[#FAFBFA]/90">
                <p className="text-2xl lg:text-3xl font-bold font-mono text-[#276A4E]">47 Days</p>
                <p className="text-xs font-mono text-[#4B5A57] mt-1">Faster Response</p>
              </SpotlightCard>
              <SpotlightCard className="p-4 text-center bg-[#FAFBFA]/90">
                <p className="text-2xl lg:text-3xl font-bold font-mono text-[#2B4C6F]">6 Agents</p>
                <p className="text-xs font-mono text-[#4B5A57] mt-1">Autonomous AI Core</p>
              </SpotlightCard>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE STATS BAR */}
      <div className="bg-[#FAFBFA] border-y border-[#DCE1DF] py-2.5 overflow-hidden relative">
        <div className="flex space-x-8 animate-ticker whitespace-nowrap font-mono text-xs text-[#0E6E6A] font-semibold">
          {[...tickerItems, ...tickerItems].map((item, index) => (
            <span key={index} className="inline-flex items-center space-x-2">
              <span>{item}</span>
              <span className="text-[#DCE1DF]">·</span>
            </span>
          ))}
        </div>
      </div>

      {/* FEATURES SECTION (6 AGENTS) */}
      <section id="features" className="py-20 border-b border-[#DCE1DF] bg-[#FAFBFA]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight-title text-[#10201E]">
              Six Agents. One Mission.
            </h2>
            <p className="text-[#4B5A57] text-sm mt-3 max-w-xl mx-auto">
              Autonomous AI multi-agent orchestration working continuously to detect, model, and neutralize crude oil supply chain disruptions.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => {
              const Icon = agent.icon;
              return (
                <SpotlightCard key={agent.name} className="p-6 flex flex-col justify-between group">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 rounded bg-[#EAEDEC] border border-[#DCE1DF]">
                        <Icon className="w-6 h-6 text-[#0E6E6A]" />
                      </div>
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#EAEDEC] text-[#4B5A57] border border-[#DCE1DF]">
                        AUTONOMOUS
                      </span>
                    </div>

                    <h3 className="text-xl font-semibold text-[#10201E] group-hover:text-[#0E6E6A] transition-colors mb-1">
                      {agent.name}
                    </h3>
                    <p className="text-xs font-mono text-[#0E6E6A] mb-3">{agent.role}</p>
                    <p className="text-xs text-[#4B5A57] leading-relaxed mb-4">{agent.desc}</p>

                    <ul className="space-y-2 border-t border-[#DCE1DF] pt-4">
                      {agent.bullets.map((bullet, idx) => (
                        <li key={idx} className="flex items-start space-x-2 text-xs text-[#10201E]">
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#276A4E] mt-0.5 flex-shrink-0" />
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </SpotlightCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-20 border-b border-[#DCE1DF] bg-[#F2F4F3]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight-title text-[#10201E]">
              From News to Action in Minutes
            </h2>
            <p className="text-[#4B5A57] text-sm mt-3 max-w-xl mx-auto">
              How EnergyGuard turns 47-day traditional bureaucratic crisis responses into automated 6-minute tactical resolutions.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {workflowSteps.map((item) => {
              const Icon = item.icon;
              return (
                <SpotlightCard key={item.step} className="p-3 text-center flex flex-col items-center justify-between group">
                  <div className="w-7 h-7 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 flex items-center justify-center text-[#0E6E6A] font-mono text-xs font-bold mb-2">
                    {item.step}
                  </div>
                  <Icon className="w-5 h-5 text-[#4B5A57] mb-2 group-hover:text-[#0E6E6A] transition-colors" />
                  <h4 className="text-xs font-semibold text-[#10201E]">{item.name}</h4>
                  <p className="text-[10px] text-[#4B5A57] mt-1 leading-snug">{item.desc}</p>
                </SpotlightCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS SECTION */}
      <section id="testimonials" className="py-20 border-b border-[#DCE1DF] bg-[#FAFBFA]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight-title text-[#10201E]">
              Trusted by India's Energy Leaders
            </h2>
            <p className="text-[#4B5A57] text-sm mt-3 max-w-xl mx-auto">
              Empowering decision-makers across the Ministry, state refineries, and national security bodies.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, idx) => (
              <SpotlightCard key={idx} className="p-6 flex flex-col justify-between">
                <div>
                  <div className="flex space-x-1 text-[#B07A2C] mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-current" />
                    ))}
                  </div>
                  <p className="text-sm italic text-[#10201E] leading-relaxed mb-6">
                    "{t.quote}"
                  </p>
                </div>

                <div className="flex items-center space-x-3 pt-4 border-t border-[#DCE1DF]">
                  <div className="w-10 h-10 rounded-full bg-[#E4EFEE] border border-[#0E6E6A]/30 flex items-center justify-center text-[#0E6E6A] font-bold text-sm">
                    {t.initials}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-[#10201E]">{t.name}</h4>
                    <p className="text-xs text-[#4B5A57]">{t.title}</p>
                    <p className="text-[11px] font-mono text-[#0E6E6A]">{t.org}</p>
                  </div>
                </div>
              </SpotlightCard>
            ))}
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="py-20 bg-[#F2F4F3]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <SpotlightCard className="p-10 text-center relative overflow-hidden">
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight-title text-[#10201E] mb-4">
              India's energy security cannot wait
            </h2>
            <p className="text-[#4B5A57] text-sm max-w-xl mx-auto mb-8 leading-relaxed">
              Join the defense teams already using EnergyGuard AI to turn 47-day supply disruptions into 6-day automated recoveries.
            </p>

            <MagnetButton>
              <Link
                to="/register"
                className="inline-flex items-center space-x-2 px-8 py-3.5 bg-[#0E6E6A] hover:bg-[#0A5653] text-white font-semibold rounded-md transition-all duration-150 shadow-sm"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </MagnetButton>
          </SpotlightCard>
        </div>
      </section>

      <Footer />
    </div>
  );
}
