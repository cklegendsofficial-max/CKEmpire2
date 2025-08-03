#!/usr/bin/env node
/**
 * Mobile UI Test Script
 * Tests React Native components and functionality
 */

const fs = require('fs');
const path = require('path');

class MobileUITester {
  constructor() {
    this.testResults = [];
    this.projectPath = __dirname;
  }

  printHeader(title) {
    console.log('\n' + '='.repeat(60));
    console.log(`📱 ${title}`);
    console.log('='.repeat(60));
  }

  printSuccess(message) {
    console.log(`✅ ${message}`);
    this.testResults.push({ test: message, status: 'PASS' });
  }

  printError(message) {
    console.log(`❌ ${message}`);
    this.testResults.push({ test: message, status: 'FAIL' });
  }

  printInfo(message) {
    console.log(`ℹ️  ${message}`);
  }

  testProjectStructure() {
    this.printHeader('Testing Project Structure');
    
    const requiredFiles = [
      'App.tsx',
      'package.json',
      'src/components/Dashboard.js',
      'src/components/AIChatbot.js',
      'src/components/Settings.js',
      'src/components/Navigation.js',
    ];

    let allFilesExist = true;
    
    for (const file of requiredFiles) {
      const filePath = path.join(this.projectPath, file);
      if (fs.existsSync(filePath)) {
        this.printSuccess(`Found ${file}`);
      } else {
        this.printError(`Missing ${file}`);
        allFilesExist = false;
      }
    }

    if (allFilesExist) {
      this.printSuccess('All required files exist');
    } else {
      this.printError('Some required files are missing');
    }
  }

  testPackageJson() {
    this.printHeader('Testing Package.json Dependencies');
    
    try {
      const packageJsonPath = path.join(this.projectPath, 'package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      
      const requiredDependencies = [
        'axios',
        'react-native-chart-kit',
        'react-native-svg',
        '@react-native-async-storage/async-storage',
        'react-native-gesture-handler',
        'react-native-reanimated',
      ];

      let allDepsInstalled = true;
      
      for (const dep of requiredDependencies) {
        if (packageJson.dependencies && packageJson.dependencies[dep]) {
          this.printSuccess(`Dependency installed: ${dep}`);
        } else {
          this.printError(`Missing dependency: ${dep}`);
          allDepsInstalled = false;
        }
      }

      if (allDepsInstalled) {
        this.printSuccess('All required dependencies are installed');
      } else {
        this.printError('Some dependencies are missing');
      }
    } catch (error) {
      this.printError(`Error reading package.json: ${error.message}`);
    }
  }

  testComponentFiles() {
    this.printHeader('Testing Component Files');
    
    const components = [
      { name: 'Dashboard', file: 'src/components/Dashboard.js' },
      { name: 'AIChatbot', file: 'src/components/AIChatbot.js' },
      { name: 'Settings', file: 'src/components/Settings.js' },
      { name: 'Navigation', file: 'src/components/Navigation.js' },
    ];

    for (const component of components) {
      const filePath = path.join(this.projectPath, component.file);
      
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Check for React Native imports
        if (content.includes('react-native') && content.includes('import')) {
          this.printSuccess(`${component.name} component is properly structured`);
        } else {
          this.printError(`${component.name} component may have issues`);
        }
      } else {
        this.printError(`${component.name} component file not found`);
      }
    }
  }

  testAppIntegration() {
    this.printHeader('Testing App Integration');
    
    const appPath = path.join(this.projectPath, 'App.tsx');
    
    if (fs.existsSync(appPath)) {
      const content = fs.readFileSync(appPath, 'utf8');
      
      // Check for component imports
      const requiredImports = [
        'Dashboard',
        'AIChatbot', 
        'Settings',
        'Navigation'
      ];
      
      let allImportsFound = true;
      
      for (const importName of requiredImports) {
        if (content.includes(importName)) {
          this.printSuccess(`Import found: ${importName}`);
        } else {
          this.printError(`Import missing: ${importName}`);
          allImportsFound = false;
        }
      }
      
      // Check for navigation logic
      if (content.includes('activeTab') && content.includes('setActiveTab')) {
        this.printSuccess('Navigation logic implemented');
      } else {
        this.printError('Navigation logic missing');
      }
      
      if (allImportsFound) {
        this.printSuccess('App integration looks good');
      } else {
        this.printError('App integration has issues');
      }
    } else {
      this.printError('App.tsx not found');
    }
  }

