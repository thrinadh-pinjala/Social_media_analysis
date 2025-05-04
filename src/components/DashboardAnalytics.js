import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Title, Legend } from "chart.js";
import { Bar } from "react-chartjs-2";

// Register Chart.js components
Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Title, Legend);

const DashboardAnalytics = () => {
  const [trendingVideos, setTrendingVideos] = useState([]);
  const [wordCloudUrl, setWordCloudUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [region, setRegion] = useState("IN");

  const fetchData = async (selectedRegion) => {
    console.log(`Fetching data for region: ${selectedRegion}`);
    setLoading(true);
    setError(null);
    setWordCloudUrl('');

    const explicitBackendUrl = 'http://localhost:5000';
    const trendingUrl = `${explicitBackendUrl}/dash/get_trending_data`;
    const wordCloudUrlPath = `${explicitBackendUrl}/dash/wordcloud`;

    try {
        // Fetch trending video data
        console.log(`GET Request to: ${trendingUrl}?region=${selectedRegion}`);
        const trendingResponse = await axios.get(trendingUrl, { 
            params: { region: selectedRegion },
            timeout: 30000, // 30 second timeout
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            withCredentials: false
        });
        
        console.log("Trending Response:", trendingResponse);
        
        if (trendingResponse.data && trendingResponse.data.videos && trendingResponse.data.videos.length > 0) {
            setTrendingVideos(trendingResponse.data.videos);
            
            // Fetch word cloud image
            console.log(`GET Request to: ${wordCloudUrlPath}?region=${selectedRegion}`);
            const wordCloudResponse = await axios.get(wordCloudUrlPath, { 
                params: { region: selectedRegion },
                timeout: 30000,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                withCredentials: false
            });
            
            if (wordCloudResponse.data && wordCloudResponse.data.wordcloud) {
                setWordCloudUrl(wordCloudResponse.data.wordcloud);
            } else {
                console.warn("Word cloud data not found in response:", wordCloudResponse.data);
            }
        } else {
            throw new Error("No videos found in response");
        }

    } catch (err) {
        console.error("--- Fetch Error ---");
        if (err.response) {
            console.error("Response Error:", {
                status: err.response.status,
                data: err.response.data,
                headers: err.response.headers
            });
            
            setError(`Failed to load data: ${err.response.data?.error || err.response.statusText} (Status: ${err.response.status})`);
        } else if (err.request) {
            console.error("Request Error:", err.request);
            setError("Failed to connect to server. Please check if the backend is running.");
        } else {
            console.error("Error:", err.message);
            setError(`Error: ${err.message}`);
        }
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(region);
  }, [region]);

  const topVideos = Array.isArray(trendingVideos) ? trendingVideos.slice(0, 10) : [];
  const chartData = {
    labels: topVideos.map(video => video?.title || 'Untitled'),
    datasets: [{
      label: "Views",
      data: topVideos.map(video => Number(video?.views) || 0),
      backgroundColor: 'rgba(50, 179, 199, 0.6)',
      borderColor: 'rgba(50, 179, 199, 1)',
      borderWidth: 1,
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top', labels: { color: 'var(--text)' } },
      title: { display: true, text: `Top 10 Trending Videos by Views (${region})`, color: 'var(--text)', font: { size: 16 } },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleColor: '#fff',
        bodyColor: '#fff',
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) label += ': ';
            if (context.parsed.y !== null) label += context.parsed.y.toLocaleString();
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { 
          color: 'var(--text)', 
          callback: function(value) {
            if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
            if (value >= 1e3) return (value / 1e3).toFixed(0) + 'K';
            return value;
          }
        },
        grid: { color: 'var(--border)' }
      },
      x: {
        ticks: { color: 'var(--text)', autoSkip: true, maxRotation: 0 },
        grid: { display: false }
      }
    }
  };

  const styles = {
    page: {
      padding: '8rem 5% 4rem',
      minHeight: 'calc(100vh - 6rem)',
      background: 'var(--bg)',
      color: 'var(--text)'
    },
    heading: { 
      marginBottom: '2rem', 
      color: 'var(--primary)', 
      fontSize: '2rem', 
      fontWeight: '600' 
    },
    section: {
      background: 'var(--card-bg)', 
      padding: '1.5rem 2rem', 
      marginBottom: '2.5rem', 
      borderRadius: '12px',
      border: '1px solid var(--border)', 
      boxShadow: '0 6px 15px rgba(0, 0, 0, 0.07)',
    },
    selectLabel: { 
      marginRight: '0.75rem', 
      fontWeight: '500', 
      color: 'var(--text)'
    },
    select: {
      padding: '0.6rem 1rem', 
      borderRadius: '6px', 
      border: '1px solid var(--border)', 
      background: 'var(--bg)',
      color: 'var(--text)', 
      minWidth: '180px', 
      fontSize: '1rem', 
      cursor: 'pointer'
    },
    tableContainer: { 
      overflowX: 'auto', 
      WebkitOverflowScrolling: 'touch' 
    },
    table: { 
      width: '100%', 
      borderCollapse: 'collapse', 
      marginTop: '1rem' 
    },
    th: {
      background: 'rgba(42, 92, 130, 0.08)',
      color: 'var(--primary)', 
      padding: '0.8rem 1rem',
      textAlign: 'left', 
      borderBottom: '2px solid var(--border)', 
      fontSize: '0.85em', 
      textTransform: 'uppercase', 
      letterSpacing: '0.5px'
    },
    td: { 
      padding: '0.8rem 1rem', 
      borderBottom: '1px solid var(--border)', 
      verticalAlign: 'middle', 
      fontSize: '0.95em' 
    },
    wordCloudImage: { 
      display: 'block', 
      maxWidth: '100%', 
      height: 'auto', 
      margin: '1rem auto', 
      background: '#fff', 
      borderRadius: '8px', 
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)' 
    },
    loadingText: { 
      textAlign: 'center', 
      padding: '3rem', 
      fontSize: '1.2em', 
      color: 'var(--secondary)' 
    },
    errorContainer: { 
      padding: '1.5rem', 
      color: 'var(--accent)', 
      background: 'rgba(255, 107, 107, 0.1)', 
      border: '1px solid var(--accent)', 
      borderRadius: '8px', 
      marginTop: '1rem', 
      textAlign: 'center', 
      whiteSpace: 'pre-wrap'
    },
    chartContainer: { 
      height: '400px', 
      position: 'relative' 
    }
  };

  const handleRegionChange = (event) => {
    setRegion(event.target.value);
  };

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>YouTube Trending Dashboard</h2>

      {/* Region Selector */}
      <div style={{ marginBottom: '2.5rem', display: 'flex', alignItems: 'center' }}>
        <label htmlFor="region" style={styles.selectLabel}>Select Country:</label>
        <select 
          id="region" 
          value={region} 
          onChange={handleRegionChange} 
          style={styles.select} 
          disabled={loading}
        >
          <option value="IN">India</option>
          <option value="US">United States</option>
          <option value="GB">United Kingdom</option>
          <option value="JP">Japan</option>
          <option value="CA">Canada</option>
          <option value="KR">South Korea</option>
          <option value="DE">Germany</option>
          <option value="FR">France</option>
          <option value="BR">Brazil</option>
          <option value="AU">Australia</option>
          <option value="MX">Mexico</option>
        </select>
      </div>

      {/* Loading State */}
      {loading && <p style={styles.loadingText}>Loading trending data for {region}...</p>}

      {/* Error State */}
      {error && <div style={styles.errorContainer}>Error: {error}</div>}

      {/* Content Display */}
      {!loading && !error && (
        <>
          {/* Chart Section */}
          {topVideos.length > 0 && (
            <section style={styles.section}>
              <div style={styles.chartContainer}>
                <Bar data={chartData} options={chartOptions} />
              </div>
            </section>
          )}

          {/* Word Cloud Section */}
          {wordCloudUrl && (
            <section style={styles.section}>
              <h3 style={{marginBottom: '1rem', color: 'var(--primary)'}}>Trending Keywords</h3>
              <img 
                src={wordCloudUrl} 
                alt={`Word Cloud for ${region}`} 
                style={styles.wordCloudImage} 
              />
            </section>
          )}

          {/* Table Section */}
          {topVideos.length > 0 && (
            <section style={styles.section}>
              <h3 style={{marginBottom: '1rem', color: 'var(--primary)'}}>Top 10 Trending Videos</h3>
              <div style={styles.tableContainer}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>Title</th>
                      <th style={styles.th}>Views</th>
                      <th style={styles.th}>Likes</th>
                      <th style={styles.th}>Published</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topVideos.map((video, index) => (
                      <tr key={`${region}-${video?.title?.slice(0,10)}-${index}`}>
                        <td style={styles.td}>{video?.title || 'N/A'}</td>
                        <td style={styles.td}>{video?.views?.toLocaleString() ?? 'N/A'}</td>
                        <td style={styles.td}>{video?.likes?.toLocaleString() ?? 'N/A'}</td>
                        <td style={styles.td}>
                          {video?.published_at ? new Date(video.published_at).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
};

export default DashboardAnalytics;
