import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import Signup from "./components/Signup";
import NetworkVisualization from "./components/NetworkVisualization";
import InfluencerDetection from "./components/InfluencerDetection";
import SentimentAnalysis from "./components/SentimentAnalysis";
import DashboardAnalytics from "./components/DashboardAnalytics";
import Reports from "./components/Reports"; // Import the Reports page
import Recommendations from "./components/Recommendations"; // Add this line

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/network-visualization" element={<NetworkVisualization />} />
        <Route path="/influencer-detection" element={<InfluencerDetection />} />
        <Route path="/sentiment-analysis" element={<SentimentAnalysis />} />
        <Route path="/dashboard-analytics" element={<DashboardAnalytics />} />
        <Route path="/reports" element={<Reports />} /> {/* Added Reports Page Route */}
        <Route path="/recommendations" element={<Recommendations />} /> {/* Add this line */}
      </Routes>
    </Router>
  );
}

export default App;