  testMobileFeatures() {
    this.printHeader('Testing Mobile Features');
    
    // Test Dashboard features
    const dashboardPath = path.join(this.projectPath, 'src/components/Dashboard.js');
    if (fs.existsSync(dashboardPath)) {
      const dashboardContent = fs.readFileSync(dashboardPath, 'utf8');
      
      if (dashboardContent.includes('react-native-chart-kit')) {
        this.printSuccess('Chart integration found in Dashboard');
      } else {
        this.printError('Chart integration missing in Dashboard');
      }
      
      if (dashboardContent.includes('axios')) {
        this.printSuccess('API integration found in Dashboard');
      } else {
        this.printError('API integration missing in Dashboard');
      }
    }
    
    // Test AI Chatbot features
    const chatbotPath = path.join(this.projectPath, 'src/components/AIChatbot.js');
    if (fs.existsSync(chatbotPath)) {
      const chatbotContent = fs.readFileSync(chatbotPath, 'utf8');
      
      if (chatbotContent.includes('KeyboardAvoidingView')) {
        this.printSuccess('Mobile keyboard handling implemented');
      } else {
        this.printError('Mobile keyboard handling missing');
      }
      
      if (chatbotContent.includes('ScrollView')) {
        this.printSuccess('Scrollable chat interface implemented');
      } else {
        this.printError('Scrollable chat interface missing');
      }
    }
    
    // Test Settings features
    const settingsPath = path.join(this.projectPath, 'src/components/Settings.js');
    if (fs.existsSync(settingsPath)) {
      const settingsContent = fs.readFileSync(settingsPath, 'utf8');
      
      if (settingsContent.includes('AsyncStorage')) {
        this.printSuccess('Local storage integration found');
      } else {
        this.printError('Local storage integration missing');
      }
      
      if (settingsContent.includes('Switch')) {
        this.printSuccess('Toggle switches implemented');
      } else {
        this.printError('Toggle switches missing');
      }
    }
  }

  testBackendIntegration() {
    this.printHeader('Testing Backend Integration');
    
    const components = [
      { name: 'Dashboard', file: 'src/components/Dashboard.js' },
      { name: 'AIChatbot', file: 'src/components/AIChatbot.js' },
    ];
    
    for (const component of components) {
      const filePath = path.join(this.projectPath, component.file);
      
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        if (content.includes('axios') && content.includes('API_BASE_URL')) {
          this.printSuccess(`${component.name} has API integration`);
        } else {
          this.printError(`${component.name} missing API integration`);
        }
        
        if (content.includes('10.0.2.2:8000')) {
          this.printSuccess(`${component.name} configured for Android emulator`);
        } else {
          this.printError(`${component.name} not configured for Android emulator`);
        }
      }
    }
  }

  printSummary() {
    this.printHeader('Mobile UI Test Summary');
    
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.status === 'PASS').length;
    const failedTests = totalTests - passedTests;
    
    console.log(`Total Tests: ${totalTests}`);
    console.log(`Passed: ${passedTests}`);
    console.log(`Failed: ${failedTests}`);
    console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    if (failedTests > 0) {
      console.log('\nFailed Tests:');
      this.testResults
        .filter(r => r.status === 'FAIL')
        .forEach(result => {
          console.log(`  ❌ ${result.test}`);
        });
    }
  }

  runAllTests() {
    console.log('📱 Starting CKEmpire Mobile UI Tests');
    console.log(`Project Path: ${this.projectPath}`);
    console.log(`Timestamp: ${new Date().toISOString()}`);
    
    this.testProjectStructure();
    this.testPackageJson();
    this.testComponentFiles();
    this.testAppIntegration();
    this.testMobileFeatures();
    this.testBackendIntegration();
    
    this.printSummary();
  }
}

// Run tests
const tester = new MobileUITester();
tester.runAllTests(); 