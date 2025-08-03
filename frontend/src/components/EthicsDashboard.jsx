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

const EthicsDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    overall_ethical_score: 0,
    bias_detection_rate: 0,
    correction_success_rate: 0,
    avg_bias_reduction: 0,
    compliance_rate: 0,
    risk_level_distribution: {},
    bias_types_detected: {},
    correction_methods_used: {},
    total_corrections: 0,
    total_reports: 0,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`${API_BASE_URL}/ethics/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching ethics dashboard data:', error);
      Alert.alert('Error', 'Failed to load ethics dashboard data');
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

  const getRiskLevelColor = (level) => {
    switch (level) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getEthicalScoreColor = (score) => {
    if (score >= 0.8) return '#4CAF50';
    if (score >= 0.6) return '#FF9800';
    return '#F44336';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading Ethics Dashboard...</Text>
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
        <Text style={styles.title}>Ethics Dashboard</Text>
        <Text style={styles.subtitle}>AI Bias Monitoring & Correction</Text>
      </View>

      {/* Ethical Score */}
      <View style={styles.scoreContainer}>
        <Text style={styles.scoreTitle}>Overall Ethical Score</Text>
        <View style={[styles.scoreCircle, { borderColor: getEthicalScoreColor(dashboardData.overall_ethical_score) }]}>
          <Text style={[styles.scoreValue, { color: getEthicalScoreColor(dashboardData.overall_ethical_score) }]}>
            {(dashboardData.overall_ethical_score * 100).toFixed(1)}%
          </Text>
        </View>
        <Text style={styles.scoreLabel}>
          {dashboardData.overall_ethical_score >= 0.8 ? 'Excellent' : 
           dashboardData.overall_ethical_score >= 0.6 ? 'Good' : 'Needs Attention'}
        </Text>
      </View>

      {/* Key Metrics */}
      <View style={styles.metricsContainer}>
        <Text style={styles.metricsTitle}>Key Metrics</Text>
        
        <View style={styles.metricRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {(dashboardData.bias_detection_rate * 100).toFixed(1)}%
            </Text>
            <Text style={styles.metricLabel}>Bias Detection Rate</Text>
          </View>
          
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {(dashboardData.correction_success_rate * 100).toFixed(1)}%
            </Text>
            <Text style={styles.metricLabel}>Correction Success Rate</Text>
          </View>
        </View>

        <View style={styles.metricRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {(dashboardData.avg_bias_reduction * 100).toFixed(1)}%
            </Text>
            <Text style={styles.metricLabel}>Avg Bias Reduction</Text>
          </View>
          
          <View style={styles.metricCard}>
            <Text style={styles.metricValue}>
              {(dashboardData.compliance_rate * 100).toFixed(1)}%
            </Text>
            <Text style={styles.metricLabel}>Compliance Rate</Text>
          </View>
        </View>
      </View>

      {/* Risk Level Distribution */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Risk Level Distribution</Text>
        <PieChart
          data={[
            {
              name: 'Low Risk',
              population: dashboardData.risk_level_distribution.low || 0,
              color: '#4CAF50',
              legendFontColor: '#7F7F7F',
            },
            {
              name: 'Medium Risk',
              population: dashboardData.risk_level_distribution.medium || 0,
              color: '#FF9800',
              legendFontColor: '#7F7F7F',
            },
            {
              name: 'High Risk',
              population: dashboardData.risk_level_distribution.high || 0,
              color: '#F44336',
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

      {/* Bias Types Detected */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Bias Types Detected</Text>
        <BarChart
          data={{
            labels: Object.keys(dashboardData.bias_types_detected || {}),
            datasets: [{
              data: Object.values(dashboardData.bias_types_detected || {})
            }]
          }}
          width={screenWidth - 40}
          height={220}
          chartConfig={chartConfig}
          style={styles.chart}
        />
      </View>

      {/* Correction Methods */}
      <View style={styles.methodsContainer}>
        <Text style={styles.methodsTitle}>Correction Methods Used</Text>
        {Object.entries(dashboardData.correction_methods_used || {}).map(([method, count]) => (
          <View key={method} style={styles.methodItem}>
            <Text style={styles.methodName}>{method.replace('_', ' ').toUpperCase()}</Text>
            <Text style={styles.methodCount}>{count}</Text>
          </View>
        ))}
      </View>

      {/* Summary Stats */}
      <View style={styles.summaryContainer}>
        <Text style={styles.summaryTitle}>Summary Statistics</Text>
        
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Total Corrections:</Text>
          <Text style={styles.summaryValue}>{dashboardData.total_corrections}</Text>
        </View>
        
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Total Reports:</Text>
          <Text style={styles.summaryValue}>{dashboardData.total_reports}</Text>
        </View>
        
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Last Updated:</Text>
          <Text style={styles.summaryValue}>
            {dashboardData.last_updated ? new Date(dashboardData.last_updated).toLocaleString() : 'N/A'}
          </Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.actionsContainer}>
        <Text style={styles.actionsTitle}>Quick Actions</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Run Bias Detection</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Generate Report</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Test Correction</Text>
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
  scoreContainer: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    margin: 20,
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
  scoreTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  scoreCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 10,
  },
  scoreValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#666',
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
    textAlign: 'center',
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
  methodsContainer: {
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
  methodsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  methodItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  methodName: {
    fontSize: 16,
    color: '#333',
  },
  methodCount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1cc910',
  },
  summaryContainer: {
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
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  summaryLabel: {
    fontSize: 16,
    color: '#666',
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
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

export default EthicsDashboard; 