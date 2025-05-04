const express = require("express");
const cors = require("cors");
const Sentiment = require("sentiment");

const app = express();
const port = 5000;
const sentiment = new Sentiment();

app.use(cors());
app.use(express.json());

// Dummy function to simulate fetching YouTube comments
const fetchYouTubeComments = (channelName) => {
  return [
    "This video is amazing!",
    "I hate this content.",
    "Not bad, could be better.",
    "Great work! Keep it up.",
    "Terrible video, very disappointing.",
    "Loved this content, very informative!",
    "This is okay, nothing special."
  ];
};

// Process sentiment analysis
const analyzeSentiments = (comments) => {
  let positive = 0, neutral = 0, negative = 0;
  let hourlySentiment = {};
  let engagementMetrics = {
    likes: Math.floor(Math.random() * 1000),
    comments: comments.length,
    shares: Math.floor(Math.random() * 500),
  };

  comments.forEach((comment, index) => {
    let result = sentiment.analyze(comment);
    if (result.score > 0) positive++;
    else if (result.score < 0) negative++;
    else neutral++;

    // Simulate hourly sentiment values
    let hour = index % 24;
    hourlySentiment[hour] = (hourlySentiment[hour] || 0) + result.score;
  });

  let total = positive + neutral + negative;
  return {
    percentages: {
      Positive: ((positive / total) * 100).toFixed(2),
      Neutral: ((neutral / total) * 100).toFixed(2),
      Negative: ((negative / total) * 100).toFixed(2),
    },
    hourly_sentiment: hourlySentiment,
    engagement_metrics: engagementMetrics,
    best_time: "6:00 PM - 8:00 PM"
  };
};

// API Endpoint for Sentiment Analysis
app.get("/analyze_sentiment", (req, res) => {
  const channel = req.query.channel;
  if (!channel) {
    return res.status(400).json({ error: "Channel name is required." });
  }

  const comments = fetchYouTubeComments(channel);
  const sentimentData = analyzeSentiments(comments);

  res.json(sentimentData);
});

// Start the server
app.listen(port, () => {
  console.log(`Sentiment Analysis server running on http://localhost:${port}`);
});
