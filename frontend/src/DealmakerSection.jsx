import { ShieldCheck, Star } from "lucide-react";

/* ───────────────────────────────────────────────────────────
   Inline checkmark SVG (stroke updated to accent-600)
   ─────────────────────────────────────────────────────────── */

function CheckmarkCircle() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0"
    >
      <circle cx="12" cy="12" r="10" stroke="#4f46e5" strokeWidth="1.8" fill="#eef2ff" />
      <path
        d="M8 12l2.5 2.5L16 10"
        stroke="#4f46e5"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/* ───────────────────────────────────────────────────────────
   Loading skeleton
   ─────────────────────────────────────────────────────────── */

function SkeletonCard() {
  return (
    <div className="animate-pulse bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-4">
      <div className="flex items-center gap-2">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
      </div>
      <div className="h-3 bg-gray-200 rounded w-1/2" />
      <div className="space-y-3 pt-2">
        <div className="h-3 bg-gray-100 rounded" />
        <div className="h-3 bg-gray-100 rounded w-5/6" />
        <div className="h-3 bg-gray-100 rounded w-2/3" />
      </div>
      <div className="h-9 bg-gray-200 rounded-lg mt-4" />
    </div>
  );
}

/* ───────────────────────────────────────────────────────────
   Main component
   ─────────────────────────────────────────────────────────── */

export default function DealmakerSection({ data, loading, error, onApprove }) {
  // ── Loading ──
  if (loading) {
    return (
      <div className="text-left">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="w-5 h-5 text-accent-600 shrink-0" />
          <h2 className="text-xl font-bold tracking-tight text-gray-900 m-0">
            Dealmaker: Where to Buy More
          </h2>
        </div>
        <p className="text-sm text-gray-500 mb-8">
          Autonomous spot-market bidding for replacement volume.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  // ── Error ──
  if (error) {
    return (
      <div className="text-left">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="w-5 h-5 text-accent-600 shrink-0" />
          <h2 className="text-xl font-bold tracking-tight text-gray-900 m-0">
            Dealmaker: Finding Alternate Suppliers
          </h2>
        </div>
        <p className="text-sm text-gray-500 mb-8">
          Autonomous spot-market bidding for replacement volume.
        </p>
        <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-red-700 text-sm leading-relaxed">
          {error}
        </div>
      </div>
    );
  }

  // ── Empty ──
  if (!data || !data.options || data.options.length === 0) {
    return (
      <div className="text-left">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="w-5 h-5 text-accent-600 shrink-0" />
          <h2 className="text-xl font-bold tracking-tight text-gray-900 m-0">
            Dealmaker: Finding Alternate Suppliers
          </h2>
        </div>
        <p className="text-sm text-gray-500 mb-8">
          Autonomous spot-market bidding for replacement volume.
        </p>
        <div className="bg-gray-50 border border-gray-100 rounded-xl p-5 text-gray-500 text-sm">
          No supplier options available.
        </div>
      </div>
    );
  }

  // ── Data ──
  const isRecommended = (country) => country === data.recommended_country;

  return (
    <div className="text-left">
      {/* ── Header ── */}
      <div className="flex items-center gap-2 mb-1">
        <ShieldCheck className="w-5 h-5 text-accent-600 shrink-0" />
        <h2 className="text-xl font-bold tracking-tight text-gray-900 m-0">
          Dealmaker: Finding Alternate Suppliers
        </h2>
      </div>
      <p className="text-sm text-gray-500 mb-8">
        Autonomous spot-market bidding for replacement volume.
      </p>

      {/* ── Card grid ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {data.options.map((opt) => {
          const recommended = isRecommended(opt.country);
          const reliabilityPct = opt.reliability_score * 10;

          let reliabilityPill = "";
          if (reliabilityPct >= 90) reliabilityPill = "bg-green-50 text-green-700";
          else if (reliabilityPct >= 70) reliabilityPill = "bg-amber-50 text-amber-700";
          else reliabilityPill = "bg-red-50 text-red-700";

          const tradeLabel = opt.existing_trade_relation
            ? "Existing trade partner"
            : "New trade partner";

          return (
            <div
              key={opt.country}
              className={`
                relative
                bg-white
                rounded-xl
                p-6
                flex flex-col
                transition-all duration-200
                hover:-translate-y-0.5
                overflow-visible
                ${
                  recommended
                    ? "shadow-xl ring-2 ring-accent-500/30 border-2 border-accent-600 bg-white"
                    : "shadow-sm hover:shadow-md border border-gray-200"
                }
              `}
            >
              {/* ── Recommended badge ── */}
              {recommended && (
                <span className="absolute -top-3.5 left-4 inline-flex items-center gap-1.5 bg-accent-600 text text-[11px] font-bold uppercase tracking-wider rounded-full pl-2 pr-3.5 py-1 shadow-md z-20 ring-2 ring-accent-500/30 border-2 border-accent-600 bg-white">
                  <Star className="w-3.5 h-3.5 fill-white" />
                  RECOMMENDED
                </span>
              )}

              {/* ── Checkmark icon top-right ── */}
              {recommended && (
                <div className="absolute top-3 right-3 z-20">
                  <CheckmarkCircle />
                </div>
              )}

              {/* ── Country name ── */}
              <div className="text-lg font-semibold text-accent-700 mb-0.5">
                {opt.country}
              </div>

              {/* ── Trade relation ── */}
              <div className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-4">
                {tradeLabel}
              </div>

              {/* ── Stats ── */}
              <div className="space-y-2.5 mb-5 flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Price</span>
                  <span className="text-sm font-semibold text-gray-900 tabular-nums">
                    ${opt.price_per_unit_usd.toFixed(2)}/{opt.unit}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Max Cap.</span>
                  <span className="text-sm font-semibold text-gray-900 tabular-nums">
                    {opt.available_capacity}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Reliability</span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${reliabilityPill}`}
                  >
                    {reliabilityPct}%
                  </span>
                </div>
              </div>

              {/* ── Button ── */}
              {recommended ? (
                <button
                  className="w-full bg-accent-600 hover:bg-accent-700 text-white font-semibold rounded-lg py-2.5 transition-colors duration-150 active:scale-[0.98] cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent-500"
                  onClick={() => onApprove?.(opt.country)}
                >
                  APPROVE BID
                </button>
              ) : (
                <button className="w-full border border-gray-300 hover:border-accent-300 hover:text-accent-700 hover:bg-accent-50/50 text-gray-900 font-semibold rounded-lg py-2.5 transition-colors duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent-500">
                  VIEW TERMS
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Recommendation reason ── */}
      {data.recommendation_reason && (
        <div className="bg-accent-50/40 border border-accent-100 border-l-4 border-l-accent-500 rounded-xl p-5">
          <p className="m-0 italic text-gray-600 text-sm leading-relaxed">
            &ldquo;{data.recommendation_reason}&rdquo;
          </p>
        </div>
      )}
    </div>
  );
}
