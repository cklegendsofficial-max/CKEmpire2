import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';

const Navigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'dashboard', title: 'Dashboard', icon: '📊' },
    { id: 'chat', title: 'AI Chat', icon: '🤖' },
    { id: 'settings', title: 'Ayarlar', icon: '⚙️' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.tabBar}>
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.id}
            style={[
              styles.tab,
              activeTab === tab.id && styles.activeTab,
            ]}
            onPress={() => onTabChange(tab.id)}
          >
            <Text style={styles.tabIcon}>{tab.icon}</Text>
            <Text
              style={[
                styles.tabText,
                activeTab === tab.id && styles.activeTabText,
              ]}
            >
              {tab.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'white',
    paddingBottom: 10,
    paddingTop: 5,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  activeTab: {
    backgroundColor: '#f0f8f0',
  },
  tabIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  tabText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#1cc910',
    fontWeight: 'bold',
  },
});

export default Navigation; 