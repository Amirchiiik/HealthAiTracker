#!/usr/bin/env python3
"""
Test script for extended lab categories: biochemical analysis, hormonal profile, 
coagulation tests, and viral hepatitis markers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import ocr_service

def test_biochemical_analysis():
    """Test biochemical blood analysis metrics."""
    
    print("🧪 Testing Biochemical Analysis")
    print("=" * 50)
    
    biochemical_tests = [
        "Общий белок: 75.5 г/л (норма: 65,0 - 85,0)",
        "Альбумин: 42.3 г/л (норма: 35,0 - 50,0)",
        "Креатинин: 89 мкмоль/л (норма: 62 - 115)",
        "Глюкоза: 5.8 ммоль/л (норма: 3,9 - 6,1)",
        "Магний: 0.95 ммоль/л (норма: 0,75 - 1,25)",
        "АЛТ: 28 U/L (норма: менее 40)",
        "АСТ: 32 U/L (норма: менее 40)",
        "Билирубин общий: 18.5 мкмоль/л (норма: 8,5 - 20,5)",
        "Билирубин прямой: 4.2 мкмоль/л (норма: 0 - 8,6)",
        "ГГТ: 25 U/L (норма: менее 50)",
        "Щелочная фосфатаза: 78 U/L (норма: 44 - 147)",
        "Гликированный гемоглобин: 5.8 % (норма: менее 6,5)",
        "С-реактивный белок: 2.1 мг/л (норма: менее 3,0)",
        "Холестерин общий: 5.2 ммоль/л (норма: менее 5,2)",
        "Холестерин ЛПВП: 1.4 ммоль/л (норма: более 1,0)",
        "Холестерин ЛПНП: 3.1 ммоль/л (норма: менее 3,0)",
        "Триглицериды: 1.8 ммоль/л (норма: менее 1,7)",
        "Калий: 4.2 ммоль/л (норма: 3,5 - 5,1)",
    ]
    
    success_count = 0
    for test_case in biochemical_tests:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                metric = metrics[0]
                print(f"✅ {test_case}")
                print(f"   → {metric['name']} = {metric['value']} {metric['unit']} [{metric['status']}]")
                success_count += 1
            else:
                print(f"❌ Failed to parse: {test_case}")
        except Exception as e:
            print(f"❌ Error with: {test_case} - {e}")
    
    print(f"\n📊 Biochemical Analysis Success: {success_count}/{len(biochemical_tests)} ({success_count/len(biochemical_tests)*100:.1f}%)")
    return success_count == len(biochemical_tests)

def test_hormonal_profile():
    """Test hormonal profile metrics."""
    
    print("\n🔬 Testing Hormonal Profile")
    print("=" * 40)
    
    hormonal_tests = [
        "ТТГ: 2.5 мкМЕ/мл (норма: 0,27 - 4,20)",
        "Свободный Т3: 4.8 пг/мл (норма: 2,0 - 4,4)",
        "Свободный Т4: 16.2 нг/дл (норма: 12,0 - 22,0)",
        "25-ОН витамин D: 32 нг/мл (норма: более 30)",
    ]
    
    success_count = 0
    for test_case in hormonal_tests:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                metric = metrics[0]
                print(f"✅ {test_case}")
                print(f"   → {metric['name']} = {metric['value']} {metric['unit']} [{metric['status']}]")
                success_count += 1
            else:
                print(f"❌ Failed to parse: {test_case}")
        except Exception as e:
            print(f"❌ Error with: {test_case} - {e}")
    
    print(f"\n📊 Hormonal Profile Success: {success_count}/{len(hormonal_tests)} ({success_count/len(hormonal_tests)*100:.1f}%)")
    return success_count == len(hormonal_tests)

def test_coagulation_tests():
    """Test coagulation (coagulogram) metrics."""
    
    print("\n🩸 Testing Coagulation Tests")
    print("=" * 35)
    
    coagulation_tests = [
        "АЧТВ: 28.5 сек (норма: 25,4 - 36,9)",
        "МНО: 1.1 (норма: 0,85 - 1,15)",
        "Протромбиновое время: 13.2 сек (норма: 11,0 - 15,0)",
        "Тромбиновое время: 16.8 сек (норма: 14,0 - 21,0)",
        "Протромбиновый индекс: 95 % (норма: 78 - 142)",
        "Фибриноген: 3.2 г/л (норма: 2,0 - 4,0)",
    ]
    
    success_count = 0
    for test_case in coagulation_tests:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                metric = metrics[0]
                print(f"✅ {test_case}")
                print(f"   → {metric['name']} = {metric['value']} {metric['unit']} [{metric['status']}]")
                success_count += 1
            else:
                print(f"❌ Failed to parse: {test_case}")
        except Exception as e:
            print(f"❌ Error with: {test_case} - {e}")
    
    print(f"\n📊 Coagulation Tests Success: {success_count}/{len(coagulation_tests)} ({success_count/len(coagulation_tests)*100:.1f}%)")
    return success_count == len(coagulation_tests)

def test_hepatitis_markers():
    """Test viral hepatitis markers with qualitative results."""
    
    print("\n🧫 Testing Hepatitis Markers")
    print("=" * 35)
    
    hepatitis_tests = [
        "Антитела к гепатиту C: Не обнаружено",
        "Anti-HCV: Отрицательно",
        "HBsAg: Не обнаружено", 
        "Гепатит B: Отрицательно",
    ]
    
    success_count = 0
    for test_case in hepatitis_tests:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                metric = metrics[0]
                result_text = "Negative" if metric['value'] == 0.0 else "Positive" if metric['value'] == 1.0 else "Normal"
                print(f"✅ {test_case}")
                print(f"   → {metric['name']} = {result_text} [{metric['status']}]")
                success_count += 1
            else:
                print(f"❌ Failed to parse: {test_case}")
        except Exception as e:
            print(f"❌ Error with: {test_case} - {e}")
    
    print(f"\n📊 Hepatitis Markers Success: {success_count}/{len(hepatitis_tests)} ({success_count/len(hepatitis_tests)*100:.1f}%)")
    return success_count == len(hepatitis_tests)

def test_alternative_spellings():
    """Test alternative spellings and abbreviations."""
    
    print("\n📝 Testing Alternative Spellings")
    print("=" * 40)
    
    alternative_tests = [
        "АЛАТ: 25 U/L (норма: менее 40)",     # Alternative for АЛТ
        "АСАТ: 30 U/L (норма: менее 40)",     # Alternative for АСТ
        "ГГТП: 35 U/L (норма: менее 50)",     # Alternative for ГГТ
        "ЩФ: 82 U/L (норма: 44 - 147)",      # Short for Щелочная фосфатаза
        "СРБ: 1.8 мг/л (норма: менее 3,0)",   # Short for С-реактивный белок
        "ЛПВП: 1.3 ммоль/л (норма: более 1,0)", # Short for Холестерин ЛПВП
        "ЛПНП: 2.9 ммоль/л (норма: менее 3,0)", # Short for Холестерин ЛПНП
        "TSH: 2.8 мкМЕ/мл (норма: 0,27 - 4,20)", # English abbreviation
        "HbA1c: 5.9 % (норма: менее 6,5)",    # Glycated hemoglobin
        "INR: 1.0 (норма: 0,85 - 1,15)",      # International normalized ratio
    ]
    
    success_count = 0
    for test_case in alternative_tests:
        try:
            metrics = ocr_service.extract_metrics_from_text(test_case)
            if len(metrics) > 0:
                metric = metrics[0]
                print(f"✅ {test_case}")
                print(f"   → {metric['name']} = {metric['value']} {metric['unit']} [{metric['status']}]")
                success_count += 1
            else:
                print(f"❌ Failed to parse: {test_case}")
        except Exception as e:
            print(f"❌ Error with: {test_case} - {e}")
    
    print(f"\n📊 Alternative Spellings Success: {success_count}/{len(alternative_tests)} ({success_count/len(alternative_tests)*100:.1f}%)")
    return success_count == len(alternative_tests)

def test_mixed_comprehensive_report():
    """Test a comprehensive mixed medical report with all categories."""
    
    print("\n📋 Testing Comprehensive Mixed Report")
    print("=" * 45)
    
    comprehensive_report = """
