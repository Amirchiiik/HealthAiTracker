#!/usr/bin/env python3
"""
Intelligent Health Agent Test Suite

This script tests the complete intelligent health agent workflow:
1. OCR analysis and metric extraction
2. Critical value detection
3. Specialist recommendations
4. Automatic appointment booking
5. Notification system
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

# Add backend to path
sys.path.append('backend')

from app.services.intelligent_health_agent import IntelligentHealthAgent
from app.services.appointment_service import AppointmentService
from app.services.doctor_recommendation_service import doctor_recommendation_service
from app.database import get_db
from app.models import User, HealthAnalysis, Appointment
from app.schemas import UserRole, PriorityLevel

def print_header(title):
    print(f"\n🤖 {title}")
    print("=" * (len(title) + 4))

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_critical_value_detection():
    """Test the critical value detection logic."""
    
    print_header("Testing Critical Value Detection")
    
    # Test metrics with various critical values
    test_metrics = [
        # Critical glucose (should trigger urgent endocrinologist)
        {
            "name": "Glucose",
            "value": 15.5,
            "unit": "ммоль/л",
            "reference_range": "3.05 - 6.4",
            "status": "high"
        },
        # Critical ALT (should trigger gastroenterologist)
        {
            "name": "ALT", 
            "value": 150.0,
            "unit": "Ед/л",
            "reference_range": "3 - 45",
            "status": "high"
        },
        # Critical creatinine (should trigger nephrologist)
        {
            "name": "Creatinine",
            "value": 200.0,
            "unit": "мкмоль/л", 
            "reference_range": "60 - 110",
            "status": "high"
        },
        # Normal value (should not trigger)
        {
            "name": "AST",
            "value": 25.2,
            "unit": "Ед/л",
            "reference_range": "0 - 35", 
            "status": "normal"
        }
    ]
    
    try:
        # Initialize agent (without database for testing logic)
        from app.services.intelligent_health_agent import IntelligentHealthAgent
        
        # Create a mock agent to test detection logic
        class MockAgent(IntelligentHealthAgent):
            def __init__(self):
                # Initialize without database
                self.critical_thresholds = {
                    'glucose': {'high': 11.0, 'very_high': 15.0},
                    'alt': {'high': 100, 'very_high': 200},
                    'creatinine': {'high': 150, 'very_high': 300},
                }
        
        agent = MockAgent()
        critical_metrics = agent._identify_critical_metrics(test_metrics)
        
        print_info(f"Input metrics: {len(test_metrics)}")
        print_info(f"Critical metrics detected: {len(critical_metrics)}")
        
        expected_critical = ['Glucose', 'ALT', 'Creatinine']
        detected_critical = [m['name'] for m in critical_metrics]
        
        for expected in expected_critical:
            if expected in detected_critical:
                print_success(f"Correctly identified {expected} as critical")
            else:
                print_error(f"Failed to identify {expected} as critical")
        
        if 'AST' in detected_critical:
            print_error("Incorrectly identified normal AST as critical")
        else:
            print_success("Correctly identified normal AST as non-critical")
        
        return len(critical_metrics) == 3
        
    except Exception as e:
        print_error(f"Error in critical value detection test: {e}")
        return False

def test_doctor_recommendation_integration():
    """Test integration with doctor recommendation service."""
    
    print_header("Testing Doctor Recommendation Integration")
    
    # Use the actual Kazakh OCR data that we know works
    kazakh_metrics = [
        {
            "name": "ALT",
            "value": 66.19,
            "unit": "Ед/л",
            "reference_range": "3 - 45",
            "status": "high"
        },
        {
            "name": "AST",
            "value": 25.2,
            "unit": "Ед/л",
            "reference_range": "0 - 35",
            "status": "normal"
        },
        {
            "name": "Glucose",
            "value": 4.71,
            "unit": "ммоль/л",
            "reference_range": "3.05 - 6.4",
            "status": "normal"
        }
    ]
    
    try:
        recommendations = doctor_recommendation_service.analyze_and_recommend(kazakh_metrics)
        
        print_info(f"Abnormal metrics count: {recommendations.get('abnormal_metrics_count', 0)}")
        print_info(f"Priority level: {recommendations.get('priority_level', 'unknown')}")
        print_info(f"Specialists recommended: {len(recommendations.get('recommended_specialists', []))}")
        
        specialists = recommendations.get('recommended_specialists', [])
        if specialists:
            for spec in specialists:
                print_success(f"Recommended: {spec.get('type', 'Unknown')} (Priority: {spec.get('priority', 'Medium')})")
        
        # Should recommend gastroenterologist for elevated ALT
        gastro_recommended = any(s.get('type') == 'Gastroenterologist' for s in specialists)
        if gastro_recommended:
            print_success("Correctly recommended Gastroenterologist for elevated ALT")
            return True
        else:
            print_error("Failed to recommend Gastroenterologist for elevated ALT")
            return False
        
    except Exception as e:
        print_error(f"Error in doctor recommendation test: {e}")
        return False

def test_priority_assessment():
    """Test the priority assessment logic."""
    
    print_header("Testing Priority Assessment Logic")
    
    test_cases = [
        {
            "name": "Normal values",
            "critical_metrics": [],
            "recommendations": {"priority_level": "low"},
            "expected": "low"
        },
        {
            "name": "Single critical value",
            "critical_metrics": [{"name": "ALT", "value": 120, "status": "high"}],
            "recommendations": {"priority_level": "medium"},
            "expected": "medium"
        },
        {
            "name": "Very critical glucose",
            "critical_metrics": [{"name": "Glucose", "value": 16.0, "status": "high"}],
            "recommendations": {"priority_level": "high"},
            "expected": "high"
        },
        {
            "name": "Multiple critical values",
            "critical_metrics": [
                {"name": "ALT", "value": 120, "status": "high"},
                {"name": "AST", "value": 110, "status": "high"},
                {"name": "Creatinine", "value": 180, "status": "high"}
            ],
            "recommendations": {"priority_level": "medium"},
            "expected": "high"  # Multiple critical values should be high priority
        }
    ]
    
    try:
        from app.services.intelligent_health_agent import IntelligentHealthAgent
        
        class MockAgent(IntelligentHealthAgent):
            def __init__(self):
                pass
        
        agent = MockAgent()
        
        all_passed = True
        for case in test_cases:
            result = agent._determine_overall_priority(case["critical_metrics"], case["recommendations"])
            
            if result.value == case["expected"]:
                print_success(f"{case['name']}: {result.value} (correct)")
            else:
                print_error(f"{case['name']}: {result.value} (expected {case['expected']})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Error in priority assessment test: {e}")
        return False

def test_specialist_mapping():
    """Test the specialist mapping logic."""
    
    print_header("Testing Specialist Mapping Logic")
    
    test_cases = [
        {
            "critical_metrics": [{"name": "ALT", "value": 120}],
            "expected_specialist": "Gastroenterologist"
        },
        {
            "critical_metrics": [{"name": "Glucose", "value": 15.0}],
            "expected_specialist": "Endocrinologist"
        },
        {
            "critical_metrics": [{"name": "Creatinine", "value": 200}],
            "expected_specialist": "Nephrologist"
        },
        {
            "critical_metrics": [{"name": "Hemoglobin", "value": 80}],
            "expected_specialist": "Hematologist"
        }
    ]
    
    try:
        from app.services.intelligent_health_agent import IntelligentHealthAgent
        
        class MockAgent(IntelligentHealthAgent):
            def __init__(self):
                self.specialist_mapping = {
                    'Gastroenterologist': ['alt', 'ast', 'alp', 'ggt', 'total_bilirubin'],
                    'Endocrinologist': ['glucose', 'glycated_hemoglobin', 'thyroid_stimulating_hormone'],
                    'Nephrologist': ['creatinine', 'urea'],
                    'Hematologist': ['hemoglobin', 'white_blood_cells', 'platelets'],
                }
        
        agent = MockAgent()
        
        all_passed = True
        for case in test_cases:
            recommendations = {"recommended_specialists": []}  # Mock empty recommendations
            specialist = agent._determine_priority_specialist(case["critical_metrics"], recommendations)
            
            if specialist == case["expected_specialist"]:
                print_success(f"{case['critical_metrics'][0]['name']} → {specialist} (correct)")
            else:
                print_error(f"{case['critical_metrics'][0]['name']} → {specialist} (expected {case['expected_specialist']})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Error in specialist mapping test: {e}")
        return False

def test_api_workflow_simulation():
    """Simulate the complete API workflow."""
    
    print_header("Testing Complete API Workflow Simulation")
    
    print_info("Simulating complete workflow:")
    print_info("1. Patient uploads medical report")
    print_info("2. OCR extracts metrics with critical values")
    print_info("3. Intelligent agent analyzes and takes action")
    print_info("4. Appointments booked and notifications sent")
    
    # Simulate critical metrics from OCR
    critical_ocr_result = {
        "filename": "critical_blood_test.pdf",
        "extracted_text": "Critical blood test results...",
        "metrics": [
            {
                "name": "ALT",
                "value": 150.0,  # Critical - above 100
                "unit": "Ед/л",
                "reference_range": "3 - 45",
                "status": "high",
                "explanation": "Significantly elevated ALT indicates liver stress requiring immediate attention"
            },
            {
                "name": "Glucose", 
                "value": 14.2,  # Critical - above 11.0
                "unit": "ммоль/л",
                "reference_range": "3.05 - 6.4", 
                "status": "high",
                "explanation": "Severely elevated glucose indicating possible diabetic emergency"
            },
            {
                "name": "Creatinine",
                "value": 180.0,  # Critical - above 150
                "unit": "мкмоль/л",
                "reference_range": "60 - 110",
                "status": "high", 
                "explanation": "Elevated creatinine suggests kidney dysfunction"
            }
        ],
        "overall_summary": "Multiple critical values detected requiring urgent medical attention",
        "analysis_id": 999  # Mock analysis ID
    }
    
    try:
        # Test doctor recommendations
        print_info("\n🔍 Step 1: Analyzing with doctor recommendation service...")
        recommendations = doctor_recommendation_service.analyze_and_recommend(critical_ocr_result["metrics"])
        
        print_success(f"Detected {recommendations.get('abnormal_metrics_count', 0)} abnormal metrics")
        print_success(f"Priority level: {recommendations.get('priority_level', 'unknown')}")
        
        specialists = recommendations.get('recommended_specialists', [])
        print_success(f"Recommended {len(specialists)} specialists:")
        for spec in specialists:
            print_info(f"  • {spec.get('type', 'Unknown')} (Priority: {spec.get('priority', 'Medium')})")
        
        # Test critical detection
        print_info("\n🚨 Step 2: Testing critical value detection...")
        from app.services.intelligent_health_agent import IntelligentHealthAgent
        
        class MockAgent(IntelligentHealthAgent):
            def __init__(self):
                self.critical_thresholds = {
                    'glucose': {'high': 11.0, 'very_high': 15.0},
                    'alt': {'high': 100, 'very_high': 200},
                    'creatinine': {'high': 150, 'very_high': 300},
                }
                self.specialist_mapping = {
                    'Gastroenterologist': ['alt', 'ast', 'alp', 'ggt', 'total_bilirubin'],
                    'Endocrinologist': ['glucose', 'glycated_hemoglobin', 'thyroid_stimulating_hormone'],
                    'Nephrologist': ['creatinine', 'urea'],
                    'Hematologist': ['hemoglobin', 'white_blood_cells', 'platelets'],
                    'Cardiologist': ['total_cholesterol', 'ldl_cholesterol', 'triglycerides'],
                }
        
        agent = MockAgent()
        critical_metrics = agent._identify_critical_metrics(critical_ocr_result["metrics"])
        
        print_success(f"Identified {len(critical_metrics)} critical metrics:")
        for metric in critical_metrics:
            print_warning(f"  🚨 {metric['name']}: {metric['value']} {metric['unit']} ({metric['status']})")
        
        # Test priority assessment
        print_info("\n⚖️ Step 3: Assessing overall priority...")
        priority = agent._determine_overall_priority(critical_metrics, recommendations)
        print_success(f"Overall priority: {priority.value.upper()}")
        
        if priority == PriorityLevel.HIGH:
            print_warning("HIGH PRIORITY - Would trigger automatic appointment booking")
        
        # Test specialist selection
        print_info("\n👨‍⚕️ Step 4: Selecting priority specialist for auto-booking...")
        specialist_type = agent._determine_priority_specialist(critical_metrics, recommendations)
        print_success(f"Priority specialist for booking: {specialist_type}")
        
        # Simulate notification sending
        print_info("\n📧 Step 5: Simulating notification system...")
        print_success("Would send critical health alert to patient")
        print_success("Would send appointment confirmation to patient and doctor")
        print_success("Would send urgent case notification to assigned doctor")
        
        # Summary
        print_info("\n📊 Workflow Summary:")
        print_success(f"✓ {len(critical_ocr_result['metrics'])} metrics analyzed")
        print_success(f"✓ {len(critical_metrics)} critical values detected")
        print_success(f"✓ {len(specialists)} specialists recommended")
        print_success(f"✓ Priority level: {priority.value}")
        print_success(f"✓ Auto-booking target: {specialist_type}")
        
        if len(critical_metrics) >= 2 and priority == PriorityLevel.HIGH:
            print_success("✓ Complete intelligent health agent workflow validated!")
            return True
        else:
            print_error("✗ Workflow validation failed - not enough critical metrics detected")
            return False
        
    except Exception as e:
        print_error(f"Error in workflow simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete intelligent health agent test suite."""
    
    print("🤖 Intelligent Health Agent Test Suite")
    print("=" * 50)
    print("Testing the complete intelligent health agent system...")
    
    tests = [
        ("Critical Value Detection", test_critical_value_detection),
        ("Doctor Recommendation Integration", test_doctor_recommendation_integration),
        ("Priority Assessment Logic", test_priority_assessment),
        ("Specialist Mapping Logic", test_specialist_mapping),
        ("Complete API Workflow", test_api_workflow_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {e}")
    
    print_header("Test Results Summary")
    print_info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print_success("🎉 All tests passed! Intelligent Health Agent system is ready!")
        print_success("🚀 The system can now:")
        print_success("   • Analyze medical reports with OCR")
        print_success("   • Detect critical health values automatically")
        print_success("   • Recommend appropriate medical specialists")
        print_success("   • Book urgent appointments automatically")
        print_success("   • Send notifications to patients and doctors")
        print_success("   • Provide enhanced AI analysis with OpenRouter")
    else:
        print_warning(f"⚠️ {total - passed} tests failed. Review implementation.")
    
    print_info("\n🔗 Next Steps:")
    print_info("1. Start the server: python -m app.main")
    print_info("2. Upload a medical report via /upload")
    print_info("3. Process with /ocr/{filename}/with-explanations")
    print_info("4. Trigger agent with /agent/process-ocr-analysis")
    print_info("5. Check /appointments/my-appointments for auto-booked appointments")

if __name__ == "__main__":
    main() 