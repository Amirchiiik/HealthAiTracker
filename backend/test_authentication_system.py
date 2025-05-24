#!/usr/bin/env python3
"""
Test script for authentication and user management system
"""

import sys
import os
import requests
import json
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PATIENT = {
    "full_name": "John Patient",
    "email": "patient@test.com",
    "password": "TestPass123",
    "role": "patient"
}
TEST_DOCTOR = {
    "full_name": "Dr. Jane Smith",
    "email": "doctor@test.com", 
    "password": "DoctorPass123",
    "role": "doctor"
}

class AuthTestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_info: Optional[Dict] = None
    
    def register(self, user_data: Dict) -> Dict:
        """Register a new user"""
        response = requests.post(f"{self.base_url}/auth/register", json=user_data)
        return response.json(), response.status_code
    
    def login(self, email: str, password: str) -> Dict:
        """Login and store token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        
        if response.status_code == 200:
            self.token = data["access_token"]
            self.user_info = data["user"]
        
        return data, response.status_code
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.token:
            raise ValueError("No token available. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_profile(self) -> Dict:
        """Get current user profile"""
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def upload_file(self, file_path: str) -> Dict:
        """Upload a file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers={"Authorization": f"Bearer {self.token}"}
            )
        return response.json(), response.status_code
    
    def get_health_analyses(self) -> Dict:
        """Get user's health analyses"""
        response = requests.get(
            f"{self.base_url}/users/me/analyses",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_chat_history(self) -> Dict:
        """Get user's chat history"""
        response = requests.get(
            f"{self.base_url}/users/me/chats",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def explain_text(self, text: str) -> Dict:
        """Test explanation endpoint"""
        response = requests.post(
            f"{self.base_url}/explain/metrics",
            json={"raw_text": text},
            headers=self.get_headers()
        )
        return response.json(), response.status_code

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

def test_user_registration():
    """Test user registration"""
    print("\n🔐 Testing User Registration")
    print("=" * 40)
    
    client = AuthTestClient(BASE_URL)
    
    # Test patient registration
    print("📝 Registering patient...")
    data, status = client.register(TEST_PATIENT)
    if status == 201:
        print(f"✅ Patient registered: {data['full_name']} ({data['email']})")
    else:
        print(f"❌ Patient registration failed: {data}")
        return False
    
    # Test doctor registration
    print("📝 Registering doctor...")
    data, status = client.register(TEST_DOCTOR)
    if status == 201:
        print(f"✅ Doctor registered: {data['full_name']} ({data['email']})")
    else:
        print(f"❌ Doctor registration failed: {data}")
        return False
    
    return True

def test_user_login():
    """Test user login"""
    print("\n🔑 Testing User Login")
    print("=" * 40)
    
    client = AuthTestClient(BASE_URL)
    
    # Test patient login
    print("🔐 Logging in patient...")
    data, status = client.login(TEST_PATIENT["email"], TEST_PATIENT["password"])
    if status == 200:
        print(f"✅ Patient login successful: {data['user']['full_name']}")
        print(f"🎫 Token received: {data['access_token'][:20]}...")
    else:
        print(f"❌ Patient login failed: {data}")
        return False
    
    # Test profile access
    print("👤 Getting patient profile...")
    profile_data, status = client.get_profile()
    if status == 200:
        print(f"✅ Profile accessed: {profile_data['full_name']} - {profile_data['role']}")
    else:
        print(f"❌ Profile access failed: {profile_data}")
        return False
    
    return True

def test_protected_endpoints():
    """Test protected endpoints"""
    print("\n🛡️ Testing Protected Endpoints")
    print("=" * 40)
    
    # Test without authentication
    print("🚫 Testing without authentication...")
    response = requests.get(f"{BASE_URL}/users/me/analyses")
    if response.status_code in [401, 403]:  # Both are valid for unauthenticated requests
        print("✅ Correctly rejected unauthenticated request")
    else:
        print(f"❌ Should have rejected unauthenticated request, got {response.status_code}")
        return False
    
    # Test with authentication
    client = AuthTestClient(BASE_URL)
    client.login(TEST_PATIENT["email"], TEST_PATIENT["password"])
    
    print("🔐 Testing with authentication...")
    analyses_data, status = client.get_health_analyses()
    if status == 200:
        print(f"✅ Successfully accessed protected endpoint: {len(analyses_data)} analyses")
    else:
        print(f"❌ Failed to access protected endpoint: {analyses_data}")
        return False
    
    return True

def test_user_history():
    """Test user history functionality"""
    print("\n📊 Testing User History")
    print("=" * 40)
    
    client = AuthTestClient(BASE_URL)
    client.login(TEST_PATIENT["email"], TEST_PATIENT["password"])
    
    # Test explanation endpoint (should save to chat history)
    print("💬 Testing chat history saving...")
    sample_text = "Гемоглобин: 140 г/л (норма: 120-160)"
    explain_data, status = client.explain_text(sample_text)
    
    if status == 200:
        print("✅ Explanation generated successfully")
        if explain_data.get("saved_to_history"):
            print("✅ Chat interaction saved to history")
        else:
            print("⚠️ Chat interaction may not have been saved")
    else:
        print(f"❌ Explanation failed: {explain_data}")
    
    # Check chat history
    print("📜 Checking chat history...")
    chat_data, status = client.get_chat_history()
    if status == 200:
        print(f"✅ Chat history accessed: {len(chat_data)} interactions")
        if chat_data:
            latest_chat = chat_data[0]
            print(f"📝 Latest interaction: {latest_chat['interaction_type']}")
    else:
        print(f"❌ Failed to access chat history: {chat_data}")
        return False
    
    return True

def test_role_based_access():
    """Test role-based access control"""
    print("\n👥 Testing Role-Based Access Control")
    print("=" * 40)
    
    # Login as patient
    patient_client = AuthTestClient(BASE_URL)
    patient_client.login(TEST_PATIENT["email"], TEST_PATIENT["password"])
    
    # Login as doctor
    doctor_client = AuthTestClient(BASE_URL)
    doctor_client.login(TEST_DOCTOR["email"], TEST_DOCTOR["password"])
    
    # Test that both can access their own data
    print("🏥 Testing patient data access...")
    patient_analyses, status = patient_client.get_health_analyses()
    if status == 200:
        print("✅ Patient can access own data")
    else:
        print(f"❌ Patient cannot access own data: {status}")
        return False
    
    print("👨‍⚕️ Testing doctor data access...")
    doctor_analyses, status = doctor_client.get_health_analyses()
    if status == 200:
        print("✅ Doctor can access own data")
    else:
        print(f"❌ Doctor cannot access own data: {status}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Authentication System Tests")
    
    # Check if server is running
    if not test_server_health():
        print("❌ Server is not running. Please start the server first.")
        print("Run: python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Run tests
    tests = [
        test_user_registration,
        test_user_login,
        test_protected_endpoints,
        test_user_history,
        test_role_based_access
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 