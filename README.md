# YouTube Channel Sentiment Analysis

This project analyzes YouTube channel content using sentiment analysis and network analysis techniques. It provides insights into video performance, engagement metrics, and sentiment patterns.

## Features

- YouTube channel data fetching and analysis
- Sentiment analysis of video comments
- Network analysis with centrality metrics
- Performance prediction using machine learning
- Interactive visualizations
- Channel search functionality

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- MongoDB running locally
- YouTube Data API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Set up your YouTube API key:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API key)
   - Replace `YOUR_API_KEY_HERE` in `src/sentiment.py` with your actual API key

5. Start MongoDB:
```bash
mongod
```

## Running the Application

1. Start the Flask backend:
```bash
python src/app.py
```

2. Start the React frontend:
```bash
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Enter a YouTube channel name in the search box
2. Click "Analyze" to start the analysis
3. View the results including:
   - Sentiment distribution
   - Video performance metrics
   - Network analysis results
   - Engagement predictions

## Project Structure

```
├── src/
│   ├── components/
│   │   ├── SentimentAnalysis.js
│   │   ├── SentimentChart.js
│   │   ├── SentimentTable.js
│   │   ├── SentimentGraph.js
│   │   ├── SentimentTimeline.js
│   │   ├── SentimentMetrics.js
│   │   └── SentimentPredictions.js
│   ├── sentiment.py
│   └── app.py
├── graphs/
├── requirements.txt
└── README.md
```

## API Endpoints

- `GET /sentiment/analyze_sentiment?channel=<channel_name>`: Analyze channel sentiment
- `GET /sentiment/search_channels?query=<search_query>`: Search for YouTube channels
- `GET /sentiment/graph/sentiment`: Get sentiment analysis graph

## Error Handling

The application includes comprehensive error handling for:
- Invalid channel names
- API rate limits
- Network issues
- Data processing errors

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
