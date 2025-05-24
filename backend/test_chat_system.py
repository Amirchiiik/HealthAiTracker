#!/usr/bin/env python3
"""
Comprehensive test script for the Secure Chat System
Tests patient-doctor communication with file attachments
"""

import requests
import json
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8001"  # Adjust port if needed
TEST_FILE_PATH = "test_medical_report.txt"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_test(test_name):
    print(f"{Colors.BLUE}🧪 Testing: {test_name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def create_test_file():
    """Create a test medical report file"""
    test_content = """
    Patient Medical Report
    
    Hemoglobin: 145 g/L (Normal: 120-160)
    Glucose: 6.5 mmol/L (Normal: 3.9-6.1)
    Cholesterol: 4.2 mmol/L (Normal: <5.2)
    
    Patient shows slightly elevated glucose levels.
    Recommend follow-up in 3 months.
    """
    
    with open(TEST_FILE_PATH, 'w') as f:
        f.write(test_content)
    print_info(f"Created test file: {TEST_FILE_PATH}")

def cleanup_test_file():
    """Remove test file"""
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
        print_info(f"Cleaned up test file: {TEST_FILE_PATH}")

class ChatSystemTester:
    def __init__(self):
        self.patient_token = None
        self.doctor_token = None
        self.patient_id = None
        self.doctor_id = None
        self.test_message_id = None
        
    def register_and_login_users(self):
        """Register patient and doctor accounts"""
        print_test("User Registration and Authentication")
        
        # Register patient
        patient_data = {
            "full_name": "Test Patient",
            "email": f"patient_{datetime.now().timestamp()}@test.com",
            "password": "TestPass123",
            "role": "patient"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=patient_data)
        if response.status_code == 201:
            print_success("Patient registration successful")
        else:
            print_error(f"Patient registration failed: {response.text}")
            return False
        
        # Login patient
        login_data = {"email": patient_data["email"], "password": patient_data["password"]}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            self.patient_token = token_data["access_token"]
            self.patient_id = token_data["user"]["id"]
            print_success(f"Patient login successful - ID: {self.patient_id}")
        else:
            print_error(f"Patient login failed: {response.text}")
            return False
        
        # Register doctor
        doctor_data = {
            "full_name": "Dr. Test Doctor",
            "email": f"doctor_{datetime.now().timestamp()}@test.com",
            "password": "TestPass123",
            "role": "doctor"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=doctor_data)
        if response.status_code == 201:
            print_success("Doctor registration successful")
        else:
            print_error(f"Doctor registration failed: {response.text}")
            return False
        
        # Login doctor
        login_data = {"email": doctor_data["email"], "password": doctor_data["password"]}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            self.doctor_token = token_data["access_token"]
            self.doctor_id = token_data["user"]["id"]
            print_success(f"Doctor login successful - ID: {self.doctor_id}")
        else:
            print_error(f"Doctor login failed: {response.text}")
            return False
        
        return True
    
    def test_available_chat_users(self):
        """Test getting available users for chat"""
        print_test("Available Chat Users")
        
        # Patient should see doctors
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        response = requests.get(f"{BASE_URL}/chat/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            doctor_found = any(user["user_id"] == self.doctor_id for user in users)
            if doctor_found:
                print_success("Patient can see available doctors")
            else:
                print_warning("Doctor not found in patient's available users list")
        else:
            print_error(f"Failed to get available users for patient: {response.text}")
            return False
        
        # Doctor should see patients
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        response = requests.get(f"{BASE_URL}/chat/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            patient_found = any(user["user_id"] == self.patient_id for user in users)
            if patient_found:
                print_success("Doctor can see available patients")
            else:
                print_warning("Patient not found in doctor's available users list")
        else:
            print_error(f"Failed to get available users for doctor: {response.text}")
            return False
        
        return True
    
    def test_send_message_without_file(self):
        """Test sending a simple text message"""
        print_test("Send Text Message (Patient to Doctor)")
        
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        data = {
            "receiver_id": self.doctor_id,
            "message_text": "Hello Doctor, I have some questions about my recent lab results. Could you please review them?"
        }
        
        response = requests.post(f"{BASE_URL}/chat/send", headers=headers, data=data)
        
        if response.status_code == 200:
            message_data = response.json()
            self.test_message_id = message_data["id"]
            print_success(f"Message sent successfully - ID: {self.test_message_id}")
            print_info(f"Message content: {message_data['message_text']}")
            return True
        else:
            print_error(f"Failed to send message: {response.text}")
            return False
    
    def test_send_message_with_file(self):
        """Test sending a message with file attachment"""
        print_test("Send Message with File Attachment (Doctor to Patient)")
        
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        data = {
            "receiver_id": self.patient_id,
            "message_text": "Thank you for your question. I've reviewed your lab results and prepared a summary report for you. Please find it attached."
        }
        
        with open(TEST_FILE_PATH, 'rb') as f:
            files = {"file": (TEST_FILE_PATH, f, "text/plain")}
            response = requests.post(f"{BASE_URL}/chat/send", headers=headers, data=data, files=files)
        
        if response.status_code == 200:
            message_data = response.json()
            print_success(f"Message with attachment sent successfully")
            print_info(f"Attachment: {message_data.get('attachment_filename', 'None')}")
            print_info(f"File size: {message_data.get('attachment_size', 0)} bytes")
            return True
        else:
            print_error(f"Failed to send message with attachment: {response.text}")
            return False
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history"""
        print_test("Get Conversation History")
        
        # Patient gets history with doctor
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        response = requests.get(
            f"{BASE_URL}/chat/history", 
            headers=headers, 
            params={"with_user": self.doctor_id, "limit": 10}
        )
        
        if response.status_code == 200:
            history = response.json()
            print_success(f"Retrieved {len(history['messages'])} messages")
            print_info(f"Total messages in conversation: {history['total_count']}")
            
            for i, msg in enumerate(history['messages'][:2]):  # Show first 2 messages
                sender_role = "Patient" if msg['sender_id'] == self.patient_id else "Doctor"
                print_info(f"Message {i+1} ({sender_role}): {msg['message_text'][:50]}...")
                if msg.get('attachment_filename'):
                    print_info(f"  📎 Attachment: {msg['attachment_filename']}")
            
            return True
        else:
            print_error(f"Failed to get conversation history: {response.text}")
            return False
    
    def test_get_conversations_list(self):
        """Test getting list of all conversations"""
        print_test("Get Conversations List")
        
        # Doctor gets all conversations
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        response = requests.get(f"{BASE_URL}/chat/conversations", headers=headers)
        
        if response.status_code == 200:
            conversations = response.json()
            print_success(f"Retrieved {len(conversations['conversations'])} conversations")
            
            for conv in conversations['conversations']:
                print_info(f"Conversation with: {conv['full_name']} ({conv['role']})")
                print_info(f"  Unread messages: {conv['unread_count']}")
                if conv['last_message_at']:
                    print_info(f"  Last message: {conv['last_message_at']}")
            
            return True
        else:
            print_error(f"Failed to get conversations list: {response.text}")
            return False
    
    def test_role_validation(self):
        """Test that role validation works (patient can't message patient)"""
        print_test("Role Validation (Should Fail)")
        
        # Try to send message from patient to same patient (should fail)
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        data = {
            "receiver_id": self.patient_id,  # Same user
            "message_text": "This should fail"
        }
        
        response = requests.post(f"{BASE_URL}/chat/send", headers=headers, data=data)
        
        if response.status_code != 200:
            print_success("Role validation working - prevented patient-to-patient messaging")
            return True
        else:
            print_error("Role validation failed - allowed invalid communication")
            return False
    
    def test_unauthorized_access(self):
        """Test that unauthorized users can't access chat"""
        print_test("Unauthorized Access Prevention")
        
        # Try to access chat without token
        response = requests.get(f"{BASE_URL}/chat/conversations")
        
        if response.status_code == 401 or response.status_code == 403:
            print_success("Unauthorized access properly blocked")
            return True
        else:
            print_error(f"Unauthorized access not blocked: {response.status_code}")
            return False
    
    def test_mark_messages_read(self):
        """Test marking messages as read"""
        print_test("Mark Messages as Read")
        
        headers = {"Authorization": f"Bearer {self.patient_token}"}
        response = requests.put(
            f"{BASE_URL}/chat/mark-read/{self.doctor_id}", 
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Messages marked as read successfully")
            return True
        else:
            print_error(f"Failed to mark messages as read: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all chat system tests"""
        print(f"{Colors.PURPLE}🚀 Starting Secure Chat System Tests{Colors.END}")
        print("=" * 60)
        
        # Create test file
        create_test_file()
        
        test_results = []
        
        # Run tests in sequence
        tests = [
            ("User Authentication", self.register_and_login_users),
            ("Available Chat Users", self.test_available_chat_users),
            ("Send Text Message", self.test_send_message_without_file),
            ("Send Message with File", self.test_send_message_with_file),
            ("Get Conversation History", self.test_get_conversation_history),
            ("Get Conversations List", self.test_get_conversations_list),
            ("Role Validation", self.test_role_validation),
            ("Unauthorized Access", self.test_unauthorized_access),
            ("Mark Messages Read", self.test_mark_messages_read),
        ]
        
        for test_name, test_func in tests:
            print("\n" + "-" * 60)
            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                print_error(f"Test '{test_name}' crashed: {str(e)}")
                test_results.append((test_name, False))
        
        # Cleanup
        cleanup_test_file()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"{Colors.PURPLE}📊 Test Results Summary{Colors.END}")
        print("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
            print(f"{test_name:<25} [{status}]")
        
        print("-" * 60)
        success_rate = (passed / total) * 100
        print(f"Overall: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print(f"{Colors.GREEN}🎉 All tests passed! Chat system is working perfectly.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Some tests failed. Please check the system configuration.{Colors.END}")
        
        return passed == total

def main():
    """Main test execution"""
    print(f"{Colors.CYAN}AI Health Tracker - Secure Chat System Test Suite{Colors.END}")
    print(f"Testing server at: {BASE_URL}")
    print("")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Server is running and healthy")
        else:
            print_error("Server health check failed")
            return
    except requests.exceptions.RequestException:
        print_error(f"Cannot connect to server at {BASE_URL}")
        print_info("Please make sure the server is running:")
        print_info("  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        return
    
    # Run tests
    tester = ChatSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}✨ Secure Chat System is ready for production use!{Colors.END}")
    else:
        print(f"\n{Colors.RED}🔧 Please fix the issues before deploying.{Colors.END}")

if __name__ == "__main__":
    main() 