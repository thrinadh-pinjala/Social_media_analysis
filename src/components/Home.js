import React, { useState, useEffect, useRef } from "react";
import { Routes, Route, Link, useNavigate, useLocation } from "react-router-dom";
import DashboardAnalytics from './DashboardAnalytics';
import Recommendations from './Recommendations';

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "light");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    console.log('Current location:', location.pathname); // Debug log
  }, [theme, location]);

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

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
          100% { transform: translateY(0px); }
        }

        .loading-animate {
          animation: fadeIn 0.8s ease forwards;
          opacity: 0;
        }

        .navbar {
          padding: 1.5rem 5%;
          background: rgba(var(--bg), 0.95);
          backdrop-filter: blur(10px);
          box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
          position: fixed;
          width: 100%;
          top: 0;
          z-index: 1000;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .logo {
          font-size: 1.8rem;
          font-weight: 700;
          color: var(--primary);
          text-decoration: none;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .nav-links {
          display: flex;
          gap: 2.5rem;
          align-items: center;
        }

        .nav-link {
          color: var(--text);
          text-decoration: none;
          font-weight: 500;
          transition: all 0.3s ease;
          position: relative;
          padding: 0.5rem 0;
        }

        .user-menu {
          position: relative;
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .user-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(var(--primary), 0.1);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .user-dropdown {
          position: absolute;
          top: 120%;
          right: 0;
          background: var(--card-bg);
          border-radius: 8px;
          padding: 1rem;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
          display: none;
          min-width: 200px;
          z-index: 1000;
          border: 1px solid var(--border);
        }

        .user-dropdown.show {
          display: block;
          animation: fadeIn 0.3s ease;
        }

        .dropdown-item {
          padding: 0.75rem 1rem;
          border-radius: 6px;
          display: flex;
          align-items: center;
          gap: 1rem;
          text-decoration: none;
          color: var(--text);
          transition: background 0.3s ease;
        }

        .dropdown-item:hover {
          background: rgba(var(--primary), 0.1);
        }

        .theme-toggle {
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          background: none;
          border: none;
          color: var(--text);
        }

        .hero {
          padding: 12rem 5% 8rem;
          text-align: center;
          max-width: 1200px;
          margin: 0 auto;
        }

        .hero-title {
          font-size: 3.5rem;
          margin-bottom: 1.5rem;
          line-height: 1.2;
          color: var(--primary);
          letter-spacing: -0.05em;
        }

        .hero-subtitle {
          font-size: 1.25rem;
          color: #64748B;
          margin-bottom: 3rem;
          line-height: 1.7;
        }

        .cta-container {
          display: flex;
          gap: 1.5rem;
          justify-content: center;
          margin-top: 3rem;
        }

        .cta-button {
          padding: 1rem 2.5rem;
          border-radius: 50px;
          text-decoration: none;
          font-weight: 600;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
        }

        .primary-cta {
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          color: white;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .secondary-cta {
          background: var(--card-bg);
          color: var(--primary);
          border: 2px solid var(--primary);
        }

        .features {
          padding: 6rem 5%;
          background: var(--card-bg);
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 3rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .feature-card {
          padding: 2.5rem;
          border-radius: 1rem;
          background: var(--bg);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
          transition: all 0.3s ease;
          border: 1px solid var(--border);
        }

        .feature-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        .feature-icon {
          width: 50px;
          height: 50px;
          margin-bottom: 1.5rem;
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          animation: float 4s ease-in-out infinite;
        }

        .about-page {
          padding: 8rem 5% 4rem;
          min-height: 100vh;
        }

        .team-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 3rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .team-card {
          background: var(--card-bg);
          border-radius: 1.5rem;
          padding: 2rem;
          text-align: center;
          border: 1px solid var(--border);
          transform: scale(0);
          animation: popIn 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards;
        }

        @keyframes popIn {
          0% { transform: scale(0); }
          80% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }

        .avatar-circle {
          width: 120px;
          height: 120px;
          margin: 0 auto 1.5rem;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--primary), var(--secondary));
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2.5rem;
          color: white;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        }

        .team-name {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
          color: var(--primary);
        }

        .team-role {
          color: var(--secondary);
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .team-education {
          color: #64748B;
          font-size: 0.95rem;
        }

        @media (max-width: 768px) {
          .hero-title {
            font-size: 2.5rem;
          }
          .nav-links {
            gap: 1rem;
          }
          .cta-container {
            flex-direction: column;
          }
        }
      `}} />

      <Navbar toggleTheme={toggleTheme} handleLogout={handleLogout} />
      
      <div className="content-wrapper" style={{ marginTop: '80px' }}>
        <Routes>
          <Route path="/" element={
            <>
              <Hero />
              <Features />
            </>
          } />
          <Route path="/about" element={<About />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/influencer-detection" element={<div>Influencer Detection Page</div>} />
          <Route path="/sentiment-analysis" element={<div>Sentiment Analysis Page</div>} />
          <Route path="/dashboard-analytics" element={<DashboardAnalytics />} />
        </Routes>
      </div>
    </div>
  );
}

const Navbar = ({ toggleTheme, handleLogout }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setShowDropdown(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        <div className="logo-icon"></div>
        InsightSphere
      </Link>
      <div className="nav-links">
        <Link to="/network-visualization" className="nav-link">Analytics</Link>
        <Link to="/influencer-detection" className="nav-link">Influencer Detection</Link>
        <Link to="/sentiment-analysis" className="nav-link">Sentiment Analysis</Link>
        <Link to="/dashboard-analytics" className="nav-link">Dashboard Analytics</Link>
        <Link to="/about" className="nav-link">About Us</Link>

        <div className="user-menu" ref={dropdownRef}>
          <button className="theme-toggle" onClick={toggleTheme}>🌓</button>
          <div className="user-avatar" onClick={() => setShowDropdown(!showDropdown)}>👤</div>
          <div className={`user-dropdown ${showDropdown ? 'show' : ''}`}>
            <button className="dropdown-item"><span>👤</span> Profile</button>
            <button className="dropdown-item"><span>⚙</span> Settings</button>
            <button className="dropdown-item" onClick={toggleTheme}><span>🌓</span> Dark Mode</button>
            <button className="dropdown-item"><span>🔔</span> Notifications</button>
            <button className="dropdown-item" onClick={handleLogout}><span>🔒</span> Logout</button>
          </div>
        </div>
      </div>
    </nav>
  );
};

const Hero = () => (
  <section className="hero loading-animate" style={{ animationDelay: '0.2s' }}>
    <h1 className="hero-title">Advanced Social Media Analytics</h1>
    <p className="hero-subtitle">
      Harness AI-powered insights to optimize your social strategy, identify key influencers,
      and track brand sentiment across platforms.
    </p>
    <div className="cta-container">
      <Link to="/network-visualization" className="cta-button primary-cta">YouTube Analytics</Link>
      <Link to="/dashboard-analytics" className="cta-button secondary-cta">View Dashboard</Link>
    </div>
  </section>
);

const Features = () => (
  <section className="features" id="features">
    <div className="features-grid">
      {[
        { 
          icon: '📈', 
          title: 'Real-time Monitoring', 
          text: 'Track social metrics across platforms',
          link: '/recommendations'
        },
        { 
          icon: '🎯', 
          title: 'Influencer Scoring', 
          text: 'AI-driven influencer identification',
          link: '/influencer-detection'
        },
        { 
          icon: '🧠', 
          title: 'Sentiment Analysis', 
          text: 'NLP for brand perception tracking',
          link: '/sentiment-analysis'
        }
      ].map((feature, index) => (
        <Link 
          key={feature.title} 
          to={feature.link}
          className="feature-card loading-animate" 
          style={{ animationDelay: `${0.4 + index * 0.2}s`, textDecoration: 'none' }}
        >
          <div className="feature-icon">{feature.icon}</div>
          <h3>{feature.title}</h3>
          <p>{feature.text}</p>
        </Link>
      ))}
    </div>
  </section>
);

const About = () => {
  const teamMembers = [
    { 
      name: "A. D Sathyamurthy",
      role: "Back End Developer",
      education: "B.Tech CSE",
      emoji: "👨‍💻"
    },
    {
      name: "V Hemanth",
      role: "Scrum Master",
      education: "B.Tech CSE",
      emoji: "🧑🏻‍💼"
    },
    {
      name: "D L Prasad",
      role: "Front End Developer",
      education: "B.Tech CSE",
      emoji: "👨‍🎨"
    },
    {
      name: "M. Abhisree",
      role: "Q&A Engineer",
      education: "B.Tech CSE",
      emoji: "👮🏻‍♀  "
    },
    {
      name: "A. Gurusree",
      role: "Product Owner",
      education: "B.Tech CSE",
      emoji: "👩‍💼"
    }
  ];

  return (
    <div className="about-page">
      <div className="team-grid">
        {teamMembers.map((member, index) => (
          <div 
            key={member.name}
            className="team-card"
            style={{ animationDelay: `${index * 0.2}s` }}
          >
            <div className="avatar-circle">{member.emoji}</div>
            <h3 className="team-name">{member.name}</h3>
            <p className="team-role">{member.role}</p>
            <p className="team-education">{member.education}</p>
          </div>
        ))}
      </div>
    </div>
  );
};