Дата: 26.04.2025
Время: 16:12
Пациент: Иванов И.И.

ОБЩИЙ АНАЛИЗ КРОВИ:
HGB: 145.0 г/л (норма: 130,00 - 160,00)
RBC: 4.8 10^12/л (норма: 4,50 - 5,90)
WBC: 7.2 10^9/л (норма: 4,00 - 9,00)

БИОХИМИЧЕСКИЙ АНАЛИЗ:
Глюкоза: 5.4 ммоль/л (норма: 3,9 - 6,1)
Креатинин: 92 мкмоль/л (норма: 62 - 115)
АЛТ: 32 U/L (норма: менее 40)
Холестерин: 5.0 ммоль/л (норма: менее 5,2)

ГОРМОНЫ:
ТТГ: 3.1 мкМЕ/мл (норма: 0,27 - 4,20)
Свободный Т4: 18.5 нг/дл (норма: 12,0 - 22,0)

КОАГУЛОГРАММА:
АЧТВ: 30.2 сек (норма: 25,4 - 36,9)
МНО: 1.05 (норма: 0,85 - 1,15)

ВИРУСНЫЕ МАРКЕРЫ:
Anti-HCV: Не обнаружено
HBsAg: Отрицательно

Заключение: результаты в пределах нормы
"""
    
    print("📄 Processing comprehensive report...")
    
    try:
        metrics = ocr_service.extract_metrics_from_text(comprehensive_report)
        
        print(f"\n📊 Extracted {len(metrics)} metrics:")
        print("=" * 60)
        
        # Categorize metrics
        categories = {
            'Complete Blood Count': [],
            'Biochemical Analysis': [],
            'Hormonal Profile': [],
            'Coagulation Tests': [],
            'Viral Markers': []
        }
        
        for metric in metrics:
            name = metric['name']
            if any(x in name for x in ['hemoglobin', 'blood_cells', 'white_blood', 'red_blood']):
                categories['Complete Blood Count'].append(metric)
            elif any(x in name for x in ['glucose', 'creatinine', 'alt_', 'cholesterol']):
                categories['Biochemical Analysis'].append(metric)
            elif any(x in name for x in ['thyroid', 'free_t']):
                categories['Hormonal Profile'].append(metric)
            elif any(x in name for x in ['thromboplastin', 'normalized_ratio']):
                categories['Coagulation Tests'].append(metric)
            elif any(x in name for x in ['hepatitis', 'antibodies']):
                categories['Viral Markers'].append(metric)
        
        total_expected = 12  # Expected metrics from the report
        
        for category, metrics_list in categories.items():
            if metrics_list:
                print(f"\n🔹 {category} ({len(metrics_list)} metrics):")
                for metric in metrics_list:
                    if metric['unit'] == 'qualitative':
                        result = "Negative" if metric['value'] == 0.0 else "Positive" if metric['value'] == 1.0 else "Normal"
                        print(f"   • {metric['name']:30} = {result:>8} [{metric['status']}]")
                    else:
                        print(f"   • {metric['name']:30} = {metric['value']:>8.2f} {metric['unit']:10} [{metric['status']}]")
        
        success = len(metrics) >= total_expected * 0.8  # 80% success rate
        print(f"\n🎯 Comprehensive Report: {'✅ PASS' if success else '❌ FAIL'}")
        print(f"   Extracted: {len(metrics)}/{total_expected} metrics")
        
        return success
        
    except Exception as e:
        print(f"❌ Error processing comprehensive report: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Extended Lab Categories Test Suite")
    print("=" * 80)
    
    # Run all category tests
    biochemical_result = test_biochemical_analysis()
    hormonal_result = test_hormonal_profile()
    coagulation_result = test_coagulation_tests()
    hepatitis_result = test_hepatitis_markers()
    spelling_result = test_alternative_spellings()
    comprehensive_result = test_mixed_comprehensive_report()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 EXTENDED LAB CATEGORIES TEST RESULTS:")
    print(f"  Biochemical Analysis:     {'✅ PASS' if biochemical_result else '❌ FAIL'}")
    print(f"  Hormonal Profile:         {'✅ PASS' if hormonal_result else '❌ FAIL'}")
    print(f"  Coagulation Tests:        {'✅ PASS' if coagulation_result else '❌ FAIL'}")
    print(f"  Hepatitis Markers:        {'✅ PASS' if hepatitis_result else '❌ FAIL'}")
    print(f"  Alternative Spellings:    {'✅ PASS' if spelling_result else '❌ FAIL'}")
    print(f"  Comprehensive Report:     {'✅ PASS' if comprehensive_result else '❌ FAIL'}")
    
    overall_success = all([biochemical_result, hormonal_result, coagulation_result, 
                          hepatitis_result, spelling_result, comprehensive_result])
    
    print(f"\n🎯 OVERALL: {'✅ ALL LAB CATEGORIES WORKING' if overall_success else '❌ SOME ISSUES REMAIN'}")
    
    if overall_success:
        print("\n🎉 SUCCESS: Extended lab categories are working correctly!")
        print("   • Biochemical analysis metrics properly parsed")
        print("   • Hormonal profile tests recognized")  
        print("   • Coagulation tests handled correctly")
        print("   • Qualitative hepatitis markers working")
        print("   • Alternative spellings and abbreviations supported")
        print("   • Comprehensive mixed reports processed successfully")
    else:
        print("\n⚠️  Some lab categories need attention - see details above")
    
    print("=" * 80) 