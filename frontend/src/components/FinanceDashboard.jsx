import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const FinanceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dcfData, setDcfData] = useState(null);
  const [cacLtvData, setCacLtvData] = useState(null);
  const [roiData, setRoiData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    // DCF Form
    dcf: {
      initial_investment: 50000,
      target_revenue: 200000,
      growth_rate: 0.15,
      discount_rate: 0.10,
      time_period: 5
    },
    // CAC/LTV Form
    cacLtv: {
      customer_acquisition_cost: 100,
      customer_lifetime_value: 300,
      marketing_spend: 10000,
      new_customers: 100
    },
    // ROI Form
    roi: {
      target_amount: 20000,
      initial_investment: 10000,
      time_period: 1.0
    }
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const calculateDCF = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/finance/dcf-advanced', formData.dcf);
      setDcfData(response.data);
      toast.success('DCF model calculated successfully!');
    } catch (error) {
      console.error('DCF calculation error:', error);
      toast.error('Failed to calculate DCF model');
    } finally {
      setLoading(false);
    }
  };

  const calculateCACLTV = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/finance/cac-ltv-advanced', formData.cacLtv);
      setCacLtvData(response.data);
      toast.success('CAC/LTV analysis completed!');
    } catch (error) {
      console.error('CAC/LTV calculation error:', error);
      toast.error('Failed to calculate CAC/LTV');
    } finally {
      setLoading(false);
    }
  };

  const calculateROI = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/finance/roi', formData.roi);
      setRoiData(response.data);
      toast.success('ROI calculated successfully!');
    } catch (error) {
      console.error('ROI calculation error:', error);
      toast.error('Failed to calculate ROI');
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const renderDCFChart = () => {
    if (!dcfData?.dcf_model?.projected_revenue) return null;

    const chartData = dcfData.dcf_model.projected_revenue.map((revenue, index) => ({
      year: `Year ${index + 1}`,
      revenue: revenue,
      cumulative: dcfData.dcf_model.projected_revenue.slice(0, index + 1).reduce((sum, r) => sum + r, 0)
    }));

    return (
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Revenue Projection</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="revenue" 
              stroke="#3B82F6" 
              strokeWidth={3}
              name="Annual Revenue"
            />
            <Line 
              type="monotone" 
              dataKey="cumulative" 
              stroke="#10B981" 
              strokeWidth={3}
              name="Cumulative Revenue"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderCACLTVChart = () => {
    if (!cacLtvData?.unit_economics) return null;

    const { unit_economics } = cacLtvData;
    const chartData = [
      { name: 'CAC', value: unit_economics.customer_acquisition_cost, color: '#EF4444' },
      { name: 'LTV', value: unit_economics.customer_lifetime_value, color: '#10B981' }
    ];

    return (
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">Unit Economics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: $${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="space-y-4">
            <div className="bg-dark-700 rounded-lg p-4">
              <h4 className="text-lg font-medium text-white mb-2">Key Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-dark-300">LTV/CAC Ratio:</span>
                  <span className="text-white font-semibold">{unit_economics.ltv_cac_ratio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-300">Payback Period:</span>
                  <span className="text-white font-semibold">{unit_economics.payback_period_months.toFixed(1)} months</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-300">Profitability:</span>
                  <span className="text-white font-semibold">{unit_economics.profitability_score}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-300">Growth Potential:</span>
                  <span className="text-white font-semibold">{unit_economics.growth_potential}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderROIChart = () => {
    if (!roiData) return null;

    const chartData = [
      { name: 'Investment', value: roiData.initial_investment, color: '#EF4444' },
      { name: 'Return', value: roiData.total_return, color: '#10B981' }
    ];

    return (
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">ROI Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F9FAFB'
                }}
              />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
          
          <div className="space-y-4">
            <div className="bg-dark-700 rounded-lg p-4">
              <h4 className="text-lg font-medium text-white mb-2">ROI Metrics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-dark-300">ROI Percentage:</span>
                  <span className="text-white font-semibold">{roiData.roi_percentage.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-300">Annualized ROI:</span>
                  <span className="text-white font-semibold">{roiData.annualized_roi.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-dark-300">Payback Period:</span>
                  <span className="text-white font-semibold">{roiData.payback_period.toFixed(1)} years</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderForm = (section) => {
    const data = formData[section];
    const fields = {
      dcf: [
        { name: 'initial_investment', label: 'Initial Investment ($)', type: 'number' },
        { name: 'target_revenue', label: 'Target Revenue ($)', type: 'number' },
        { name: 'growth_rate', label: 'Growth Rate (%)', type: 'number', step: 0.01 },
        { name: 'discount_rate', label: 'Discount Rate (%)', type: 'number', step: 0.01 },
        { name: 'time_period', label: 'Time Period (years)', type: 'number' }
      ],
      cacLtv: [
        { name: 'customer_acquisition_cost', label: 'Customer Acquisition Cost ($)', type: 'number' },
        { name: 'customer_lifetime_value', label: 'Customer Lifetime Value ($)', type: 'number' },
        { name: 'marketing_spend', label: 'Marketing Spend ($)', type: 'number' },
        { name: 'new_customers', label: 'New Customers', type: 'number' }
      ],
      roi: [
        { name: 'target_amount', label: 'Target Amount ($)', type: 'number' },
        { name: 'initial_investment', label: 'Initial Investment ($)', type: 'number' },
        { name: 'time_period', label: 'Time Period (years)', type: 'number', step: 0.1 }
      ]
    };

    return (
      <div className="bg-dark-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-white mb-4">
          {section === 'dcf' ? 'DCF Model Parameters' : 
           section === 'cacLtv' ? 'CAC/LTV Parameters' : 'ROI Parameters'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fields[section].map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                {field.label}
              </label>
              <input
                type={field.type}
                step={field.step}
                value={data[field.name]}
                onChange={(e) => handleFormChange(section, field.name, parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 bg-dark-700 border border-dark-600 rounded-md text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-empire-500 focus:border-transparent"
              />
            </div>
          ))}
        </div>
        <button
          onClick={section === 'dcf' ? calculateDCF : section === 'cacLtv' ? calculateCACLTV : calculateROI}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-empire-gradient text-white rounded-md hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {loading ? 'Calculating...' : `Calculate ${section.toUpperCase()}`}
        </button>
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Finance Dashboard</h1>
          <p className="text-dark-300 mt-2">DCF Modeling, CAC/LTV Analysis & ROI Calculations</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-dark-800 rounded-lg p-1">
        {['overview', 'dcf', 'cac-ltv', 'roi'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-empire-gradient text-white'
                : 'text-dark-300 hover:text-white hover:bg-dark-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-dark-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">DCF Model</h3>
              <p className="text-dark-300 mb-4">Discounted Cash Flow analysis for investment decisions</p>
              <button
                onClick={() => setActiveTab('dcf')}
                className="px-4 py-2 bg-empire-gradient text-white rounded-md hover:opacity-90 transition-opacity"
              >
                Create DCF Model
              </button>
            </div>
            
            <div className="bg-dark-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">CAC/LTV Analysis</h3>
              <p className="text-dark-300 mb-4">Customer Acquisition Cost vs Lifetime Value analysis</p>
              <button
                onClick={() => setActiveTab('cac-ltv')}
                className="px-4 py-2 bg-empire-gradient text-white rounded-md hover:opacity-90 transition-opacity"
              >
                Analyze CAC/LTV
              </button>
            </div>
            
            <div className="bg-dark-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">ROI Calculator</h3>
              <p className="text-dark-300 mb-4">Return on Investment calculations and analysis</p>
              <button
                onClick={() => setActiveTab('roi')}
                className="px-4 py-2 bg-empire-gradient text-white rounded-md hover:opacity-90 transition-opacity"
              >
                Calculate ROI
              </button>
            </div>
          </div>
        )}

        {activeTab === 'dcf' && (
          <div className="space-y-6">
            {renderForm('dcf')}
            {dcfData && (
              <div className="space-y-6">
                {renderDCFChart()}
                
                {/* DCF Results */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">NPV</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      ${dcfData.dcf_model.npv.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">IRR</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      {(dcfData.dcf_model.irr * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">Risk Level</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      {dcfData.risk_assessment.risk_level}
                    </p>
                  </div>
                </div>

                {/* Investment Recommendation */}
                <div className="bg-dark-800 rounded-lg p-6">
                  <h4 className="text-lg font-medium text-white mb-4">Investment Recommendation</h4>
                  <div className="bg-dark-700 rounded-lg p-4">
                    <p className="text-white font-semibold mb-2">
                      {dcfData.investment_recommendation.recommendation}
                    </p>
                    <p className="text-dark-300 text-sm">
                      Confidence Level: {dcfData.investment_recommendation.confidence_level}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'cac-ltv' && (
          <div className="space-y-6">
            {renderForm('cacLtv')}
            {cacLtvData && (
              <div className="space-y-6">
                {renderCACLTVChart()}
                
                {/* CAC/LTV Results */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-4">Scaling Recommendations</h4>
                    <ul className="space-y-2">
                      {cacLtvData.scaling_recommendations.map((rec, index) => (
                        <li key={index} className="text-dark-300 text-sm flex items-start">
                          <span className="text-empire-400 mr-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-4">Risk Assessment</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-dark-300">Risk Level:</span>
                        <span className="text-white">{cacLtvData.risk_assessment.risk_level}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dark-300">Sustainability:</span>
                        <span className="text-white">{cacLtvData.risk_assessment.sustainability_score}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dark-300">Scaling Readiness:</span>
                        <span className="text-white">{cacLtvData.risk_assessment.scaling_readiness}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'roi' && (
          <div className="space-y-6">
            {renderForm('roi')}
            {roiData && (
              <div className="space-y-6">
                {renderROIChart()}
                
                {/* ROI Results */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">ROI Percentage</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      {roiData.roi_percentage.toFixed(2)}%
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">Annualized ROI</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      {roiData.annualized_roi.toFixed(2)}%
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-white mb-2">Payback Period</h4>
                    <p className="text-2xl font-bold text-empire-400">
                      {roiData.payback_period.toFixed(1)} years
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FinanceDashboard; 