import React, { useState } from 'react';

function Analysis() {
  const [username, setUsername] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = () => {
    setIsLoading(true);
    // Simulate API call with a delay
    setTimeout(() => {
      const mockAnalysis = {
        followers: 12000,
        posts: 345,
        engagementRate: '4.5%',
      };
      setAnalysis(mockAnalysis);
      setIsLoading(false);
    }, 2000); // 2-second delay to simulate loading
  };

  const styles = {
    container: {
      textAlign: 'center',
      padding: '20px',
      backgroundColor: '#fff3e0', // Light orange background
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
    },
    input: {
      padding: '15px',
      width: '300px',
      marginRight: '10px',
      border: '1px solid #ccc',
      borderRadius: '50px',
      fontSize: '1rem',
      outline: 'none',
      transition: 'border-color 0.3s ease',
    },
    inputFocus: {
      borderColor: '#007bff',
    },
    button: {
      padding: '15px 30px',
      backgroundColor: '#007bff',
      color: 'white',
      border: 'none',
      borderRadius: '50px',
      cursor: 'pointer',
      fontSize: '1rem',
      transition: 'background-color 0.3s ease, transform 0.3s ease',
    },
    buttonHover: {
      backgroundColor: '#0056b3',
      transform: 'scale(1.1)',
    },
    results: {
      marginTop: '20px',
      padding: '20px',
      border: '1px solid #ccc',
      borderRadius: '20px',
      backgroundColor: '#f9f9f9',
      display: 'inline-block',
      animation: 'slideIn 1s ease-in-out',
    },
    loadingSpinner: {
      border: '4px solid #f3f3f3',
      borderTop: '4px solid #007bff',
      borderRadius: '50%',
      width: '40px',
      height: '40px',
      animation: 'spin 1s linear infinite',
      margin: '20px auto',
    },
  };

  const handleMouseOver = (e) => {
    e.target.style.backgroundColor = styles.buttonHover.backgroundColor;
    e.target.style.transform = styles.buttonHover.transform;
  };

  const handleMouseOut = (e) => {
    e.target.style.backgroundColor = styles.button.backgroundColor;
    e.target.style.transform = 'scale(1)';
  };

  const handleInputFocus = (e) => {
    e.target.style.borderColor = styles.inputFocus.borderColor;
  };

  const handleInputBlur = (e) => {
    e.target.style.borderColor = '#ccc';
  };

  return (
    <div style={styles.container}>
      <h1>Social Media Analysis</h1>
      <div>
        <input
          type="text"
          placeholder="Enter social media handle"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
        />
        <button
          onClick={handleAnalyze}
          style={styles.button}
          onMouseOver={handleMouseOver}
          onMouseOut={handleMouseOut}
        >
          Analyze
        </button>
      </div>

      {isLoading && <div style={styles.loadingSpinner}></div>}

      {analysis && (
        <div style={styles.results}>
          <h2>Analysis Results</h2>
          <p><strong>Followers:</strong> {analysis.followers}</p>
          <p><strong>Posts:</strong> {analysis.posts}</p>
          <p><strong>Engagement Rate:</strong> {analysis.engagementRate}</p>
        </div>
      )}

      <button
        style={{ ...styles.button, marginTop: '20px' }}
        onClick={() => (window.location.href = '/')}
      >
        Go Back to Home
      </button>
    </div>
  );
}

export default Analysis;