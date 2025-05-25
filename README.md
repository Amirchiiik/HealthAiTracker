# 🏥 AI Health Tracker - Frontend Application

## 📋 **Overview**

This is the React frontend application for the AI Health Tracker system, providing a comprehensive web interface for patients and doctors to manage health data, upload medical documents, and access AI-powered health analysis.

## 🚀 **Features**

### **Patient Features**
- **Document Upload**: Upload medical documents with drag-and-drop interface
- **OCR Analysis**: Automatic text extraction from medical documents
- **Health Dashboard**: View health metrics and analysis results
- **AI Agent**: Access intelligent health recommendations
- **Appointment Booking**: Schedule appointments with doctors
- **Real-time Chat**: Communicate with healthcare providers
- **Health History**: Track health metrics over time

### **Doctor Features**
- **Patient Management**: View and manage patient cases
- **AI Agent Dashboard**: Access comprehensive AI analysis tools
- **Appointment Management**: Manage doctor schedules and appointments
- **Analytics Dashboard**: View patient statistics and trends
- **Real-time Chat**: Communicate with patients
- **Critical Alerts**: Receive notifications for critical patient values

### **AI-Powered Features**
- **Critical Value Detection**: Automatic detection of dangerous health values
- **Emergency Alerts**: Full-screen alerts for critical conditions
- **Specialist Recommendations**: AI-powered specialist matching
- **Automatic Appointment Booking**: Emergency appointment scheduling
- **Health Insights**: Detailed explanations for each health metric

## 🛠 **Technology Stack**

- **Framework**: React 18.2.0 with TypeScript
- **Styling**: Tailwind CSS 3.3.0
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router 6.8.1
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **WebSockets**: Native WebSocket API
- **Build Tool**: Create React App
- **Testing**: Jest & React Testing Library

## 📁 **Project Structure**

```
frontend/
├── public/                     # Static assets
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── alerts/            # Alert components
│   │   ├── analysis/          # Analysis components
│   │   ├── common/            # Common UI components
│   │   ├── layout/            # Layout components
│   │   └── upload/            # File upload components
│   ├── pages/                 # Main application pages
│   │   ├── agent/             # AI Agent pages
│   │   ├── appointments/      # Appointment management
│   │   ├── auth/              # Authentication pages
│   │   ├── chat/              # Chat interface
│   │   ├── doctor/            # Doctor dashboard pages
│   │   ├── history/           # Health history pages
│   │   ├── patient/           # Patient dashboard pages
│   │   └── settings/          # Settings pages
│   ├── services/              # API integration services
│   │   ├── agentService.ts    # AI Agent API calls
│   │   ├── authService.ts     # Authentication service
│   │   ├── chatService.ts     # Chat functionality
│   │   ├── criticalAnalysisService.ts # Critical analysis
│   │   ├── healthService.ts   # Health data service
│   │   └── uploadService.ts   # File upload service
│   ├── contexts/              # React Context providers
│   │   └── AuthContext.tsx    # Authentication state
│   ├── hooks/                 # Custom React hooks
│   │   └── useWebSocket.ts    # WebSocket hook
│   ├── types/                 # TypeScript definitions
│   │   └── index.ts           # All type definitions
│   ├── config/                # Configuration files
│   │   └── api.ts             # API configuration
│   ├── App.tsx                # Main App component
│   ├── index.tsx              # Application entry point
│   └── index.css              # Global styles
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── README.md                  # This file
```

## 🔧 **Installation & Setup**

### **Prerequisites**
- **Node.js**: Version 16.0 or higher
- **npm**: Version 7.0 or higher
- **Backend API**: AI Health Tracker backend running on port 8000

### **1. Clone Repository**
```bash
git clone https://github.com/Amirchiiik/HealthAiTracker.git -b frontend-only
cd HealthAiTracker/frontend
```

### **2. Install Dependencies**
```bash
npm install
```

