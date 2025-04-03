import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';

const CategoryButton = styled(Button)(({ theme, active }) => ({
  backgroundColor: active ? '#2A7BA8' : 'rgba(42, 123, 168, 0.1)',
  color: active ? '#fff' : '#2A7BA8',
  padding: '12px 24px',
  margin: '8px',
  borderRadius: '25px',
  fontWeight: 'bold',
  transition: 'all 0.3s ease',
  '&:hover': {
    backgroundColor: active ? '#3991C4' : 'rgba(42, 123, 168, 0.2)',
    transform: 'translateY(-2px)',
  },
}));

const ChannelCard = styled(Card)({
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  color: '#2C3E50',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 8px 20px rgba(0, 0, 0, 0.2)',
  },
});

const StyledButton = styled(Button)({
  backgroundColor: '#2A7BA8',
  color: '#fff',
  '&:hover': {
    backgroundColor: '#3991C4',
  },
});

const CATEGORIES = [
  { id: "1", name: "Film & Animation" },
  { id: "2", name: "Autos & Vehicles" },
  { id: "10", name: "Music" },
  { id: "15", name: "Pets & Animals" },
  { id: "17", name: "Sports" },
  { id: "20", name: "Gaming" },
  { id: "22", name: "People & Blogs" },
  { id: "23", name: "Comedy" },
  { id: "24", name: "Entertainment" },
  { id: "25", name: "News & Politics" },
  { id: "26", name: "How-to & Style" },
  { id: "27", name: "Education" },
  { id: "28", name: "Science & Technology" }
];

const Recommendations = () => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);

  // Check if backend is running
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/ping');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'ok') {
            setBackendStatus('connected');
            setError(null);
          } else {
            setBackendStatus('error');
            setError('Backend server is not responding correctly');
          }
        } else {
          throw new Error(`Server returned ${response.status}`);
        }
      } catch (err) {
        console.error('Backend connection error:', err);
        setBackendStatus('error');
        setError('Cannot connect to backend server. Please make sure it is running on http://127.0.0.1:5000');
      }
    };

    checkBackendStatus();
    // Check connection every 30 seconds
    const intervalId = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const handleCategoryClick = async (categoryId) => {
    if (backendStatus !== 'connected') {
      setError('Cannot fetch recommendations: Backend server is not connected');
      return;
    }

    setSelectedCategory(categoryId);
    setLoading(true);
    setError(null);

    try {
      console.log('Fetching recommendations for category:', categoryId);
      const response = await fetch('http://127.0.0.1:5000/recommendations/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ categories: [categoryId] }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data:', data);

      if (data.success) {
        if (data.results && data.results.length > 0) {
          console.log(`Found ${data.results.length} channels`);
          setChannels(data.results);
          setError(null);
        } else {
          console.log('No channels found in the response');
          setChannels([]);
          setError('No channels found for this category. Please try another category.');
        }
      } else {
        throw new Error(data.error || 'Failed to fetch channels');
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message || 'Failed to fetch recommendations. Please try again.');
      setChannels([]);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  if (backendStatus === 'checking') {
    return (
      <Box sx={{ 
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        gap: 2
      }}>
        <CircularProgress />
        <Typography>
          Connecting to backend server...
        </Typography>
      </Box>
    );
  }

  if (backendStatus === 'error') {
    return (
      <Box sx={{ 
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        p: 3
      }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => window.location.reload()}
          sx={{ mt: 2 }}
        >
          Retry Connection
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #FFFFFF 0%, #F5F8FA 100%)',
      color: '#2C3E50',
      pt: 4,
      pb: 8
    }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Typography 
          variant="h2" 
          align="center" 
          sx={{ 
            color: '#2A7BA8',
            fontWeight: 'bold',
            mb: 2
          }}
        >
          YouTube Channel Recommendations
        </Typography>
        <Typography 
          variant="h6" 
          align="center" 
          sx={{ 
            color: '#5A6B7B',
            mb: 6,
            maxWidth: '800px',
            mx: 'auto'
          }}
        >
          Discover and analyze top YouTube channels across different categories
        </Typography>

        {/* Categories */}
        <Box sx={{ mb: 6 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#2A7BA8',
              mb: 3,
              fontWeight: 'bold',
              textAlign: 'center'
            }}
          >
            Content Categories
          </Typography>
          <Container maxWidth="lg">
            <Box 
              sx={{ 
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1,
                justifyContent: 'center',
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '20px'
              }}
            >
              {CATEGORIES.map((category) => (
                <CategoryButton
                  key={category.id}
                  active={selectedCategory === category.id}
                  onClick={() => handleCategoryClick(category.id)}
                  sx={{
                    minWidth: '180px',
                    textAlign: 'center'
                  }}
                >
                  {category.name}
                </CategoryButton>
              ))}
            </Box>
          </Container>
        </Box>

        {/* Content */}
        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress sx={{ color: '#2A7BA8' }} />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        ) : channels.length > 0 ? (
          <>
            <Typography 
              variant="h5" 
              sx={{ 
                color: '#2A7BA8',
                mb: 4,
                fontWeight: 'bold'
              }}
            >
              Channel Analytics
            </Typography>
            <Grid container spacing={3}>
              {channels.map((channel) => (
                <Grid item xs={12} md={6} lg={4} key={channel.channel_id}>
                  <ChannelCard>
                    <CardMedia
                      component="img"
                      height="180"
                      image={channel.thumbnails?.high?.url || channel.thumbnails?.medium?.url || channel.thumbnails?.default?.url || '/default-channel.png'}
                      alt={channel.channel_name}
                      onError={(e) => {
                        e.target.src = '/default-channel.png';
                      }}
                    />
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ color: '#2C3E50', fontWeight: 'bold' }}>
                        {channel.channel_name}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#5A6B7B',
                          mb: 2,
                          height: '3em',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {channel.description}
                      </Typography>
                      <Stack spacing={1}>
                        <Typography variant="body2" sx={{ color: '#5A6B7B' }}>
                          👥 {formatNumber(channel.subscriber_count)} subscribers
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#5A6B7B' }}>
                          🎥 {formatNumber(channel.video_count)} videos
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#5A6B7B' }}>
                          👁 {formatNumber(channel.view_count)} views
                        </Typography>
                      </Stack>
                    </CardContent>
                    <CardActions sx={{ mt: 'auto', p: 2 }}>
                      <StyledButton
                        fullWidth
                        variant="contained"
                        href={`https://www.youtube.com/channel/${channel.channel_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Visit Channel
                      </StyledButton>
                    </CardActions>
                  </ChannelCard>
                </Grid>
              ))}
            </Grid>
          </>
        ) : selectedCategory ? (
          <Alert severity="info">
            No channels found for this category. Please try another category.
          </Alert>
        ) : (
          <Typography 
            align="center" 
            sx={{ 
              color: '#5A6B7B',
              mt: 4
            }}
          >
            Select a category to see channel recommendations
          </Typography>
        )}
      </Container>
    </Box>
  );
};

export default Recommendations;