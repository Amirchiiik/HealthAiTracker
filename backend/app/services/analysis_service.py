from typing import Dict, List
from app.services import ocr_service, llm_service

def analyze_medical_document_with_explanations(file_path: str) -> Dict:
    """
    Analyze a medical document and provide individual explanations for each metric
    
    Args:
        file_path: Path to the medical document file
        
    Returns:
        Dictionary containing extracted metrics with individual explanations plus overall summary
    """
    # First, extract text and metrics using existing OCR service
    ocr_result = ocr_service.extract_text_from_file(file_path)
    
    # Get the metrics from the analysis
    metrics = ocr_result.get("analysis", {}).get("metrics", [])
    
    if not metrics:
        return {
            "metrics": [],
            "overall_summary": "No health metrics were detected in the document.",
            "extracted_text": ocr_result.get("extracted_text", ""),
            "analysis": ocr_result.get("analysis", {})
        }
    
    # Generate individual explanations for each metric
    explained_metrics = llm_service.generate_individual_metric_explanations(metrics)
    
    # Generate overall summary
    overall_summary = _generate_overall_summary(explained_metrics)
    
    # Return enhanced analysis with individual explanations
    enhanced_analysis = ocr_result.get("analysis", {}).copy()
    enhanced_analysis["metrics"] = explained_metrics
    
    return {
        "metrics": explained_metrics,
        "overall_summary": overall_summary,
        "extracted_text": ocr_result.get("extracted_text", ""),
        "analysis": enhanced_analysis
    }

def analyze_metrics_from_text_with_explanations(raw_text: str) -> Dict:
    """
    Analyze metrics from raw text and provide individual explanations
    
    Args:
        raw_text: Raw text containing health metrics
        
    Returns:
        Dictionary containing analyzed metrics with individual explanations
    """
    # Extract metrics from the raw text
    metrics = ocr_service.extract_metrics_from_text(raw_text)
    
    if not metrics:
        return {
            "metrics": [],
            "overall_summary": "No health metrics were detected in the provided text.",
            "analysis": {
                "metrics": [],
                "valid": False,
                "validation_message": "No metrics found in text"
            }
        }
    
    # Generate individual explanations for each metric
    explained_metrics = llm_service.generate_individual_metric_explanations(metrics)
    
    # Generate overall summary
    overall_summary = _generate_overall_summary(explained_metrics)
    
    # Validate the metrics
    is_valid, validation_message = ocr_service.validate_medical_document(metrics, raw_text)
    
    return {
        "metrics": explained_metrics,
        "overall_summary": overall_summary,
        "analysis": {
            "metrics": explained_metrics,
            "valid": is_valid,
            "validation_message": validation_message,
            "summary": overall_summary
        }
    }

def _generate_overall_summary(metrics: List[Dict]) -> str:
    """Generate an overall summary of all metrics"""
    if not metrics:
        return "No health metrics analyzed."
    
    total_metrics = len(metrics)
    normal_count = len([m for m in metrics if m.get('status') == 'normal'])
    low_count = len([m for m in metrics if m.get('status') == 'low'])
    high_count = len([m for m in metrics if m.get('status') in ['high', 'elevated']])
    attention_needed = total_metrics - normal_count
    
    summary_parts = [f"{total_metrics} показателей проанализировано."]
    
    if normal_count > 0:
        summary_parts.append(f"{normal_count} в норме.")
    
    if attention_needed > 0:
        attention_details = []
        if low_count > 0:
            attention_details.append(f"{low_count} ниже нормы")
        if high_count > 0:
            attention_details.append(f"{high_count} выше нормы")
        
        summary_parts.append(f"{attention_needed} требуют внимания ({', '.join(attention_details)}).")
    
    if attention_needed > 0:
        summary_parts.append("Рекомендуется консультация с врачом для интерпретации результатов.")
    
    return " ".join(summary_parts)

def get_metrics_by_status(metrics: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group metrics by their status for easier analysis
    
    Args:
        metrics: List of metric dictionaries
        
    Returns:
        Dictionary with status as keys and lists of metrics as values
    """
    grouped = {
        'normal': [],
        'low': [],
        'high': [],
        'elevated': []
    }
    
    for metric in metrics:
        status = metric.get('status', 'normal')
        if status in grouped:
            grouped[status].append(metric)
        else:
            grouped['normal'].append(metric)
    
    return grouped 