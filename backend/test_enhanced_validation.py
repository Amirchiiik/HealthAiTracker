#!/usr/bin/env python3
"""
Test script for enhanced validation that filters out timestamps and headers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import ocr_service

def test_validation_filtering():
    """Test that the enhanced validation properly filters out non-metric content."""
    
    print("🔍 Testing Enhanced Validation Filtering")
    print("=" * 60)
    
    # Test cases that should be REJECTED (not treated as metrics)
    should_reject = [
        # Timestamps and dates
        "26.04.2025: 16:12",
        "14: 19",
        "Дата: 26.04.2025",
        "Время: 16:12",
        "26.04.2025_16: 12",
        
        # Section headers
        "Лимфоциты (абс: кол-во)",
        "Общий анализ: крови",
        "Биохимический: анализ",
        "Показатели: основные",
        "Результаты: анализа",
        
        # Invalid structures
        "Описание: без числовых данных",
        "Комментарий: нормальные значения",
        "Заключение: в пределах нормы",
        
        # Values without proper units
        "Тест: 123",
        "Значение: только число",
    ]
    
    # Test cases that should be ACCEPTED (treated as metrics)
    should_accept = [
        # Valid metrics with standard units
        "HGB: 163.00 г/л (норма: 130,00 - 160,00)",
        "MCV: 83.20 фл (норма: 80,00 - 100,00)",
        "RDW: 12.60 % (норма: 11,50 - 14,50)",
        
        # Valid metrics with scientific notation
        "RBC: 5.66 10^12/л (норма: 4,50 - 5,90)",
        "PLT: 319.00 10^9/л (норма: 180,00 - 320,00)",
        "WBC: 6.37 10^9/л (норма: 4,00 - 9,00)",
        
        # Valid metrics with different formats
        "Глюкоза: 5.2 ммоль/л",
        "Холестерин: 4.8 ммоль/л",
        "Креатинин: 85 мкмоль/л",
    ]
    
    print("🚫 Testing REJECTION of non-metric content:")
    print("-" * 50)
    
    rejection_success = 0
    for test_case in should_reject:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) == 0:
                print(f"✅ CORRECTLY REJECTED: {test_case}")
                rejection_success += 1
            else:
                print(f"❌ INCORRECTLY ACCEPTED: {test_case}")
                for metric in metrics:
                    print(f"   → {metric['name']} = {metric['value']} {metric['unit']}")
        except Exception as e:
            print(f"❌ ERROR with: {test_case} - {e}")
    
    print(f"\n📊 Rejection Success Rate: {rejection_success}/{len(should_reject)} ({rejection_success/len(should_reject)*100:.1f}%)")
    
    print("\n✅ Testing ACCEPTANCE of valid metrics:")
    print("-" * 50)
    
    acceptance_success = 0
    for test_case in should_accept:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                print(f"✅ CORRECTLY ACCEPTED: {test_case}")
                for metric in metrics:
                    print(f"   → {metric['name']} = {metric['value']} {metric['unit']} (conf: {metric.get('confidence', 0):.2f})")
                acceptance_success += 1
            else:
                print(f"❌ INCORRECTLY REJECTED: {test_case}")
        except Exception as e:
            print(f"❌ ERROR with: {test_case} - {e}")
    
    print(f"\n📊 Acceptance Success Rate: {acceptance_success}/{len(should_accept)} ({acceptance_success/len(should_accept)*100:.1f}%)")
    
    # Overall assessment
    overall_success = (rejection_success == len(should_reject)) and (acceptance_success == len(should_accept))
    
    print(f"\n🎯 OVERALL VALIDATION: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    return overall_success

def test_mixed_content():
    """Test parsing of mixed content that includes both valid metrics and invalid content."""
    
    print("\n🧪 Testing Mixed Content Parsing")
    print("=" * 45)
    
    # Simulate a medical report with mixed content
    mixed_content = """
Дата: 26.04.2025
Время: 16:12
Пациент: Иванов И.И.
Общий анализ крови:

