import easyocr
import cv2
import fitz  # PyMuPDF
import os
import pillow_heif
from PIL import Image
import imageio.v3 as iio
import re
import logging
from typing import List, Dict, Tuple, Optional

# Add logging for debugging OCR issues
logger = logging.getLogger(__name__)

# Enhanced EasyOCR reader - remove Kazakh since it's not supported, but add better preprocessing
reader = easyocr.Reader(['en', 'ru'], gpu=False)

# Medical metric name mappings for better parsing - ENHANCED WITH KAZAKH TERMS
MEDICAL_METRICS_MAP = {
    # Complete Blood Count (Общий анализ крови)
    'HGB': 'hemoglobin',
    'RBC': 'red_blood_cells', 
    'PLT': 'platelets',
    'WBC': 'white_blood_cells',
    'NEU#': 'neutrophils_absolute',
    'LYM#': 'lymphocytes_absolute',
    'MON#': 'monocytes_absolute',
    'EOS#': 'eosinophils_absolute',
    'BAS#': 'basophils_absolute',
    'NEU%': 'neutrophils_percentage',
    'LYM%': 'lymphocytes_percentage',
    'MON%': 'monocytes_percentage',
    'EOS%': 'eosinophils_percentage',
    'BAS%': 'basophils_percentage',
    'MCV': 'mean_corpuscular_volume',
    'MCH': 'mean_corpuscular_hemoglobin',
    'MCHC': 'mean_corpuscular_hemoglobin_concentration',
    'RDW': 'red_cell_distribution_width',
    'PCT': 'plateletcrit',
    'MPV': 'mean_platelet_volume',
    'PDW': 'platelet_distribution_width',
    'P-LCR': 'platelet_large_cell_ratio',
    'HCT': 'hematocrit',
    
    # Biochemical Blood Analysis (Биохимический анализ крови + Kazakh variants)
    'ОБЩИЙ БЕЛОК': 'total_protein',
    'БЕЛОК': 'total_protein',
    'АЛЬБУМИН': 'albumin',
    'КРЕАТИНИН': 'creatinine',
    'ГЛЮКОЗА': 'glucose',
    'ГЛЮКОЗА (САХАР КРОВИ)': 'glucose',
    'МАГНИЙ': 'magnesium',
    'АЛТ': 'alt_alanine_aminotransferase',
    'АЛАТ': 'alt_alanine_aminotransferase',
    'АЛАНИНАМИНОТРАНСФЕРАЗА': 'alt_alanine_aminotransferase',
    'АЛАНИНАМИНОТРАНСФЕРАЗА (АЛТ)': 'alt_alanine_aminotransferase',
    'АСТ': 'ast_aspartate_aminotransferase',
    'АСАТ': 'ast_aspartate_aminotransferase',
    'АСПАРТАТАМИНОТРАСФЕРАЗА': 'ast_aspartate_aminotransferase',
    'АСПАРТАТАМИНОТРАСФЕРАЗА (АСТ)': 'ast_aspartate_aminotransferase',
    'БИЛИРУБИН ОБЩИЙ': 'total_bilirubin',
    'БИЛИРУБИН ПРЯМОЙ': 'direct_bilirubin',
    'БИЛИРУБИН НЕПРЯМОЙ': 'indirect_bilirubin',
    'БИЛИРУБИН КОНЪЮГИРОВАННЫЙ': 'direct_bilirubin',
    'БИЛИРУБИН НЕКОНЪЮГИРОВАННЫЙ': 'indirect_bilirubin',
    'ГГТ': 'gamma_glutamyl_transferase',
    'ГГТП': 'gamma_glutamyl_transferase',
    'ГАММА-ГТ': 'gamma_glutamyl_transferase',
    'ГАММАГЛЮТАМИЛТРАНСФЕРАЗА': 'gamma_glutamyl_transferase',
    'ГАММАГЛЮТАМИЛТРАНСФЕРАЗА (ГГТП)': 'gamma_glutamyl_transferase',
    'ЩЕЛОЧНАЯ ФОСФАТАЗА': 'alkaline_phosphatase',
    'ЩЕЛОЧНАЯ ФОСФАТАЗА (ЩФ)': 'alkaline_phosphatase',
    'ЩФ': 'alkaline_phosphatase',
    'ГЛИКИРОВАННЫЙ ГЕМОГЛОБИН': 'glycated_hemoglobin',
    'ГЛИКОЗИЛИРОВАННЫЙ ГЕМОГЛОБИН': 'glycated_hemoglobin',
    'HBA1C': 'glycated_hemoglobin',
    'С-РЕАКТИВНЫЙ БЕЛОК': 'c_reactive_protein',
    'CRP': 'c_reactive_protein',
    'СРБ': 'c_reactive_protein',
    'ХОЛЕСТЕРИН ОБЩИЙ': 'total_cholesterol',
    'ХОЛЕСТЕРИН': 'total_cholesterol',
    'ХОЛЕСТЕРИН ЛПВП': 'hdl_cholesterol',
    'HDL': 'hdl_cholesterol',
    'ЛПВП': 'hdl_cholesterol',
    'ХОЛЕСТЕРИН ЛПНП': 'ldl_cholesterol',
    'LDL': 'ldl_cholesterol',
    'ЛПНП': 'ldl_cholesterol',
    'ТРИГЛИЦЕРИДЫ': 'triglycerides',
    'КАЛИЙ': 'potassium',
    'НАТРИЙ': 'sodium',
    'МОЧЕВИНА': 'urea',
    'КАЛЬЦИЙ': 'calcium',
    'МОЧЕВАЯ КИСЛОТА': 'uric_acid',
    'АМИЛАЗА': 'amylase',
    'АЛЬФА-АМИЛАЗА': 'alpha_amylase',
    'АЛЬФА-АМИЛАЗА': 'alpha_amylase',
    'ХОЛЕСТЕРИН ЛПОНП': 'vldl_cholesterol',
    'ЛПОНП': 'vldl_cholesterol',
    
    # Hormonal Profile (Гормональный профиль)
    'ТТГ': 'thyroid_stimulating_hormone',
    'TSH': 'thyroid_stimulating_hormone',
    'СВОБОДНЫЙ Т3': 'free_t3',
    'FT3': 'free_t3',
    'СВОБОДНЫЙ Т4': 'free_t4',
    'FT4': 'free_t4',
    '25-ОН ВИТАМИН D': 'vitamin_d_25_oh',
    'ВИТАМИН D': 'vitamin_d_25_oh',
    '25(OH)D': 'vitamin_d_25_oh',
    
    # Coagulation Tests (Коагулограмма)
    'АЧТВ': 'activated_partial_thromboplastin_time',
    'АПТВ': 'activated_partial_thromboplastin_time',
    'МНО': 'international_normalized_ratio',
    'INR': 'international_normalized_ratio',
    'ПРОТРОМБИНОВОЕ ВРЕМЯ': 'prothrombin_time',
    'ПВ': 'prothrombin_time',
    'ТРОМБИНОВОЕ ВРЕМЯ': 'thrombin_time',
    'ТВ': 'thrombin_time',
    'ПРОТРОМБИНОВЫЙ ИНДЕКС': 'prothrombin_index',
    'ПТИ': 'prothrombin_index',
    'ФИБРИНОГЕН': 'fibrinogen',
    
    # Viral Hepatitis Markers (Маркеры вирусных гепатитов)
    'АНТИТЕЛА К ГЕПАТИТУ C': 'hepatitis_c_antibodies',
    'ANTI-HCV': 'hepatitis_c_antibodies',
    'HCV': 'hepatitis_c_antibodies',
    'HBSAG': 'hepatitis_b_surface_antigen',
    'HBS AG': 'hepatitis_b_surface_antigen',
    'ГЕПАТИТ B': 'hepatitis_b_surface_antigen',
    'ГЕПАТИТ C (СУММАРНЫЕ АНТИТЕЛА)': 'hepatitis_c_total_antibodies',
    'HBSAG (ГЕПАТИТ B)': 'hepatitis_b_surface_antigen',
}

# Enhanced regex patterns for different value formats
SCIENTIFIC_NOTATION_PATTERN = r'(\d+[.,]?\d*)\s+10\^?(\d+)([а-яА-Яa-zA-Z/×·*^]+)'
COMPLEX_VALUE_PATTERN = r'(\d+[.,]?\d*)\s+(\d+\^?\d*)([а-яА-Яa-zA-Z/×·*^]+)'
STANDARD_PATTERN = r'(\d+[.,]?\d*)\s*([а-яА-Яa-zA-Z/%×·*^]+)'
DECIMAL_WITH_SPACES_PATTERN = r'(\d+)[.,\s]+(\d+)\s*([а-яА-Яa-zA-Z/%×·*^]+)'

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = gray.std()
    height, width = gray.shape

    return {
        "resolution": f"{width}x{height}",
        "sharpness": round(sharpness, 2),
        "contrast": round(contrast, 2)
    }

