#!/usr/bin/env python3
"""
Test script for enhanced OCR extraction functionality
Tests scientific notation parsing and complex unit handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import ocr_service

def test_scientific_notation_parsing():
    """Test enhanced parsing with scientific notation examples from the issue report."""
    
    print("🧪 Testing Enhanced OCR Extraction")
    print("=" * 60)
    
    # Test cases based on the issue report
    test_cases = [
        # Correctly extracted cases (should still work)
        "HGB: 163.00 г/л (норма: 130,00 - 160,00)",
        "MCV: 83.20 фл (норма: 80,00 - 100,00)",
        "MCH: 28.80 пг (норма: 27,00 - 32,00)",
        "MCHC: 346.00 г/л (норма: 320,00 - 360,00)",
        "RDW: 12.60 % (норма: 11,50 - 14,50)",
        "PCT: 0.30 % (норма: 0,20 - 0,50)",
        "EOS%: 1.40 % (норма: 1,00 - 4,00)",
        "MON%: 6.90 % (норма: 3,00 - 9,00)",
        
        # Previously incorrectly extracted cases (should now work)
        "RBC: 5.66 10^12/л (норма: 4,50 - 5,90)",
        "PLT: 319.00 10^9/л (норма: 180,00 - 320,00)", 
        "WBC: 6.37 10^9/л (норма: 4,00 - 9,00)",
        "NEU#: 3.67 10^9/л (норма: 2,00 - 7,00)",
        "EOS#: 0.09 10^9/л (норма: 0,02 - 0,50)",
        "BAS#: 0.040 10^9/л (норма: 0,00 - 0,20)",
        "LYM#: 2.62 10^9/л (норма: 1,20 - 3,40)",
        
        # Edge cases and variations
        "TEST1: 5,66 10^12/л (норма: 4,50 - 5,90)",  # Comma instead of period
        "TEST2: 319 10^9 /л (норма: 180 - 320)",      # Space before unit
        "TEST3: 2,62E+9/л (норма: 1,20 - 3,40)",     # E notation
        "TEST4: 6.37 × 10^9/л (норма: 4,00 - 9,00)", # Multiplication symbol
    ]
    
    print(f"Testing {len(test_cases)} cases...\n")
    
    # Combine all test cases into a single text
    test_text = "\n".join(test_cases)
    
    # Extract metrics using enhanced function
    try:
        extracted_metrics = ocr_service.extract_metrics_from_text(test_text)
        
        print(f"✅ Successfully extracted {len(extracted_metrics)} metrics")
        print("\n📊 Extraction Results:")
        print("-" * 80)
        
        for i, metric in enumerate(extracted_metrics, 1):
            print(f"{i:2d}. {metric['name']:25} = {metric['value']:>12} {metric['unit']:15}")
            print(f"     Reference: {metric['reference_range']:30} Status: {metric['status']:8}")
            print(f"     Confidence: {metric.get('confidence', 0):.2f} | Original: {metric.get('original_line', 'N/A')[:50]}...")
            print()
        
        # Validate specific problematic cases
        print("\n🔍 Validation of Previously Problematic Cases:")
        print("-" * 60)
        
        problematic_cases = {
            'red_blood_cells': {
                'expected_base_value': 5.66, 
                'expected_unit_contains': '10^12',
                'range': (4.0, 7.0)  # Reasonable base value range
            },
            'platelets': {
                'expected_base_value': 319.0, 
                'expected_unit_contains': '10^9',
                'range': (100.0, 500.0)
            },
            'white_blood_cells': {
                'expected_base_value': 6.37, 
                'expected_unit_contains': '10^9',
                'range': (3.0, 10.0)
            },
            'neutrophils_absolute': {
                'expected_base_value': 3.67, 
                'expected_unit_contains': '10^9',
                'range': (2.0, 8.0)
            },
            'eosinophils_absolute': {
                'expected_base_value': 0.09, 
                'expected_unit_contains': '10^9',
                'range': (0.01, 1.0)
            },
            'basophils_absolute': {
                'expected_base_value': 0.04, 
                'expected_unit_contains': '10^9',
                'range': (0.01, 0.2)
            },
            'lymphocytes_absolute': {
                'expected_base_value': 2.62, 
                'expected_unit_contains': '10^9',
                'range': (1.0, 4.0)
            },
        }
        
        validation_results = {}
        for metric in extracted_metrics:
            metric_name = metric['name']
            if metric_name in problematic_cases:
                expected = problematic_cases[metric_name]
                
                # Check base value is in reasonable range and close to expected
                base_value_ok = (abs(metric['value'] - expected['expected_base_value']) < 0.1 and
                               expected['range'][0] <= metric['value'] <= expected['range'][1])
                
                # Check unit contains expected scientific notation pattern
                unit_ok = expected['expected_unit_contains'] in metric['unit']
                
                # Check for suspicious values (the old "9 /л" problem)
                not_suspicious = not (metric['value'] == 9.0 and metric['unit'] == '/л')
                
                validation_results[metric_name] = {
                    'value_ok': base_value_ok,
                    'unit_ok': unit_ok,
                    'not_suspicious': not_suspicious,
                    'overall_ok': base_value_ok and unit_ok and not_suspicious,
                    'actual_value': metric['value'],
                    'actual_unit': metric['unit'],
                    'expected_value': expected['expected_base_value'],
                    'confidence': metric.get('confidence', 0)
                }
        
        # Print validation results
        for metric_name, result in validation_results.items():
            status = "✅ PASS" if result['overall_ok'] else "❌ FAIL"
            print(f"{status} {metric_name:25} | Value: {result['actual_value']:>8.2f} | Unit: {result['actual_unit']:15}")
            if not result['overall_ok']:
                print(f"     Expected: ~{result['expected_value']:>8.2f} with scientific notation | Issues: ", end="")
                if not result['value_ok']:
                    print("VALUE ", end="")
                if not result['unit_ok']:
                    print("UNIT ", end="")
                if not result['not_suspicious']:
                    print("SUSPICIOUS ", end="")
                print()
        
        # Summary
        passed_count = sum(1 for r in validation_results.values() if r['overall_ok'])
        total_count = len(validation_results)
        
        print(f"\n📈 Validation Summary:")
        if total_count > 0:
            print(f"   Passed: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
        else:
            print(f"   No problematic cases found in extracted metrics")
        
        if total_count > 0 and passed_count == total_count:
            print("🎉 All previously problematic cases now parse correctly!")
            return True
        elif total_count == 0:
            print("⚠️  No problematic cases were detected in the extracted metrics")
            print("    This could mean the parsing is failing completely or metric names changed")
            return False
        else:
            print("⚠️  Some issues remain - see details above")
            return False
            
    except Exception as e:
        print(f"❌ Error during metric extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases and potential parsing issues."""
    
    print("\n🔬 Testing Edge Cases")
    print("=" * 40)
    
    edge_cases = [
        # Comma vs period variations
        "TEST_COMMA1: 5,66 г/л (норма: 4,00 - 6,00)",
        "TEST_COMMA2: 12,5 % (норма: 10,0 - 15,0)",
        
        # Different spacing patterns
        "TEST_SPACE1: 123 г/л (норма: 100 - 150)",
        "TEST_SPACE2: 45.6  мг/дл (норма: 40 - 50)",
        
        # Numbers that should be flagged as suspicious
        "SUSPICIOUS1: 9 /л (норма: 100 - 200)",  # The old parsing error
        "SUSPICIOUS2: 0 г/л (норма: 100 - 200)",  # Zero value
        
        # Complex units
        "COMPLEX1: 2.5 мкмоль/л (норма: 1.0 - 3.0)",
        "COMPLEX2: 15.2 мм/час (норма: 10 - 20)",
    ]
    
    test_text = "\n".join(edge_cases)
    
    try:
        metrics = ocr_service.extract_metrics_from_text(test_text)
        
        print(f"Extracted {len(metrics)} metrics from {len(edge_cases)} test cases")
        
        for metric in metrics:
            confidence = metric.get('confidence', 0)
            confidence_icon = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.5 else "🔴"
            print(f"{confidence_icon} {metric['name']:15} = {metric['value']:8} {metric['unit']:10} (conf: {confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in edge case testing: {e}")
        return False

