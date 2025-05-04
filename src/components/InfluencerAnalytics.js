import React, { useState, useRef } from "react";
import styled from "styled-components";
import { useNavigate } from "react-router-dom";
import NavBar from "./Navbar";
import GlobalStyle from "../styles/GlobalStyle";
import Chart from "chart.js/auto";

// Styled Components
const Container = styled.div`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const SearchForm = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Input = styled.input`
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
`;

const Button = styled.button`
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;

  &:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
`;

const Results = styled.div`
  margin-top: 30px;
`;

const Card = styled.div`
  background: white;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const ChannelTitle = styled.h2`
  margin-bottom: 10px;
`;

const StatContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
`;

const StatBox = styled.div`
  padding: 5px 10px;
  background: #f0f0f0;
  border-radius: 4px;
`;

const HighlightedCategory = styled.span`
  font-weight: bold;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: space-between;
`;

const ViewReportButton = styled.button`
  padding: 10px 20px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;

  &:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
`;

const ChartContainer = styled.div`
  margin-top: 20px;
  margin-bottom: 20px;
`;

const LineChartContainer = styled.div`
  margin-top: 20px;
  margin-bottom: 20px;
`;

const LoadingOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ErrorMessage = styled.div`
  color: red;
  text-align: center;
  margin: 10px 0;
`;

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