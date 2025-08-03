# CKEmpire Mobile App

React Native mobile application for CKEmpire platform with AI-powered empire consulting and analytics.

## 🚀 Features

### 📊 Dashboard
- **Mobile-optimized metrics display** with responsive charts
- **Revenue tracking** with interactive line charts
- **Subscription analytics** with pie chart distribution
- **Key metrics cards** showing MRR, customers, ROI, AI requests
- **Pull-to-refresh** functionality for real-time data
- **Quick action buttons** for common tasks

### 🤖 AI Chatbot
- **OpenAI-powered empire consultant** for strategy advice
- **Real-time chat interface** with message history
- **Quick suggestion buttons** for common queries
- **Mobile keyboard handling** with KeyboardAvoidingView
- **Scrollable chat interface** for long conversations
- **Loading states** and error handling

### ⚙️ Settings
- **Push notification controls** for mobile alerts
- **Dark mode toggle** for user preference
- **Auto-sync settings** for data synchronization
- **AI suggestion controls** for personalized recommendations
- **Cache management** for storage optimization
- **Account management** with logout functionality

### 🧭 Navigation
- **Bottom tab navigation** with intuitive icons
- **Smooth transitions** between screens
- **Active state indicators** for current tab
- **Responsive design** for different screen sizes

## 📱 Mobile-Specific Features

### Android Emulator Configuration
- **API endpoint**: `http://10.0.2.2:8000/api/v1` (Android emulator localhost)
- **Backend integration** with FastAPI server
- **Real-time data sync** with pull-to-refresh

### Responsive Design
- **Flexible layouts** that adapt to screen sizes
- **Touch-friendly interfaces** with proper button sizes
- **Mobile-optimized charts** with react-native-chart-kit
- **Gesture support** with react-native-gesture-handler

### Performance Optimizations
- **AsyncStorage** for local data persistence
- **Efficient re-rendering** with React hooks
- **Memory management** with proper component lifecycle
- **Network optimization** with axios interceptors

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Installation

1. **Navigate to mobile directory:**
   ```bash
   cd mobile/CKEmpireMobile
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Install additional mobile dependencies:**
   ```bash
   npm install axios react-native-chart-kit react-native-svg @react-native-async-storage/async-storage react-native-gesture-handler react-native-reanimated
   ```

4. **iOS specific setup (macOS only):**
   ```bash
   cd ios && pod install && cd ..
   ```

### Running the App

#### Android
```bash
# Start Android emulator first, then:
npx react-native run-android
```

#### iOS (macOS only)
```bash
npx react-native run-ios
```

### Backend Integration

Ensure the CKEmpire backend server is running:
```bash
cd ../../backend
python main.py
```

The mobile app will connect to `http://10.0.2.2:8000` (Android emulator) or `http://localhost:8000` (iOS simulator).

## 🧪 Testing

### Run Mobile UI Tests
```bash
node test_mobile_ui.js
```

### Manual Testing Checklist
- [ ] Dashboard loads with charts
- [ ] AI chatbot responds to messages
- [ ] Settings toggles work properly
- [ ] Navigation between tabs works
- [ ] Pull-to-refresh updates data
- [ ] Error handling shows appropriate messages

## 📁 Project Structure

```
mobile/CKEmpireMobile/
├── src/
│   └── components/
│       ├── Dashboard.js          # Main dashboard with charts
│       ├── AIChatbot.js         # AI chat interface
│       ├── Settings.js          # App settings and preferences
│       └── Navigation.js        # Bottom tab navigation
├── App.tsx                      # Main app component
├── package.json                 # Dependencies and scripts
├── test_mobile_ui.js           # Mobile UI test script
└── README_MOBILE.md            # This file
```

## 🔧 Configuration

### API Endpoints
The app connects to these backend endpoints:
- `GET /api/v1/revenue/metrics` - Revenue data for charts
- `GET /api/v1/subscription/metrics` - Subscription analytics
- `GET /api/v1/ai/strategy-types` - AI strategy types
- `POST /api/v1/ai/empire-strategy` - AI strategy generation

### Environment Variables
Create `.env` file in the mobile app root:
```
API_BASE_URL=http://10.0.2.2:8000/api/v1
```

## 🎨 UI/UX Features

### Design System
- **Primary Color**: `#1cc910` (CKEmpire green)
- **Background**: `#f5f5f5` (light gray)
- **Text Colors**: `#333` (dark), `#666` (medium), `#999` (light)
- **Shadows**: Consistent elevation for cards and buttons

### Mobile Optimizations
- **Touch targets**: Minimum 44px for buttons
- **Font sizes**: Responsive typography
- **Spacing**: Consistent padding and margins
- **Loading states**: Visual feedback for async operations

## 🚀 Deployment

### Android APK Build
```bash
cd android
./gradlew assembleRelease
```

### iOS Build (macOS only)
```bash
cd ios
xcodebuild -workspace CKEmpireMobile.xcworkspace -scheme CKEmpireMobile -configuration Release
```

## 🔮 Future Enhancements

### Planned Features
- [ ] **Push notifications** for AI insights
- [ ] **Offline mode** with local data caching
- [ ] **Biometric authentication** (fingerprint/face ID)
- [ ] **Dark theme** implementation
- [ ] **Multi-language support** (Turkish/English)
- [ ] **Video calling** for AI consultations
- [ ] **Voice input** for AI chatbot
- [ ] **AR/VR integration** for immersive experiences

### Performance Improvements
- [ ] **Image optimization** for faster loading
- [ ] **Code splitting** for smaller bundle size
- [ ] **Lazy loading** for components
- [ ] **Background sync** for data updates

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues:**
   ```bash
   npx react-native start --reset-cache
   ```

2. **Android build errors:**
   ```bash
   cd android && ./gradlew clean && cd ..
   ```

3. **iOS build errors:**
   ```bash
   cd ios && pod deintegrate && pod install && cd ..
   ```

4. **API connection issues:**
   - Ensure backend server is running
   - Check API_BASE_URL configuration
   - Verify network connectivity

### Debug Mode
Enable debug mode for development:
```bash
npx react-native run-android --variant=debug
```

## 📞 Support

For mobile app issues:
1. Check the troubleshooting section
2. Run `node test_mobile_ui.js` for diagnostics
3. Review console logs for error messages
4. Ensure backend server is running and accessible

## 📄 License

This mobile app is part of the CKEmpire project and follows the same licensing terms.

---

**CKEmpire Mobile v1.0.0** - Empowering entrepreneurs with AI-driven insights on mobile devices. 