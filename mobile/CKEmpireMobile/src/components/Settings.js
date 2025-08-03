import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Switch,
  ScrollView,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Settings = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [aiSuggestions, setAiSuggestions] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Çıkış Yap',
      'Hesabınızdan çıkış yapmak istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel',
        },
        {
          text: 'Çıkış Yap',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.clear();
              Alert.alert('Başarılı', 'Başarıyla çıkış yapıldı.');
            } catch (error) {
              Alert.alert('Hata', 'Çıkış yapılırken bir hata oluştu.');
            }
          },
        },
      ]
    );
  };

  const handleClearCache = () => {
    Alert.alert(
      'Önbelleği Temizle',
      'Tüm önbellek verilerini temizlemek istediğinizden emin misiniz?',
      [
        {
          text: 'İptal',
          style: 'cancel',
        },
        {
          text: 'Temizle',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.clear();
              Alert.alert('Başarılı', 'Önbellek temizlendi.');
            } catch (error) {
              Alert.alert('Hata', 'Önbellek temizlenirken bir hata oluştu.');
            }
          },
        },
      ]
    );
  };

  const settingsSections = [
    {
      title: 'Bildirimler',
      items: [
        {
          title: 'Push Bildirimleri',
          type: 'switch',
          value: notifications,
          onValueChange: setNotifications,
        },
        {
          title: 'AI Önerileri',
          type: 'switch',
          value: aiSuggestions,
          onValueChange: setAiSuggestions,
        },
      ],
    },
    {
      title: 'Görünüm',
      items: [
        {
          title: 'Karanlık Mod',
          type: 'switch',
          value: darkMode,
          onValueChange: setDarkMode,
        },
      ],
    },
    {
      title: 'Veri',
      items: [
        {
          title: 'Otomatik Senkronizasyon',
          type: 'switch',
          value: autoSync,
          onValueChange: setAutoSync,
        },
        {
          title: 'Önbelleği Temizle',
          type: 'button',
          onPress: handleClearCache,
        },
      ],
    },
    {
      title: 'Hesap',
      items: [
        {
          title: 'Çıkış Yap',
          type: 'button',
          onPress: handleLogout,
          destructive: true,
        },
      ],
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Ayarlar</Text>
        <Text style={styles.headerSubtitle}>CKEmpire Mobile</Text>
      </View>

      {settingsSections.map((section, sectionIndex) => (
        <View key={sectionIndex} style={styles.section}>
          <Text style={styles.sectionTitle}>{section.title}</Text>
          
          {section.items.map((item, itemIndex) => (
            <View key={itemIndex} style={styles.settingItem}>
              <Text style={[
                styles.settingTitle,
                item.destructive && styles.destructiveText,
              ]}>
                {item.title}
              </Text>
              
              {item.type === 'switch' ? (
                <Switch
                  value={item.value}
                  onValueChange={item.onValueChange}
                  trackColor={{ false: '#767577', true: '#1cc910' }}
                  thumbColor={item.value ? '#fff' : '#f4f3f4'}
                />
              ) : (
                <TouchableOpacity
                  style={[
                    styles.button,
                    item.destructive && styles.destructiveButton,
                  ]}
                  onPress={item.onPress}
                >
                  <Text style={[
                    styles.buttonText,
                    item.destructive && styles.destructiveButtonText,
                  ]}>
                    {item.title}
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          ))}
        </View>
      ))}

      <View style={styles.footer}>
        <Text style={styles.versionText}>CKEmpire Mobile v1.0.0</Text>
        <Text style={styles.copyrightText}>© 2024 CKEmpire</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#1cc910',
    padding: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'white',
    marginTop: 5,
  },
  section: {
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    padding: 15,
    backgroundColor: '#f8f8f8',
    color: '#333',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  settingTitle: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  destructiveText: {
    color: '#ff4444',
  },
  button: {
    backgroundColor: '#1cc910',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 5,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  destructiveButton: {
    backgroundColor: '#ff4444',
  },
  destructiveButtonText: {
    color: 'white',
  },
  footer: {
    alignItems: 'center',
    padding: 20,
    marginTop: 20,
  },
  versionText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  copyrightText: {
    fontSize: 12,
    color: '#999',
  },
});

export default Settings; 