import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { Toaster } from 'react-hot-toast';

// Components
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Projects from './components/Projects';
import Revenue from './components/Revenue';
import AI from './components/AI';
import Ethics from './components/Ethics';
import Performance from './components/Performance';
import LogViewer from './components/LogViewer';

// Context
import { MetricsProvider } from './context/MetricsContext';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configure axios defaults
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = 10000;

// Add request interceptor for loading states
axios.interceptors.request.use(
  (config) => {
    // Add loading indicator
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if backend is available
    const checkBackendHealth = async () => {
      try {
        await axios.get('/health');
        setIsLoading(false);
      } catch (err) {
        console.warn('Backend not available:', err.message);
        setError('Backend connection failed. Some features may not work.');
        setIsLoading(false);
      }
    };

    checkBackendHealth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-gradient flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-empire-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-white mb-2">CK Empire Builder</h2>
          <p className="text-dark-300">Initializing your digital empire...</p>
        </div>
      </div>
    );
  }

  return (
    <MetricsProvider>
      <Router>
        <div className="flex h-screen bg-dark-900">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <main className="flex-1 overflow-y-auto bg-dark-900">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/revenue" element={<Revenue />} />
                <Route path="/ai" element={<AI />} />
                <Route path="/ethics" element={<Ethics />} />
                <Route path="/performance" element={<Performance />} />
                <Route path="/logs" element={<LogViewer />} />
              </Routes>
            </main>
          </div>
        </div>
        
        {/* Global toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1e293b',
              color: '#f8fafc',
              border: '1px solid #475569',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#f8fafc',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f8fafc',
              },
            },
          }}
        />
        
        {/* Error banner */}
        {error && (
          <div className="fixed top-0 left-0 right-0 bg-red-900/90 text-white p-4 z-50">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-white hover:text-red-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </Router>
    </MetricsProvider>
  );
}

export default App; 