#!/usr/bin/env python3
"""
Test script for individual metric explanations functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import analysis_service, llm_service

def test_individual_explanations():
    """Test the individual metric explanations with sample data"""
    
    # Sample metrics data (similar to what OCR service would extract)
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
            "status": "elevated"
        },
        {
            "name": "Холестерин",
            "value": 4.2,
            "unit": "ммоль/л",
            "reference_range": "3.0-5.0",
            "status": "normal"
        }
    ]
    
    print("🧪 Testing Individual Metric Explanations")
    print("=" * 50)
    
    # Test 1: Individual metric explanations
    print("\n1. Testing individual metric explanations...")
    try:
        explained_metrics = llm_service.generate_individual_metric_explanations(sample_metrics)
        
        for metric in explained_metrics:
            print(f"\n📊 {metric['name']}: {metric['value']} {metric['unit']}")
            print(f"   Status: {metric['status']}")
            print(f"   Explanation: {metric.get('explanation', 'No explanation generated')}")
            
        print(f"\n✅ Successfully generated explanations for {len(explained_metrics)} metrics")
        
    except Exception as e:
        print(f"❌ Error in individual explanations: {e}")
        return False
    
    # Test 2: Analysis from text
    print("\n2. Testing analysis from text...")
    sample_text = """
    Гемоглобин: 140 г/л (норма: 120-160)
    Глюкоза: 110 мг/дл (норма: 70-99)
    Холестерин: 4.2 ммоль/л (норма: 3.0-5.0)
    """
    
    try:
        result = analysis_service.analyze_metrics_from_text_with_explanations(sample_text)
        
        print(f"📝 Overall Summary: {result['overall_summary']}")
        print(f"📈 Metrics found: {len(result['metrics'])}")
        
        for metric in result['metrics']:
            print(f"   • {metric['name']}: {metric['status']}")
            
        print("✅ Successfully analyzed text with explanations")
        
    except Exception as e:
        print(f"❌ Error in text analysis: {e}")
        return False
    
    # Test 3: Status grouping
    print("\n3. Testing metric grouping by status...")
    try:
        grouped = analysis_service.get_metrics_by_status(explained_metrics)
        
        for status, metrics in grouped.items():
            if metrics:
                print(f"   {status.upper()}: {len(metrics)} metrics")
                for metric in metrics:
                    print(f"     - {metric['name']}")
                    
        print("✅ Successfully grouped metrics by status")
        
    except Exception as e:
        print(f"❌ Error in metric grouping: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_fallback_explanations():
    """Test fallback explanations when API is not available"""
    print("\n🔧 Testing fallback explanations...")
    
    sample_metric = {
        "name": "Test Metric",
        "value": 100.0,
        "unit": "mg/dl",
        "reference_range": "80-120",
        "status": "normal"
    }
    
    try:
        fallback = llm_service._get_fallback_metric_explanation(sample_metric)
        print(f"📝 Fallback explanation: {fallback}")
        print("✅ Fallback explanations working correctly")
        return True
    except Exception as e:
        print(f"❌ Error in fallback explanations: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Individual Metric Explanations Tests")
    
    # Test fallback functionality first (doesn't require API)
    fallback_success = test_fallback_explanations()
    
    # Test main functionality
    main_success = test_individual_explanations()
    
    if fallback_success and main_success:
        print("\n✅ All tests passed! Individual metric explanations are working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1) 