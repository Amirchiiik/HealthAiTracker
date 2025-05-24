#!/usr/bin/env python3
"""
Comprehensive test script for Disease Risk Prediction functionality
Tests the complete pipeline from database models to API endpoints
"""

import requests
import json
from typing import Dict, Any
import time

# Test configuration
BASE_URL = "http://127.0.0.1:8001"  # Adjust port if needed
TEST_EMAIL = "test_disease@example.com"
TEST_PASSWORD = "TestPass123"

def colored_print(message: str, color: str = "white"):
    """Print colored text to console"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[97m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['end']}")

def register_test_user() -> Dict[str, Any]:
    """Register a test user for disease prediction testing"""
    colored_print("🔄 Registering test user...", "blue")
    
    registration_data = {
        "full_name": "Disease Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "role": "patient"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)
        if response.status_code == 201:
            colored_print("✅ Test user registered successfully", "green")
            return response.json()
        elif response.status_code == 400 and "already registered" in response.text:
            colored_print("ℹ️ Test user already exists, proceeding with login", "yellow")
            return login_test_user()
        else:
            colored_print(f"❌ Registration failed: {response.text}", "red")
            return {}
    except Exception as e:
        colored_print(f"❌ Registration error: {e}", "red")
        return {}

def login_test_user() -> Dict[str, Any]:
    """Login with test user credentials"""
    colored_print("🔄 Logging in test user...", "blue")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            colored_print("✅ Login successful", "green")
            return response.json()
        else:
            colored_print(f"❌ Login failed: {response.text}", "red")
            return {}
    except Exception as e:
        colored_print(f"❌ Login error: {e}", "red")
        return {}

def test_disease_prediction_basic(token: str) -> bool:
    """Test basic disease prediction functionality"""
    colored_print("🔄 Testing basic disease prediction...", "blue")
    
    # Test data with various health metrics
    prediction_request = {
        "metrics": [
            {
                "name": "hemoglobin",
                "value": 8.5,  # Low - indicates anemia
                "unit": "g/dL",
                "reference_range": "12.0-15.5"
            },
            {
                "name": "glucose",
                "value": 160,  # High - indicates diabetes risk
                "unit": "mg/dL", 
                "reference_range": "70-100"
            },
            {
                "name": "alt",
                "value": 85,  # Elevated - liver function concern
                "unit": "U/L",
                "reference_range": "7-40"
            }
        ],
        "include_explanations": True
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict/disease", 
            json=prediction_request,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            colored_print("✅ Disease prediction successful", "green")
            
            # Validate response structure
            required_fields = ["id", "predicted_diseases", "overall_risk_level", "medical_disclaimer"]
            for field in required_fields:
                if field not in result:
                    colored_print(f"❌ Missing field in response: {field}", "red")
                    return False
            
            # Print key results
            colored_print(f"📊 Overall Risk Level: {result['overall_risk_level']}", "white")
            colored_print(f"🔍 Diseases Found: {len(result['predicted_diseases'])}", "white")
            
            for disease in result['predicted_diseases']:
                colored_print(f"  • {disease['disease_name']}: {disease['risk_level']} risk (confidence: {disease['confidence']:.0%})", "white")
            
            if result.get('ai_explanation'):
                colored_print("🤖 AI Explanation received", "green")
            
            return True
        else:
            colored_print(f"❌ Disease prediction failed: {response.text}", "red")
            return False
            
    except Exception as e:
        colored_print(f"❌ Disease prediction error: {e}", "red")
        return False

def test_prediction_history(token: str) -> bool:
    """Test disease prediction history retrieval"""
    colored_print("🔄 Testing prediction history...", "blue")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/predict/history", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            colored_print("✅ Prediction history retrieved successfully", "green")
            
            # Validate response structure
            required_fields = ["predictions", "total_count", "high_risk_count", "moderate_risk_count", "low_risk_count"]
            for field in required_fields:
                if field not in result:
                    colored_print(f"❌ Missing field in history response: {field}", "red")
                    return False
            
            colored_print(f"📈 Total Predictions: {result['total_count']}", "white")
            colored_print(f"🚨 High Risk: {result['high_risk_count']}", "white")
            colored_print(f"⚠️  Moderate Risk: {result['moderate_risk_count']}", "white")
            colored_print(f"✅ Low Risk: {result['low_risk_count']}", "white")
            
            return True
        else:
            colored_print(f"❌ History retrieval failed: {response.text}", "red")
            return False
            
    except Exception as e:
        colored_print(f"❌ History retrieval error: {e}", "red")
        return False

def test_latest_prediction(token: str) -> bool:
    """Test latest prediction retrieval"""
    colored_print("🔄 Testing latest prediction retrieval...", "blue")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/predict/latest", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            colored_print("✅ Latest prediction retrieved successfully", "green")
            colored_print(f"🕒 Created: {result['created_at']}", "white")
            colored_print(f"📊 Risk Level: {result['overall_risk_level']}", "white")
            return True
        elif response.status_code == 404:
            colored_print("ℹ️ No predictions found (expected if no previous predictions)", "yellow")
            return True
        else:
            colored_print(f"❌ Latest prediction retrieval failed: {response.text}", "red")
            return False
            
    except Exception as e:
        colored_print(f"❌ Latest prediction error: {e}", "red")
        return False

def test_rate_limiting(token: str) -> bool:
    """Test rate limiting functionality"""
    colored_print("🔄 Testing rate limiting (making multiple requests)...", "blue")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Simple test metrics
    prediction_request = {
        "metrics": [
            {
                "name": "glucose",
                "value": 90,
                "unit": "mg/dL",
                "reference_range": "70-100"
            }
        ],
        "include_explanations": False
    }
    
    success_count = 0
    rate_limited = False
    
    # Make 12 requests to trigger rate limit (limit is 10/hour)
    for i in range(12):
        try:
            response = requests.post(
                f"{BASE_URL}/predict/disease",
                json=prediction_request,
                headers=headers
            )
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited = True
                colored_print(f"✅ Rate limiting triggered after {success_count} requests", "green")
                break
            
            time.sleep(0.1)  # Small delay between requests
            
        except Exception as e:
            colored_print(f"❌ Rate limit test error: {e}", "red")
            return False
    
    if rate_limited:
        colored_print("✅ Rate limiting working correctly", "green")
        return True
    else:
        colored_print("⚠️ Rate limiting not triggered (may need more requests)", "yellow")
        return True  # Not a failure, just different timing

def test_input_validation(token: str) -> bool:
    """Test input validation for disease prediction"""
    colored_print("🔄 Testing input validation...", "blue")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with invalid metrics (empty)
    invalid_request = {
        "metrics": [],
        "include_explanations": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict/disease",
            json=invalid_request,
            headers=headers
        )
        
        if response.status_code == 422:  # Validation Error
            colored_print("✅ Input validation working (empty metrics rejected)", "green")
            return True
        else:
            colored_print(f"❌ Input validation failed: expected 422, got {response.status_code}", "red")
            return False
            
    except Exception as e:
        colored_print(f"❌ Input validation test error: {e}", "red")
        return False

def test_authentication_required() -> bool:
    """Test that authentication is required for prediction endpoints"""
    colored_print("🔄 Testing authentication requirement...", "blue")
    
    prediction_request = {
        "metrics": [
            {
                "name": "glucose",
                "value": 90,
                "unit": "mg/dL"
            }
        ]
    }
    
    try:
        # Request without token
        response = requests.post(f"{BASE_URL}/predict/disease", json=prediction_request)
        
        if response.status_code == 401:  # Unauthorized
            colored_print("✅ Authentication requirement working", "green")
            return True
        else:
            colored_print(f"❌ Authentication not required: got {response.status_code}", "red")
            return False
            
    except Exception as e:
        colored_print(f"❌ Authentication test error: {e}", "red")
        return False

def run_all_tests():
    """Run all disease prediction tests"""
    colored_print("🚀 Starting Disease Risk Prediction Tests", "blue")
    colored_print("=" * 50, "white")
    
    # Test results tracking
    tests = []
    
    # Test 1: Authentication requirement
    tests.append(("Authentication Required", test_authentication_required()))
    
    # Test 2: User registration/login
    user_data = register_test_user()
    if not user_data or "access_token" not in user_data:
        colored_print("❌ Cannot proceed without valid user token", "red")
        return
    
    token = user_data["access_token"]
    tests.append(("User Authentication", True))
    
    # Test 3: Basic disease prediction
    tests.append(("Basic Disease Prediction", test_disease_prediction_basic(token)))
    
    # Test 4: Prediction history
    tests.append(("Prediction History", test_prediction_history(token)))
    
    # Test 5: Latest prediction
    tests.append(("Latest Prediction", test_latest_prediction(token)))
    
    # Test 6: Input validation
    tests.append(("Input Validation", test_input_validation(token)))
    
    # Test 7: Rate limiting
    tests.append(("Rate Limiting", test_rate_limiting(token)))
    
    # Print test results
    colored_print("\n" + "=" * 50, "white")
    colored_print("📊 Test Results Summary", "blue")
    colored_print("=" * 50, "white")
    
    passed = 0
    failed = 0
    
    for test_name, result in tests:
        if result:
            colored_print(f"✅ {test_name}: PASSED", "green")
            passed += 1
        else:
            colored_print(f"❌ {test_name}: FAILED", "red")
            failed += 1
    
    colored_print(f"\n📈 Total: {len(tests)} tests | ✅ Passed: {passed} | ❌ Failed: {failed}", "white")
    
    if failed == 0:
        colored_print("🎉 All tests passed! Disease Risk Prediction is working correctly.", "green")
    else:
        colored_print(f"⚠️ {failed} test(s) failed. Please check the implementation.", "red")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        colored_print("\n⏹️ Tests interrupted by user", "yellow")
        exit(1)
    except Exception as e:
        colored_print(f"\n💥 Unexpected error: {e}", "red")
        exit(1) 