### **3. Environment Configuration**
Create a `.env` file in the frontend directory:
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# App Configuration
REACT_APP_NAME=AI Health Tracker
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_DEMO_MODE=true
REACT_APP_ENABLE_CRITICAL_ALERTS=true
```

### **4. Start Development Server**
```bash
npm start
```

The application will be available at: `http://localhost:3000`

## 🎨 **Design System**

### **Color Palette**
- **Primary**: Blue (#3B82F6) - Medical trust and reliability
- **Secondary**: Green (#10B981) - Health and wellness
- **Success**: Green (#22C55E) - Positive health indicators
- **Warning**: Orange (#F59E0B) - Attention needed
- **Error**: Red (#EF4444) - Critical health values
- **Critical**: Dark Red (#DC2626) - Emergency situations

### **Typography**
- **Headings**: Inter font family for clarity
- **Body**: System fonts for readability
- **Medical Data**: Monospace for precise values

### **Components**
- **Cards**: Clean, shadowed containers for content
- **Buttons**: Consistent styling with hover states
- **Forms**: Accessible form inputs with validation
- **Modals**: Full-screen alerts for critical information
- **Navigation**: Responsive navigation with role-based menus

## 🔐 **Authentication & Security**

### **Authentication Flow**
1. **Login/Register**: Email and password authentication
2. **JWT Tokens**: Secure token-based authentication
3. **Role-Based Access**: Patient and doctor role management
4. **Session Management**: Automatic token refresh and logout

### **Security Features**
- **Protected Routes**: Authentication required for sensitive pages
- **CORS Protection**: Configured for backend API communication
- **Input Validation**: Client-side validation for all forms
- **XSS Protection**: Sanitized user inputs and outputs

## 🚨 **Critical Analysis Integration**

### **Automatic Detection**
- **Upload Monitoring**: Checks for critical values after file upload
- **Real-time Analysis**: Immediate processing of health metrics
- **Threshold-Based**: Uses medical thresholds for detection
- **Multi-metric Support**: Analyzes various health indicators

### **Emergency Alerts**
- **Full-screen Modals**: Unmissable critical value notifications
- **Urgency Levels**: Color-coded priority indicators (low/medium/high/critical)
- **Action Plans**: Step-by-step recommended actions
- **Emergency Contacts**: Quick access to emergency information

### **AI Agent Integration**
- **Automatic Triggering**: Critical values trigger AI analysis
- **Specialist Recommendations**: AI suggests appropriate doctors
- **Appointment Booking**: Automatic emergency appointment scheduling
- **Comprehensive Reports**: Detailed analysis and next steps

## 💬 **Real-time Features**

### **WebSocket Integration**
- **Live Chat**: Real-time messaging between patients and doctors
- **Notifications**: Instant alerts for appointments and messages
- **Connection Management**: Automatic reconnection and error handling
- **Message Scoping**: Proper message routing to intended recipients

### **Chat System**
- **Conversation Management**: Organized chat threads
- **Message History**: Persistent chat history
- **Read Receipts**: Message read status tracking
- **File Sharing**: Share medical documents in chat

## 📱 **Responsive Design**

### **Mobile Optimization**
- **Touch-friendly**: Large buttons and touch targets
- **Responsive Layout**: Adapts to all screen sizes
- **Mobile Navigation**: Collapsible navigation menu
- **Swipe Gestures**: Intuitive mobile interactions

### **Desktop Experience**
- **Multi-column Layout**: Efficient use of screen space
- **Keyboard Navigation**: Full keyboard accessibility
- **Hover States**: Interactive feedback for desktop users
- **Context Menus**: Right-click functionality where appropriate

## 🧪 **Testing**

### **Run Tests**
```bash
# Unit tests
npm test

# Test coverage
npm run test:coverage

# E2E tests (if configured)
npm run test:e2e
```

### **Linting & Formatting**
```bash
# ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Prettier formatting
npm run format
```

## 🚀 **Build & Deployment**

### **Production Build**
```bash
npm run build
```

### **Deployment Options**

#### **Static Hosting (Netlify, Vercel)**
```bash
# Build the app
npm run build

# Deploy the build folder
# Follow platform-specific deployment guides
```

#### **Docker Deployment**
```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### **Environment Variables for Production**
```bash
REACT_APP_API_URL=https://your-backend-api.com
REACT_APP_WS_URL=wss://your-backend-api.com
REACT_APP_ENABLE_DEMO_MODE=false
```

## 📊 **Performance Optimization**

### **Code Splitting**
- **Lazy Loading**: Route-based code splitting
- **Component Splitting**: Large components split into chunks
- **Bundle Analysis**: Regular bundle size monitoring

### **Caching Strategy**
- **React Query**: Intelligent data caching and synchronization
- **Service Worker**: Static asset caching (if configured)
- **Browser Caching**: Optimized cache headers

### **Performance Monitoring**
- **Web Vitals**: Core web vitals tracking
- **Bundle Size**: Monitor and optimize bundle size
- **Load Times**: Track page load performance

## 🔧 **Development**

### **Code Standards**
- **TypeScript**: Strict typing for all components
- **ESLint**: Code linting with React best practices
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for quality assurance

### **Component Development**
- **Functional Components**: React hooks-based components
- **Custom Hooks**: Reusable logic extraction
- **Context API**: State management for global data
- **Error Boundaries**: Graceful error handling

## 📚 **API Integration**

### **Service Layer**
- **Axios Client**: Configured HTTP client with interceptors
- **Error Handling**: Centralized error handling and user feedback
- **Request/Response Transformation**: Data formatting and validation
- **Authentication**: Automatic token attachment and refresh

### **Key Endpoints**
- **Authentication**: `/auth/login`, `/auth/register`
- **File Upload**: `/upload/file`, `/upload/ocr/{filename}`
- **Health Data**: `/health/analyses`, `/health/metrics`
- **Chat**: `/chat/conversations`, `/chat/send`
- **Appointments**: `/appointments` (CRUD operations)
- **AI Agent**: `/agent/analyze-and-act`, `/agent/notifications`

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork**: Fork the repository
2. **Branch**: Create feature branch from main
3. **Develop**: Implement feature with tests
4. **Test**: Run all tests and linting
5. **Review**: Submit pull request for review

### **Code Review Guidelines**
- **TypeScript**: Ensure proper typing
- **Testing**: Include unit tests for new features
- **Documentation**: Update documentation for new features
- **Performance**: Consider performance implications

## 📞 **Support**

### **Common Issues**
1. **API Connection**: Check backend server is running on port 8000
2. **WebSocket Errors**: Verify WebSocket URL configuration
3. **Build Errors**: Clear node_modules and reinstall dependencies
4. **Authentication Issues**: Check JWT token configuration

### **Debugging**
- **Browser DevTools**: Use React Developer Tools
- **Console Logs**: Check browser console for errors
- **Network Tab**: Monitor API requests and responses
- **React Query DevTools**: Debug data fetching and caching

## 📄 **License**

This project is licensed under the MIT License.

---

## 🎯 **Frontend Status: Production Ready**

✅ **Authentication System**: Complete with JWT and role-based access  
✅ **File Upload & OCR**: Drag-and-drop with progress indicators  
✅ **Health Dashboard**: Comprehensive patient and doctor dashboards  
✅ **AI Agent Integration**: Full AI analysis and recommendations  
✅ **Critical Alerts**: Emergency notification system  
✅ **Real-time Chat**: WebSocket-based messaging  
✅ **Appointment System**: Complete booking and management  
✅ **Responsive Design**: Mobile and desktop optimized  
✅ **TypeScript**: Fully typed codebase  
✅ **Testing**: Unit tests and linting configured  

**Ready for production deployment!**

*Last updated: January 25, 2025* 