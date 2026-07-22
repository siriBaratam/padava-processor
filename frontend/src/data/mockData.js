export const mockScoutAlerts = [
  {
    id: 1,
    type: 'BAD',
    riskScore: 8.7,
    headline: "Houthi forces fire missiles at crude tanker near Aden",
    summary: "Command forces report anti-ship ballistic missile attack targeting commercial tanker in southern Red Sea. Risk level set to maximum.",
    corridor: "Red Sea",
    stations: ["Kochi", "Paradip"],
    eventType: "military_attack",
    source: "Reuters",
    timeAgo: "4m ago",
  },
  {
    id: 2,
    type: 'BAD',
    riskScore: 7.9,
    headline: "Iran threatens to close Strait of Hormuz amid escalating US sanctions",
    summary: "IRGC naval commander warns that passage through Strait of Hormuz could be restricted if sanctions target petroleum exports.",
    corridor: "Hormuz",
    stations: ["Jamnagar", "Vadinar"],
    eventType: "sanctions",
    source: "BBC Security",
    timeAgo: "22m ago",
  },
  {
    id: 3,
    type: 'GOOD',
    riskScore: 2.1,
    headline: "India and UAE sign 3-month crude oil supply agreement worth $2.4 billion",
    summary: "ADNOC agrees to supply 250,000 bpd directly to Indian ports via Persian Gulf route under emergency trade protocol.",
    corridor: "Persian Gulf",
    stations: ["All stations"],
    eventType: "trade_deal",
    source: "Economic Times",
    timeAgo: "1h ago",
  },
  {
    id: 4,
    type: 'BAD',
    riskScore: 6.8,
    headline: "OPEC+ announces emergency 500,000 bpd production cut effective immediately",
    summary: "Surprise ministerial meeting concludes with production limits aimed at stabilizing spot prices following geopolitical tension.",
    corridor: "Global",
    stations: ["All"],
    eventType: "supply_cut",
    source: "Reuters Energy",
    timeAgo: "2h ago",
  },
  {
    id: 5,
    type: 'BAD',
    riskScore: 5.4,
    headline: "Russian oil tanker detained at Danish straits over sanctions violations",
    summary: "Maritime authorities seize tanker carrying Ural crude destined for Asian markets following dark fleet inspection.",
    corridor: "Russia",
    stations: ["HPCL Vizag"],
    eventType: "sanctions",
    source: "The Guardian",
    timeAgo: "3h ago",
  },
  {
    id: 6,
    type: 'GOOD',
    riskScore: 1.8,
    headline: "Red Sea shipping insurance rates decline as Houthi attacks decrease",
    summary: "Underwriters trim war risk premium surcharges by 12% following naval escort deployment by joint coalition forces.",
    corridor: "Red Sea",
    stations: ["Kochi", "Paradip"],
    eventType: "general",
    source: "Lloyd's List",
    timeAgo: "5h ago",
  },
  {
    id: 7,
    type: 'BAD',
    riskScore: 7.2,
    headline: "Saudi Arabia cuts crude allocations to Asian buyers by 10% for next month",
    summary: "Aramco notifies state refiners of reduced term contract volumes due to domestic refinery maintenance schedule.",
    corridor: "Persian Gulf",
    stations: ["Jamnagar"],
    eventType: "supply_cut",
    source: "S&P Global Commodities",
    timeAgo: "6h ago",
  },
  {
    id: 8,
    type: 'NEUTRAL',
    riskScore: 1.0,
    headline: "Global oil demand forecast revised upward by IEA for Q3 2026",
    summary: "International Energy Agency adjusts daily consumption estimates by 180,000 bpd on strong Asian transportation growth.",
    corridor: "Global",
    stations: ["None"],
    eventType: "general",
    source: "IEA Monthly",
    timeAgo: "8h ago",
  }
];

export const mockStations = [
  {
    name: "Kochi Refinery",
    corridor: "Red Sea",
    stockDays: 10,
    incomingShip: "MT Kaveri",
    originalEta: "9 days",
    delay: "+15 days",
    newEta: "24 days",
    daysGap: "14 days gap",
    risk: "CRITICAL",
    riskLevel: "CRITICAL"
  },
  {
    name: "Paradip Refinery",
    corridor: "Red Sea",
    stockDays: 8,
    incomingShip: "MT Sindhu",
    originalEta: "14 days",
    delay: "+15 days",
    newEta: "29 days",
    daysGap: "21 days gap",
    risk: "CRITICAL",
    riskLevel: "CRITICAL"
  },
  {
    name: "Haldia Port",
    corridor: "Red Sea",
    stockDays: 6,
    incomingShip: "MT Ganga",
    originalEta: "12 days",
    delay: "+15 days",
    newEta: "27 days",
    daysGap: "23 days gap",
    risk: "CRITICAL",
    riskLevel: "CRITICAL"
  },
  {
    name: "Jamnagar Refinery",
    corridor: "Persian Gulf",
    stockDays: 7,
    incomingShip: "MT Anand",
    originalEta: "12 days",
    delay: "+0 days",
    newEta: "12 days",
    daysGap: "5 days gap",
    risk: "HIGH",
    riskLevel: "HIGH"
  },
  {
    name: "HPCL Vizag",
    corridor: "Russia",
    stockDays: 8,
    incomingShip: "MT Volga",
    originalEta: "18 days",
    delay: "+3 days",
    newEta: "21 days",
    daysGap: "13 days gap",
    risk: "HIGH",
    riskLevel: "HIGH"
  }
];