def test_with_actual_ocr_output():
    """Test with simulated OCR output that might contain the parsing issues."""
    
    print("\n📄 Testing with Simulated OCR Text")
    print("=" * 45)
    
    # Simulate problematic OCR output that would cause the "9 /л" issue
    simulated_ocr_text = """
HGB: 163.00 г/л (норма: 130,00 - 160,00)
RBC
5.66 10^12
/л
4.50 - 5.90
PLT
319.00 10^9
/л
180.00 - 320.00
WBC: 6.37 10^9/л (норма: 4,00 - 9,00)
MCV: 83.20 фл (норма: 80,00 - 100,00)
MCH: 28.80 пг (норма: 27,00 - 32,00)
"""
    
    print("Raw OCR text simulation:")
    print("-" * 30)
    print(simulated_ocr_text)
    print("-" * 30)
    
    # First, test the lab line extraction
    print("\n1. Testing extract_lab_lines():")
    lab_lines = ocr_service.extract_lab_lines(simulated_ocr_text)
    print(f"Extracted lab lines:\n{lab_lines}")
    
    # Then test metric extraction from the processed lab lines
    print("\n2. Testing extract_metrics_from_text():")
    try:
        metrics = ocr_service.extract_metrics_from_text(lab_lines)
        
        print(f"Successfully extracted {len(metrics)} metrics:")
        for metric in metrics:
            print(f"  • {metric['name']:20} = {metric['value']:>10} {metric['unit']:12} ({metric['status']})")
        
        return len(metrics) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced OCR Extraction Test Suite")
    print("=" * 80)
    
    # Run all tests
    test1_result = test_scientific_notation_parsing()
    test2_result = test_edge_cases()
    test3_result = test_with_actual_ocr_output()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS:")
    print(f"  Scientific Notation Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  Edge Cases Test:         {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"  OCR Simulation Test:     {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result and test3_result
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    print("=" * 80) 