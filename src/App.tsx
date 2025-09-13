import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Launch from "@/pages/Launch";
import TechDebtReport from "@/pages/TechDebtReport";
import LearningCenter from "@/pages/LearningCenter";
import CodeAnalysis from "@/pages/CodeAnalysis";
import CodeRecord from "@/pages/CodeRecord";
import Settings from "@/pages/Settings";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Launch />} />
        <Route path="/home" element={<Home />} />
        <Route path="/tech-debt-report" element={<TechDebtReport />} />
        <Route path="/learning-center" element={<LearningCenter />} />
        <Route path="/code-analysis" element={<CodeAnalysis />} />
        <Route path="/code-record" element={<CodeRecord />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/other" element={<div className="text-center text-xl">Other Page - Coming Soon</div>} />
      </Routes>
    </Router>
  );
}