export const mockRefineries = [
  { name: "Kochi Refinery", status: "Reduced", capacity: 62 },
  { name: "Paradip Refinery", status: "Reduced", capacity: 55 },
  { name: "Haldia Port Terminal", status: "Shutdown", capacity: 15 },
  { name: "Jamnagar Complex", status: "Running", capacity: 94 },
];

export const mockSuppliers = [
  {
    rank: 1,
    name: "ADNOC",
    country: "UAE",
    corridor: "Persian Gulf",
    volume: "250 kbd",
    price: "$84.50",
    delivery: "10 days",
    contract: "Spot",
    isBest: true
  },
  {
    rank: 2,
    name: "Saudi Aramco",
    country: "Saudi Arabia",
    corridor: "Persian Gulf",
    volume: "160 kbd",
    price: "$86.00",
    delivery: "12 days",
    contract: "Spot",
    isBest: false
  },
  {
    rank: 3,
    name: "Kuwait Petroleum",
    country: "Kuwait",
    corridor: "Persian Gulf",
    volume: "200 kbd",
    price: "$87.20",
    delivery: "14 days",
    contract: "Spot",
    isBest: false
  }
];

export const mockVessels = [
  {
    vessel: "MT Kaveri",
    supplier: "IOCL Term",
    origin: "Aden",
    destination: "Kochi",
    originalRoute: "Red Sea → Suez",
    status: "BLOCKED",
    alternateRoute: "Cape of Good Hope",
    eta: "26 days",
    distance: "11,200 nm"
  },
  {
    vessel: "MT New Charter 1",
    supplier: "ADNOC UAE",
    origin: "Ruwais UAE",
    destination: "Kochi",
    originalRoute: "Persian Gulf → Indian Ocean",
    status: "CLEAR",
    alternateRoute: "—",
    eta: "10 days",
    distance: "1,840 nm"
  },
  {
    vessel: "MT New Charter 2",
    supplier: "Saudi Aramco",
    origin: "Ras Tanura",
    destination: "Paradip",
    originalRoute: "Persian Gulf → Indian Ocean",
    status: "CLEAR",
    alternateRoute: "—",
    eta: "14 days",
    distance: "2,200 nm"
  }
];

export const mockAlertsHistory = [
  { id: "ALT-901", severity: "CRITICAL", message: "Red Sea Corridor Missile Strike — Vessel Reroute Mandate", agent: "Scout Agent", corridor: "Red Sea", timestamp: "2026-07-21 22:15:02", status: "New" },
  { id: "ALT-902", severity: "CRITICAL", message: "Kochi Refinery SPR Drawdown Triggered (5-day emergency cover)", agent: "Strategist Agent", corridor: "Kochi", timestamp: "2026-07-21 22:10:14", status: "New" },
  { id: "ALT-903", severity: "HIGH", message: "Paradip Stock Days Depletion Rate Accelerated to 1.8x", agent: "Accountant Agent", corridor: "Paradip", timestamp: "2026-07-21 21:45:00", status: "Acknowledged" },
  { id: "ALT-904", severity: "HIGH", message: "Strait of Hormuz Escorts Required for MT Anand Cargo", agent: "Navigator Agent", corridor: "Hormuz", timestamp: "2026-07-21 20:30:11", status: "Acknowledged" },
  { id: "ALT-905", severity: "MEDIUM", message: "Spot Market ADNOC Quote Accepted ($84.50/bbl)", agent: "Dealmaker Agent", corridor: "Persian Gulf", timestamp: "2026-07-21 19:12:44", status: "Acknowledged" },
  { id: "ALT-906", severity: "CRITICAL", message: "Haldia Port Reserve Stock Reaches Threshold Below 7 Days", agent: "Accountant Agent", corridor: "Haldia", timestamp: "2026-07-21 18:05:30", status: "Acknowledged" },
  { id: "ALT-907", severity: "LOW", message: "Danish Straits Detention Monitoring Routine Update", agent: "Scout Agent", corridor: "Russia Corridor", timestamp: "2026-07-21 16:40:00", status: "Acknowledged" },
  { id: "ALT-908", severity: "MEDIUM", message: "Essential Power Sector Allocation Priority Locked", agent: "Allocator Agent", corridor: "National Grid", timestamp: "2026-07-21 15:20:10", status: "Acknowledged" },
  { id: "ALT-909", severity: "LOW", message: "Daily Crude Import Vulnerability Report Generated", agent: "Reports Module", corridor: "Global", timestamp: "2026-07-21 12:00:00", status: "Acknowledged" },
  { id: "ALT-910", severity: "HIGH", message: "OPEC+ 500k bpd Emergency Cut Market Volatility Alert", agent: "Scout Agent", corridor: "Global Market", timestamp: "2026-07-21 10:15:22", status: "Acknowledged" },
];

export const crudePriceData = [
  { day: 'Day 1', price: 78.2 },
  { day: 'Day 5', price: 79.5 },
  { day: 'Day 10', price: 81.0 },
  { day: 'Day 15', price: 80.4 },
  { day: 'Day 20', price: 83.2 },
  { day: 'Day 25', price: 88.5 },
  { day: 'Day 30', price: 84.5 },
];

export const allocationVsReqData = [
  { station: 'Kochi', required: 450, allocated: 310 },
  { station: 'Paradip', required: 380, allocated: 190 },
  { station: 'Haldia', required: 290, allocated: 150 },
];
