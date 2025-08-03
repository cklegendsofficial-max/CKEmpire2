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
import './ROIGraph.css';

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

const ROIGraph = () => {
  const [financialData, setFinancialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [targetAmount, setTargetAmount] = useState(20000);
  const [initialInvestment, setInitialInvestment] = useState(6000);

  const fetchFinancialReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/finance/report', {
        target_amount: targetAmount,
        initial_investment: initialInvestment
      });
      
      setFinancialData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch financial data');
      console.error('Error fetching financial report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinancialReport();
  }, []);

  const handleCalculateROI = () => {
    fetchFinancialReport();
  };

  if (loading) {
    return (
      <div className="roi-graph-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Calculating financial metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="roi-graph-container">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={fetchFinancialReport} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!financialData) {
    return (
      <div className="roi-graph-container">
        <p>No financial data available</p>
      </div>
    );
  }

  // ROI Analysis Chart
  const roiChartData = {
    labels: ['Initial Investment', 'Total Return', 'Net Profit'],
    datasets: [
      {
        label: 'Amount ($)',
        data: [
          financialData.roi_analysis.initial_investment,
          financialData.roi_analysis.total_return,
          financialData.roi_analysis.total_return - financialData.roi_analysis.initial_investment
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 2
      }
    ]
  };

  // Cash Flow Forecast Chart
  const cashFlowData = {
    labels: financialData.cash_flow_forecast.map(item => `Month ${item.month}`),
    datasets: [
      {
        label: 'Revenue',
        data: financialData.cash_flow_forecast.map(item => item.revenue),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        tension: 0.4
      },
      {
        label: 'Expenses',
        data: financialData.cash_flow_forecast.map(item => item.expenses),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        tension: 0.4
      },
      {
        label: 'Net Cash Flow',
        data: financialData.cash_flow_forecast.map(item => item.net_cash_flow),
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.4
      }
    ]
  };

  // Financial Ratios Chart
  const ratiosData = {
    labels: ['Profit Margin', 'ROA', 'ROE', 'Current Ratio', 'Quick Ratio'],
    datasets: [
      {
        label: 'Percentage/Ratio',
        data: [
          financialData.financial_ratios.profit_margin,
          financialData.financial_ratios.return_on_assets,
          financialData.financial_ratios.return_on_equity,
          financialData.financial_ratios.current_ratio,
          financialData.financial_ratios.quick_ratio
        ],
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 2
      }
    ]
  };

  // DCF Analysis Chart
  const dcfData = {
    labels: financialData.dcf_analysis.projected_revenue.map((_, index) => `Year ${index + 1}`),
    datasets: [
      {
        label: 'Projected Revenue',
        data: financialData.dcf_analysis.projected_revenue,
        borderColor: 'rgba(255, 159, 64, 1)',
        backgroundColor: 'rgba(255, 159, 64, 0.1)',
        tension: 0.4
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
        text: 'Financial Analysis'
      }
    }
  };

  return (
    <div className="roi-graph-container">
      <div className="roi-header">
        <h2>Financial ROI Analysis</h2>
        <div className="roi-inputs">
          <div className="input-group">
            <label htmlFor="targetAmount">Target Amount ($):</label>
            <input
              type="number"
              id="targetAmount"
              value={targetAmount}
              onChange={(e) => setTargetAmount(parseFloat(e.target.value) || 0)}
              min="0"
              step="1000"
            />
          </div>
          <div className="input-group">
            <label htmlFor="initialInvestment">Initial Investment ($):</label>
            <input
              type="number"
              id="initialInvestment"
              value={initialInvestment}
              onChange={(e) => setInitialInvestment(parseFloat(e.target.value) || 0)}
              min="0"
              step="1000"
            />
          </div>
          <button onClick={handleCalculateROI} className="calculate-button">
            Calculate ROI
          </button>
        </div>
      </div>

      <div className="roi-summary">
        <div className="summary-card">
          <h3>ROI Summary</h3>
          <div className="metric">
            <span className="label">ROI Percentage:</span>
            <span className="value">{financialData.roi_analysis.roi_percentage.toFixed(2)}%</span>
          </div>
          <div className="metric">
            <span className="label">Annualized ROI:</span>
            <span className="value">{financialData.roi_analysis.annualized_roi.toFixed(2)}%</span>
          </div>
          <div className="metric">
            <span className="label">Payback Period:</span>
            <span className="value">{financialData.roi_analysis.payback_period.toFixed(1)} years</span>
          </div>
        </div>

        <div className="summary-card">
          <h3>DCF Analysis</h3>
          <div className="metric">
            <span className="label">NPV:</span>
            <span className="value">${financialData.dcf_analysis.npv.toFixed(2)}</span>
          </div>
          <div className="metric">
            <span className="label">IRR:</span>
            <span className="value">{financialData.dcf_analysis.irr.toFixed(2)}%</span>
          </div>
          <div className="metric">
            <span className="label">Present Value:</span>
            <span className="value">${financialData.dcf_analysis.present_value.toFixed(2)}</span>
          </div>
        </div>

        <div className="summary-card">
          <h3>Break-Even Analysis</h3>
          <div className="metric">
            <span className="label">Break-Even Units:</span>
            <span className="value">{financialData.break_even_analysis.break_even_units.toFixed(0)}</span>
          </div>
          <div className="metric">
            <span className="label">Break-Even Revenue:</span>
            <span className="value">${financialData.break_even_analysis.break_even_revenue.toFixed(2)}</span>
          </div>
          <div className="metric">
            <span className="label">Profitable:</span>
            <span className="value">{financialData.break_even_analysis.is_profitable ? 'Yes' : 'No'}</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>ROI Analysis</h3>
          <Bar data={roiChartData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <h3>Cash Flow Forecast</h3>
          <Line data={cashFlowData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <h3>Financial Ratios</h3>
          <Bar data={ratiosData} options={chartOptions} />
        </div>

        <div className="chart-container">
          <h3>DCF Projected Revenue</h3>
          <Line data={dcfData} options={chartOptions} />
        </div>
      </div>

      <div className="recommendations">
        <h3>Financial Recommendations</h3>
        <ul>
          {financialData.recommendations.map((recommendation, index) => (
            <li key={index}>{recommendation}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ROIGraph; 