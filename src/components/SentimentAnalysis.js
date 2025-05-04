import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";
import { MatrixController, MatrixElement } from "chartjs-chart-matrix";
import "chartjs-chart-matrix";
import NavBar from "./Navbar";

Chart.register(MatrixController, MatrixElement);

const YouTubeSentiment = () => {
    // State management
    const [channel, setChannel] = useState("");
    const [bestTime, setBestTime] = useState("");
    const [error, setError] = useState(null);
    const [showCharts, setShowCharts] = useState(false);
    const [chartData, setChartData] = useState(null);
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showCentralities, setShowCentralities] = useState(false);

    // Hooks and refs
    const navigate = useNavigate();
    const charts = useRef({});

    // Navigate to Reports Page
    const handleViewReport = () => {
        if (!channel.trim()) {
            setError("⚠ Please enter a channel name.");
            return;
        }
        sessionStorage.setItem("channelData", JSON.stringify({
            channelName: channel,
            sentiment: chartData,
            videos: videos
        }));
        sessionStorage.setItem("reportType", "Sentiment Analysis");
        navigate("/reports");
    };

    // Fetch sentiment data
    const fetchSentiment = async () => {
        if (!channel.trim()) {
            setError("⚠ Please enter a channel name.");
            setShowCharts(false);
            return;
        }
    
        setError(null);
        setLoading(true);
        setShowCharts(false);
        
        // Clear old data
        setChartData(null);
        setBestTime("");
        setVideos([]);
    
        // Destroy existing charts before fetching new data
        Object.values(charts.current).forEach(chart => chart.destroy());
        charts.current = {};
    
        try {
            const response = await fetch(`http://127.0.0.1:5000/sentiment/analyze_sentiment?channel=${encodeURIComponent(channel)}`);
            if (!response.ok) throw new Error("❌ Channel not found.");
    
            const data = await response.json();
            if (!data) throw new Error("❌ Invalid data received from the server.");
    
            setChartData(data);
            setBestTime(data.best_time);
            setVideos(data.video_sentiments || []);
            setShowCharts(true);
        } catch (error) {
            setError(error.message);
            setShowCharts(false);
        } finally {
            setLoading(false);
        }
    };
    

    // Chart initialization effect
    useEffect(() => {
        if (!chartData) return;
        updatePieChart(chartData.percentages);
        updateLineChart(chartData.video_sentiments);
        updateHeatmapChart(chartData.hourly_sentiment);
        updatePerformanceChart(chartData.predicted_performance);
    }, [chartData]);

    // Chart creation utilities
    const createChart = (id, type, data, options) => {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        if (charts.current[id]) {
            charts.current[id].destroy();
        }

        charts.current[id] = new Chart(ctx, { 
            type, 
            data, 
            options: {
                ...options,
                responsive: true,
                maintainAspectRatio: false
            }
        });
    };

    const updatePieChart = (data) => {
        if (!data) return;
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        createChart("sentimentChart", "pie", {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.8)',  // Positive
                    'rgba(255, 99, 132, 0.8)',  // Negative
                    'rgba(54, 162, 235, 0.8)',  // Neutral
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                ],
                borderWidth: 1
            }]
        }, {
            plugins: {
                title: {
                    display: true,
                    text: 'Comment Sentiment Distribution',
                    font: { size: 16 }
                },
                legend: {
                    position: 'bottom'
                }
            }
        });
    };

    const updateLineChart = (videoSentiments) => {
        if (!videoSentiments || !videoSentiments.length) return;

        const labels = videoSentiments.map(v => v.video_title.substring(0, 20) + '...');
        const datasets = [
            {
                label: 'Positive',
                data: videoSentiments.map(v => v.Positive),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true
            },
            {
                label: 'Negative',
                data: videoSentiments.map(v => v.Negative),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: true
            },
            {
                label: 'Neutral',
                data: videoSentiments.map(v => v.Neutral),
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                fill: true
            }
        ];

        createChart("lineChart", "line", { labels, datasets }, {
            plugins: {
                title: {
                    display: true,
                    text: 'Sentiment Trends Across Videos',
                    font: { size: 16 }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Comments'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        });
    };

    const updateHeatmapChart = (hourlyData) => {
        if (!hourlyData) return;
        const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        const heatmapData = [];
    
        for (let day = 0; day < 7; day++) {
            for (let hour = 0; hour < 24; hour++) {
                const key = day + '-' + hour;
                heatmapData.push({ x: hour, y: day, v: hourlyData[key] || 0 });
            }
        }
    
        createChart("heatmapChart", "matrix", {
            datasets: [{
                label: "Sentiment Intensity",
                data: heatmapData,
                backgroundColor: ctx => {
                    const value = ctx.dataset.data[ctx.dataIndex].v;
                    return `rgba(255, 0, 0, ${Math.min(value / 10, 1)})`;
                },
                borderWidth: 1,
                width: 20,
                height: 20
            }]
        }, {
            plugins: {
                title: {
                    display: true,
                    text: "Hourly Sentiment Heatmap",
                    font: { size: 16 }
                },
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => `Sentiment Score: ${ctx.dataset.data[ctx.dataIndex].v}`
                    }
                }
            },
            scales: {
                x: { type: "linear", position: "bottom", ticks: { callback: val => val + ":00" } },
                y: { type: "linear", ticks: { callback: (val) => days[val] } }
            }
        });
    };
    


    const updatePerformanceChart = (predictions) => {
        if (!predictions) return;

        const labels = Object.keys(predictions);
        const values = Object.values(predictions);

        createChart("performanceChart", "bar", {
            labels: labels.map(l => l.substring(0, 20) + '...'),
            datasets: [{
                label: 'Predicted Views',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        }, {
            plugins: {
                title: {
                    display: true,
                    text: 'Predicted Video Performance',
                    font: { size: 16 }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Predicted Views'
                    },
                    ticks: {
                        callback: (value) => {
                            if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
                            if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
                            return value;
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        });
    };

    return (
        <React.Fragment>
            <NavBar />
            <div className="loading-overlay" style={{ display: loading ? 'flex' : 'none' }}>
                <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }}></div>
            </div>

            <div className="container">
                <h2>YouTube Sentiment Analysis</h2>
                <div className="input-group">
                    <input 
                        type="text" 
                        placeholder="Enter Channel Name" 
                        value={channel} 
                        onChange={(e) => setChannel(e.target.value)} 
                    />
                    <button onClick={fetchSentiment}>Analyze</button>
                    <button className="view-report" onClick={handleViewReport}>📄 View Report</button>
                </div>

                {error && <p className="error-message">{error}</p>}

                {showCharts && (
                    <>
                        <div className="charts-container">
                            <div className="chart-box"><canvas id="sentimentChart"></canvas></div>
                            <div className="chart-box"><canvas id="lineChart"></canvas></div>
                            <div className="chart-box"><canvas id="heatmapChart"></canvas></div>
                            <div className="chart-box"><canvas id="performanceChart"></canvas></div>
                        </div>
                        <div className="highlight">
                            🚀 Best Time to Post: <span className="best-time">{bestTime}</span>
                        </div>
                        <button 
                            className="view-report" 
                            onClick={() => setShowCentralities(!showCentralities)}
                        >
                            {showCentralities ? 'Hide Centralities' : 'View Centralities'}
                        </button>
                    </>
                )}

                {showCentralities && (
                    <div className="centrality-table">
                        <h3>Centrality Metrics</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Video Title</th>
                                    <th>Degree Centrality</th>
                                    <th>Betweenness Centrality</th>
                                    <th>Closeness Centrality</th>
                                </tr>
                            </thead>
                            <tbody>
                                {videos.map((video, index) => (
                                    <tr key={index}>
                                        <td>{video.video_title}</td>
                                        <td>{video.degree}</td>
                                        <td>{video.betweenness}</td>
                                        <td>{video.closeness}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style jsx>{`
                .container {
                    max-width: 1200px;
                    margin: auto;
                    padding: 30px;
                }
                .input-group {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 25px;
                    gap: 15px;
                    flex-wrap: wrap;
                }
                .input-group input {
                    padding: 12px 20px;
                    width: 1000px;
                    border: 2px solid #007bff;
                    border-radius: 8px;
                    font-size: 1.1em;
                    transition: all 0.3s ease;
                }
                .input-group input:focus {
                    outline: none;
                    box-shadow: 0 0 8px rgba(0,123,255,0.3);
                }
                .input-group button {
                    padding: 0px 30px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 1.1em;
                    transition: transform 0.2s, background-color 0.3s;
                }
                .input-group button:hover {
                    transform: scale(1.05);
                    background-color: #0056b3;
                }
                .input-group .view-report {
                    background-color: #28a745;
                }
                .input-group .view-report:hover {
                    background-color: #1e7e34;
                }
                .charts-container {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 40px;
                    margin-top: 0px;
                }
                .chart-box {
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    min-height: 500px;
                    position: relative;
                }
                .chart-box canvas {
                    width: 100% !important;
                    height: 100% !important;
                    min-height: 450px;
                }
                .highlight {
                    text-align: center;
                    margin: 40px 0;
                    padding: 25px;
                    font-size: 1.8em;
                    background: linear-gradient(135deg, #e8f4ff, #cce5ff);
                    color: #004085;
                    border-radius: 12px;
                    border: 2px solid #007bff;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    animation: pulse 2s infinite;
                }
                .best-time {
                    font-weight: 700;
                    color: #007bff;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                    100% { transform: scale(1); }
                }
                .view-report {
                    display: block;
                    margin: 30px auto;
                    padding: 15px 35px;
                    font-size: 1.1em;
                }
                .centrality-table {
                    margin-top: 40px;
                    overflow-x: auto;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                th, td {
                    padding: 15px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: 600;
                }
                tr:hover {
                    background-color: #f8f9fa;
                }
                .error-message {
                    color: #dc3545;
                    text-align: center;
                    margin: 20px 0;
                    font-size: 1.1em;
                    font-weight: 500;
                }
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(255, 255, 255, 0.9);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                    backdrop-filter: blur(3px);
                }
                @media (max-width: 1200px) {
                    .charts-container {
                        grid-template-columns: 1fr;
                    }
                    .chart-box {
                        min-height: 400px;
                    }
                    .container {
                        padding: 20px;
                    }
                }
            `}</style>
        </React.Fragment>
    );
};

export default YouTubeSentiment;