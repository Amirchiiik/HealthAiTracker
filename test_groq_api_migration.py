#!/usr/bin/env python3
"""
Test script for Groq API migration verification
"""

import sys
import os
import requests
from typing import Dict

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import llm_service, analysis_service

# Configuration for testing
BASE_URL = "http://127.0.0.1:8000"

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

def test_groq_api_key_setup():
    """Test if Groq API key is configured"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY=your_groq_api_key_here")
        return False
    
    print(f"✅ GROQ_API_KEY configured: {groq_api_key[:10]}...")
    return True

def test_llm_service_direct():
    """Test LLM service directly"""
    print("\n🧪 Testing LLM Service Direct Calls")
    print("=" * 40)
    
    # Test sample medical text
    sample_text = """
    Гемоглобин: 140 г/л (норма: 120-160)
    Лейкоциты: 8.5 x10^9/л (норма: 4.0-9.0)
    Тромбоциты: 350 x10^9/л (норма: 150-400)
    """
    
    try:
        print("📝 Testing general explanation generation...")
        explanation = llm_service.generate_explanation(sample_text)
        print(f"✅ General explanation received: {len(explanation)} characters")
        print(f"Preview: {explanation[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Direct LLM service test failed: {e}")
        return False

def test_individual_metric_explanations():
    """Test individual metric explanations"""
    print("\n🔬 Testing Individual Metric Explanations")
    print("=" * 40)
    
    # Sample metrics data
    sample_metrics = [
        {
            "name": "Гемоглобин",
            "value": 140.0,
            "unit": "г/л",
            "reference_range": "120-160",
            "status": "normal"
        },
        {
            "name": "Глюкоза",
            "value": 110.0,
            "unit": "мг/дл",
            "reference_range": "70-99",
            "status": "high"
        }
    ]
    
    try:
        print("🔍 Testing individual metric explanations...")
        explained_metrics = llm_service.generate_individual_metric_explanations(sample_metrics)
        
        if len(explained_metrics) == len(sample_metrics):
            print(f"✅ Individual explanations generated for {len(explained_metrics)} metrics")
            
            for i, metric in enumerate(explained_metrics):
                if 'explanation' in metric:
                    print(f"✅ Metric {i+1}: {metric['name']} has explanation ({len(metric['explanation'])} chars)")
                else:
                    print(f"❌ Metric {i+1}: {metric['name']} missing explanation")
                    return False
            return True
        else:
            print(f"❌ Expected {len(sample_metrics)} metrics, got {len(explained_metrics)}")
            return False
            
    except Exception as e:
        print(f"❌ Individual metric explanations test failed: {e}")
        return False

def test_analysis_service_integration():
    """Test analysis service integration with Groq API"""
    print("\n🏥 Testing Analysis Service Integration")
    print("=" * 40)
    
    sample_text = """
    Результаты анализа крови:
    Гемоглобин: 140 г/л (норма: 120-160)
    Эритроциты: 4.5 x10^12/л (норма: 4.0-5.0)
    Лейкоциты: 12.0 x10^9/л (норма: 4.0-9.0)
    """
    
    try:
        print("🔄 Testing complete analysis with explanations...")
        result = analysis_service.analyze_metrics_from_text_with_explanations(sample_text)
        
        if 'metrics' in result and 'overall_summary' in result:
            print(f"✅ Analysis service returned complete result")
            print(f"📊 Metrics analyzed: {len(result['metrics'])}")
            print(f"📝 Summary length: {len(result['overall_summary'])} characters")
            
            # Check if metrics have explanations
            metrics_with_explanations = 0
            for metric in result['metrics']:
                if 'explanation' in metric and metric['explanation']:
                    metrics_with_explanations += 1
            
            print(f"✅ Metrics with explanations: {metrics_with_explanations}/{len(result['metrics'])}")
            return True
        else:
            print("❌ Analysis service returned incomplete result")
            return False
            
    except Exception as e:
        print(f"❌ Analysis service integration test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints with authentication"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 40)
    
    # First login to get token
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "patient@test.com", "password": "TestPass123"}
        )
        
        if login_response.status_code != 200:
            print("❌ Could not login - please ensure test user exists")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test the explain/metrics endpoint
        print("🔍 Testing /explain/metrics endpoint...")
        explain_response = requests.post(
            f"{BASE_URL}/explain/metrics",
            json={"raw_text": "Гемоглобин: 140 г/л (норма: 120-160)"},
            headers=headers
        )
        
        if explain_response.status_code == 200:
            result = explain_response.json()
            print(f"✅ Explain endpoint working: {len(result.get('metrics', []))} metrics")
            print(f"📝 Summary: {len(result.get('overall_summary', ''))} characters")
            return True
        else:
            print(f"❌ Explain endpoint failed: {explain_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def main():
    """Run all Groq API migration tests"""
    print("🚀 Starting Groq API Migration Tests")
    print("=" * 50)
    
    # Check server health
    if not test_server_health():
        print("❌ Server is not running. Please start the server first.")
        print("Run: python -m uvicorn app.main:app --reload")
        sys.exit(1)
    print("✅ Server is running")
    
    # Check Groq API key
    if not test_groq_api_key_setup():
        sys.exit(1)
    
    # Run tests
    tests = [
        test_llm_service_direct,
        test_individual_metric_explanations,
        test_analysis_service_integration,
        test_api_endpoints
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
        print("🎉 All Groq API migration tests passed!")
        print("\n✅ Migration Summary:")
        print("- Groq API is properly configured")
        print("- General explanations are working")
        print("- Individual metric explanations are working")
        print("- Analysis service integration is working")
        print("- API endpoints are functioning correctly")
        print("\n🚀 The system is ready to use with Groq API!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the errors above.")
        print("\n📝 Common issues:")
        print("- Ensure GROQ_API_KEY environment variable is set")
        print("- Verify Groq API key has proper permissions")
        print("- Check internet connectivity for API calls")
        print("- Ensure test user credentials are correct")
        sys.exit(1)

if __name__ == "__main__":
    main() 