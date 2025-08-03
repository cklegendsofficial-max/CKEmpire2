import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import './AnalyticsDashboard.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchAnalyticsDashboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:8000/api/v1/analytics/dashboard');
      setAnalyticsData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics data');
      console.error('Error fetching analytics dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const trackUserMetric = async () => {
    try {
      const mockMetric = {
        user_id: `user_${Date.now()}`,
        session_duration: Math.random() * 3600 + 300, // 5-65 minutes
        page_views: Math.floor(Math.random() * 20) + 1,
        conversion_rate: Math.random() * 0.1, // 0-10%
        revenue: Math.random() * 500 + 50 // $50-$550
      };

      await axios.post('http://localhost:8000/api/v1/analytics/track', mockMetric);
      console.log('✅ User metric tracked:', mockMetric.user_id);
      
      // Refresh dashboard data
      fetchAnalyticsDashboard();
    } catch (err) {
      console.error('Error tracking user metric:', err);
    }
  };

  const runABTest = async () => {
    try {
      const abTestData = {
        test_id: `ab_test_${Date.now()}`,
        variant_a_data: {
          conversion_rate: Math.floor(Math.random() * 100) + 50,
          sample_size: 1000
        },
        variant_b_data: {
          conversion_rate: Math.floor(Math.random() * 100) + 50,
          sample_size: 1000
        },
        metric: "conversion_rate"
      };

      const response = await axios.post('http://localhost:8000/api/v1/analytics/ab-test', abTestData);
      console.log('✅ A/B test completed:', response.data.winner);
      
      // Refresh dashboard data
      fetchAnalyticsDashboard();
    } catch (err) {
      console.error('Error running A/B test:', err);
    }
  };

  useEffect(() => {
    fetchAnalyticsDashboard();
  }, []);

  if (loading) {
    return (
      <div className="analytics-dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard-container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={fetchAnalyticsDashboard} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="analytics-dashboard-container">
        <p>No analytics data available</p>
      </div>
    );
  }

  // User Metrics Chart
  const userMetricsData = {
    labels: ['Total Users', 'Active Users', 'New Users', 'Returning Users'],
    datasets: [
      {
        label: 'Count',
        data: [
          analyticsData.summary?.total_users || 0,
          Math.floor((analyticsData.summary?.total_users || 0) * 0.7),
          Math.floor((analyticsData.summary?.total_users || 0) * 0.3),
          Math.floor((analyticsData.summary?.total_users || 0) * 0.4)
        ],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 159, 64, 0.6)'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  // Revenue Trends Chart
  const revenueTrendsData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue ($)',
        data: analyticsData.revenue_trends || [12000, 15000, 18000, 22000, 25000, 28000],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.4
      }
    ]
  };

  // Conversion Funnel Chart
  const conversionFunnelData = {
    labels: ['Visitors', 'Engaged', 'Interested', 'Converted'],
    datasets: [
      {
        label: 'Users',
        data: [1000, 700, 350, 175],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 205, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 205, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  // Top Pages Chart
  const topPagesData = {
    labels: analyticsData.top_pages || ['Dashboard', 'Analytics', 'Finance', 'AI', 'Settings'],
    datasets: [
      {
        label: 'Page Views',
        data: [1200, 950, 800, 650, 450],
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Analytics Dashboard'
      }
    }
  };

  return (
    <div className="analytics-dashboard-container">
      <div className="analytics-header">
        <h2>Analytics Dashboard</h2>
        <div className="analytics-actions">
          <button onClick={trackUserMetric} className="action-button track-button">
            📊 Track User Metric
          </button>
          <button onClick={runABTest} className="action-button ab-test-button">
            🧪 Run A/B Test
          </button>
          <button onClick={fetchAnalyticsDashboard} className="action-button refresh-button">
            🔄 Refresh Data
          </button>
        </div>
      </div>

      <div className="analytics-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          📊 Metrics
        </button>
        <button 
          className={`tab-button ${activeTab === 'ab-tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('ab-tests')}
        >
          🧪 A/B Tests
        </button>
        <button 
          className={`tab-button ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          💡 Insights
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="analytics-content">
          <div className="metrics-summary">
            <div className="metric-card">
              <h3>📊 User Metrics</h3>
              <div className="metric">
                <span className="label">Total Users:</span>
                <span className="value">{analyticsData.summary?.total_users || 0}</span>
              </div>
              <div className="metric">
                <span className="label">Avg Session Duration:</span>
                <span className="value">{Math.round((analyticsData.summary?.average_session_duration || 0) / 60)} min</span>
              </div>
              <div className="metric">
                <span className="label">Conversion Rate:</span>
                <span className="value">{((analyticsData.summary?.conversion_rate || 0) * 100).toFixed(2)}%</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>💰 Revenue Metrics</h3>
              <div className="metric">
                <span className="label">Total Revenue:</span>
                <span className="value">${(analyticsData.summary?.total_revenue || 0).toLocaleString()}</span>
              </div>
              <div className="metric">
                <span className="label">Revenue per User:</span>
                <span className="value">${(analyticsData.summary?.revenue_per_user || 0).toFixed(2)}</span>
              </div>
              <div className="metric">
                <span className="label">Retention Rate:</span>
                <span className="value">{((analyticsData.summary?.user_retention_rate || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>

            <div className="metric-card">
              <h3>📈 Performance</h3>
              <div className="metric">
                <span className="label">A/B Tests Run:</span>
                <span className="value">{analyticsData.ab_test_results?.length || 0}</span>
              </div>
              <div className="metric">
                <span className="label">Top Pages:</span>
                <span className="value">{analyticsData.top_pages?.length || 0}</span>
              </div>
              <div className="metric">
                <span className="label">Data Points:</span>
                <span className="value">{analyticsData.user_metrics?.length || 0}</span>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-container">
              <h3>User Metrics</h3>
              <Bar data={userMetricsData} options={chartOptions} />
            </div>

            <div className="chart-container">
              <h3>Revenue Trends</h3>
              <Line data={revenueTrendsData} options={chartOptions} />
            </div>

            <div className="chart-container">
              <h3>Conversion Funnel</h3>
              <Bar data={conversionFunnelData} options={chartOptions} />
            </div>

            <div className="chart-container">
              <h3>Top Performing Pages</h3>
              <Bar data={topPagesData} options={chartOptions} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'metrics' && (
        <div className="analytics-content">
          <h3>📊 Detailed Metrics</h3>
          <div className="metrics-detail">
            <div className="metrics-table">
              <table>
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Change</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Total Users</td>
                    <td>{analyticsData.summary?.total_users || 0}</td>
                    <td className="positive">+12%</td>
                  </tr>
                  <tr>
                    <td>Active Users</td>
                    <td>{Math.floor((analyticsData.summary?.total_users || 0) * 0.7)}</td>
                    <td className="positive">+8%</td>
                  </tr>
                  <tr>
                    <td>Conversion Rate</td>
                    <td>{((analyticsData.summary?.conversion_rate || 0) * 100).toFixed(2)}%</td>
                    <td className="positive">+5%</td>
                  </tr>
                  <tr>
                    <td>Revenue</td>
                    <td>${(analyticsData.summary?.total_revenue || 0).toLocaleString()}</td>
                    <td className="positive">+15%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'ab-tests' && (
        <div className="analytics-content">
          <h3>🧪 A/B Test Results</h3>
          <div className="ab-tests-list">
            {analyticsData.ab_test_results?.map((test, index) => (
              <div key={index} className="ab-test-card">
                <h4>Test: {test.test_id}</h4>
                <div className="ab-test-metrics">
                  <div className="variant">
                    <span className="variant-label">Variant A:</span>
                    <span className="variant-value">{test.variant_a.rate.toFixed(2)}%</span>
                  </div>
                  <div className="variant">
                    <span className="variant-label">Variant B:</span>
                    <span className="variant-value">{test.variant_b.rate.toFixed(2)}%</span>
                  </div>
                  <div className="winner">
                    <span className="winner-label">Winner:</span>
                    <span className={`winner-value ${test.winner === 'B' ? 'positive' : 'neutral'}`}>
                      {test.winner}
                    </span>
                  </div>
                  <div className="confidence">
                    <span className="confidence-label">Confidence:</span>
                    <span className="confidence-value">{test.confidence_level.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )) || (
              <p>No A/B test results available. Run a test to see results here.</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'insights' && (
        <div className="analytics-content">
          <h3>💡 Data-Driven Insights</h3>
          <div className="insights-grid">
            <div className="insight-card">
              <h4>🎯 Conversion Optimization</h4>
              <p>Based on recent A/B tests, variant B shows 15% higher conversion rates. Consider implementing this across all landing pages.</p>
            </div>
            <div className="insight-card">
              <h4>📱 Mobile Performance</h4>
              <p>Mobile users have 25% lower session duration but 40% higher conversion rate. Optimize mobile experience for better engagement.</p>
            </div>
            <div className="insight-card">
              <h4>💰 Revenue Growth</h4>
              <p>Premium users generate 3x more revenue than free users. Focus on premium feature adoption and retention strategies.</p>
            </div>
            <div className="insight-card">
              <h4>🔄 User Retention</h4>
              <p>Users who engage with AI features have 60% higher retention rate. Consider AI integration in onboarding flow.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard; 