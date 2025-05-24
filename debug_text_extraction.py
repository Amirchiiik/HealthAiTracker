#!/usr/bin/env python3
"""
Debug script to examine extracted text and parsing pipeline
"""

import easyocr
import sys
import os

# Add backend to path to import services
sys.path.append('backend')
from app.services.ocr_service import extract_lab_lines, extract_metrics_from_text

def analyze_text_extraction():
    """Analyze what text is being extracted and how it's processed"""
    
    image_path = "backend/uploads/user_3/WhatsApp Image 2025-05-24 at 23.09.02.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("🔍 Analyzing text extraction pipeline...")
    
    # Step 1: Raw OCR extraction
    reader = easyocr.Reader(['en', 'ru'], gpu=False)
    results = reader.readtext(image_path, detail=0)
    raw_text = "\n".join(results)
    
    print(f"\n📝 Step 1: Raw OCR Results ({len(results)} pieces)")
    print("="*60)
    for i, text in enumerate(results):
        print(f"{i+1:3d}: {text}")
    
    # Step 2: Lab lines processing
    print(f"\n🔬 Step 2: Lab Lines Processing")
    print("="*60)
    clean_text = extract_lab_lines(raw_text)
    print("Processed text:")
    print(clean_text)
    
    # Step 3: Metrics extraction
    print(f"\n⚗️ Step 3: Metrics Extraction")
    print("="*60)
    extracted_metrics = extract_metrics_from_text(clean_text)
    print(f"Found {len(extracted_metrics)} metrics:")
    for metric in extracted_metrics:
        print(f"  - {metric}")
    
    # Step 4: Look for specific medical terms
    print(f"\n🔍 Step 4: Medical Terms Detection")
    print("="*60)
    
    medical_terms = [
        'АЛТ', 'АЛАТ', 'АСТ', 'АСАТ',
        'Амилаза', 'альфа-амилаза', 'амилаза',
        'Щелочная фосфатаза', 'ЩФ',
        'ГГТ', 'ГГТП',
        'Глюкоза', 'глюкоза',
        'Билирубин', 'билирубин',
        'Ед/л', 'ммоль/л', 'мкмоль/л'
    ]
    
    found_terms = []
    for term in medical_terms:
        for text_piece in results:
            if term.lower() in text_piece.lower():
                found_terms.append((term, text_piece))
    
    if found_terms:
        print("Found medical terms:")
        for term, context in found_terms:
            print(f"  '{term}' in: {context}")
    else:
        print("❌ No medical terms found!")
    
    # Step 5: Look for biochemical data patterns
    print(f"\n🧪 Step 5: Biochemical Data Patterns")
    print("="*60)
    
    import re
    
    # Look for number + unit patterns
    value_patterns = [
        r'\d+[.,]\d+\s*Ед/л',
        r'\d+[.,]\d+\s*ммоль/л', 
        r'\d+[.,]\d+\s*мкмоль/л',
        r'\d+[.,]\d+.*?Ед',
        r'\d+[.,]\d+.*?ммоль',
        r'\d+[.,]\d+.*?мкмоль'
    ]
    
    pattern_matches = []
    for pattern in value_patterns:
        for text_piece in results:
            matches = re.findall(pattern, text_piece, re.IGNORECASE)
            if matches:
                pattern_matches.extend([(match, text_piece) for match in matches])
    
    if pattern_matches:
        print("Found value patterns:")
        for match, context in pattern_matches:
            print(f"  '{match}' in: {context}")
    else:
        print("❌ No value patterns found!")

if __name__ == "__main__":
    print("🚀 Starting Text Extraction Analysis")
    analyze_text_extraction()
    print(f"\n{'='*60}")
    print("🎯 Analysis complete!") 