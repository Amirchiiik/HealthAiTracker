#!/usr/bin/env python3
"""
Debug script to diagnose OCR failure with Kazakh medical documents
"""

import easyocr
import cv2
import os
from PIL import Image
import numpy as np

def test_ocr_configurations():
    """Test different EasyOCR language configurations"""
    
    # Use the actual failing image
    image_path = "backend/uploads/user_3/WhatsApp Image 2025-05-24 at 23.09.02.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"🔍 Testing OCR with image: {image_path}")
    
    # Test different language configurations
    configs = [
        (['en', 'ru'], "English + Russian"),
        (['en', 'ru', 'kk'], "English + Russian + Kazakh"), 
        (['ru', 'kk'], "Russian + Kazakh"),
        (['kk'], "Kazakh only"),
    ]
    
    for languages, description in configs:
        print(f"\n{'='*50}")
        print(f"Testing: {description} {languages}")
        print('='*50)
        
        try:
            reader = easyocr.Reader(languages, gpu=False)
            results = reader.readtext(image_path, detail=0)
            
            if results:
                print(f"✅ SUCCESS: Found {len(results)} text pieces")
                for i, text in enumerate(results[:10]):  # Show first 10 results
                    print(f"  {i+1:2d}: {text}")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more pieces")
            else:
                print("❌ FAILURE: No text extracted")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

def test_image_preprocessing():
    """Test different image preprocessing techniques"""
    
    image_path = "backend/uploads/user_3/WhatsApp Image 2025-05-24 at 23.09.02.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"\n🔧 Testing image preprocessing...")
    
    # Load image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Test different preprocessing
    preprocessed_images = [
        (gray, "Original grayscale"),
        (cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)[1], "Binary threshold"),
        (cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2), "Adaptive threshold"),
        (cv2.medianBlur(gray, 3), "Median blur"),
        (cv2.GaussianBlur(gray, (5,5), 0), "Gaussian blur"),
    ]
    
    reader = easyocr.Reader(['en', 'ru'], gpu=False)
    
    for processed_img, description in preprocessed_images:
        print(f"\n--- {description} ---")
        
        # Save temp processed image
        temp_path = f"/tmp/processed_{description.replace(' ', '_')}.jpg"
        cv2.imwrite(temp_path, processed_img)
        
        try:
            results = reader.readtext(temp_path, detail=0)
            if results:
                print(f"✅ Found {len(results)} pieces: {results[:3]}...")
            else:
                print("❌ No text found")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

def check_image_properties():
    """Check basic image properties"""
    
    image_path = "backend/uploads/user_3/WhatsApp Image 2025-05-24 at 23.09.02.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"\n📊 Image Properties:")
    
    # OpenCV analysis
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = gray.std()
    
    print(f"  Resolution: {width}x{height}")
    print(f"  Sharpness: {sharpness:.2f}")
    print(f"  Contrast: {contrast:.2f}")
    print(f"  File size: {os.path.getsize(image_path)} bytes")
    
    # PIL analysis
    with Image.open(image_path) as pil_img:
        print(f"  Format: {pil_img.format}")
        print(f"  Mode: {pil_img.mode}")
        print(f"  PIL Size: {pil_img.size}")

if __name__ == "__main__":
    print("🚀 Starting Kazakh OCR Debug Session")
    
    check_image_properties()
    test_image_preprocessing()
    test_ocr_configurations()
    
    print(f"\n{'='*60}")
    print("🎯 Debug session complete!")
    print("Check results above to identify the best OCR configuration.") 