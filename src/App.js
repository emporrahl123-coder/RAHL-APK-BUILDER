import React, { useState } from 'react';
import './App.css';
import { FaRobot, FaDownload, FaLightbulb, FaCode, FaAndroid, FaMagic } from 'react-icons/fa';

function App() {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [examples] = useState([
    {
      text: "Create a calculator app with dark mode and history feature",
      icon: <FaCode />,
      color: "#4CAF50"
    },
    {
      text: "Build a webview app for my blog at https://myblog.com",
      icon: <FaAndroid />,
      color: "#2196F3"
    },
    {
      text: "Make a todo list app with notifications and categories",
      icon: <FaMagic />,
      color: "#9C27B0"
    },
    {
      text: "Generate a simple game app like tic-tac-toe",
      icon: <FaLightbulb />,
      color: "#FF9800"
    }
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      // Call our backend API
      const response = await fetch('http://localhost:5000/api/build', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: description })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({
        status: 'error',
        message: 'Failed to connect to server. Make sure backend is running on port 5000.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleText) => {
    setDescription(exampleText);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <FaRobot className="header-icon" />
          <h1>Rahl AI</h1>
          <span className="tagline">Natural Language to APK Builder</span>
        </div>
        <p className="header-subtitle">
          Describe your app idea in plain English. Get a fully functional Android APK in minutes.
        </p>
      </header>

      <main className="main-container">
        {/* Input Section */}
        <div className="input-section">
          <div className="input-header">
            <h2><FaMagic /> Describe Your App</h2>
            <p>Be as detailed or as simple as you want</p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <textarea
              className="description-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Example: I want a calculator app with dark theme, memory functions, and a modern UI..."
              rows={6}
              disabled={loading}
            />
            
            <div className="char-count">
              {description.length} characters
            </div>
            
            <button 
              type="submit" 
              className="build-button"
              disabled={loading || !description.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Building Your APK...
                </>
              ) : (
                <>
                  <FaAndroid /> Build APK
                </>
              )}
            </button>
          </form>
        </div>

        {/* Examples Section */}
        <div className="examples-section">
          <h3><FaLightbulb /> Example Ideas</h3>
          <p>Try these examples or create your own:</p>
          
          <div className="examples-grid">
            {examples.map((example, index) => (
              <div 
                key={index}
                className="example-card"
                onClick={() => handleExampleClick(example.text)}
                style={{ borderLeftColor: example.color }}
              >
                <div className="example-icon" style={{ color: example.color }}>
                  {example.icon}
                </div>
                <p>{example.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Results Section */}
        {result && (
          <div className={`result-section ${result.status === 'error' ? 'error' : 'success'}`}>
            {result.status === 'error' ? (
              <>
                <h3>❌ Something Went Wrong</h3>
                <p>{result.message}</p>
                <button 
                  className="retry-button"
                  onClick={() => setResult(null)}
                >
                  Try Again
                </button>
              </>
            ) : (
              <>
                <h3>🎉 Your APK is Ready!</h3>
                <div className="result-details">
                  <div className="detail-item">
                    <strong>App Type:</strong>
                    <span className="badge">{result.app_type}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Project ID:</strong>
                    <code>{result.project_id}</code>
                  </div>
                  <div className="detail-item">
                    <strong>Status:</strong>
                    <span className="status-success">✓ Success</span>
                  </div>
                </div>
                
                <a 
                  href={`http://localhost:5000${result.download_url}`}
                  className="download-button"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FaDownload /> Download APK File
                </a>
                
                <div className="build-info">
                  <p>Your APK file is ready for installation on Android devices.</p>
                  <p className="note">
                    <small>
                      Note: This is a demo version. Real APK generation requires Android SDK setup.
                    </small>
                  </p>
                </div>
              </>
            )}
          </div>
        )}

        {/* Features Section */}
        <div className="features-section">
          <h3>✨ How Rahl Works</h3>
          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">1</div>
              <h4>Describe Your Idea</h4>
              <p>Use natural language to explain what you want your app to do.</p>
            </div>
            <div className="feature">
              <div className="feature-icon">2</div>
              <h4>AI Analysis</h4>
              <p>Our AI understands your requirements and selects the right template.</p>
            </div>
            <div className="feature">
              <div className="feature-icon">3</div>
              <h4>Code Generation</h4>
              <p>We generate Android code with all the features you requested.</p>
            </div>
            <div className="feature">
              <div className="feature-icon">4</div>
              <h4>Build & Download</h4>
              <p>Get your APK file ready for installation on any Android device.</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <FaRobot /> Rahl AI Builder
          </div>
          <p className="footer-text">
            Transform your ideas into Android apps instantly. No coding required.
          </p>
          <div className="footer-links">
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
            <a href="#contact">Contact</a>
            <a href="#github">GitHub</a>
          </div>
          <p className="copyright">
            © 2024 Rahl AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
