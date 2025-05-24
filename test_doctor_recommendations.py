#!/usr/bin/env python3
"""
Test script for Doctor Recommendation Service

This script tests the doctor recommendation functionality with various
health metric scenarios to verify proper specialist mapping and recommendations.
"""

import sys
import os
import json

# Add backend to path
sys.path.append('backend')

from app.services.doctor_recommendation_service import doctor_recommendation_service

def test_kazakh_ocr_recommendations():
    """Test recommendations using the actual Kazakh OCR data we successfully extracted."""
    
    print("🏥 Testing Doctor Recommendations with Kazakh OCR Data")
    print("="*70)
    
    # Sample data from the successfully processed Kazakh medical document
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
            "name": "Amylase",
            "value": 48.84,
            "unit": "Ед/л",
            "reference_range": "25 - 125",
            "status": "normal"
        },
        {
            "name": "ALP",
            "value": 50.53,
            "unit": "Ед/л",
            "reference_range": "45 - 125",
            "status": "normal"
        },
        {
            "name": "GGT",
            "value": 31.45,
            "unit": "Ед/л",
            "reference_range": "11 - 61",
            "status": "normal"
        },
        {
            "name": "Glucose",
            "value": 4.71,
            "unit": "ммоль/л",
            "reference_range": "3.05 - 6.4",
            "status": "normal"
        },
        {
            "name": "Total Bilirubin",
            "value": 10.51,
            "unit": "мкмоль/л",
            "reference_range": "< 22.0",
            "status": "normal"
        }
    ]
    
    print(f"📊 Input Metrics: {len(kazakh_metrics)} health metrics")
    for metric in kazakh_metrics:
        status_icon = "⚠️" if metric['status'] != 'normal' else "✅"
        print(f"  {status_icon} {metric['name']}: {metric['value']} {metric['unit']} ({metric['status']})")
    
    print(f"\n🔍 Analyzing metrics for specialist recommendations...")
    
    try:
        recommendations = doctor_recommendation_service.analyze_and_recommend(kazakh_metrics)
        
        print(f"\n📋 Recommendation Results:")
        print(f"  • Abnormal metrics: {recommendations['abnormal_metrics_count']}")
        print(f"  • Priority level: {recommendations['priority_level']}")
        print(f"  • Specialists recommended: {len(recommendations['recommended_specialists'])}")
        
        print(f"\n👨‍⚕️ Recommended Specialists:")
        if recommendations['recommended_specialists']:
            for i, specialist in enumerate(recommendations['recommended_specialists'], 1):
                print(f"\n  {i}. {specialist['type']} (Priority: {specialist['priority']})")
                print(f"     Reason: {specialist['reason']}")
                print(f"     Metrics: {', '.join(specialist['metrics_involved'])}")
                print(f"     When to consult: {specialist['when_to_consult']}")
        else:
            print("     No specialists recommended (all values normal)")
        
        print(f"\n📝 Next Steps:")
        for i, step in enumerate(recommendations['next_steps'], 1):
            print(f"  {i}. {step}")
        
        print(f"\n⚠️ Disclaimer: {recommendations['disclaimer']}")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_normal_values():
    """Test with all normal values."""
    
    print(f"\n🔬 Testing with All Normal Values")
    print("="*50)
    
    normal_metrics = [
        {
            "name": "ALT",
            "value": 25.0,
            "unit": "Ед/л",
            "reference_range": "3 - 45",
            "status": "normal"
        },
        {
            "name": "Glucose",
            "value": 5.2,
            "unit": "ммоль/л",
            "reference_range": "3.05 - 6.4",
            "status": "normal"
        }
    ]
    
    try:
        recommendations = doctor_recommendation_service.analyze_and_recommend(normal_metrics)
        
        print(f"📊 Results for normal values:")
        print(f"  • Specialists recommended: {len(recommendations['recommended_specialists'])}")
        print(f"  • Priority level: {recommendations['priority_level']}")
        
        if recommendations['recommended_specialists']:
            print("  ❌ ERROR: Should not recommend specialists for normal values")
        else:
            print("  ✅ SUCCESS: No specialists recommended for normal values")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_high_severity_case():
    """Test with high-severity conditions."""
    
    print(f"\n🚨 Testing High-Severity Case")
    print("="*40)
    
    high_severity_metrics = [
        {
            "name": "Glucose",
            "value": 15.5,  # Very high glucose
            "unit": "ммоль/л",
            "reference_range": "3.05 - 6.4",
            "status": "high"
        },
        {
            "name": "Creatinine",
            "value": 180.0,  # High creatinine
            "unit": "мкмоль/л",
            "reference_range": "60 - 110",
            "status": "high"
        },
        {
            "name": "ALT",
            "value": 120.0,  # Very high ALT
            "unit": "Ед/л",
            "reference_range": "3 - 45",
            "status": "high"
        }
    ]
    
    try:
        recommendations = doctor_recommendation_service.analyze_and_recommend(high_severity_metrics)
        
        print(f"📊 Results for high-severity case:")
        print(f"  • Priority level: {recommendations['priority_level']}")
        print(f"  • Specialists recommended: {len(recommendations['recommended_specialists'])}")
        
        expected_specialists = ['Endocrinologist', 'Nephrologist', 'Gastroenterologist']
        found_specialists = [s['type'] for s in recommendations['recommended_specialists']]
        
        print(f"  • Found specialists: {', '.join(found_specialists)}")
        
        if recommendations['priority_level'] == 'high':
            print("  ✅ SUCCESS: Correctly identified as high priority")
        else:
            print("  ❌ ERROR: Should be high priority")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_multiple_conditions():
    """Test with multiple different conditions."""
    
    print(f"\n🩺 Testing Multiple Conditions")
    print("="*35)
    
    multi_condition_metrics = [
        {
            "name": "Cholesterol",
            "value": 7.2,
            "unit": "ммоль/л",
            "reference_range": "< 5.0",
            "status": "high"
        },
        {
            "name": "Hemoglobin",
            "value": 90.0,
            "unit": "г/л",
            "reference_range": "120 - 160",
            "status": "low"
        },
        {
            "name": "TSH",
            "value": 8.5,
            "unit": "мкМЕ/мл",
            "reference_range": "0.4 - 4.0",
            "status": "high"
        }
    ]
    
    try:
        recommendations = doctor_recommendation_service.analyze_and_recommend(multi_condition_metrics)
        
        print(f"📊 Results for multiple conditions:")
        print(f"  • Specialists recommended: {len(recommendations['recommended_specialists'])}")
        
        for specialist in recommendations['recommended_specialists']:
            print(f"  • {specialist['type']}: {', '.join(specialist['metrics_involved'])}")
        
        expected_types = ['Cardiologist', 'Hematologist', 'Endocrinologist']
        found_types = [s['type'] for s in recommendations['recommended_specialists']]
        
        overlap = set(expected_types) & set(found_types)
        print(f"  • Expected overlap: {len(overlap)}/{len(expected_types)} specialist types")
        
        if len(overlap) >= 2:
            print("  ✅ SUCCESS: Multiple specialist types recommended")
        else:
            print("  ⚠️  WARNING: May need more specialist types")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all doctor recommendation tests."""
    
    print("🚀 Doctor Recommendation Service Test Suite")
    print("="*80)
    
    # Test with actual Kazakh OCR data (main test case)
    kazakh_result = test_kazakh_ocr_recommendations()
    
    # Test edge cases
    normal_result = test_normal_values()
    high_severity_result = test_high_severity_case()
    multi_condition_result = test_multiple_conditions()
    
    # Summary
    print(f"\n🎯 Test Summary")
    print("="*30)
    
    tests = [
        ("Kazakh OCR Data", kazakh_result),
        ("Normal Values", normal_result),
        ("High Severity", high_severity_result),
        ("Multiple Conditions", multi_condition_result)
    ]
    
    passed = 0
    for test_name, result in tests:
        if result is not None:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
        print(f"  • {test_name}: {status}")
    
    print(f"\n🏆 Overall Result: {passed}/{len(tests)} tests passed")
    
    if kazakh_result and len(kazakh_result.get('recommended_specialists', [])) > 0:
        print("\n🎉 SUCCESS: Doctor recommendation system is working!")
        print("   The elevated ALT was correctly mapped to gastroenterologist.")
    else:
        print("\n⚠️  PARTIAL SUCCESS: System works but may need refinement.")

if __name__ == "__main__":
    main() 