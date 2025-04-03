  import React, { useState, useRef } from "react";
  import styled, { createGlobalStyle } from "styled-components";
  import Chart from "chart.js/auto";
  import { useNavigate } from "react-router-dom";
  import NavBar from "./Navbar";

  // Global Styles
  const GlobalStyle = createGlobalStyle`
    :root {
      --primary: #6366f1;
      --success: #10b981;
      --error: #ef4444;
      --background: #f8fafc;
      --surface: #ffffff;
      --text: #1e293b;
      --text-light: #64748b;
      --radius: 12px;
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    body {
      font-family: 'Inter', sans-serif;
      background: var(--background);
      color: var(--text);
      margin: 0;
      padding: 0;
    }
  `;

  // Styled Components
  const Container = styled.div`
    width: 100vw;
    padding: 2rem;
    text-align: center;
  `;

  const Header = styled.header`
    background: var(--surface);
    padding: 2rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 2rem;
    width: 100%;
  `;

  const InputGroup = styled.div`
    background: var(--surface);
    padding: 1rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    width: 100%;
  `;

  const Input = styled.input`
    width: 50%;
    padding: 10px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    background: var(--background);
    color: var(--text);
  `;

  const Button = styled.button`
    background: ${(props) => (props.variant === "report" ? "#10b981" : "#6366f1")};
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    width: 48%;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;

    &:hover {
      opacity: 0.9;
    }

    &:active {
      transform: scale(0.98);
    }

    &:disabled {
      background: var(--text-light);
      cursor: not-allowed;
      opacity: 0.7;
    }
  `;

  const Results = styled.section`
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    width: 100%;
  `;

  const Card = styled.div`
    background: var(--surface);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    text-align: left;
    width: 90%;
  `;

  const ChannelTitle = styled.h2`
    font-size: 2rem;
    font-weight: bold;
    color: var(--text);
    flex-grow: 1;
  `;

  const StatContainer = styled.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    padding: 10px 0;
  `;

  const StatBox = styled.div`
    font-size: 1.2rem;
    font-weight: bold;
    color: var(--primary);
    flex: 1;
    text-align: center;
  `;

  const HighlightedCategory = styled.div`
    font-size: 1.2rem;
    font-weight: bold;
    color: white;
    background: var(--error);
    padding: 5px 10px;
    border-radius: var(--radius);
    text-align: center;
    flex: 1;
  `;

  const ChartContainer = styled.div`
    width: 100%;
    height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
  `;

  const LineChartContainer = styled.div`
    width: 100%;
    height: 350px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
  `;

  const LoadingOverlay = styled.div`
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  `;

  const ErrorMessage = styled.div`
    color: var(--error);
    text-align: center;
    margin: 10px 0;
    padding: 10px;
    background-color: rgba(239, 68, 68, 0.1);
    border-radius: var(--radius);
  `;
  // ... existing imports and GlobalStyle ...

  // Add these styled components after the existing Button component
  const ButtonContainer = styled.div`
    display: flex;
    justify-content: space-between;
    width: 100%;
    gap: 1rem;
    margin-top: 1rem;
  `;

  const ViewReportButton = styled(Button)`
    background: var(--success);
    display: block;
    margin: 20px auto;
    padding: 10px 25px;
    width: auto;
  `;

// ... keep all the existing imports and styled components ...

const InfluencerAnalytics = () => {
  const [country, setCountry] = useState("");
  const [minSubs, setMinSubs] = useState("");
  const [influencers, setInfluencers] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [engagementData, setEngagementData] = useState(null);
  const barChartInstance = useRef(null);
  const lineChartInstance = useRef(null);
  const navigate = useNavigate();

  const fetchInfluencers = async () => {
    if (!country.trim()) {
      setError("Please enter a country name");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://127.0.0.1:5000/influencer/filter?country=${country}&min_subscribers=${minSubs}`
      );
      
      if (!response.ok) {
        throw new Error("Failed to fetch influencers");
      }

      const data = await response.json();
      setInfluencers(Array.isArray(data) ? data : []);
      setSelectedChannel(null);
    } catch (err) {
      setError("Failed to fetch influencers. Please try again.");
      setInfluencers([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchEngagementData = async (channelId, barCanvasId, lineCanvasId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://127.0.0.1:5000/influencer/fetch_channel_engagement?channel_id=${channelId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setEngagementData(data);

      if (barChartInstance.current) barChartInstance.current.destroy();
      if (lineChartInstance.current) lineChartInstance.current.destroy();

      setTimeout(() => {
        const barCtx = document.getElementById(barCanvasId);
        if (barCtx) {
          barChartInstance.current = new Chart(barCtx, {
            type: "bar",
            data: {
              labels: Object.keys(data.engagement_scores),
              datasets: [
                {
                  label: "Engagement Rate",
                  data: Object.values(data.engagement_scores),
                  backgroundColor: "rgba(99, 102, 241, 0.5)",
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: { y: { beginAtZero: true, max: 100 } },
            },
          });
        }

        const lineCtx = document.getElementById(lineCanvasId);
        if (lineCtx) {
          lineChartInstance.current = new Chart(lineCtx, {
            type: "line",
            data: {
              labels: Object.keys(data.growth_rates),
              datasets: [
                {
                  label: "Monthly Growth Rate (%)",
                  data: Object.values(data.growth_rates),
                  borderColor: "rgba(16, 185, 129, 1)",
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  fill: true,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: { y: { beginAtZero: true } },
            },
          });
        }
      }, 200);
    } catch (error) {
      console.error("Error fetching engagement data:", error);
      setError("Failed to fetch engagement data.");
    } finally {
      setLoading(false);
    }
  };

  const handleViewInsights = (channelId) => {
    setSelectedChannel(channelId);
    fetchEngagementData(channelId, `chart-${channelId}`, `line-chart-${channelId}`);
  };

  const handleViewReport = () => {
    if (influencers.length > 0) {
      const reportData = {
        influencers: influencers,
        filters: {
          country: country,
          minSubscribers: minSubs
        }
      };

      sessionStorage.setItem("channelData", JSON.stringify(reportData));
      sessionStorage.setItem("reportType", "Influencer Analysis");
      navigate("/reports");
    } else {
      setError("Please search for influencers first");
    }
  };

  return (
    <>
      <GlobalStyle />
      <NavBar />
      <Container>
        <Header>
          <h1>Influencer Analytics Pro</h1>
          <p>Advanced Creator Performance Analysis</p>
        </Header>

        <InputGroup>
          <Input
            type="text"
            placeholder="Enter country name..."
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
          <Input
            type="number"
            placeholder="Minimum subscribers"
            value={minSubs}
            onChange={(e) => setMinSubs(e.target.value)}
          />
          <ButtonContainer>
            <Button onClick={fetchInfluencers} disabled={loading}>
              {loading ? "Loading..." : "🔍 Search Influencers"}
            </Button>
            <Button 
              variant="report" 
              onClick={handleViewReport}
              disabled={loading || influencers.length === 0}
            >
              📄 View Report
            </Button>
          </ButtonContainer>
        </InputGroup>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        <Results>
          {influencers.map((inf) => (
            <Card key={inf.channel_id}>
              <ChannelTitle>{inf.title}</ChannelTitle>
              <StatContainer>
                <StatBox>{inf.subscriber_count.toLocaleString()} Subscribers</StatBox>
                <StatBox>{inf.engagement_rate}% Engagement</StatBox>
                <HighlightedCategory>{inf.influencer_type} Category</HighlightedCategory>
              </StatContainer>
              <Button onClick={() => handleViewInsights(inf.channel_id)} disabled={loading}>
                {loading ? "Loading..." : "📊 View Insights"}
              </Button>

              {selectedChannel === inf.channel_id && (
                <>
                  <ChartContainer><canvas id={`chart-${inf.channel_id}`} /></ChartContainer>
                  <LineChartContainer><canvas id={`line-chart-${inf.channel_id}`} /></LineChartContainer>
                  <ViewReportButton 
                    variant="report" 
                    onClick={handleViewReport}
                    disabled={loading}
                  >
                    📄 View Report
                  </ViewReportButton>
                </>
              )}
            </Card>
          ))}
        </Results>

        {loading && (
          <LoadingOverlay>
            <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }}></div>
          </LoadingOverlay>
        )}
      </Container>
    </>
  );
};

export default InfluencerAnalytics;