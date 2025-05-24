#!/usr/bin/env python3
"""
Quick test script for disease prediction functionality
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_disease_prediction():
    print("🚀 Testing Disease Risk Prediction System")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1️⃣ Registering test user...")
    register_data = {
        "full_name": "Disease Test User",
        "email": "disease.test@example.com",
        "password": "TestPass123",
        "role": "patient"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ User registered successfully")
            user_data = response.json()
            token = user_data["access_token"]
        else:
            # User might already exist, try to login
            print("ℹ️ User may already exist, trying login...")
            login_data = {"email": register_data["email"], "password": register_data["password"]}
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ Login successful")
                user_data = response.json()
                token = user_data["access_token"]
            else:
                print(f"❌ Registration/Login failed: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 2: Test disease prediction with HGB value
    print("\n2️⃣ Testing disease prediction...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with your exact request data
    prediction_request = {
        "metrics": [
            {
                "name": "hemoglobin",  # Normalized name
                "value": 163.0,
                "unit": "г/л",
                "reference_range": "130,00 - 160,00"
            }
        ],
        "include_explanations": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict/disease", json=prediction_request, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Disease prediction successful!")
            print(f"📊 Overall Risk Level: {result['overall_risk_level']}")
            print(f"🔍 Diseases Found: {len(result['predicted_diseases'])}")
            
            for disease in result['predicted_diseases']:
                print(f"  • {disease['disease_name']}: {disease['risk_level']} risk (confidence: {disease['confidence']:.0%})")
                print(f"    Description: {disease['description']}")
            
            if result.get('ai_explanation'):
                print(f"\n🤖 AI Explanation: {result['ai_explanation'][:200]}...")
            
            if result.get('recommendations'):
                print(f"\n💡 Recommendations: {result['recommendations'][:200]}...")
            
            print(f"\n⚖️ Medical Disclaimer: {result['medical_disclaimer'][:100]}...")
            
            return True
        else:
            print(f"❌ Disease prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Disease prediction error: {e}")
        return False

if __name__ == "__main__":
    success = test_disease_prediction()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Disease Risk Prediction System is working correctly!")
    else:
        print("❌ There were issues with the Disease Risk Prediction System")
    print("=" * 50) 