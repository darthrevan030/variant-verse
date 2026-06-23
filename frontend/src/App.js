import React, { useState } from 'react';
import './App.css';

function App() {
  const [geneName, setGeneName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleClick = async () => {
    console.log('Button clicked, gene name:', geneName); // Debug log
    
    try {
      setLoading(true);
      setError('');

      const response = await fetch('http://localhost:8001/api/variants/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ geneName }),
      });

      console.log('Response:', response); // Debug log

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Data:', data); // Debug log
      
      alert('Success! Check console for details');

    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>The Variant-Verse</h1>
      <h2>Process, Analyse and Classify Variants of Any Gene</h2>

      <div className="search-section">
        <label>Gene Name</label>
        <input
          type="text"
          value={geneName}
          onChange={(e) => setGeneName(e.target.value)}
          placeholder="Enter gene name..."
        />

        <button 
          onClick={handleClick}
          disabled={loading}
          style={{ 
            padding: '10px 20px', 
            marginTop: '20px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Processing...' : 'Find Variants in the Gene-Verse'}
        </button>

        {error && (
          <div style={{ color: 'red', marginTop: '10px' }}>
            Error: {error}
          </div>
        )}

        <div style={{ marginTop: '10px' }}>
          Examples: cfh, mc4r, brca1
        </div>
      </div>
    </div>
  );
}

export default App;