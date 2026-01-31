// src/App.jsx
import React, { useState } from 'react';
import './App.css';

function App() {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [templates, setTemplates] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/build', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🤖 Rahl - AI APK Builder</h1>
        <p>Describe your app in natural language. Get an APK in minutes.</p>
      </header>

      <div className="main-content">
        <div className="input-section">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your app idea... 
            Example: 'I want a simple calculator app with dark mode'
            Example: 'Create a webview app for my website https://example.com'
            Example: 'Build a todo list app with notifications'"
            rows="6"
          />
          
          <button 
            onClick={handleSubmit} 
            disabled={loading || !description}
            className="build-btn"
          >
            {loading ? 'Building...' : 'Build APK'}
          </button>
        </div>

        {result && (
          <div className="result-section">
            <h3>🎉 Your APK is ready!</h3>
            <div className="apk-info">
              <p>Project ID: {result.project_id}</p>
              <a 
                href={`http://localhost:5000/download/${result.project_id}`}
                className="download-btn"
              >
                Download APK
              </a>
            </div>
          </div>
        )}

        <div className="examples">
          <h3>💡 Examples you can try:</h3>
          <div className="example-cards">
            <div className="example-card">
              <h4>WebView App</h4>
              <p>"Create an app that shows my website https://myblog.com"</p>
            </div>
            <div className="example-card">
              <h4>Calculator</h4>
              <p>"Build a calculator with basic operations and dark theme"</p>
            </div>
            <div className="example-card">
              <h4>Notes App</h4>
              <p>"Make a simple notes app with save and delete features"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