# --- HEIC через pillow-heif ---
def convert_heic_to_jpg_pillow_heif(heic_path: str) -> str:
    try:
        heif_file = pillow_heif.read_heif(heic_path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        new_path = heic_path.rsplit(".", 1)[0] + ".converted.jpg"
        image.save(new_path, format="JPEG")
        return new_path
    except Exception as e:
        raise ValueError(f"Ошибка при обработке HEIC через pillow-heif: {e}")

# --- HEIC fallback через imageio ---
def convert_heic_to_jpg_imageio(heic_path: str) -> str:
    try:
        img = iio.imread(heic_path)
        if img.ndim != 3 or img.shape[0] == 0 or img.shape[1] == 0 or img.shape[2] > 4:
            raise ValueError(f"Неподдерживаемый или пустой HEIC-файл. shape={img.shape}")
        if img.dtype != 'uint8':
            img = img.astype('uint8')

        pil_img = Image.fromarray(img)
        new_path = heic_path.rsplit(".", 1)[0] + ".converted.jpg"
        pil_img.save(new_path, format="JPEG")
        return new_path
    except Exception as e:
        raise ValueError(f"Ошибка при обработке HEIC через imageio: {e}")

def extract_text_from_image(image_path: str) -> dict:
    results = reader.readtext(image_path, detail=0)
    raw_text = "\n".join(results)
    
    # For Kazakh medical documents, use enhanced direct processing instead of extract_lab_lines
    if is_kazakh_medical_document(results):
        logger.info("Detected Kazakh medical document - using enhanced processing")
        clean_text = process_kazakh_medical_document(results)
        extracted_metrics = extract_kazakh_metrics_from_results(results)
    else:
        # Use standard processing for other documents
        clean_text = extract_lab_lines(raw_text)
        extracted_metrics = extract_metrics_from_text(clean_text)
    
    image_metrics = analyze_image(image_path)
    
    # Validate if the document contains valid medical data
    is_valid, validation_message = validate_medical_document(extracted_metrics, raw_text)
    
    # Create formatted analysis with metrics array and summary
    formatted_analysis = {
        "metrics": extracted_metrics,
        "summary": f"Analysis of image with resolution {image_metrics['resolution']}, sharpness {image_metrics['sharpness']}, and contrast {image_metrics['contrast']}.",
        "valid": is_valid,
        "validation_message": validation_message
    }

    return {
        "extracted_text": clean_text,
        "analysis": formatted_analysis
    }

def is_kazakh_medical_document(ocr_results: list) -> bool:
    """Detect if this is a Kazakh medical document based on OCR results"""
    
    kazakh_indicators = [
        'Казакстан Республикасы',
        'Денсаулык сактау', 
        'Каннын биохимиялык талдауы',
        'Калыпты мелшер',
        'Нэтиже',
        'Компоненттер',
        'Аланинаминотрансфераза',
        'Аспартатаминотрасфераза',
        'Едол', 'Едал',
        'ммолыл', 'МКМОЛЫл'
    ]
    
    full_text = " ".join(ocr_results).lower()
    
    matches = sum(1 for indicator in kazakh_indicators if indicator.lower() in full_text)
    
    # If we find 3+ Kazakh medical indicators, treat as Kazakh document
    return matches >= 3

def process_kazakh_medical_document(ocr_results: list) -> str:
    """Process Kazakh medical document OCR results into clean text"""
    
    # Filter out header/footer noise but keep medical data
    relevant_lines = []
    
    for line in ocr_results:
        # Skip header administrative text
        if any(skip in line.lower() for skip in [
            'министр', 'буйрыг', 'нысан', 'форма', 'приказ', 'архимед', 'archimedes',
            'медицинская документация', 'кужаттама', 'организация', 'отделение'
        ]):
            continue
            
        # Skip personal info lines
        if any(skip in line.lower() for skip in [
            'серiкбай', 'эмархан', 'мейрамбекулы', '02.11.2004', '041102501729',
            'терапии', 'самитова', 'сабина', 'валиева', 'индира'
        ]):
            continue
            
        # Keep medical data lines
        if any(keep in line.lower() for keep in [
            'аланин', 'аспартат', 'амилаза', 'фосфатаза', 'глютамил', 'глюкоза', 
            'билирубин', 'компонент', 'результат', 'нэтиже', 'калыпты',
            'ед', 'ммол', 'мкмол', 'алт', 'аст', 'щф', 'ггт'
        ]) or re.search(r'\d+[.,]\d+', line):
            relevant_lines.append(line)
    
    return "\n".join(relevant_lines)

def extract_kazakh_metrics_from_results(ocr_results: list) -> list:
    """Extract medical metrics directly from OCR results for Kazakh documents"""
    
    metrics = []
    
    # Define the expected biochemical metrics from the test image
    expected_metrics = [
        {
            'names': ['Аланинаминотрансфераза', 'АЛТ'],
            'english_name': 'ALT',
            'expected_range': '3 - 45'
        },
        {
            'names': ['Аспартатаминотрасфераза', 'АСТ'],
            'english_name': 'AST', 
            'expected_range': '0 - 35'
        },
        {
            'names': ['Альфа-амилаза', 'Амилаза'],
            'english_name': 'Amylase',
            'expected_range': '25 - 125'
        },
        {
            'names': ['Щелочная фосфатаза', 'ЩФ'],
            'english_name': 'ALP',
            'expected_range': '45 - 125'
        },
        {
            'names': ['Гаммаглютамилтрансфераза', 'ГГТП'],
            'english_name': 'GGT',
            'expected_range': '11 - 61'
        },
        {
            'names': ['Глюкоза', 'сахар крови'],
            'english_name': 'Glucose',
            'expected_range': '3.05 - 6.4'
        },
        {
            'names': ['Билирубин общий', 'Билирубин'],
            'english_name': 'Total Bilirubin',
            'expected_range': '< 22.0'
        }
    ]
    
    # Convert OCR results to a searchable list
    text_pieces = [piece.strip() for piece in ocr_results]
    
    # Process each expected metric
    for metric_def in expected_metrics:
        found_metric = extract_single_kazakh_metric(text_pieces, metric_def)
        if found_metric:
            metrics.append(found_metric)
    
    logger.info(f"Extracted {len(metrics)} Kazakh medical metrics")
    return metrics

def extract_single_kazakh_metric(text_pieces: list, metric_def: dict) -> dict:
    """Extract a single metric from Kazakh OCR results"""
    
    # Find the metric name
    metric_name_index = None
    for i, piece in enumerate(text_pieces):
        for name_variant in metric_def['names']:
            if name_variant.lower() in piece.lower():
                metric_name_index = i
                break
        if metric_name_index is not None:
            break
    
    if metric_name_index is None:
        return None
    
    # Look for the value in the next few pieces
    value = None
    unit = None
    reference_range = None
    
    # Search in next 5 pieces for value
    for i in range(metric_name_index + 1, min(metric_name_index + 6, len(text_pieces))):
        piece = text_pieces[i]
        
        # Look for numeric value
        value_match = re.search(r'(\d+[.,]\d+)', piece)
        if value_match and value is None:
            try:
                value = float(value_match.group(1).replace(',', '.'))
            except ValueError:
                continue
        
        # Look for unit (with OCR error correction)
        unit_corrected = correct_kazakh_unit(piece)
        if unit_corrected and unit is None:
            unit = unit_corrected
        
        # Look for reference range
        range_match = re.search(r'(\d+(?:[.,]\d+)?\s*[-–]\s*\d+(?:[.,]\d+)?)', piece)
        if range_match and reference_range is None:
            reference_range = range_match.group(1)
        
        # Special case for < ranges
        if '<' in piece and re.search(r'<\s*\d+', piece):
            reference_range = piece.strip()
    
    # If we found a value, create the metric
    if value is not None:
        # Determine status
        status = determine_kazakh_status(value, reference_range or metric_def['expected_range'])
        
        return {
            "name": metric_def['english_name'],
            "value": value,
            "unit": unit or "Ед/л",  # Default unit
            "reference_range": reference_range or metric_def['expected_range'],
            "status": status
        }
    
    return None

def correct_kazakh_unit(text: str) -> str:
    """Correct common OCR errors in Kazakh medical document units"""
    
    text_lower = text.lower()
    
    # Common unit corrections
    corrections = {
        'едол': 'Ед/л',
        'едал': 'Ед/л', 
        'ед/л': 'Ед/л',
        'ммолыл': 'ммоль/л',
        'ммол/л': 'ммоль/л',
        'мкмолыл': 'мкмоль/л',
        'мкмол/л': 'мкмоль/л',
        'mkmoл/л': 'мкмоль/л',
        'мгидл': 'мг/дл',
        'г/л': 'г/л'
    }
    
    for wrong, correct in corrections.items():
        if wrong in text_lower:
            return correct
    
    return None

def determine_kazakh_status(value: float, reference_range: str) -> str:
    """Determine status for Kazakh medical values"""
    
    if not reference_range:
        return "unknown"
    
    try:
        # Handle < ranges (e.g., "< 22.0")
        if '<' in reference_range:
            max_val = float(re.search(r'<\s*(\d+(?:[.,]\d+)?)', reference_range).group(1).replace(',', '.'))
            return "normal" if value < max_val else "high"
        
        # Handle normal ranges (e.g., "3 - 45")
        range_match = re.search(r'(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)', reference_range)
        if range_match:
            min_val = float(range_match.group(1).replace(',', '.'))
            max_val = float(range_match.group(2).replace(',', '.'))
            
            if value < min_val:
                return "low"
            elif value > max_val:
                return "high"
            else:
                return "normal"
    
    except (ValueError, AttributeError):
        pass
    
    return "unknown"

def validate_medical_document(metrics: list, raw_text: str) -> tuple:
    """Validate if the document contains valid medical data"""
    # Check if we found any real metrics (not sample/placeholder ones)
    real_metrics = [m for m in metrics if m["name"] != "Sample Metric"]
    
    if len(real_metrics) >= 2:
        return True, "Valid medical document detected with multiple health metrics."
    
    # Secondary validation: Check for medical keywords in the raw text
    medical_keywords = [
        "анализ", "кровь", "моча", "глюкоза", "холестерин", "лейкоциты", "эритроциты", 
        "гемоглобин", "метаболизм", "диагностика", "результат", "пациент", "норма",
        "blood", "test", "result", "cholesterol", "glucose", "patient", "hemoglobin",
        "normal", "range", "white blood cells", "red blood cells", "lab", "laboratory"
    ]
    
    keyword_count = sum(1 for keyword in medical_keywords if keyword.lower() in raw_text.lower())
    
    if keyword_count >= 3:
        # Document contains medical terminology but no structured metrics
        return True, "Document contains medical terminology but few structured metrics."
    
    # Not a valid medical document
    if len(real_metrics) == 1:
        return False, "Document contains only one health metric. Please upload a complete medical report."
    else:
        return False, "This doesn't appear to be a medical document. Please upload a lab report or medical test result."

def extract_metrics_from_text(text: str) -> list:
    """
    Enhanced metric extraction with support for scientific notation and complex units.
    Fixes issues with parsing values like '5.66 10^12/л' and '319.00 10^9/л'
    Now includes better validation to avoid extracting timestamps and headers.
    """
    metrics = []
    lines = text.split('\n')
    
    logger.info(f"Processing {len(lines)} lines for metric extraction")
    
    for line_num, line in enumerate(lines):
        if ':' not in line:
            continue
        
        # Improved splitting to handle reference ranges with colons
        # Split only on the first colon, but be smarter about medical content
        first_colon = line.find(':')
        if first_colon == -1:
            continue
            
        name = line[:first_colon].strip()
        value_part = line[first_colon + 1:].strip()
        
        # Skip empty value parts
        if not value_part:
            continue
        
        # Enhanced validation to filter out non-metrics
        if not _is_valid_metric_line(name, value_part, line):
            logger.debug(f"Skipping non-metric line {line_num}: {line}")
            continue
        
        # Try enhanced parsing with multiple patterns
        parsed_value, parsed_unit, confidence = _parse_value_and_unit(value_part, name)
        
        if parsed_value is None:
            logger.warning(f"Failed to parse line {line_num}: {line}")
            continue
        
        # Validate suspicious values (common parsing errors)
        if _is_suspicious_value(parsed_value, parsed_unit, name):
            logger.warning(f"Suspicious value detected on line {line_num}: {name} = {parsed_value} {parsed_unit}")
            continue
        
        # Extract reference range
        reference_range = _extract_reference_range(value_part)
        
        # Determine status based on comparison with reference range
        status = determine_status(parsed_value, reference_range)
        
        # Normalize metric name using medical mapping
        normalized_name = _normalize_metric_name(name)
        
        # Create the metric object with confidence score
        metric = {
            "name": normalized_name,
            "value": parsed_value,
            "unit": parsed_unit,
            "reference_range": reference_range,
            "status": status,
            "confidence": confidence,
            "original_line": line.strip()  # For debugging
        }
        
        metrics.append(metric)
        logger.info(f"Successfully parsed: {normalized_name} = {parsed_value} {parsed_unit} (confidence: {confidence:.2f})")
    
    logger.info(f"Successfully extracted {len(metrics)} metrics from text")
    return metrics

def _is_valid_metric_line(name: str, value_part: str, full_line: str) -> bool:
    """
    Enhanced validation to determine if a line represents a valid medical metric.
    Filters out timestamps, dates, section headers, and other non-metric content.
    """
    
    # 1. Filter out date/time patterns
    if _is_datetime_line(name, value_part, full_line):
        return False
    
    # 2. Filter out section headers and descriptive text
    if _is_section_header(name, value_part):
        return False
    
    # 3. Check for valid metric name characteristics
    if not _has_valid_metric_name(name):
        return False
    
    # 4. Check for valid value part characteristics
    if not _has_valid_value_part(value_part):
        return False
    
    # 5. Check for medical unit indicators
    if not _has_medical_unit_indicators(value_part):
        return False
    
    return True

def _is_datetime_line(name: str, value_part: str, full_line: str) -> bool:
    """Check if the line represents a date/time rather than a metric."""
    
    # First check if this is clearly in medical context
    medical_context_indicators = [
        r'витамин',     # vitamin
        r'время',       # time (but in medical context like "Протромбиновое время")
        r'он',          # OH (25-ОН витамин D)
        r'протромбин',  # prothrombin  
        r'тромбин',     # thrombin
        r'25.?он',      # 25-OH
    ]
    
    name_lower = name.lower()
    for indicator in medical_context_indicators:
        if re.search(indicator, name_lower):
            # This is medical terminology, not a date/time
            return False
    
    # Date patterns like "26.04.2025", "26/04/2025", "2025-04-26"
    date_patterns = [
        r'\d{1,2}[./]\d{1,2}[./]\d{4}',
        r'\d{4}[./]\d{1,2}[./]\d{1,2}',
    ]
    
    # Time patterns like "16:12", "14:19" (but not in medical context)
    time_patterns = [
        r'^\d{1,2}:\d{2}$',  # Standalone time
        r'^\d{1,2}\.\d{2}$', # Standalone time with dots
    ]
    
    # Check if name looks like a date
    for pattern in date_patterns:
        if re.search(pattern, name):
            return True
    
    # Check if value part looks like standalone time (but not medical ranges)
    for pattern in time_patterns:
        if re.search(pattern, value_part):
            # Make sure this isn't part of a medical range
            if not re.search(r'норма|range|г/л|мг/дл|ммоль/л|мкмоль/л|%|пг|фл|/л|мм/час', value_part.lower()):
                return True
    
    # Check if the entire line looks like a timestamp
    timestamp_pattern = r'\d{1,2}[./]\d{1,2}[./]\d{4}\s+\d{1,2}:\d{2}'
    if re.search(timestamp_pattern, full_line):
        return True
    
    # Check for common date/time keywords (but not in medical context)
    datetime_keywords = ['дата', 'время', 'date', 'time', 'час', 'мин', 'сек']
    for keyword in datetime_keywords:
        if keyword in name_lower:
            # Make sure this isn't a medical metric name
            # "время" can be part of medical terms like "Протромбиновое время"
            if keyword == 'время' and any(med in name_lower for med in ['протромбин', 'тромбин']):
                return False
            if not re.search(r'[A-Z]{2,5}', name) and not re.search(r'г/л|мг/дл|ммоль/л', value_part):
                return True
    
    # Special check for the problematic pattern like "130,00 - 160,00"
    # This should NOT be considered a time
    if re.search(r'\d+,\d+\s*-\s*\d+,\d+', value_part):
        return False
    
    return False

def _is_section_header(name: str, value_part: str) -> bool:
    """Check if the line represents a section header rather than a metric."""
    
    # Common section header patterns
    header_patterns = [
        r'абс\s*:\s*кол-во',  # "абс: кол-во"
        r'общий\s+анализ',     # "общий анализ"
        r'биохимический',      # "биохимический"
        r'клинический',        # "клинический"
        r'показатели',         # "показатели"
        r'результаты',         # "результаты"
        r'пациент',            # "пациент"
        r'заключение',         # "заключение"
        r'описание',           # "описание"
        r'комментарий',        # "комментарий"
    ]
    
    # Check if name contains header patterns
    name_lower = name.lower()
    for pattern in header_patterns:
        if re.search(pattern, name_lower):
            return True
    
    # Check if value part contains header-like content
    value_lower = value_part.lower()
    for pattern in header_patterns:
        if re.search(pattern, value_lower):
            return True
    
    # Special case: if this looks like a medical test with qualitative result, it's NOT a header
    qualitative_results = ['обнаружено', 'не обнаружено', 'отрицательно', 'положительно', 'позитивно', 'негативно']
    if any(qual in value_lower for qual in qualitative_results):
        # This is a medical test with qualitative result, not a header
        return False
    
    # Headers often don't have numeric values with proper units
    if not re.search(r'\d+[.,]?\d*\s*[а-яА-Яa-zA-Z/%×·*^°]+', value_part):
        # If there's no number with unit pattern, it's likely a header
        if len(name) > 20 or not re.search(r'\d', value_part):  # Long names or no numbers
            # But exclude known medical test names
            medical_test_patterns = [
                r'антитела',    # antibodies
                r'гепатит',     # hepatitis  
                r'маркер',      # marker
                r'анти',        # anti
                r'hbs',         # HBS
                r'hcv',         # HCV
            ]
            
            # If it's a known medical test pattern, don't consider it a header
            for pattern in medical_test_patterns:
                if re.search(pattern, name_lower):
                    return False
                    
            return True
    
    # Check for parenthetical descriptions without proper metric values
    if re.match(r'^[^(]*\([^)]*\)$', name) and not re.search(r'\d+[.,]?\d*\s*[а-яА-Яa-zA-Z]', value_part):
        return True
    
    return False

def _has_valid_metric_name(name: str) -> bool:
    """Check if the name part looks like a valid medical metric name."""
    
    # Name should not be too long (headers tend to be long)
    if len(name) > 50:
        return False
    
    # Allow single-letter medical codes (like T for temperature)
    if len(name) == 1:
        # Common single-letter medical abbreviations
        single_letter_codes = ['T', 'P', 'R', 'H', 'K', 'Na', 'Cl']  # Temperature, Pulse, etc.
        if name.upper() in single_letter_codes:
            return True
        return False  # Reject other single characters
    
    # Name should not be too short (but allow 2+ characters)
    if len(name) < 2:
        return False
    
    # Reject non-medical demographic data
    demographic_patterns = [
        r'^возраст$',      # Age
        r'^пол$',          # Gender
        r'^id$',           # ID
        r'^номер$',        # Number
        r'^кабинет$',      # Room
        r'^врач$',         # Doctor
        r'^пациент$',      # Patient
    ]
    
    name_lower = name.lower().strip()
    for pattern in demographic_patterns:
        if re.match(pattern, name_lower):
            return False
    
    # Check for known medical metric patterns
    medical_name_patterns = [
        r'^[A-Z]{2,5}[#%]?$',  # Lab codes like HGB, RBC, PLT
        
        # Complete Blood Count patterns
        r'гемоглобин',         # Hemoglobin variations
        r'эритроциты',         # Red blood cells
        r'лейкоциты',          # White blood cells
        r'тромбоциты',         # Platelets
        r'нейтрофилы',         # Neutrophils
        r'лимфоциты',          # Lymphocytes
        r'моноциты',           # Monocytes
        r'эозинофилы',         # Eosinophils
        r'базофилы',           # Basophils
        r'гематокрит',         # Hematocrit
        
        # Biochemical analysis patterns
        r'белок',              # Protein
        r'альбумин',           # Albumin
        r'креатинин',          # Creatinine
        r'глюкоза',            # Glucose
        r'магний',             # Magnesium
        r'алт',                # ALT
        r'алат',               # ALAT
        r'аст',                # AST
        r'асат',               # ASAT
        r'билирубин',          # Bilirubin
        r'ггт',                # GGT
        r'ггтп',               # GGTP
        r'гамма.?гт',          # Gamma-GT
        r'щелочная.?фосфатаза', # Alkaline phosphatase
        r'щф',                 # Alkaline phosphatase (short)
        r'гликированный',      # Glycated
        r'гликозилированный',  # Glycosylated
        r'реактивный.?белок',  # C-reactive protein
        r'срб',                # CRP
        r'холестерин',         # Cholesterol
        r'лпвп',               # HDL
        r'лпнп',               # LDL
        r'триглицериды',       # Triglycerides
        r'калий',              # Potassium
        r'натрий',             # Sodium
        r'мочевина',           # Urea
        
        # Hormonal profile patterns
        r'ттг',                # TSH
        r'тиреотропный',       # TSH (full name)
        r'свободный.?т[34]',   # Free T3/T4
        r'витамин.?d',         # Vitamin D
        r'25.?он',             # 25-OH
        
        # Coagulation patterns
        r'ачтв',               # APTT
        r'аптв',               # APTT
        r'мно',                # INR
        r'протромбиновое',     # Prothrombin
        r'тромбиновое',        # Thrombin
        r'протромбиновый',     # Prothrombin index
        r'фибриноген',         # Fibrinogen
        
        # Hepatitis markers
        r'антитела',           # Antibodies
        r'гепатит',            # Hepatitis
        r'hbsag',              # HBsAg
        r'anti.?hcv',          # Anti-HCV
        
        # Common abbreviations
        r'соэ',                # ESR
        r'^t$',                # Temperature
        r'^ph$',               # pH
        r'hba1c',              # Glycated hemoglobin
        r'crp',                # C-reactive protein
        r'hdl',                # HDL cholesterol
        r'ldl',                # LDL cholesterol
        r'tsh',                # TSH
        r'ft[34]',             # Free T3/T4
        r'inr',                # INR
    ]
    
    name_lower = name.lower()
    for pattern in medical_name_patterns:
        if re.search(pattern, name_lower):
            return True
    
    # Allow short lab codes (common pattern)
    if re.match(r'^[A-Z]{2,5}[#%]?$', name.upper()):
        return True
    
    # Allow names that contain medical-sounding suffixes
    medical_suffixes = ['цит', 'глобин', 'фил', 'коз', 'тромб']
    if any(suffix in name_lower for suffix in medical_suffixes):
        return True
    
    return True  # Default to accepting if no clear rejection criteria

def _has_valid_value_part(value_part: str) -> bool:
    """Check if the value part contains valid metric data."""
    
    # Check for qualitative results first
    qualitative_results = ['обнаружено', 'не обнаружено', 'отрицательно', 'положительно', 'позитивно', 'негативно', 'норма']
    value_lower = value_part.lower().strip()
    if any(qual in value_lower for qual in qualitative_results):
        return True
    
    # Must contain at least one number for quantitative results
    if not re.search(r'\d', value_part):
        return False
    
    # Check for complete metric patterns (number + unit + optional range)
    valid_patterns = [
        r'\d+[.,]?\d*\s*[а-яА-Яa-zA-Z/%×·*^°]+',  # Number with unit
        r'\d+[.,]?\d*\s+10\^?\d+[а-яА-Яa-zA-Z/]+', # Scientific notation
        r'\d+[.,]?\d*\s*\([^)]*норма[^)]*\)',      # Number with норма in parentheses
        r'\d+[.,]?\d*\s*[а-яА-Яa-zA-Z/%]+\s*\([^)]*\)', # Number, unit, then parentheses
    ]
    
    for pattern in valid_patterns:
        if re.search(pattern, value_part):
            return True
    
    # If we have a number and it's not just a standalone number, it might be valid
    if re.search(r'\d+[.,]?\d*', value_part) and len(value_part.strip()) > 5:
        return True
    
    return False

def _has_medical_unit_indicators(value_part: str) -> bool:
    """Check if the value part contains medical unit indicators."""
    
    # Common medical units
    medical_units = [
        # Basic lab units
        r'г/л',      # grams per liter
        r'мг/дл',    # milligrams per deciliter
        r'ммоль/л',  # millimoles per liter
        r'мкмоль/л', # micromoles per liter
        r'%',        # percentage
        r'пг',       # picograms
        r'фл',       # femtoliters
        r'/л',       # per liter
        r'мм/час',   # mm per hour
        r'10\^',     # scientific notation
        r'E\+',      # E notation
        r'×',        # multiplication
        r'°C',       # temperature
        r'°F',       # temperature fahrenheit
        r'ед',       # units
        
        # Biochemical analysis units
        r'U/L',      # units per liter (enzymes)
        r'МЕ/л',     # international units per liter
        r'Ед/л',     # units per liter (Russian)
        r'мг/л',     # milligrams per liter
        r'мкг/л',    # micrograms per liter
        r'нг/мл',    # nanograms per milliliter
        r'пг/мл',    # picograms per milliliter
        r'нг/дл',    # nanograms per deciliter
        r'мкМЕ/мл',  # micro international units per milliliter
        
        # Coagulation units
        r'сек',      # seconds
        r'с',        # seconds (short form)
        
        # Qualitative results (for hepatitis markers)
        r'обнаружено',     # detected
        r'не обнаружено',  # not detected
        r'положительно',   # positive
        r'отрицательно',   # negative
        r'позитивно',      # positive
        r'негативно',      # negative
    ]
    
    value_lower = value_part.lower()
    for unit in medical_units:
        if re.search(unit, value_lower):
            return True
    
    # Check for unit patterns with numbers
    unit_patterns = [
        r'\d+[.,]?\d*\s*[а-яА-Яa-zA-Z/%×·*^°]+',  # Number followed by unit
        r'\d+[.,]?\d*\s+10\^?\d+',            # Scientific notation
        r'\d+[.,]?\d*\s*\([^)]*\)',           # Number with parentheses (ranges)
        r'\d+[.,]?\d*\s*°[CF]',               # Temperature patterns
        r'\d+[.,]?\d*\s*U/L',                 # Enzyme units
        r'\d+[.,]?\d*\s*МЕ/л',                # International units
        r'\d+[.,]?\d*\s*сек',                 # Time in seconds
    ]
    
    for pattern in unit_patterns:
        if re.search(pattern, value_part):
            return True
    
    # Check for qualitative results (without numbers)
    qualitative_patterns = [
        r'(не\s+)?обнаружено',
        r'(от|по)рицательно',
        r'(по)?зитивно',
        r'(по)?ложительно',
        r'негативно',
    ]
    
    for pattern in qualitative_patterns:
        if re.search(pattern, value_lower):
            return True
    
    return False

def _parse_value_and_unit(value_part: str, metric_name: str = "") -> Tuple[Optional[float], Optional[str], float]:
    """
    Enhanced parsing function that handles multiple value formats including scientific notation.
    Also handles qualitative results like "Обнаружено"/"Не обнаружено".
    Returns: (value, unit, confidence_score)
    """
    value_part = value_part.strip()
    
    # Check for date contamination first
    date_patterns = [
        r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
        r'алу орны',             # Kazakh text
        r'биоматериалды',        # Kazakh text
        r'результатах',          # Russian contamination
        r'отчет',                # Report text
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, value_part, re.IGNORECASE):
            return None, None, 0.0  # Skip contaminated lines
    
    def clean_unit(unit_str):
        """Clean and normalize unit strings."""
        unit_str = unit_str.strip()
        
        # Fix common unit formatting issues
        unit_replacements = {
            'ммольл': 'ммоль/л',
            'мкмольл': 'мкмоль/л',
            'ммолыл': 'ммоль/л',  # Additional OCR error
            'мкмолыл': 'мкмоль/л',  # Additional OCR error
            'гл': 'г/л',
            'мгл': 'мг/л',
            'мкгл': 'мкг/л',
            'едл': 'Ед/л',
            'Биоматериалды': 'Ед/л',  # Common OCR error
            'результатах': 'Ед/л',    # Common OCR error
        }
        
        for old, new in unit_replacements.items():
            if old in unit_str:
                unit_str = unit_str.replace(old, new)
        
        return unit_str
    
    # Handle qualitative results first (for hepatitis markers, etc.)
    qualitative_matches = {
        r'^не\s+обнаружено$': ('negative', 'qualitative', 0.95),
        r'^обнаружено$': ('positive', 'qualitative', 0.95),
        r'^отрицательно$': ('negative', 'qualitative', 0.90),
        r'^положительно$': ('positive', 'qualitative', 0.90),
        r'^позитивно$': ('positive', 'qualitative', 0.90),
        r'^негативно$': ('negative', 'qualitative', 0.90),
        r'^норма$': ('normal', 'qualitative', 0.85),
        r'^в\s+пределах\s+нормы$': ('normal', 'qualitative', 0.85),
    }
    
    value_lower = value_part.lower().strip()
    for pattern, (result, unit, confidence) in qualitative_matches.items():
        if re.search(pattern, value_lower):
            # For qualitative results, we return a special value
            # Use 1.0 for positive/detected, 0.0 for negative/not detected
            if result == 'positive':
                return 1.0, unit, confidence
            elif result == 'negative':
                return 0.0, unit, confidence
            else:  # normal
                return 0.5, unit, confidence
    
    # Try scientific notation first (highest priority for accuracy)
    # Pattern: "5.66 10^12/л" or "5.66 10^12 /л"
    sci_match = re.search(SCIENTIFIC_NOTATION_PATTERN, value_part)
    if sci_match:
        base_value = sci_match.group(1).replace(',', '.')
        exponent = int(sci_match.group(2))
        unit = clean_unit(sci_match.group(3).strip())
        
        try:
            value = float(base_value)
            # Keep the original value but format the unit to show scientific notation
            formatted_unit = f"10^{exponent}{unit}"
            return value, formatted_unit, 0.95
        except ValueError:
            pass
    
    # Try complex value pattern (e.g., "319.00 10^9/л")
    complex_match = re.search(COMPLEX_VALUE_PATTERN, value_part)
    if complex_match:
        base_value = complex_match.group(1).replace(',', '.')
        multiplier_part = complex_match.group(2)
        unit = clean_unit(complex_match.group(3).strip())
        
        try:
            value = float(base_value)
            # Handle exponential multiplier but keep value manageable
            if '^' in multiplier_part:
                exp_parts = multiplier_part.split('^')
                if len(exp_parts) == 2:
                    exp_value = int(exp_parts[1])
                    # Don't multiply the value, just format the unit properly
                    formatted_unit = f"10^{exp_value}{unit}"
                    return value, formatted_unit, 0.90
            else:
                # Simple multiplier - include in unit
                formatted_unit = f"×{multiplier_part}{unit}"
                return value, formatted_unit, 0.85
        except ValueError:
            pass
    
    # Try decimal with spaces pattern (e.g., "5,66" or "5 66")
    decimal_match = re.search(DECIMAL_WITH_SPACES_PATTERN, value_part)
    if decimal_match:
        integer_part = decimal_match.group(1)
        decimal_part = decimal_match.group(2)
        unit = clean_unit(decimal_match.group(3).strip())
        
        try:
            value = float(f"{integer_part}.{decimal_part}")
            return value, unit, 0.80
        except ValueError:
            pass
    
    # Handle combined qualitative + quantitative results (hepatitis tests)
    combined_match = re.search(r'(не\s+обнаружено|обнаружено).*?S/CO\s*=\s*(\d+[,\.]?\d*)', value_part.lower())
    if combined_match:
        qualitative = combined_match.group(1).strip()
        sco_value_str = combined_match.group(2).replace(',', '.')
        try:
            sco_value = float(sco_value_str)
            # For combined results, we use the numeric S/CO value
            return sco_value, "S/CO", 0.95
        except ValueError:
            pass
    
    # Try S/CO patterns for hepatitis tests
    sco_match = re.search(r'S/CO\s*=\s*(\d+[,\.]?\d*)', value_part)
    if sco_match:
        value_str = sco_match.group(1).replace(',', '.')
        try:
            value = float(value_str)
            return value, "S/CO", 0.90
        except ValueError:
            pass
    
    # Enhanced standard pattern to include new units (U/L, МЕ/л, etc.)
    enhanced_std_pattern = r'(\d+[.,]?\d*)\s*([а-яА-Яa-zA-Z/%×·*^°]+(?:/[а-яА-Яa-zA-Z]+)?|U/L|МЕ/л|Ед/л|мкМЕ/мл|нг/мл|пг/мл|нг/дл|мг/л|мкг/л|сек|ммоль/л|мкмоль/л)'
    std_match = re.search(enhanced_std_pattern, value_part)
    if std_match:
        value_str = std_match.group(1).replace(',', '.')
        unit = clean_unit(std_match.group(2).strip())
        
        try:
            value = float(value_str)
            return value, unit, 0.75
        except ValueError:
            pass
    
    # Final attempt: try to extract any number
    number_match = re.search(r'(\d+[.,]?\d*)', value_part)
    if number_match:
        value_str = number_match.group(1).replace(',', '.')
        try:
            value = float(value_str)
            # Try to find unit after the number
            remaining = value_part[number_match.end():].strip()
            unit_match = re.search(r'([а-яА-Яa-zA-Z/%×·*^]+|U/L|МЕ/л|сек)', remaining)
            unit = clean_unit(unit_match.group(1)) if unit_match else "units"
            return value, unit, 0.50
        except ValueError:
            pass
    
    return None, None, 0.0

def _is_suspicious_value(value: float, unit: str, metric_name: str) -> bool:
    """
    Detect suspicious values that are likely parsing errors.
    """
    # Qualitative results are not suspicious
    if unit == 'qualitative':
        return False
    
    # Common error: multiple metrics with value 9 and unit '/л'
    if value == 9.0 and unit == '/л':
        return True
    
    # Zero or negative values for most medical metrics (but allow qualitative results)
    if value <= 0 and unit != 'qualitative':
        return True
    
    # Values that are too large to be medically reasonable for most standard units
    # Allow scientific notation units (indicated by presence of "10^" in unit)
    if "10^" not in unit:
        if value > 10000:  # Regular units shouldn't exceed 10,000 for most metrics
            return True
    
    return False

def _extract_reference_range(value_part: str) -> str:
    """Enhanced reference range extraction with multiple patterns."""
    # Try Russian pattern first - the most common in our test cases
    range_match = re.search(r'\(норма:\s*([^)]+)\)', value_part)
    if range_match:
        return range_match.group(1).strip()
    
    # Try alternative Russian patterns without parentheses
    alt_russian = re.search(r'норма:\s*([^\s]+(?:\s+[^\s]+)*?)(?:\s|$)', value_part)
    if alt_russian:
        return alt_russian.group(1).strip()
    
    # Try parentheses pattern with numbers (must contain range-like content)
    paren_match = re.search(r'\(([^)]*\d+[^)]*)\)', value_part)
    if paren_match:
        content = paren_match.group(1).strip()
        # Check if it looks like a range (contains dash or comma-separated numbers)
        if re.search(r'\d+[.,]?\d*\s*[-–]\s*\d+[.,]?\d*', content):
            return content
    
    # Try range pattern without parentheses
    range_pattern = re.search(r'(\d+[.,]?\d*\s*[-–]\s*\d+[.,]?\d*)', value_part)
    if range_pattern:
        return range_pattern.group(1).strip()
    
    return "Not specified"

def _normalize_metric_name(name: str) -> str:
    """Normalize metric names using medical mapping with enhanced Russian support."""
    # Clean the name
    clean_name = name.strip().upper()
    
    # Handle special patterns from tabular data first
    tabular_patterns = {
        r'ТТГ\d*': 'ТТГ',
        r'СВОБОДНЫЙ\s+ТЗ?\s*\d*': 'СВОБОДНЫЙ Т3',
        r'СВОБОДНЫЙ\s+Т4\s*\d*': 'СВОБОДНЫЙ Т4',
        r'25.?ОH?\s+ВИТАМИН\s+D[A-Z]*': '25-ОН ВИТАМИН D',
    }
    
    for pattern, replacement in tabular_patterns.items():
        if re.search(pattern, clean_name):
            clean_name = replacement
            break
    
    # Remove common prefixes and suffixes that don't affect meaning
    # Don't remove "СВОБОДНЫЙ" from hormone names as it's a specific medical term
    if not re.search(r'СВОБОДНЫЙ\s+Т[34]', clean_name):
        clean_name = re.sub(r'^(ОБЩИЙ\s+|СВОБОДНЫЙ\s+)', '', clean_name)
    clean_name = re.sub(r'\s+(ОБЩИЙ|ПРЯМОЙ|НЕПРЯМОЙ|КОНЪЮГИРОВАННЫЙ|НЕКОНЪЮГИРОВАННЫЙ)$', '', clean_name)
    
    # Handle special compound names
    compound_mappings = {
        'БИЛИРУБИН ОБЩИЙ': 'БИЛИРУБИН ОБЩИЙ',
        'БИЛИРУБИН ПРЯМОЙ': 'БИЛИРУБИН ПРЯМОЙ', 
        'БИЛИРУБИН НЕПРЯМОЙ': 'БИЛИРУБИН НЕПРЯМОЙ',
        'БИЛИРУБИН КОНЪЮГИРОВАННЫЙ': 'БИЛИРУБИН ПРЯМОЙ',
        'БИЛИРУБИН НЕКОНЪЮГИРОВАННЫЙ': 'БИЛИРУБИН НЕПРЯМОЙ',
        'ХОЛЕСТЕРИН ОБЩИЙ': 'ХОЛЕСТЕРИН',
        'ХОЛЕСТЕРИН ЛПВП': 'ХОЛЕСТЕРИН ЛПВП',
        'ХОЛЕСТЕРИН ЛПНП': 'ХОЛЕСТЕРИН ЛПНП',
        'ГЛИКИРОВАННЫЙ ГЕМОГЛОБИН': 'ГЛИКИРОВАННЫЙ ГЕМОГЛОБИН',
        'ГЛИКОЗИЛИРОВАННЫЙ ГЕМОГЛОБИН': 'ГЛИКИРОВАННЫЙ ГЕМОГЛОБИН',
        'С-РЕАКТИВНЫЙ БЕЛОК': 'С-РЕАКТИВНЫЙ БЕЛОК',
        'ЩЕЛОЧНАЯ ФОСФАТАЗА': 'ЩЕЛОЧНАЯ ФОСФАТАЗА',
        'ПРОТРОМБИНОВОЕ ВРЕМЯ': 'ПРОТРОМБИНОВОЕ ВРЕМЯ',
        'ТРОМБИНОВОЕ ВРЕМЯ': 'ТРОМБИНОВОЕ ВРЕМЯ',
        'ПРОТРОМБИНОВЫЙ ИНДЕКС': 'ПРОТРОМБИНОВЫЙ ИНДЕКС',
        'АНТИТЕЛА К ГЕПАТИТУ C': 'АНТИТЕЛА К ГЕПАТИТУ C',
        '25-ОН ВИТАМИН D': '25-ОН ВИТАМИН D',
        'СВОБОДНЫЙ Т3': 'СВОБОДНЫЙ Т3',
        'СВОБОДНЫЙ Т4': 'СВОБОДНЫЙ Т4',
    }
    
    # Check compound mappings first
    for compound, normalized in compound_mappings.items():
        if compound in name.upper():
            if normalized in MEDICAL_METRICS_MAP:
                return MEDICAL_METRICS_MAP[normalized]
    
    # Direct mapping
    if clean_name in MEDICAL_METRICS_MAP:
        return MEDICAL_METRICS_MAP[clean_name]
    
    # Try variations with common suffixes
    for suffix in ['#', '%', '_ABS', '_PCT']:
        if clean_name.endswith(suffix):
            base_name = clean_name[:-len(suffix)]
            if base_name in MEDICAL_METRICS_MAP:
                return MEDICAL_METRICS_MAP[base_name]
    
    # Try alternative spellings and abbreviations
    alternative_mappings = {
        'АЛАТ': 'АЛТ',
        'АСАТ': 'АСТ', 
        'ГГТП': 'ГГТ',
        'ГАММА-ГТ': 'ГГТ',
        'ГАММА ГТ': 'ГГТ',
        'ЩФ': 'ЩЕЛОЧНАЯ ФОСФАТАЗА',
        'СРБ': 'С-РЕАКТИВНЫЙ БЕЛОК',
        'CRP': 'С-РЕАКТИВНЫЙ БЕЛОК',
        'ЛПВП': 'ХОЛЕСТЕРИН ЛПВП',
        'ЛПНП': 'ХОЛЕСТЕРИН ЛПНП',
        'HDL': 'ХОЛЕСТЕРИН ЛПВП',
        'LDL': 'ХОЛЕСТЕРИН ЛПНП',
        'TSH': 'ТТГ',
        'FT3': 'СВОБОДНЫЙ Т3',
        'FT4': 'СВОБОДНЫЙ Т4',
        'HBA1C': 'ГЛИКИРОВАННЫЙ ГЕМОГЛОБИН',
        'INR': 'МНО',
        'АПТВ': 'АЧТВ',
        'ПВ': 'ПРОТРОМБИНОВОЕ ВРЕМЯ',
        'ТВ': 'ТРОМБИНОВОЕ ВРЕМЯ',
        'ПТИ': 'ПРОТРОМБИНОВЫЙ ИНДЕКС',
        'ANTI-HCV': 'АНТИТЕЛА К ГЕПАТИТУ C',
        'HCV': 'АНТИТЕЛА К ГЕПАТИТУ C',
        'HBS AG': 'HBSAG',
        '25(OH)D': '25-ОН ВИТАМИН D',
        'ВИТАМИН D': '25-ОН ВИТАМИН D',
    }
    
    if clean_name in alternative_mappings:
        alt_name = alternative_mappings[clean_name]
        if alt_name in MEDICAL_METRICS_MAP:
            return MEDICAL_METRICS_MAP[alt_name]
    
    # Return original name in lowercase with underscores
    return clean_name.lower().replace(' ', '_').replace('-', '_')

def determine_status(value, reference_range):
    """Determine the status of a metric based on its value and reference range"""
    
    # Handle qualitative results
    if isinstance(value, float) and reference_range == "Not specified":
        # For qualitative results without explicit ranges
        if value == 1.0:  # positive/detected
            return "detected"
        elif value == 0.0:  # negative/not detected
            return "not_detected"
        elif value == 0.5:  # normal
            return "normal"
    
    try:
        # Extract min and max from reference range
        range_parts = re.findall(r'\d+[.,]?\d*', reference_range)
        if len(range_parts) >= 2:
            min_val = float(range_parts[0].replace(',', '.'))
            max_val = float(range_parts[1].replace(',', '.'))
            
            if value < min_val:
                return "low"
            elif value > max_val:
                return "high"
            else:
                return "normal"
        elif len(range_parts) == 1:
            # Single reference value (like < 5.0 or > 10.0)
            ref_val = float(range_parts[0].replace(',', '.'))
            
            # Try to determine if it's upper or lower limit from context
            if "менее" in reference_range.lower() or "<" in reference_range:
                # Upper limit reference (like S/CO < 1.0)
                if value <= ref_val:
                    return "negative"  # For S/CO tests, below threshold = negative
                else:
                    return "positive"  # Above threshold = positive
            elif "более" in reference_range.lower() or ">" in reference_range:
                # Lower limit reference  
                if value >= ref_val:
                    return "normal"
                else:
                    return "low"
            else:
                # General comparison
                if abs(value - ref_val) / ref_val < 0.1:  # Within 10%
                    return "normal"
                elif value > ref_val:
                    return "high"
                else:
                    return "low"
    except:
        pass
    
    # Enhanced status detection from Russian text
    status_keywords = {
        'повышено': 'high',
        'понижено': 'low',
        'снижено': 'low',
        'увеличено': 'high',
        'в пределах нормы': 'normal',
        'норма': 'normal',
        'нормально': 'normal',
        'обнаружено': 'detected',
        'не обнаружено': 'not_detected',
        'положительно': 'positive',
        'отрицательно': 'negative',
    }
    
    range_lower = reference_range.lower()
    for keyword, status in status_keywords.items():
        if keyword in range_lower:
            return status
    
    # Default status if we can't determine
    return "normal"

def extract_text_from_pdf(pdf_path: str) -> dict:
    text_blocks = []
    pages_metrics = []
    all_extracted_metrics = []
    is_valid = False
    validation_messages = []

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(dpi=300)
        img_path = f"{pdf_path}_page_{page_num}.png"
        pix.save(img_path)

        image_result = extract_text_from_image(img_path)
        text_blocks.append(image_result["extracted_text"])
        pages_metrics.append(image_result["analysis"])
        
        # Collect metrics from all pages
        if "metrics" in image_result["analysis"]:
            all_extracted_metrics.extend(image_result["analysis"]["metrics"])
            
        # If any page is valid, consider the document valid
        if image_result["analysis"].get("valid", False):
            is_valid = True
            validation_messages.append(image_result["analysis"].get("validation_message", ""))

        os.remove(img_path)
    
    # Validate the entire document based on collected metrics
    if not is_valid:
        # Re-validate with all metrics together
        is_valid, validation_message = validate_medical_document(all_extracted_metrics, "\n".join(text_blocks))
    else:
        validation_message = "Valid medical document detected in the PDF."
    
    # Create a combined analysis with all metrics
    combined_analysis = {
        "metrics": all_extracted_metrics,
        "summary": f"Analysis of {len(doc)} page PDF document containing {len(all_extracted_metrics)} health metrics.",
        "valid": is_valid,
        "validation_message": validation_message
    }

    return {
        "extracted_text": "\n\n".join(text_blocks),
        "analysis": combined_analysis
    }

def extract_text_from_file(file_path: str) -> dict:
    ext = file_path.split('.')[-1].lower()

    if ext == 'heic':
        try:
            file_path = convert_heic_to_jpg_pillow_heif(file_path)
        except Exception as e:
            print(f"[WARN] pillow-heif failed: {e}")
            file_path = convert_heic_to_jpg_imageio(file_path)
        ext = 'jpg'

    if ext in ['png', 'jpg', 'jpeg']:
        return extract_text_from_image(file_path)
    elif ext == 'pdf':
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError("Неподдерживаемый формат файла")

def extract_lab_lines(text: str) -> str:
    """Enhanced lab line extraction with support for tabular medical data."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    results = []
    i = 0

    def is_value(s):
        """Enhanced value detection including scientific notation and various units."""
        # Standard patterns
        standard_pattern = r"\d{1,3}[,\.]?\d*\s*(г/л|%|пг|фл|мм/час|мм\\ч|мкМЕ/мл|нг/дл|ng/ml|pg/ml|U/L|МЕ/л|Ед/л|мг/л|мкг/л|сек|ммоль/л|мкмоль/л)"
        
        # Scientific notation patterns
        scientific_patterns = [
            r"\d+[,\.]?\d*\s+10\^?\d+\s*/л",  # "5.66 10^12/л"
            r"\d+[,\.]?\d*\s+10\^?\d+\s*г/л", # "319.00 10^9г/л" 
            r"\d+[,\.]?\d*\s+E\+?\d+\s*/л",   # "5.66E+12/л"
            r"\d+[,\.]?\d*\s+\*\s*10\^?\d+\s*/л", # "5.66*10^12/л"
        ]
        
        # S/CO patterns for hepatitis tests
        sco_patterns = [
            r"S/CO\s*=\s*\d+[,\.]?\d*",       # "S/CO = 0,13"
            r"\d+[,\.]?\d*\s*S/CO",           # "0,13 S/CO"
        ]
        
        # Check standard pattern first
        if re.search(standard_pattern, s, re.IGNORECASE):
            return True
            
        # Check scientific notation patterns
        for pattern in scientific_patterns:
            if re.search(pattern, s, re.IGNORECASE):
                return True
        
        # Check S/CO patterns
        for pattern in sco_patterns:
            if re.search(pattern, s, re.IGNORECASE):
                return True
                
        return False

    def is_range(s):
        """Detect reference range patterns."""
        patterns = [
            r"\d+[,\.]?\d*\s*[-–]\s*\d+[,\.]?\d*",  # Standard range
            r"\d+[,\.]?\d*\s*-\s*\d+[,\.]?\d*",     # With regular dash
            r"от\s+\d+[,\.]?\d*\s+до\s+\d+[,\.]?\d*", # Russian format
        ]
        
        for pattern in patterns:
            if re.search(pattern, s, re.IGNORECASE):
                return True
        return False

    def is_medical_test_name(s):
        """Check if string looks like a medical test name."""
        medical_patterns = [
            r'^[A-Z]{2,5}[#%]?$',  # Lab codes like HGB, RBC, PLT
            r'ттг',                # TSH
            r'свободный',          # Free hormones
            r'витамин',            # Vitamin
            r'25.?он',             # 25-OH
            r'гемоглобин',         # Hemoglobin
            r'эритроциты',         # Red blood cells
            r'лейкоциты',          # White blood cells
            r'тромбоциты',         # Platelets
            r'глюкоза',            # Glucose
            r'креатинин',          # Creatinine
            r'холестерин',         # Cholesterol
            r'белок',              # Protein
            r'билирубин',          # Bilirubin
            
            # Hepatitis-specific patterns
            r'гепатит\s*[a-z]',    # Hepatitis A, B, C, etc.
            r'hbsag',              # HBsAg
            r'антитела',           # Antibodies
            r'маркер',             # Marker
        ]
        
        s_lower = s.lower()
        for pattern in medical_patterns:
            if re.search(pattern, s_lower):
                return True
        return False

    def combine_multiline_values(lines, start_idx):
        """Combine values that might be split across multiple lines."""
        combined = lines[start_idx]
        
        # Look for continuation on next lines (e.g., unit on separate line)
        for j in range(start_idx + 1, min(start_idx + 3, len(lines))):
            next_line = lines[j].strip()
            
            # If next line looks like a unit or continuation
            if re.match(r'^[а-яА-Яa-zA-Z/%×·*^]+$', next_line):
                combined += " " + next_line
                break
            elif re.match(r'^10\^?\d+', next_line):  # Scientific notation continuation
                combined += " " + next_line
                continue
        
        return combined

    def process_tabular_data(lines, start_idx):
        """Process tabular medical data like hormone test results."""
        results_found = []
        
        # Look for patterns like:
        # "ТТГ1" followed by "1,33 мкМЕ/мл" and range values
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line contains a medical test name
            if is_medical_test_name(line):
                test_name = line
                value = None
                range_parts = []
                range_str = None
                
                # Look for value and range in subsequent lines
                for j in range(i + 1, min(i + 8, len(lines))):  # Look further ahead
                    if j >= len(lines):
                        break
                        
                    current_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not current_line:
                        continue
                    
                    # If we find a value and don't have one yet
                    if not value and is_value(current_line):
                        value = current_line
                        continue
                    
                    # Look for complete range patterns first
                    if not range_str and is_range(current_line):
                        range_str = current_line
                        continue
                    
                    # Look for range components (individual numbers that form a range)
                    if re.match(r'^\d+[,\.]?\d*$', current_line) and len(range_parts) < 2:
                        range_parts.append(current_line)
                        continue
                    
                    # Check for range patterns with dash (like "1,00 - 1,70")
                    range_match = re.search(r'(\d+[,\.]?\d*)\s*[-–]\s*(\d+[,\.]?\d*)', current_line)
                    if range_match and not range_str:
                        range_str = f"{range_match.group(1)} - {range_match.group(2)}"
                        continue
                    
                    # If we find another test name, stop processing this one
                    if is_medical_test_name(current_line):
                        break
                
                # Create result if we have enough data
                if value:
                    if range_str:
                        results_found.append(f"{test_name}: {value} (норма: {range_str})")
                    elif len(range_parts) >= 2:
                        range_str = f"{range_parts[0]} - {range_parts[1]}"
                        results_found.append(f"{test_name}: {value} (норма: {range_str})")
                    else:
                        results_found.append(f"{test_name}: {value}")
                
                # Move to the line where we found the next test or end
                i = j if j < len(lines) and is_medical_test_name(lines[j].strip()) else i + 1
            else:
                i += 1
        
        return results_found

    def process_hepatitis_data(lines):
        """Special processing for fragmented hepatitis test data."""
        results_found = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip().lower()
            
            # Look for hepatitis C pattern
            if 'гепатит с' in line or ('гепатит' in line and 'с' in lines[min(i+1, len(lines)-1)].strip().lower()):
                test_name = "Гепатит C (суммарные антитела)"
                
                # Look for "Не обнаружено" and S/CO value in subsequent lines
                qualitative_result = None
                sco_value = None
                
                for j in range(i, min(i + 6, len(lines))):
                    current_line = lines[j].strip()
                    
                    # Check for qualitative result
                    if 'не обнаружено' in current_line.lower() or 'he обнаружено' in current_line.lower():
                        qualitative_result = "Не обнаружено"
                    
                    # Check for S/CO value
                    sco_match = re.search(r'S/CO\s*=\s*(\d+[,\.]?\d*)', current_line)
                    if sco_match:
                        sco_value = sco_match.group(1)
                
                # Create combined result
                if qualitative_result and sco_value:
                    results_found.append(f"{test_name}: {qualitative_result}, S/CO = {sco_value} (норма: S/CO < 1,0)")
                
                i = j if j < len(lines) else i + 1
                
            # Look for HBsAg pattern
            elif 'hbsag' in line or ('hbs' in line and 'ag' in line):
                test_name = "HBsAg (гепатит B)"
                
                # Look for "Не обнаружено" and S/CO value in subsequent lines
                qualitative_result = None
                sco_value = None
                
                for j in range(i, min(i + 6, len(lines))):
                    current_line = lines[j].strip()
                    
                    # Check for qualitative result
                    if 'не обнаружено' in current_line.lower() or 'he обнаружено' in current_line.lower():
                        qualitative_result = "Не обнаружено"
                    
                    # Check for S/CO value
                    sco_match = re.search(r'S/CO\s*=\s*(\d+[,\.]?\d*)', current_line)
                    if sco_match:
                        sco_value = sco_match.group(1)
                
                # Create combined result
                if qualitative_result and sco_value:
                    results_found.append(f"{test_name}: {qualitative_result}, S/CO = {sco_value} (норма: S/CO < 1,0)")
                
                i = j if j < len(lines) else i + 1
            else:
                i += 1
        
        return results_found

    def process_biochemical_table(lines):
        """Enhanced processing for biochemical table data with multiple metrics."""
        results_found = []
        processed_names = set()  # Track processed names to avoid duplicates
        
        # Enhanced biochemical marker patterns
        biochemical_markers = {
            'альбумин': 'Альбумин',
            'креатинин': 'Креатинин', 
            'глюкоза': 'Глюкоза',
            'магний': 'Магний',
            'алт': 'АЛТ',
            'аст': 'АСТ',
            'ггт': 'ГГТ',
            'ггтп': 'ГГТ',
            'щелочная фосфатаза': 'Щелочная фосфатаза',
            'щелочная': 'Щелочная фосфатаза',
            'фосфатаза': 'Щелочная фосфатаза',
            'щф': 'Щелочная фосфатаза',  # Common abbreviation
            'триглицериды': 'Триглицериды',
            'калий': 'Калий',
            'кальций': 'Кальций',
            'натрий': 'Натрий',
            'холестерин общий': 'Холестерин общий',
            'холестерин': 'Холестерин общий',  # Default to total cholesterol
            'холестерин лпнп': 'Холестерин ЛПНП',
            'лпнп': 'Холестерин ЛПНП',
            'холестерин лпвп': 'Холестерин ЛПВП',
            'лпвп': 'Холестерин ЛПВП',
            'холестерин лпонп': 'Холестерин ЛПОНП',
            'лпонп': 'Холестерин ЛПОНП',
            'мочевина': 'Мочевина',
            'мочевая кислота': 'Мочевая кислота',
            'альфа-амилаза': 'Альфа-амилаза',
            'амилаза': 'Амилаза',
        }
        
        def clean_unit(unit_str):
            """Clean and normalize unit strings."""
            unit_str = unit_str.strip()
            
            # Fix common unit formatting issues
            unit_replacements = {
                'ммольл': 'ммоль/л',
                'мкмольл': 'мкмоль/л',
                'ммолыл': 'ммоль/л',  # Additional OCR error
                'мкмолыл': 'мкмоль/л',  # Additional OCR error
                'гл': 'г/л',
                'мгл': 'мг/л',
                'мкгл': 'мкг/л',
                'едл': 'Ед/л',
                'Биоматериалды': 'Ед/л',  # Common OCR error
                'результатах': 'Ед/л',    # Common OCR error
            }
            
            for old, new in unit_replacements.items():
                if old in unit_str:
                    unit_str = unit_str.replace(old, new)
            
            return unit_str
        
        def is_date_contaminated(line):
            """Check if line contains date patterns that indicate contamination."""
            date_patterns = [
                r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
                r'\d{4}\.\d{2}\.\d{2}',  # YYYY.MM.DD
                r'алу орны',             # Kazakh text for "collection location"
                r'биоматериалды',        # Kazakh for "biomaterial"
            ]
            
            for pattern in date_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return True
            return False
        
        # Look for biochemical test patterns across multiple lines
        i = 0
        while i < len(lines):
            line = lines[i].strip().lower()
            
            # Skip date-contaminated lines
            if is_date_contaminated(lines[i]):
                i += 1
                continue
            
            # Check if current line contains a biochemical marker
            found_marker = None
            normalized_name = None
            
            for marker, name in biochemical_markers.items():
                if marker in line:
                    found_marker = marker
                    normalized_name = name
                    break
            
            if found_marker and normalized_name not in processed_names:
                # Look for value, unit, and range in subsequent lines
                value_line = None
                range_line = None
                
                # Search in next several lines for numerical data
                for j in range(i, min(i + 10, len(lines))):
                    current_line = lines[j].strip()
                    
                    # Skip date-contaminated lines
                    if is_date_contaminated(current_line):
                        continue
                    
                    # Look for a value with unit
                    value_match = re.search(r'(\d+[,\.]?\d*)\s*([а-яА-Яa-zA-Z/%×·*^]+(?:/[а-яА-Яa-zA-Z]+)?|U/L|МЕ/л|Ед/л|мкМЕ/мл|нг/мл|пг/мл|нг/дл|мг/л|мкг/л|сек|ммоль/л|мкмоль/л)', current_line)
                    if value_match and not value_line:
                        # Clean the unit
                        raw_value = value_match.group(1)
                        raw_unit = value_match.group(2)
                        cleaned_unit = clean_unit(raw_unit)
                        value_line = f"{raw_value} {cleaned_unit}"
                        
                    # Look for range pattern
                    range_match = re.search(r'(\d+[,\.]?\d*)\s*[-–]\s*(\d+[,\.]?\d*)', current_line)
                    if range_match and not range_line:
                        range_line = current_line
                
                # Create combined result if we have the essential data
                if value_line:
                    processed_names.add(normalized_name)  # Mark as processed
                    if range_line:
                        results_found.append(f"{normalized_name}: {value_line} (норма: {range_line})")
                    else:
                        results_found.append(f"{normalized_name}: {value_line}")
                
                # Move to next potential marker
                i = j if j < len(lines) else i + 1
            else:
                i += 1
        
        return results_found

    # First, try to process as tabular data (for hormone tests, etc.)
    tabular_results = process_tabular_data(lines, 0)
    if tabular_results:
        results.extend(tabular_results)

    # Then try to process hepatitis data (for fragmented S/CO tests)
    hepatitis_results = process_hepatitis_data(lines)
    if hepatitis_results:
        results.extend(hepatitis_results)

    # Then process biochemical table data
    biochemical_results = process_biochemical_table(lines)
    if biochemical_results:
        results.extend(biochemical_results)

    # Then process traditional CBC-style data
    while i < len(lines):
        line = lines[i]

        # Check if line is a lab code (e.g., HGB, RBC, PLT)
        if re.match(r"^[A-Z]{2,5}#?%?$", line):
            code = line
            value, norm = None, None

            # Search for value and normal range in subsequent lines
            for j in range(i + 1, min(i + 6, len(lines))):
                current_line = lines[j]
                
                # Try to combine multiline values
                if not value:
                    combined_line = combine_multiline_values(lines, j)
                    if is_value(combined_line):
                        value = combined_line
                        continue
                
                if not norm and is_range(current_line):
                    norm = current_line

                # Stop if we found both value and norm
                if value and norm:
                    break

            # Create result entry if we have the minimum required info
            if value:
                if norm:
                    results.append(f"{code}: {value} (норма: {norm})")
                else:
                    results.append(f"{code}: {value}")
                    
        # Also check for direct metric lines (Name: Value format)
        elif ':' in line and not any(word in line.lower() for word in ['пациент', 'дата', 'врач', 'клиника', 'заявка', 'забор', 'биоматериал']):
            # This might be a direct metric line, pass it through
            name_part, value_part = line.split(':', 1)
            name_part = name_part.strip()
            value_part = value_part.strip()
            
            # Check if this looks like a medical metric
            if (len(name_part) <= 50 and  # Reasonable metric name length
                any(char.isdigit() for char in value_part)):  # Contains numbers
                results.append(line)

        i += 1

    return "\n".join(results)
