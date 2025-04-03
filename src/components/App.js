import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import About from './About';
// Import any other components

const App = () => {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
  };

  const handleLogout = () => {
    navigate("/");
  };

  return (
    <div className="App">
      <style dangerouslySetInnerHTML={{ __html: `
        :root {
          --primary: #2A5C82;
          --secondary: #32B3C7;
          --accent: #FF6B6B;
          --bg: #ffffff;
          --text: #0A192F;
          --card-bg: #ffffff;
          --border: #e2e8f0;
        }

        [data-theme="dark"] {
          --bg: #0A192F;
          --text: #F8F9FA;
          --card-bg: #1E293B;
          --border: #334155;
        }

        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          font-family: 'Inter', system-ui, sans-serif;
          transition: background-color 0.3s ease, color 0.3s ease;
        }

        body {
          background-color: var(--bg);
          color: var(--text);
          line-height: 1.6;
          overflow-x: hidden;
        }
      `}} />

      <Navbar toggleTheme={toggleTheme} handleLogout={handleLogout} />

      <Routes>
        {/* Catch-all route for your home layout */}
        <Route path="/" element={<><Hero /><Features /></>} />
        
        <Route path="/about" element={<About />} />
        <Route path="/network-visualization" element={<div>Network Visualization</div>} />
        <Route path="/influencer-detection" element={<div>Influencer Detection</div>} />
        <Route path="/sentiment-analysis" element={<div>Sentiment Analysis</div>} />
        <Route path="/dashboard-analytics" element={<div>Dashboard Analytics</div>} />
        
        {/* Consider adding a route for the filter page */}
        <Route path="/filter" element={<FilterComponent />} />

        {/* Optional: Add a NotFound component for unmatched routes */}
        <Route path="*" element={<div>404 Not Found</div>} />
      </Routes>
    </div>
  );
};

// Export the App component
export default App;