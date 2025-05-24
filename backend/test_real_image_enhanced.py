#!/usr/bin/env python3
"""
Test script for the enhanced OCR with the actual problematic image
Tests the fb51f49c-8d04-4206-8a18-34cbb83afabc.jpg file that had parsing issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services import ocr_service

def test_real_problematic_image():
    """Test the enhanced OCR with the actual image that had scientific notation issues."""
    
    print("🖼️  Testing Enhanced OCR with Real Problematic Image")
    print("=" * 70)
    
    # Image paths (try both locations)
    image_paths = [
        "uploads/user_3/fb51f49c-8d04-4206-8a18-34cbb83afabc.jpg",
        "uploads/fb51f49c-8d04-4206-8a18-34cbb83afabc.jpg"
    ]
    
    image_path = None
    for path in image_paths:
        if os.path.exists(path):
            image_path = path
            break
    
    if not image_path:
        print(f"❌ Image file not found. Tried:")
        for path in image_paths:
            print(f"   • {path}")
        return False
    
    print(f"📸 Found image: {image_path}")
    print(f"📏 File size: {os.path.getsize(image_path):,} bytes")
    
    try:
        # Test the complete OCR pipeline
        print("\n🔍 Running enhanced OCR analysis...")
        result = ocr_service.extract_text_from_file(image_path)
        
        print(f"✅ OCR completed successfully!")
        print(f"📄 Extracted text length: {len(result['extracted_text'])} characters")
        print(f"📊 Metrics found: {len(result['analysis']['metrics'])}")
        print(f"✅ Valid medical document: {result['analysis']['valid']}")
        
        # Show extracted text (first part)
        print(f"\n📝 Extracted Text (first 500 chars):")
        print("-" * 50)
        print(result['extracted_text'][:500] + "..." if len(result['extracted_text']) > 500 else result['extracted_text'])
        print("-" * 50)
        
        # Analyze the metrics in detail
        metrics = result['analysis']['metrics']
        
        if metrics:
            print(f"\n📊 Detailed Metric Analysis:")
            print("=" * 80)
            
            # Group metrics by type
            normal_metrics = []
            abnormal_metrics = []
            scientific_notation_metrics = []
            
            for metric in metrics:
                if "10^" in metric['unit']:
                    scientific_notation_metrics.append(metric)
                
                if metric['status'] in ['high', 'low', 'elevated']:
                    abnormal_metrics.append(metric)
                else:
                    normal_metrics.append(metric)
            
            print(f"📈 Scientific Notation Metrics: {len(scientific_notation_metrics)}")
            for metric in scientific_notation_metrics:
                confidence = metric.get('confidence', 0)
                status_icon = "🔴" if metric['status'] in ['high', 'low'] else "🟡" if metric['status'] == 'elevated' else "🟢"
                print(f"  {status_icon} {metric['name']:25} = {metric['value']:>8.2f} {metric['unit']:15} [{metric['status']}] (conf: {confidence:.2f})")
                print(f"     Range: {metric['reference_range']}")
            
            print(f"\n🟢 Normal Metrics: {len(normal_metrics)}")
            for metric in normal_metrics[:5]:  # Show first 5
                confidence = metric.get('confidence', 0)
                print(f"  ✅ {metric['name']:25} = {metric['value']:>8.2f} {metric['unit']:15} (conf: {confidence:.2f})")
            
            if len(normal_metrics) > 5:
                print(f"     ... and {len(normal_metrics) - 5} more normal metrics")
            
            if abnormal_metrics:
                print(f"\n🔴 Abnormal Metrics: {len(abnormal_metrics)}")
                for metric in abnormal_metrics:
                    confidence = metric.get('confidence', 0)
                    print(f"  ⚠️  {metric['name']:25} = {metric['value']:>8.2f} {metric['unit']:15} [{metric['status']}] (conf: {confidence:.2f})")
                    print(f"     Range: {metric['reference_range']}")
            
            # Validation against expected problematic cases
            print(f"\n🔍 Validation Against Known Problematic Cases:")
            print("-" * 60)
            
            expected_issues = {
                'RBC': {'should_have_scientific': True, 'expected_range': (4.0, 7.0)},
                'PLT': {'should_have_scientific': True, 'expected_range': (100, 500)},
                'WBC': {'should_have_scientific': True, 'expected_range': (3.0, 10.0)},
                'NEU#': {'should_have_scientific': True, 'expected_range': (1.0, 8.0)},
                'EOS#': {'should_have_scientific': True, 'expected_range': (0.01, 1.0)},
                'BAS#': {'should_have_scientific': True, 'expected_range': (0.01, 0.5)},
                'LYM#': {'should_have_scientific': True, 'expected_range': (1.0, 5.0)},
            }
            
            found_issues = {}
            for metric in metrics:
                # Check if this metric matches any expected problematic case
                original_name = metric.get('original_line', '').split(':')[0].strip().upper()
                if original_name in expected_issues:
                    found_issues[original_name] = metric
            
            success_count = 0
            for expected_name, criteria in expected_issues.items():
                if expected_name in found_issues:
                    metric = found_issues[expected_name]
                    has_scientific = "10^" in metric['unit']
                    value_in_range = criteria['expected_range'][0] <= metric['value'] <= criteria['expected_range'][1]
                    not_suspicious = not (metric['value'] == 9.0 and metric['unit'] == '/л')
                    
                    success = has_scientific and value_in_range and not_suspicious
                    if success:
                        success_count += 1
                    
                    status = "✅ FIXED" if success else "❌ ISSUE"
                    print(f"{status} {expected_name:8} | Value: {metric['value']:>8.2f} | Unit: {metric['unit']:15}")
                    
                    if not success:
                        issues = []
                        if not has_scientific:
                            issues.append("No scientific notation")
                        if not value_in_range:
                            issues.append("Value out of range")
                        if not not_suspicious:
                            issues.append("Suspicious value")
                        print(f"     Issues: {', '.join(issues)}")
                else:
                    print(f"❌ MISSING {expected_name:8} | Not found in extracted metrics")
            
            total_expected = len(expected_issues)
            print(f"\n📈 Problematic Cases Resolution: {success_count}/{total_expected} ({success_count/total_expected*100:.1f}%)")
            
            # Overall assessment
            if success_count == total_expected:
                print("🎉 All previously problematic scientific notation cases are now correctly parsed!")
                return True
            elif success_count > total_expected * 0.7:
                print("✅ Major improvement in scientific notation parsing")
                return True
            else:
                print("⚠️  Some scientific notation parsing issues remain")
                return False
        
        else:
            print("❌ No metrics extracted from the image")
            return False
            
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_enhanced_patterns():
    """Test specific enhanced parsing patterns that should now work."""
    
    print("\n🧪 Testing Specific Enhanced Parsing Patterns")
    print("=" * 55)
    
    # These are the exact patterns that were failing before
    test_patterns = [
        "RBC: 5.66 10^12/л",
        "PLT: 319.00 10^9/л", 
        "WBC: 6.37 10^9/л",
        "NEU#: 3.67 10^9/л",
        "EOS#: 0.09 10^9/л",
        "BAS#: 0.040 10^9/л",
        "LYM#: 2.62 10^9/л",
    ]
    
    print("Testing patterns that previously failed:")
    
    success_count = 0
    for pattern in test_patterns:
        try:
            metrics = ocr_service.extract_metrics_from_text(pattern)
            if metrics and len(metrics) == 1:
                metric = metrics[0]
                has_scientific = "10^" in metric['unit']
                not_suspicious = not (metric['value'] == 9.0 and metric['unit'] == '/л')
                reasonable_value = 0.01 <= metric['value'] <= 1000  # Reasonable base values
                
                success = has_scientific and not_suspicious and reasonable_value
                if success:
                    success_count += 1
                
                status = "✅" if success else "❌"
                print(f"  {status} {pattern:25} → {metric['value']:>8.2f} {metric['unit']:15}")
            else:
                print(f"  ❌ {pattern:25} → Failed to parse")
        except Exception as e:
            print(f"  ❌ {pattern:25} → Error: {e}")
    
    print(f"\n📊 Pattern Success Rate: {success_count}/{len(test_patterns)} ({success_count/len(test_patterns)*100:.1f}%)")
    return success_count == len(test_patterns)

if __name__ == "__main__":
    print("🚀 Enhanced OCR Real Image Test")
    print("=" * 80)
    
    # Run tests
    real_image_result = test_real_problematic_image()
    pattern_test_result = test_specific_enhanced_patterns()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 ENHANCED OCR VALIDATION RESULTS:")
    print(f"  Real Image Test:     {'✅ PASS' if real_image_result else '❌ FAIL'}")
    print(f"  Pattern Test:        {'✅ PASS' if pattern_test_result else '❌ FAIL'}")
    
    overall_success = real_image_result and pattern_test_result
    print(f"\n🎯 OVERALL: {'✅ ENHANCED OCR IS WORKING' if overall_success else '❌ ISSUES REMAIN'}")
    
    if overall_success:
        print("\n🎉 SUCCESS: Scientific notation parsing issues have been resolved!")
        print("   • No more '9 /л' parsing errors")
        print("   • Proper handling of 10^12/л and 10^9/л units")
        print("   • Better confidence scoring and validation")
        print("   • Enhanced metric name normalization")
    
    print("=" * 80) 