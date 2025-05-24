#!/usr/bin/env python3
"""
Comprehensive API Test Suite for AI Health Tracker
Tests all endpoints, user workflows, and integrations end-to-end
"""

import sys
import os
import requests
import json
import time
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8001"
TEST_DATABASE_URL = "sqlite:///test_health_tracker.db"

# Test data
TEST_PATIENT = {
    "full_name": "Alice Patient",
    "email": f"patient_{int(time.time())}@test.com",
    "password": "TestPass123",
    "role": "patient"
}

TEST_DOCTOR = {
    "full_name": "Dr. Bob Smith",
    "email": f"doctor_{int(time.time())}@test.com", 
    "password": "DoctorPass123",
    "role": "doctor"
}

# Sample medical report content for testing
SAMPLE_MEDICAL_REPORT = """
LABORATORY RESULTS
Patient: Test Patient
Date: 2024-01-15

COMPLETE BLOOD COUNT:
Hemoglobin: 145 g/L (Normal: 120-160)
White Blood Cell Count: 8.2 x10^9/L (Normal: 4.0-11.0)
Platelet Count: 350 x10^9/L (Normal: 150-450)

BIOCHEMISTRY:
Glucose: 6.8 mmol/L (Normal: 3.9-6.1)
Total Cholesterol: 5.8 mmol/L (Normal: <5.2)
HDL Cholesterol: 1.2 mmol/L (Normal: >1.0)
LDL Cholesterol: 4.1 mmol/L (Normal: <3.4)
Triglycerides: 2.1 mmol/L (Normal: <1.7)

LIVER FUNCTION:
ALT: 66 U/L (Normal: 7-45)
AST: 52 U/L (Normal: 8-40)
Bilirubin: 15 μmol/L (Normal: 5-21)

KIDNEY FUNCTION:
Creatinine: 98 μmol/L (Normal: 60-110)
BUN: 6.2 mmol/L (Normal: 2.5-7.5)

THYROID FUNCTION:
TSH: 3.8 mIU/L (Normal: 0.4-4.0)
Free T4: 16 pmol/L (Normal: 12-22)

Notes: Patient shows elevated glucose, cholesterol, and liver enzymes.
Recommend follow-up with endocrinologist and gastroenterologist.
"""

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_test(test_name: str):
    print(f"\n{Colors.CYAN}🧪 Testing: {test_name}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.PURPLE}ℹ️  {message}{Colors.END}")

class TestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_info: Optional[Dict] = None
        self.temp_files: List[str] = []
    
    def cleanup_files(self):
        """Clean up temporary test files"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print_warning(f"Failed to cleanup file {file_path}: {e}")
        self.temp_files.clear()
    
    def create_test_file(self, content: str, filename: str = "test_report.txt") -> str:
        """Create a temporary test file"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.temp_files.append(file_path)
        return file_path
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.token:
            raise ValueError("No token available. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    # Authentication methods
    def register(self, user_data: Dict) -> tuple[Dict, int]:
        """Register a new user"""
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json(), response.status_code
            else:
                return {"error": f"Non-JSON response: {response.text[:200]}"}, response.status_code
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}, 500
    
    def login(self, email: str, password: str) -> tuple[Dict, int]:
        """Login and store token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
                if response.status_code == 200:
                    self.token = data.get("access_token")
                    self.user_info = data.get("user")
                return data, response.status_code
            else:
                return {"error": f"Non-JSON response: {response.text[:200]}"}, response.status_code
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}, 500
    
    def get_profile(self) -> tuple[Dict, int]:
        """Get current user profile"""
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def update_profile(self, update_data: Dict) -> tuple[Dict, int]:
        """Update user profile"""
        response = requests.put(
            f"{self.base_url}/auth/me",
            json=update_data,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # File upload and OCR methods
    def upload_file(self, file_path: str) -> tuple[Dict, int]:
        """Upload a file"""
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers={"Authorization": f"Bearer {self.token}"}
            )
        return response.json(), response.status_code
    
    def process_ocr(self, filename: str) -> tuple[Dict, int]:
        """Process OCR on uploaded file"""
        response = requests.get(
            f"{self.base_url}/ocr/{filename}",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def process_ocr_with_explanations(self, filename: str) -> tuple[Dict, int]:
        """Process OCR with individual explanations"""
        response = requests.get(
            f"{self.base_url}/ocr/{filename}/with-explanations",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # Analysis methods
    def analyze_text(self, text: str) -> tuple[Dict, int]:
        """Analyze raw text"""
        response = requests.post(
            f"{self.base_url}/analysis/text",
            json={"raw_text": text},
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def explain_metrics(self, metrics: List[Dict]) -> tuple[Dict, int]:
        """Get individual metric explanations"""
        response = requests.post(
            f"{self.base_url}/analysis/metrics/explain",
            json={"metrics": metrics},
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_metrics_by_status(self, status: str, metrics: List[Dict] = None) -> tuple[Dict, int]:
        """Get metrics filtered by status"""
        params = {"metrics": json.dumps(metrics)} if metrics else {}
        response = requests.get(
            f"{self.base_url}/analysis/metrics/status/{status}",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # Chat methods
    def send_message(self, receiver_id: int, message_text: str, file_path: str = None) -> tuple[Dict, int]:
        """Send a chat message with optional file attachment"""
        data = {
            "receiver_id": receiver_id,
            "message_text": message_text
        }
        
        files = None
        if file_path and os.path.exists(file_path):
            files = {"file": (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/send",
                data=data,
                files=files,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.json(), response.status_code
        finally:
            if files and "file" in files:
                files["file"][1].close()
    
    def get_chat_history(self, user_id: int, limit: int = 50, offset: int = 0) -> tuple[Dict, int]:
        """Get conversation history with a user"""
        params = {"with_user": user_id, "limit": limit, "offset": offset}
        response = requests.get(
            f"{self.base_url}/chat/history",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_conversations(self) -> tuple[Dict, int]:
        """Get all conversations"""
        response = requests.get(
            f"{self.base_url}/chat/conversations",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_chat_users(self) -> tuple[Dict, int]:
        """Get available users for chat"""
        response = requests.get(
            f"{self.base_url}/chat/users",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def mark_messages_read(self, user_id: int) -> tuple[Dict, int]:
        """Mark messages from a user as read"""
        response = requests.put(
            f"{self.base_url}/chat/mark-read/{user_id}",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # User history methods
    def get_health_analyses(self, limit: int = 50, offset: int = 0) -> tuple[Dict, int]:
        """Get user's health analyses"""
        params = {"limit": limit, "offset": offset}
        response = requests.get(
            f"{self.base_url}/users/me/analyses",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_health_analysis(self, analysis_id: int) -> tuple[Dict, int]:
        """Get specific health analysis"""
        response = requests.get(
            f"{self.base_url}/users/me/analyses/{analysis_id}",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def delete_health_analysis(self, analysis_id: int) -> tuple[Dict, int]:
        """Delete health analysis"""
        response = requests.delete(
            f"{self.base_url}/users/me/analyses/{analysis_id}",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_chat_interactions(self, interaction_type: str = None, limit: int = 50) -> tuple[Dict, int]:
        """Get AI chat interactions"""
        params = {"limit": limit}
        if interaction_type:
            params["interaction_type"] = interaction_type
        response = requests.get(
            f"{self.base_url}/users/me/chats",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_user_history(self, analyses_limit: int = 10, chats_limit: int = 10) -> tuple[Dict, int]:
        """Get complete user history"""
        params = {"analyses_limit": analyses_limit, "chats_limit": chats_limit}
        response = requests.get(
            f"{self.base_url}/users/me/history",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_user_activity(self, days: int = 30) -> tuple[Dict, int]:
        """Get user activity summary"""
        params = {"days": days}
        response = requests.get(
            f"{self.base_url}/users/me/activity",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_user_stats(self) -> tuple[Dict, int]:
        """Get user statistics"""
        response = requests.get(
            f"{self.base_url}/users/me/stats",
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # Disease prediction methods
    def predict_diseases(self, metrics: List[Dict], include_explanations: bool = True) -> tuple[Dict, int]:
        """Get disease predictions based on metrics"""
        data = {
            "metrics": metrics,
            "include_explanations": include_explanations
        }
        response = requests.post(
            f"{self.base_url}/disease-prediction/predict",
            json=data,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    def get_disease_prediction_history(self, limit: int = 50, offset: int = 0) -> tuple[Dict, int]:
        """Get disease prediction history"""
        params = {"limit": limit, "offset": offset}
        response = requests.get(
            f"{self.base_url}/disease-prediction/history",
            params=params,
            headers=self.get_headers()
        )
        return response.json(), response.status_code
    
    # Doctor recommendations methods
    def get_doctor_recommendations(self, metrics: List[Dict]) -> tuple[Dict, int]:
        """Get doctor recommendations based on metrics"""
        data = {"metrics": metrics}
        response = requests.post(
            f"{self.base_url}/recommendations/analyze",
            json=data,
            headers=self.get_headers()
        )
        return response.json(), response.status_code


class ComprehensiveAPITester:
    def __init__(self):
        self.patient_client = TestClient(BASE_URL)
        self.doctor_client = TestClient(BASE_URL)
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        self.analysis_id = None
        self.message_id = None
    
    def record_test_result(self, test_name: str, success: bool, details: str = ""):
        """Record test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            print_success(f"{test_name} - {details}")
        else:
            self.test_results["failed_tests"] += 1
            print_error(f"{test_name} - {details}")
        
        self.test_results["test_details"].append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_server_health(self) -> bool:
        """Test if server is running"""
        print_test("Server Health Check")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.record_test_result("Server Health", True, "Server is running")
                return True
            else:
                self.record_test_result("Server Health", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.record_test_result("Server Health", False, f"Connection failed: {e}")
            return False
    
    def test_authentication_system(self) -> bool:
        """Test complete authentication system"""
        print_header("AUTHENTICATION SYSTEM TESTS")
        
        # Test patient registration
        print_test("Patient Registration")
        data, status = self.patient_client.register(TEST_PATIENT)
        if status == 201:
            self.record_test_result("Patient Registration", True, f"Registered: {data.get('full_name', 'Unknown')}")
        else:
            error_msg = data.get('error', data) if isinstance(data, dict) else str(data)
            self.record_test_result("Patient Registration", False, f"Status {status}: {error_msg}")
            print_error(f"Registration failed with response: {data}")
            return False
        
        # Test doctor registration
        print_test("Doctor Registration")
        data, status = self.doctor_client.register(TEST_DOCTOR)
        if status == 201:
            self.record_test_result("Doctor Registration", True, f"Registered: {data.get('full_name', 'Unknown')}")
        else:
            error_msg = data.get('error', data) if isinstance(data, dict) else str(data)
            self.record_test_result("Doctor Registration", False, f"Status {status}: {error_msg}")
            print_error(f"Registration failed with response: {data}")
            return False
        
        # Test patient login
        print_test("Patient Login")
        data, status = self.patient_client.login(TEST_PATIENT["email"], TEST_PATIENT["password"])
        if status == 200 and "access_token" in data:
            self.record_test_result("Patient Login", True, "Token received")
        else:
            self.record_test_result("Patient Login", False, f"Status {status}: {data}")
            return False
        
        # Test doctor login
        print_test("Doctor Login")
        data, status = self.doctor_client.login(TEST_DOCTOR["email"], TEST_DOCTOR["password"])
        if status == 200 and "access_token" in data:
            self.record_test_result("Doctor Login", True, "Token received")
        else:
            self.record_test_result("Doctor Login", False, f"Status {status}: {data}")
            return False
        
        # Test profile access
        print_test("Profile Access")
        data, status = self.patient_client.get_profile()
        if status == 200 and data["role"] == "patient":
            self.record_test_result("Profile Access", True, f"Patient profile: {data['full_name']}")
        else:
            self.record_test_result("Profile Access", False, f"Status {status}: {data}")
            return False
        
        # Test unauthorized access
        print_test("Unauthorized Access Protection")
        response = requests.get(f"{BASE_URL}/users/me/analyses")
        if response.status_code in [401, 403]:
            self.record_test_result("Unauthorized Access", True, "Correctly rejected")
        else:
            self.record_test_result("Unauthorized Access", False, f"Should reject, got {response.status_code}")
        
        return True
    
    def test_file_upload_and_ocr(self) -> bool:
        """Test file upload and OCR processing"""
        print_header("FILE UPLOAD & OCR PROCESSING TESTS")
        
        # Create test file
        test_file = self.patient_client.create_test_file(SAMPLE_MEDICAL_REPORT, "medical_report.txt")
        
        # Test file upload
        print_test("File Upload")
        data, status = self.patient_client.upload_file(test_file)
        if status == 200 and "filename" in data:
            filename = data["filename"]
            self.record_test_result("File Upload", True, f"Uploaded: {filename}")
        else:
            self.record_test_result("File Upload", False, f"Status {status}: {data}")
            return False
        
        # Test basic OCR processing
        print_test("Basic OCR Processing")
        data, status = self.patient_client.process_ocr(filename)
        if status == 200 and "extracted_text" in data and "analysis" in data:
            self.record_test_result("Basic OCR", True, f"Extracted {len(data['extracted_text'])} characters")
            if data.get("saved_to_history"):
                self.analysis_id = data.get("analysis_id")
        else:
            self.record_test_result("Basic OCR", False, f"Status {status}: {data}")
        
        # Test OCR with explanations
        print_test("OCR with Individual Explanations")
        test_file2 = self.patient_client.create_test_file(SAMPLE_MEDICAL_REPORT, "medical_report2.txt")
        upload_data, upload_status = self.patient_client.upload_file(test_file2)
        if upload_status == 200:
            data, status = self.patient_client.process_ocr_with_explanations(upload_data["filename"])
            if status == 200 and "metrics" in data and "overall_summary" in data:
                self.record_test_result("OCR with Explanations", True, f"Got {len(data['metrics'])} metrics")
                if not self.analysis_id:
                    self.analysis_id = data.get("analysis_id")
            else:
                self.record_test_result("OCR with Explanations", False, f"Status {status}: {data}")
        
        return True
    
    def test_analysis_endpoints(self) -> bool:
        """Test health analysis endpoints"""
        print_header("HEALTH ANALYSIS TESTS")
        
        # Test text analysis
        print_test("Text Analysis")
        data, status = self.patient_client.analyze_text(SAMPLE_MEDICAL_REPORT)
        if status == 200 and "metrics" in data:
            metrics = data["metrics"]
            self.record_test_result("Text Analysis", True, f"Analyzed {len(metrics)} metrics")
        else:
            self.record_test_result("Text Analysis", False, f"Status {status}: {data}")
            return False
        
        # Test metrics by status
        print_test("Metrics by Status")
        data, status = self.patient_client.get_metrics_by_status("high", metrics)
        if status == 200:
            self.record_test_result("Metrics by Status", True, f"Found {len(data)} high metrics")
        else:
            self.record_test_result("Metrics by Status", False, f"Status {status}: {data}")
        
        return True
    
    def test_chat_system(self) -> bool:
        """Test complete chat system"""
        print_header("CHAT COMMUNICATION TESTS")
        
        # Test getting available chat users
        print_test("Available Chat Users")
        data, status = self.patient_client.get_chat_users()
        if status == 200 and isinstance(data, list):
            doctor_found = any(user.get("role") == "doctor" for user in data)
            if doctor_found:
                doctor_id = next(user["user_id"] for user in data if user.get("role") == "doctor")
                self.record_test_result("Available Chat Users", True, f"Found {len(data)} users")
            else:
                self.record_test_result("Available Chat Users", False, "No doctors found")
                return False
        else:
            self.record_test_result("Available Chat Users", False, f"Status {status}: {data}")
            return False
        
        # Test sending message without file
        print_test("Send Text Message")
        message_text = "Hello Doctor, I have some questions about my recent lab results."
        data, status = self.patient_client.send_message(doctor_id, message_text)
        if status == 200 and "id" in data:
            self.message_id = data["id"]
            self.record_test_result("Send Text Message", True, f"Message sent, ID: {self.message_id}")
        else:
            self.record_test_result("Send Text Message", False, f"Status {status}: {data}")
        
        # Test sending message with file
        print_test("Send Message with File")
        test_file = self.doctor_client.create_test_file("Patient consultation notes:\n\nRecommend follow-up in 2 weeks.", "consultation_notes.txt")
        message_text = "Thank you for your question. I've reviewed your results. Please see attached notes."
        data, status = self.doctor_client.send_message(self.patient_client.user_info["id"], message_text, test_file)
        if status == 200 and "attachment_filename" in data:
            self.record_test_result("Send Message with File", True, f"File attached: {data['attachment_filename']}")
        else:
            self.record_test_result("Send Message with File", False, f"Status {status}: {data}")
        
        # Test conversation history
        print_test("Conversation History")
        data, status = self.patient_client.get_chat_history(doctor_id)
        if status == 200 and "messages" in data:
            self.record_test_result("Conversation History", True, f"Retrieved {len(data['messages'])} messages")
        else:
            self.record_test_result("Conversation History", False, f"Status {status}: {data}")
        
        # Test conversations list
        print_test("Conversations List")
        data, status = self.patient_client.get_conversations()
        if status == 200 and "conversations" in data:
            self.record_test_result("Conversations List", True, f"Found {len(data['conversations'])} conversations")
        else:
            self.record_test_result("Conversations List", False, f"Status {status}: {data}")
        
        # Test mark messages as read
        print_test("Mark Messages Read")
        data, status = self.patient_client.mark_messages_read(doctor_id)
        if status == 200:
            self.record_test_result("Mark Messages Read", True, "Messages marked as read")
        else:
            self.record_test_result("Mark Messages Read", False, f"Status {status}: {data}")
        
        return True
    
    def test_user_history_management(self) -> bool:
        """Test user history and statistics"""
        print_header("USER HISTORY & STATISTICS TESTS")
        
        # Test health analyses history
        print_test("Health Analyses History")
        data, status = self.patient_client.get_health_analyses()
        if status == 200 and isinstance(data, list):
            self.record_test_result("Health Analyses History", True, f"Found {len(data)} analyses")
        else:
            self.record_test_result("Health Analyses History", False, f"Status {status}: {data}")
        
        # Test specific analysis retrieval
        if self.analysis_id:
            print_test("Specific Analysis Retrieval")
            data, status = self.patient_client.get_health_analysis(self.analysis_id)
            if status == 200 and "id" in data:
                self.record_test_result("Specific Analysis", True, f"Retrieved analysis {self.analysis_id}")
            else:
                self.record_test_result("Specific Analysis", False, f"Status {status}: {data}")
        
        # Test chat interactions history
        print_test("Chat Interactions History")
        data, status = self.patient_client.get_chat_interactions()
        if status == 200:
            self.record_test_result("Chat Interactions", True, f"Retrieved interactions")
        else:
            self.record_test_result("Chat Interactions", False, f"Status {status}: {data}")
        
        # Test complete user history
        print_test("Complete User History")
        data, status = self.patient_client.get_user_history()
        if status == 200 and "health_analyses" in data and "chat_interactions" in data:
            self.record_test_result("Complete History", True, 
                f"Analyses: {data['total_analyses']}, Chats: {data['total_chats']}")
        else:
            self.record_test_result("Complete History", False, f"Status {status}: {data}")
        
        # Test user activity
        print_test("User Activity Summary")
        data, status = self.patient_client.get_user_activity()
        if status == 200:
            self.record_test_result("User Activity", True, "Activity summary retrieved")
        else:
            self.record_test_result("User Activity", False, f"Status {status}: {data}")
        
        # Test user statistics
        print_test("User Statistics")
        data, status = self.patient_client.get_user_stats()
        if status == 200:
            self.record_test_result("User Statistics", True, "Statistics retrieved")
        else:
            self.record_test_result("User Statistics", False, f"Status {status}: {data}")
        
        return True
    
    def test_disease_prediction(self) -> bool:
        """Test disease prediction system"""
        print_header("DISEASE PREDICTION TESTS")
        
        # Prepare test metrics with some abnormal values
        test_metrics = [
            {
                "name": "glucose",
                "value": 6.8,
                "unit": "mmol/L",
                "reference_range": "3.9-6.1"
            },
            {
                "name": "cholesterol",
                "value": 5.8,
                "unit": "mmol/L", 
                "reference_range": "<5.2"
            },
            {
                "name": "alt",
                "value": 66.0,
                "unit": "U/L",
                "reference_range": "7-45"
            }
        ]
        
        # Test disease prediction
        print_test("Disease Risk Prediction")
        data, status = self.patient_client.predict_diseases(test_metrics)
        if status == 200 and "predicted_diseases" in data:
            diseases = data["predicted_diseases"]
            self.record_test_result("Disease Prediction", True, f"Predicted {len(diseases)} disease risks")
        else:
            self.record_test_result("Disease Prediction", False, f"Status {status}: {data}")
        
        # Test prediction history
        print_test("Disease Prediction History")
        data, status = self.patient_client.get_disease_prediction_history()
        if status == 200:
            self.record_test_result("Prediction History", True, "History retrieved")
        else:
            self.record_test_result("Prediction History", False, f"Status {status}: {data}")
        
        return True
    
    def test_doctor_recommendations(self) -> bool:
        """Test doctor recommendations system"""
        print_header("DOCTOR RECOMMENDATIONS TESTS")
        
        # Test with metrics that should trigger specialist recommendations
        test_metrics = [
            {
                "name": "ALT",
                "value": 66.19,
                "unit": "U/L",
                "reference_range": "3-45",
                "status": "high"
            },
            {
                "name": "glucose",
                "value": 6.8,
                "unit": "mmol/L",
                "reference_range": "3.9-6.1",
                "status": "high"
            },
            {
                "name": "cholesterol",
                "value": 5.8,
                "unit": "mmol/L",
                "reference_range": "<5.2",
                "status": "high"
            }
        ]
        
        print_test("AI Doctor Recommendations")
        data, status = self.patient_client.get_doctor_recommendations(test_metrics)
        if status == 200 and "recommendations" in data:
            recommendations = data["recommendations"]
            self.record_test_result("Doctor Recommendations", True, 
                f"Got {len(recommendations)} specialist recommendations")
        else:
            self.record_test_result("Doctor Recommendations", False, f"Status {status}: {data}")
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling and edge cases"""
        print_header("ERROR HANDLING TESTS")
        
        # Test invalid file upload
        print_test("Invalid File Upload")
        response = requests.post(
            f"{BASE_URL}/upload",
            files={"file": ("test.exe", b"invalid binary data", "application/octet-stream")},
            headers={"Authorization": f"Bearer {self.patient_client.token}"}
        )
        if response.status_code == 400:
            self.record_test_result("Invalid File Upload", True, "Correctly rejected invalid file")
        else:
            self.record_test_result("Invalid File Upload", False, f"Should reject, got {response.status_code}")
        
        # Test invalid token
        print_test("Invalid Token")
        response = requests.get(
            f"{BASE_URL}/users/me/analyses",
            headers={"Authorization": "Bearer invalid_token"}
        )
        if response.status_code in [401, 403]:
            self.record_test_result("Invalid Token", True, "Correctly rejected invalid token")
        else:
            self.record_test_result("Invalid Token", False, f"Should reject, got {response.status_code}")
        
        # Test non-existent resource
        print_test("Non-existent Resource")
        data, status = self.patient_client.get_health_analysis(99999)
        if status == 404:
            self.record_test_result("Non-existent Resource", True, "Correctly returned 404")
        else:
            self.record_test_result("Non-existent Resource", False, f"Expected 404, got {status}")
        
        return True
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflows"""
        print_header("END-TO-END WORKFLOW TESTS")
        
        print_test("Complete Patient Journey")
        
        # 1. Patient uploads medical report
        test_file = self.patient_client.create_test_file(SAMPLE_MEDICAL_REPORT, "complete_workflow.txt")
        upload_data, upload_status = self.patient_client.upload_file(test_file)
        
        if upload_status != 200:
            self.record_test_result("E2E Patient Journey", False, "Failed at file upload")
            return False
        
        # 2. Process OCR and get analysis
        ocr_data, ocr_status = self.patient_client.process_ocr_with_explanations(upload_data["filename"])
        
        if ocr_status != 200:
            self.record_test_result("E2E Patient Journey", False, "Failed at OCR processing")
            return False
        
        # 3. Get disease predictions
        if "metrics" in ocr_data:
            # Convert metrics for disease prediction
            prediction_metrics = []
            for metric in ocr_data["metrics"][:3]:  # Use first 3 metrics
                if isinstance(metric, dict) and "name" in metric:
                    prediction_metrics.append({
                        "name": metric["name"],
                        "value": float(metric.get("value", 0)),
                        "unit": metric.get("unit", ""),
                        "reference_range": metric.get("reference_range", "")
                    })
            
            if prediction_metrics:
                pred_data, pred_status = self.patient_client.predict_diseases(prediction_metrics)
                if pred_status != 200:
                    print_warning("Disease prediction failed in E2E test")
        
        # 4. Get doctor recommendations
        if "metrics" in ocr_data:
            rec_metrics = []
            for metric in ocr_data["metrics"][:3]:
                if isinstance(metric, dict):
                    rec_metrics.append({
                        "name": metric.get("name", ""),
                        "value": float(metric.get("value", 0)),
                        "unit": metric.get("unit", ""),
                        "reference_range": metric.get("reference_range", ""),
                        "status": metric.get("status", "normal")
                    })
            
            if rec_metrics:
                rec_data, rec_status = self.patient_client.get_doctor_recommendations(rec_metrics)
                if rec_status != 200:
                    print_warning("Doctor recommendations failed in E2E test")
        
        # 5. Send message to doctor
        if self.doctor_client.user_info:
            message_data, message_status = self.patient_client.send_message(
                self.doctor_client.user_info["id"],
                "I've uploaded my lab results. Could you please review them?"
            )
            if message_status != 200:
                print_warning("Message sending failed in E2E test")
        
        # 6. Check user history
        history_data, history_status = self.patient_client.get_user_history()
        if history_status != 200:
            self.record_test_result("E2E Patient Journey", False, "Failed to retrieve user history")
            return False
        
        self.record_test_result("E2E Patient Journey", True, 
            f"Complete workflow: Upload → OCR → Analysis → Predictions → Messaging → History")
        
        return True
    
    def cleanup(self):
        """Clean up test data and files"""
        print_header("CLEANUP")
        
        # Clean up temporary files
        self.patient_client.cleanup_files()
        self.doctor_client.cleanup_files()
        
        # Optionally delete test analysis if we have the ID
        if self.analysis_id:
            try:
                self.patient_client.delete_health_analysis(self.analysis_id)
                print_info(f"Cleaned up test analysis {self.analysis_id}")
            except Exception as e:
                print_warning(f"Could not clean up analysis: {e}")
        
        print_info("Cleanup completed")
    
    def print_final_report(self):
        """Print final test results"""
        print_header("TEST RESULTS SUMMARY")
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}📊 COMPREHENSIVE API TEST RESULTS{Colors.END}")
        print(f"{Colors.CYAN}{'='*50}{Colors.END}")
        print(f"{Colors.GREEN}✅ Tests Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}❌ Tests Failed: {failed}{Colors.END}")
        print(f"{Colors.BLUE}📈 Total Tests: {total}{Colors.END}")
        print(f"{Colors.PURPLE}🎯 Success Rate: {success_rate:.1f}%{Colors.END}")
        
        if failed > 0:
            print(f"\n{Colors.YELLOW}⚠️  FAILED TESTS:{Colors.END}")
            for result in self.test_results["test_details"]:
                if not result["success"]:
                    print(f"{Colors.RED}  • {result['test']}: {result['details']}{Colors.END}")
        
        if success_rate >= 90:
            print(f"\n{Colors.GREEN}🎉 EXCELLENT! All major functionality is working properly.{Colors.END}")
        elif success_rate >= 75:
            print(f"\n{Colors.YELLOW}👍 GOOD! Most functionality is working with minor issues.{Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️  ATTENTION NEEDED! Multiple critical issues detected.{Colors.END}")
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print_header("AI HEALTH TRACKER - COMPREHENSIVE API TESTING")
        print_info(f"Testing server at: {BASE_URL}")
        print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Core system tests
            if not self.test_server_health():
                print_error("Server is not running! Please start the server first.")
                return False
            
            self.test_authentication_system()
            self.test_file_upload_and_ocr()
            self.test_analysis_endpoints()
            self.test_chat_system()
            self.test_user_history_management()
            self.test_disease_prediction()
            self.test_doctor_recommendations()
            self.test_error_handling()
            self.test_end_to_end_workflow()
            
        except KeyboardInterrupt:
            print_warning("\nTesting interrupted by user")
        except Exception as e:
            print_error(f"Unexpected error during testing: {e}")
        finally:
            self.cleanup()
            self.print_final_report()
        
        return self.test_results["failed_tests"] == 0


def main():
    """Main test execution"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🏥 AI HEALTH TRACKER - COMPREHENSIVE API TEST SUITE")
    print("=" * 60)
    print("Testing all endpoints, workflows, and integrations")
    print(f"{'=' * 60}{Colors.END}")
    
    tester = ComprehensiveAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 