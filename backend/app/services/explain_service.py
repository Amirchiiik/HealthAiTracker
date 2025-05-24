from app.services.llm_service import generate_explanation as llm_generate_explanation

def generate_explanation(text: str) -> str:
    """
    Generate an explanation of health metrics using the LLM service.
    
    Args:
        text: The raw text from OCR to explain
        
    Returns:
        A human-readable explanation of the health metrics
    """
    # Call the LLM service to generate an explanation
    explanation = llm_generate_explanation(text)
    
    # If the explanation is empty or too short, provide a fallback
    if not explanation or len(explanation) < 20:
        return "We couldn't generate a detailed explanation for your health metrics. Please consult with a healthcare professional for interpretation of your results."
    
    return explanation 