# AI Health Tracker Mobile App 📱

A comprehensive React Native mobile application for the AI Health Tracker system, providing patients with medical document upload, AI-powered analysis, doctor consultations, and health monitoring capabilities.

![React Native](https://img.shields.io/badge/React%20Native-0.73.0-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.1.6-blue)
![Languages](https://img.shields.io/badge/Languages-🇷🇺%20🇺🇸%20🇰🇿-green)

## 🎯 Features

### 📤 Document Upload & OCR
- **Camera Capture**: Take photos of medical documents
- **Gallery Selection**: Choose existing photos from device
- **PDF Support**: Upload PDF medical reports
- **OCR Processing**: Automatic text extraction with explanations
- **Multi-language Support**: Process documents in Russian, English, and Kazakh

### 🧠 AI-Powered Health Analysis
- **Intelligent Agent**: Advanced AI analysis of health metrics
- **Critical Detection**: Automatic identification of critical health values
- **Specialist Recommendations**: Smart matching with medical specialists
- **Localized Explanations**: Medical advice in user's preferred language
- **Auto-booking**: Automatic appointment scheduling for critical conditions

### 👩‍⚕️ Doctor Consultations
- **Specialist Matching**: Find doctors based on health analysis
- **Appointment Management**: Book, view, and manage appointments
- **Real-time Chat**: Secure messaging with assigned doctors
- **Medical History**: Share health data with healthcare providers
- **Multi-language Support**: Communicate in Russian, English, or Kazakh

### 📊 Health Monitoring
- **Health History**: Timeline of all health analyses
- **Metrics Tracking**: Monitor trends in health indicators
- **Status Categorization**: Normal, High, Critical health metrics
- **Export Functionality**: Download health reports
- **Visual Analytics**: Charts and graphs for health trends

### 🔐 Security & Privacy
- **JWT Authentication**: Secure login and registration
- **Encrypted Communication**: All data transmission encrypted
- **Biometric Login**: Fingerprint/FaceID support (optional)
- **Privacy Controls**: Manage data sharing preferences
- **HIPAA Compliance**: Medical data protection standards

## 🏗️ Architecture

### 📁 Project Structure
```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Common components (buttons, inputs)
│   │   ├── charts/          # Health data visualization
│   │   └── forms/           # Form components
│   ├── screens/             # Main application screens
│   │   ├── auth/            # Authentication screens
│   │   ├── home/            # Dashboard and overview
│   │   ├── upload/          # Document upload flow
│   │   ├── history/         # Health analysis history
│   │   ├── chat/            # Doctor communication
│   │   ├── appointments/    # Appointment management
│   │   └── profile/         # User profile management
│   ├── services/            # API integration services
│   │   ├── api.ts           # Base API client
│   │   ├── auth.ts          # Authentication service
│   │   ├── upload.ts        # File upload service
│   │   ├── health.ts        # Health data service
│   │   └── chat.ts          # Chat service
│   ├── contexts/            # React Context providers
│   │   ├── AuthContext.tsx  # Authentication state
│   │   ├── LanguageContext.tsx # Localization
│   │   └── ThemeContext.tsx # Theme management
│   ├── navigation/          # Navigation configuration
│   │   ├── RootNavigator.tsx # Main navigation
│   │   ├── AuthNavigator.tsx # Auth flow navigation
│   │   └── TabNavigator.tsx  # Bottom tab navigation
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts      # Authentication hook
│   │   ├── useApi.ts       # API request hook
│   │   └── useLanguage.ts  # Localization hook
│   ├── utils/              # Utility functions
│   │   ├── validation.ts   # Form validation
│   │   ├── formatting.ts   # Data formatting
│   │   └── storage.ts      # Local storage helpers
│   ├── types/              # TypeScript definitions
│   │   └── index.ts        # All type definitions
│   ├── constants/          # App constants
│   │   ├── theme.ts        # Design system
│   │   ├── api.ts          # API configuration
│   │   └── languages.ts    # Language constants
│   └── localization/       # Internationalization
│       ├── i18n.ts         # i18n configuration
│       ├── ru.json         # Russian translations
│       ├── en.json         # English translations
│       └── kz.json         # Kazakh translations
├── assets/                 # Static assets
│   ├── images/             # App images
│   ├── icons/              # App icons
│   └── fonts/              # Custom fonts
├── android/                # Android-specific code
├── ios/                    # iOS-specific code
└── package.json            # Dependencies and scripts
```

### 🎨 Design System
- **Medical Theme**: Clean, professional medical UI
- **Color Palette**: Medical blues, greens, and status colors
- **Typography**: Readable fonts optimized for medical content
- **Icons**: Medical and health-related iconography
- **Accessibility**: WCAG 2.1 AA compliance
- **Responsive**: Optimized for all device sizes

### 🌐 Localization
- **Russian (🇷🇺)**: Complete medical terminology in Russian
- **English (🇺🇸)**: Full English language support
- **Kazakh (🇰🇿)**: Kazakh language support (planned)
- **Dynamic Switching**: Change language without app restart
- **Medical Terms**: Specialized medical vocabulary translation
- **Date/Number Formatting**: Locale-specific formatting

## 🚀 Getting Started

### 📋 Prerequisites
- **Node.js**: Version 16.0 or higher
- **React Native CLI**: `npm install -g react-native-cli`
- **Development Environment**:
  - For iOS: Xcode 12+ (macOS only)
  - For Android: Android Studio with SDK 28+
- **Device/Emulator**: Physical device or emulator for testing

### 🛠️ Installation

1. **Clone and Navigate**
```bash
cd ai-health-backend/frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **iOS Setup** (macOS only)
```bash
cd ios && pod install && cd ..
```

4. **Configure Environment**
```bash
# Create environment configuration
cp .env.example .env

# Update with your backend API URL
# Edit .env file with your settings
```

### ▶️ Running the App

#### Development Mode
```bash
# Start Metro bundler
npm start

# Run on iOS (macOS only)
npm run ios

# Run on Android
npm run android

# Run on specific device
npm run ios -- --device "iPhone 14"
npm run android -- --device-id YOUR_DEVICE_ID
```

#### Production Build
```bash
# Build for Android
npm run build:android

# Build for iOS (requires Xcode)
npm run build:ios
```

## 🔧 Configuration

### 🌐 Backend Integration
Update the API base URL in `src/constants/api.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://your-backend-url:8001',
  // ... other configuration
};
```

### 🗣️ Language Settings
Configure supported languages in `src/localization/i18n.ts`:

```typescript
const resources = {
  ru: { translation: require('./ru.json') },
  en: { translation: require('./en.json') },
  kz: { translation: require('./kz.json') },
};
```

### 🎨 Theme Customization
Modify the medical theme in `src/constants/theme.ts`:

```typescript
export const medicalColors = {
  primary: '#2E86AB',        // Your primary color
  secondary: '#28A745',      // Your secondary color
  // ... other colors
};
```

## 📱 Core Features Guide

### 🔐 Authentication Flow
1. **Login/Register**: Email and password authentication
2. **JWT Token Management**: Automatic token refresh and storage
3. **Biometric Authentication**: Optional fingerprint/FaceID
4. **Session Management**: Secure logout and session expiry

### 📤 Document Upload Process
1. **Capture/Select**: Camera or gallery document selection
2. **Upload Progress**: Real-time upload progress indicator
3. **OCR Processing**: Automatic text extraction from images/PDFs
4. **Results Display**: Parsed health metrics with explanations

### 🧠 AI Analysis Workflow
1. **Trigger Analysis**: Process uploaded health documents
2. **Metric Extraction**: Identify health indicators and values
3. **Risk Assessment**: Categorize metrics (normal/high/critical)
4. **Specialist Matching**: Recommend appropriate doctors
5. **Auto-booking**: Schedule critical appointments automatically

### 💬 Doctor Communication
1. **Chat Interface**: Real-time messaging with doctors
2. **File Sharing**: Share medical documents and images
3. **Appointment Integration**: Link chats to specific appointments
4. **Multi-language**: Communicate in preferred language

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
# iOS
npm run test:e2e:ios

# Android
npm run test:e2e:android
```

### Linting
```bash
npm run lint
```

## 📦 Build & Deployment

### Android APK
```bash
cd android
./gradlew assembleRelease
```

### iOS IPA
```bash
cd ios
xcodebuild -workspace AIHealthTrackerMobile.xcworkspace \
  -scheme AIHealthTrackerMobile \
  -configuration Release \
  -archivePath build/AIHealthTrackerMobile.xcarchive \
  archive
```

### App Store/Play Store
- Follow platform-specific guidelines for app submission
- Ensure compliance with medical app regulations
- Include privacy policy and terms of service

## 🛡️ Security Considerations

### Data Protection
- **Encryption**: All sensitive data encrypted at rest and in transit
- **Token Security**: JWT tokens stored securely with encryption
- **API Security**: All requests authenticated and authorized
- **Medical Privacy**: HIPAA-compliant data handling

### Best Practices
- Regular security audits and updates
- Secure coding practices implementation
- Input validation and sanitization
- Error handling without data exposure

## 🤝 Contributing

### Development Workflow
1. **Branch**: Create feature branch from main
2. **Develop**: Implement feature with tests
3. **Test**: Run all tests and linting
4. **Review**: Submit pull request for review
5. **Deploy**: Merge after approval

### Code Standards
- **TypeScript**: Strict typing for all components
- **ESLint**: Code linting with medical app rules
- **Prettier**: Consistent code formatting
- **Testing**: Unit tests for all business logic

## 📞 Support

### Documentation
- **API Documentation**: Backend API endpoint documentation
- **Component Library**: Storybook documentation (planned)
- **User Guide**: End-user application guide

### Getting Help
- **Issues**: GitHub issues for bug reports
- **Discussions**: GitHub discussions for questions
- **Email**: Technical support email contact

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Medical Professionals**: For guidance on medical workflows
- **React Native Community**: For excellent tooling and support
- **Open Source Contributors**: For the libraries that make this possible

---

**🏥 AI Health Tracker Mobile - Empowering patients with intelligent health monitoring and medical consultations** 

Built with ❤️ using React Native, TypeScript, and modern mobile development practices. 