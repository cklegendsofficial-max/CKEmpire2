import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const MetricsContext = createContext();

export const useMetrics = () => {
  const context = useContext(MetricsContext);
  if (!context) {
    throw new Error('useMetrics must be used within a MetricsProvider');
  }
  return context;
};

export const MetricsProvider = ({ children }) => {
  const [metrics, setMetrics] = useState({
    consciousness: 0,
    revenue: 0,
    agents: 0,
    projects: 0,
    content: 0,
    performance: {
      queryTime: 0,
      cacheHitRate: 0,
      slowQueries: 0,
    },
    ethics: {
      totalChecks: 0,
      biasDetected: 0,
      fairnessScore: 0,
    },
    ai: {
      ideasGenerated: 0,
      videosCreated: 0,
      nftsMinted: 0,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch metrics from backend
  const fetchMetrics = async () => {
    try {
      setIsLoading(true);
      
      // Fetch various metrics from different endpoints
      const [metricsRes, performanceRes, ethicsRes, aiRes] = await Promise.allSettled([
        axios.get('/metrics'),
        axios.get('/performance/metrics'),
        axios.get('/ethics/stats'),
        axios.get('/ai/agi-state'),
      ]);

      const newMetrics = { ...metrics };

      // Update basic metrics
      if (metricsRes.status === 'fulfilled') {
        const data = metricsRes.value.data;
        newMetrics.consciousness = data.consciousness_score || 0;
        newMetrics.revenue = data.total_revenue || 0;
        newMetrics.agents = data.active_agents || 0;
        newMetrics.projects = data.total_projects || 0;
        newMetrics.content = data.total_content || 0;
      }

      // Update performance metrics
      if (performanceRes.status === 'fulfilled') {
        const data = performanceRes.value.data;
        newMetrics.performance = {
          queryTime: data.average_query_time || 0,
          cacheHitRate: data.cache_hit_rate || 0,
          slowQueries: data.slow_queries_count || 0,
        };
      }

      // Update ethics metrics
      if (ethicsRes.status === 'fulfilled') {
        const data = ethicsRes.value.data;
        newMetrics.ethics = {
          totalChecks: data.total_checks || 0,
          biasDetected: data.bias_detected || 0,
          fairnessScore: data.average_fairness_score || 0,
        };
      }

      // Update AI metrics
      if (aiRes.status === 'fulfilled') {
        const data = aiRes.value.data;
        newMetrics.ai = {
          ideasGenerated: data.ideas_generated || 0,
          videosCreated: data.videos_created || 0,
          nftsMinted: data.nfts_minted || 0,
        };
      }

      setMetrics(newMetrics);
      setLastUpdated(new Date());
      
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      toast.error('Failed to fetch metrics from backend');
    } finally {
      setIsLoading(false);
    }
  };

  // Poll metrics every 30 seconds
  useEffect(() => {
    fetchMetrics();
    
    const interval = setInterval(fetchMetrics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Manual refresh function
  const refreshMetrics = () => {
    fetchMetrics();
    toast.success('Metrics refreshed');
  };

  const value = {
    metrics,
    isLoading,
    lastUpdated,
    refreshMetrics,
    fetchMetrics,
  };

  return (
    <MetricsContext.Provider value={value}>
      {children}
    </MetricsContext.Provider>
  );
}; 