HGB: 163.00 г/л (норма: 130,00 - 160,00)
RBC: 5.66 10^12/л (норма: 4,50 - 5,90)
26.04.2025_16: 12
Лимфоциты (абс: кол-во): 4
PLT: 319.00 10^9/л (норма: 180,00 - 320,00)
WBC: 6.37 10^9/л (норма: 4,00 - 9,00)
14: 19
MCV: 83.20 фл (норма: 80,00 - 100,00)
MCH: 28.80 пг (норма: 27,00 - 32,00)
Заключение: в пределах нормы
"""
    
    print("📄 Raw mixed content:")
    print("-" * 30)
    print(mixed_content.strip())
    print("-" * 30)
    
    try:
        metrics = ocr_service.extract_metrics_from_text(mixed_content)
        
        print(f"\n📊 Extracted {len(metrics)} valid metrics:")
        print("=" * 50)
        
        # Expected valid metrics from the mixed content
        expected_metrics = ['HGB', 'RBC', 'PLT', 'WBC', 'MCV', 'MCH']
        found_metrics = []
        
        for metric in metrics:
            original_name = metric.get('original_line', '').split(':')[0].strip().upper()
            found_metrics.append(original_name)
            confidence = metric.get('confidence', 0)
            status_icon = "🟢" if metric['status'] == 'normal' else "🔴"
            print(f"  {status_icon} {metric['name']:25} = {metric['value']:>8.2f} {metric['unit']:15} (conf: {confidence:.2f})")
            print(f"     Original: {metric.get('original_line', 'N/A')}")
        
        # Check if we got the expected metrics and avoided the problematic ones
        expected_found = sum(1 for exp in expected_metrics if exp in found_metrics)
        
        # Check that we didn't extract the problematic lines
        problematic_lines = ['26.04.2025_16', '14', 'Лимфоциты (абс', 'Дата', 'Время', 'Заключение']
        problematic_found = sum(1 for prob in problematic_lines if any(prob.lower() in metric['name'].lower() for metric in metrics))
        
        print(f"\n📈 Analysis:")
        print(f"   Expected metrics found: {expected_found}/{len(expected_metrics)}")
        print(f"   Problematic content avoided: {len(problematic_lines) - problematic_found}/{len(problematic_lines)}")
        
        success = (expected_found >= len(expected_metrics) * 0.8) and (problematic_found == 0)
        print(f"\n🎯 Mixed Content Test: {'✅ PASS' if success else '❌ FAIL'}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error processing mixed content: {e}")
        return False

def test_edge_cases():
    """Test edge cases for validation."""
    
    print("\n🔬 Testing Edge Cases")
    print("=" * 30)
    
    edge_cases = [
        # Borderline cases that could go either way
        {"text": "СОЭ: 15 мм/час", "should_accept": True, "description": "Valid ESR metric"},
        {"text": "Возраст: 25 лет", "should_accept": False, "description": "Age is not a lab metric"},
        {"text": "T: 36.6 °C", "should_accept": True, "description": "Temperature with proper unit"},
        {"text": "ID: 12345", "should_accept": False, "description": "Patient ID"},
        {"text": "pH: 7.4 ед", "should_accept": True, "description": "pH value"},
        {"text": "Кабинет: 101", "should_accept": False, "description": "Room number"},
    ]
    
    success_count = 0
    for case in edge_cases:
        try:
            metrics = ocr_service.extract_metrics_from_text(case["text"])
            actually_accepted = len(metrics) > 0
            
            if actually_accepted == case["should_accept"]:
                status = "✅ CORRECT"
                success_count += 1
            else:
                status = "❌ WRONG"
            
            expected = "ACCEPT" if case["should_accept"] else "REJECT"
            actual = "ACCEPTED" if actually_accepted else "REJECTED"
            
            print(f"{status} {case['text']:20} | Expected: {expected:6} | Actual: {actual:8} | {case['description']}")
            
        except Exception as e:
            print(f"❌ ERROR {case['text']:20} | {e}")
    
    edge_success = success_count == len(edge_cases)
    print(f"\n📊 Edge Cases: {success_count}/{len(edge_cases)} ({success_count/len(edge_cases)*100:.1f}%)")
    print(f"🎯 Edge Case Test: {'✅ PASS' if edge_success else '❌ FAIL'}")
    
    return edge_success

if __name__ == "__main__":
    print("🚀 Enhanced Validation Test Suite")
    print("=" * 80)
    
    # Run all validation tests
    test1_result = test_validation_filtering()
    test2_result = test_mixed_content()
    test3_result = test_edge_cases()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION TEST RESULTS:")
    print(f"  Basic Filtering Test:   {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  Mixed Content Test:     {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"  Edge Cases Test:        {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result and test3_result
    print(f"\n🎯 OVERALL: {'✅ ENHANCED VALIDATION WORKING' if overall_success else '❌ VALIDATION ISSUES REMAIN'}")
    
    if overall_success:
        print("\n🎉 SUCCESS: Enhanced validation is working correctly!")
        print("   • Timestamps and dates are properly filtered out")
        print("   • Section headers are not treated as metrics")
        print("   • Valid medical metrics are still extracted")
        print("   • Scientific notation parsing is preserved")
    else:
        print("\n⚠️  Some validation issues remain - see details above")
    
    print("=" * 80) 