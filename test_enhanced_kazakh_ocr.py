#!/usr/bin/env python3
"""
Test script for enhanced Kazakh OCR functionality
"""

import sys
import os

# Add backend to path to import services
sys.path.append('backend')
from app.services.ocr_service import extract_text_from_image

def test_enhanced_kazakh_ocr():
    """Test the enhanced OCR service with the Kazakh medical document"""
    
    image_path = "backend/uploads/user_3/WhatsApp Image 2025-05-24 at 23.09.02.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("🚀 Testing Enhanced Kazakh OCR Service")
    print("="*60)
    
    try:
        # Use the enhanced OCR service
        result = extract_text_from_image(image_path)
        
        print(f"📝 Extracted Text Length: {len(result['extracted_text'])} characters")
        print(f"📊 Analysis Valid: {result['analysis']['valid']}")
        print(f"📋 Validation Message: {result['analysis']['validation_message']}")
        print(f"🔬 Metrics Found: {len(result['analysis']['metrics'])}")
        
        print(f"\n🎯 Extracted Metrics:")
        print("="*60)
        
        if result['analysis']['metrics']:
            for i, metric in enumerate(result['analysis']['metrics'], 1):
                print(f"{i:2d}. {metric['name']}: {metric['value']} {metric['unit']}")
                print(f"    Range: {metric['reference_range']}")
                print(f"    Status: {metric['status']}")
                print()
        else:
            print("❌ No metrics extracted!")
        
        # Show extracted text sample
        print(f"\n📄 Extracted Text Sample:")
        print("="*60)
        text_lines = result['extracted_text'].split('\n')[:10]
        for i, line in enumerate(text_lines, 1):
            if line.strip():
                print(f"{i:2d}: {line}")
        
        if len(result['extracted_text'].split('\n')) > 10:
            print(f"... and {len(result['extracted_text'].split('\n')) - 10} more lines")
        
        # Expected results validation
        print(f"\n✅ Expected Results Validation:")
        print("="*60)
        
        expected_metrics = [
            ('ALT', 66.19, 'high'),
            ('AST', 25.2, 'normal'),
            ('Amylase', 48.84, 'normal'),
            ('ALP', 50.53, 'normal'),
            ('GGT', 31.45, 'normal'),
            ('Glucose', 4.71, 'normal'),
            ('Total Bilirubin', 10.51, 'normal')
        ]
        
        found_metrics = {m['name']: m for m in result['analysis']['metrics']}
        
        for expected_name, expected_value, expected_status in expected_metrics:
            if expected_name in found_metrics:
                metric = found_metrics[expected_name]
                value_match = abs(metric['value'] - expected_value) < 0.01
                status_match = metric['status'] == expected_status
                
                status_icon = "✅" if value_match and status_match else "❌"
                print(f"{status_icon} {expected_name}: {metric['value']} (expected {expected_value}) - {metric['status']} (expected {expected_status})")
            else:
                print(f"❌ {expected_name}: NOT FOUND (expected {expected_value})")
        
        success_rate = len(found_metrics) / len(expected_metrics) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}% ({len(found_metrics)}/{len(expected_metrics)} metrics)")
        
        if success_rate >= 80:
            print("🎉 SUCCESS: Enhanced OCR is working well!")
        elif success_rate >= 50:
            print("⚠️  PARTIAL SUCCESS: Some metrics extracted, needs improvement")
        else:
            print("❌ FAILURE: OCR enhancement needs more work")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_kazakh_ocr() 