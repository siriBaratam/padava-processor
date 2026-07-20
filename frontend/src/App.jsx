import { useEffect } from "react";
import "./App.css";
import useDealmaker from "./useDealmaker";
import DealmakerSection from "./DealmakerSection";

function App() {
  const { data, loading, error, run } = useDealmaker();

  // Auto-trigger on mount
  useEffect(() => {
    run("crude_oil", "45,000 barrels/day");
  }, [run]);

  const handleApprove = (country) => {
    alert(`Bid approved for ${country}!`);
  };

  return (
    <div className="app">
      <DealmakerSection
        data={data}
        loading={loading}
        error={error}
        onApprove={handleApprove}
      />
    </div>
  );
}

export default App;
