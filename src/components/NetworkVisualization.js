import React, { useState, useCallback, useRef } from "react";
import { Chart, registerables } from "chart.js";
import { useNavigate } from "react-router-dom";
import NavBar from "./Navbar";

Chart.register(...registerables);

const YouTubeAnalytics = () => {
  const [channelName, setChannelName] = useState("");
  const [loading, setLoading] = useState(false);
  const [subscribers, setSubscribers] = useState("--");
  const [views, setViews] = useState("--");
  const [videos, setVideos] = useState("--");
  const [categoryLabel, setCategoryLabel] = useState("--");
  const [channelData, setChannelData] = useState(null);
  const chartsRef = useRef({});
  const navigate = useNavigate();

  const fetchData = async () => {
    if (!channelName) {
      alert("Please enter a channel name.");
      return;
    }

    setLoading(true);

    try {
      const [analyticsResponse, contentResponse] = await Promise.all([
        fetch("http://127.0.0.1:5000/network/fetch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channel_name: channelName }),
        }),
        fetch("http://127.0.0.1:5000/network/content_analysis", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ channel_name: channelName }),
        }),
      ]);

      if (!analyticsResponse.ok || !contentResponse.ok) {
        throw new Error("Error fetching data from server!");
      }

      const analyticsData = await analyticsResponse.json();
      const contentData = await contentResponse.json();

      setLoading(false);

      if (analyticsData.error) {
        alert(analyticsData.error);
        return;
      }

      setSubscribers(analyticsData.subscribers);
      setViews(analyticsData.views);
      setVideos(analyticsData.total_videos);

      // Store the channel data for report generation
      setChannelData({
        channelName,
        analytics: analyticsData,
        content: contentData
      });

      renderCharts(
        analyticsData.videos,
        analyticsData.keyword_analysis,
        contentData.duration_analysis,
        contentData.category_analysis
      );
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  };

  const handleViewReport = () => {
    if (!channelData) {
      alert("Please fetch channel data first!");
      return;
    }
    // Store the channel data in session storage
    sessionStorage.setItem("channelData", JSON.stringify(channelData));
    sessionStorage.setItem("reportType", "Network Analysis");
    navigate("/reports");
  };

  const renderCharts = useCallback((videos, keywords, durationData, categoryData) => {
    // Destroy existing charts
    Object.values(chartsRef.current).forEach(chart => {
        if (chart) chart.destroy();
    });
    chartsRef.current = {};

    // Views Chart
    const viewsCtx = document.getElementById("viewsChart");
    if (viewsCtx) {
        chartsRef.current.viewsChart = new Chart(viewsCtx, {
            type: "line",
            data: {
                labels: videos.map(v => v.title),
                datasets: [{
                    label: "Views Over Time",
                    data: videos.map(v => v.views),
                    borderColor: "#007bff",
                    backgroundColor: "rgba(0, 123, 255, 0.2)",
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                  x: {
                      title: {
                          display: true,
                          text: "Video Name"
                      }
                  },
                  y: {
                      title: {
                          display: true,
                          text: "Views"
                      }
                  }
              }
          }
        });
    }

    // Keyword Chart
    const keywordCtx = document.getElementById("keywordChart");
    if (keywordCtx) {
        chartsRef.current.keywordChart = new Chart(keywordCtx, {
            type: "bar",
            data: {
                labels: keywords.map(k => k.keyword),
                datasets: [{
                    label: "Keyword Frequency",
                    data: keywords.map(k => k.count),
                    backgroundColor: "#ff5733"
                }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                  x: {
                      title: {
                          display: true,
                          text: "Key Words"
                      }
                  },
                  y: {
                      title: {
                          display: true,
                          text: "Frequency"
                      }
                  }
              }
          }
        });
    }

    // Cluster Chart (Engagement Level Scatter Plot)
    const clusterCtx = document.getElementById("clusterChart");
    if (clusterCtx) {
        const lowEngagement = {
            label: "Low Engagement",
            data: [],
            backgroundColor: "#ff5733",
            pointRadius: 6
        };

        const mediumEngagement = {
            label: "Medium Engagement",
            data: [],
            backgroundColor: "#ffd700",
            pointRadius: 6
        };

        const highEngagement = {
            label: "High Engagement",
            data: [],
            backgroundColor: "#008000",
            pointRadius: 6
        };

        videos.forEach(video => {
            const dataPoint = { x: video.views, y: video.likes };

            if (video.likes < 3000000) {
                lowEngagement.data.push(dataPoint);
            } else if (video.likes >= 3000000 && video.likes < 7000000) {
                mediumEngagement.data.push(dataPoint);
            } else {
                highEngagement.data.push(dataPoint);
            }
        });

        chartsRef.current.clusterChart = new Chart(clusterCtx, {
            type: "scatter",
            data: {
                datasets: [lowEngagement, mediumEngagement, highEngagement]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Views"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "Likes"
                        }
                    }
                }
            }
        });
    }

    // Duration Chart
    const durationCtx = document.getElementById("durationChart");
    if (durationCtx) {
        chartsRef.current.durationChart = new Chart(durationCtx, {
            type: "bar",
            data: {
                labels: durationData.map(d => d.duration),
                datasets: [
                    {
                        label: "Avg Likes",
                        data: durationData.map(d => d.avg_likes),
                        backgroundColor: "#007bff"
                    },
                    {
                        label: "Avg Views",
                        data: durationData.map(d => d.avg_views),
                        backgroundColor: "#28a745"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Category Chart
    const categoryCtx = document.getElementById("categoryChart");
    if (categoryCtx) {
        chartsRef.current.categoryChart = new Chart(categoryCtx, {
            type: "pie",
            data: {
                labels: Object.keys(categoryData),
                datasets: [{
                    data: Object.values(categoryData),
                    backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Set the most frequent category
        const mostFrequentCategory = Object.keys(categoryData).reduce((a, b) =>
            categoryData[a] > categoryData[b] ? a : b
        );
        setCategoryLabel(mostFrequentCategory);
    }
}, []);


  return (
    <>
      <NavBar />

      <style>
        {`
          .homeContainer {
            position: relative;
            min-height: 100vh;
            color: black;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
          }

          .heroSection {
            margin-top: 50px;
          }

          .input {
            padding: 10px;
            width: 300px;
            margin: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
          }

          .button {
            padding: 10px 20px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
          }

          .viewReportButton {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
          }

          .viewReportButton:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
          }

          .chartContainer {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 30px;
          }

          .chartBox {
            width: 45%;
            height: 300px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }
            

          .pieChartContainer {
            margin-top: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
          }

          .pieChartContainer canvas {
            width: 1700px !important;
            height: 500px !important;
          }

          .stats {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
          }

          .statBox {
            padding: 15px;
            background: #fff;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            min-width: 200px;
          }

          .categoryLabel {
            font-size: 22px;
            font-weight: bold;
            background-color: yellow;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
          }

          .loading {
            color: #ff0000;
            font-weight: bold;
            margin: 20px 0;
          }
        `}
      </style>

      <div className="homeContainer">
        <div className="heroSection">
          <h1 className="heroTitle">Analyze YouTube Channel</h1>
          <input 
            type="text" 
            value={channelName} 
            onChange={(e) => setChannelName(e.target.value)} 
            placeholder="Enter Channel Name" 
            className="input"
          />
          <button onClick={fetchData} className="button">Fetch Data</button>
          <button 
            onClick={handleViewReport} 
            className="viewReportButton"
            disabled={!channelData}
          >
            View Report
          </button>

          {loading && <p className="loading">Fetching data... Please wait</p>}

          <div className="stats">
            <div className="statBox">
              <div>Subscribers: {subscribers}</div>
            </div>
            <div className="statBox">
              <div>Total Views: {views}</div>
            </div>
            <div className="statBox">
              <div>Total Videos: {videos}</div>
            </div>
          </div>

          <div className="chartContainer">
            <div className="chartBox">
              <canvas id="viewsChart"></canvas>
            </div>
            <div className="chartBox">
              <canvas id="keywordChart"></canvas>
            </div>
            <div className="chartBox">
              <canvas id="clusterChart"></canvas>
            </div>
            <div className="chartBox">
              <canvas id="durationChart"></canvas>
            </div>
          </div>

          <div className="pieChartContainer">
            <canvas id="categoryChart"></canvas>
            <p className="categoryLabel">Detected Category: {categoryLabel}</p>
          </div>
        </div>
      </div>
    </>
  );
};

export default YouTubeAnalytics;