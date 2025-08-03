import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import axios from 'axios';

const screenWidth = Dimensions.get('window').width;

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    revenue: [],
    projects: [],
    aiRequests: [],
    subscriptionData: {},
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const API_BASE_URL = 'http://10.0.2.2:8000/api/v1'; // Android emulator localhost

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch revenue metrics
      const revenueResponse = await axios.get(`${API_BASE_URL}/revenue/metrics`);
      
      // Fetch subscription metrics
      const subscriptionResponse = await axios.get(`${API_BASE_URL}/subscription/metrics`);
      
      // Fetch AI metrics
      const aiResponse = await axios.get(`${API_BASE_URL}/ai/strategy-types`);

      setMetrics({
        revenue: revenueResponse.data || [],
        subscriptionData: subscriptionResponse.data || {},
        aiRequests: aiResponse.data || [],
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  const chartConfig = {
    backgroundColor: '#1cc910',
    backgroundGradientFrom: '#1cc910',
    backgroundGradientTo: '#1cc910',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#1cc910',
    },
  };

  const revenueData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        data: metrics.revenue.length > 0 ? metrics.revenue.map(r => r.amount || 0) : [0, 0, 0, 0, 0, 0],
        color: (opacity = 1) => `rgba(28, 201, 16, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const subscriptionData = {
    labels: ['Freemium', 'Premium', 'Enterprise'],
    data: [
      metrics.subscriptionData.total_customers * 0.6 || 0,
      metrics.subscriptionData.total_customers * 0.3 || 0,
      metrics.subscriptionData.total_customers * 0.1 || 0,
    ],
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading Dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>CKEmpire Dashboard</Text>
        <Text style={styles.subtitle}>Mobile Analytics</Text>
      </View>

      {/* Revenue Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Revenue Trend</Text>
        <LineChart
          data={revenueData}
          width={screenWidth - 40}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Subscription Distribution */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Subscription Distribution</Text>
        <PieChart
          data={[
            {
              name: 'Freemium',
              population: subscriptionData.data[0],
              color: '#FF6B6B',
              legendFontColor: '#7F7F7F',
            },
            {
              name: 'Premium',
              population: subscriptionData.data[1],
              color: '#4ECDC4',
              legendFontColor: '#7F7F7F',
            },
            {
              name: 'Enterprise',
              population: subscriptionData.data[2],
              color: '#45B7D1',
              legendFontColor: '#7F7F7F',
            },
          ]}
          width={screenWidth - 40}
          height={220}
          chartConfig={chartConfig}
          accessor="population"
          backgroundColor="transparent"
          paddingLeft="15"
        />
      </View>

      {/* Key Metrics */}
      <View style={styles.metricsContainer}>
        <Text style={styles.metricsTitle}>Key Metrics</Text>
        
        <View style={styles.metricRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              ${metrics.subscriptionData.monthly_recurring_revenue || 0}
            </Text>
            <Text style={styles.metricLabel}>Monthly Revenue</Text>
          </View>
          
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {metrics.subscriptionData.total_customers || 0}
            </Text>
            <Text style={styles.metricLabel}>Total Customers</Text>
          </View>
        </View>

        <View style={styles.metricRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {metrics.subscriptionData.roi_percentage || 0}%
            </Text>
            <Text style={styles.metricLabel}>ROI</Text>
          </View>
          
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {metrics.aiRequests.length || 0}
            </Text>
            <Text style={styles.metricLabel}>AI Requests</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.actionsTitle}>Quick Actions</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Generate Strategy</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>View Projects</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>AI Chat</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    fontSize: 18,
    color: '#333',
  },
  header: {
    padding: 20,
    backgroundColor: '#1cc910',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: 'white',
    textAlign: 'center',
    marginTop: 5,
  },
  chartContainer: {
    margin: 20,
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  metricsContainer: {
    margin: 20,
  },
  metricsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
  },
  metricCard: {
    flex: 1,
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginHorizontal: 5,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1cc910',
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  actionsContainer: {
    margin: 20,
    marginBottom: 40,
  },
  actionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  actionButton: {
    backgroundColor: '#1cc910',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    alignItems: 'center',
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default Dashboard; 