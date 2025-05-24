import os
import time
import requests
import asyncio
import threading
from typing import Dict, Optional, Tuple, List, Any
from functools import lru_cache
from dotenv import load_dotenv
from app.schemas import DiseaseRisk, RiskLevel

# Load environment variables from .env file
load_dotenv()

# Securely load Groq API key from environment variables
api_key = os.getenv("GROQ_API_KEY")

# Validate API key on module import
if not api_key:
    print("⚠️  Warning: GROQ_API_KEY not found in environment variables.")
    print("📋 Please set your Groq API key in the .env file:")
    print("   GROQ_API_KEY=your_actual_token_here")
    print("🔗 Get your API key from: https://console.groq.com/")
elif not api_key.startswith("gsk_"):
    print("⚠️  Warning: GROQ_API_KEY does not appear to be a valid Groq API key.")
    print("📋 Groq API keys should start with 'gsk_'")
else:
    print(f"✅ Groq API key loaded successfully: {api_key[:10]}...")

# Simple in-memory cache for responses
explanation_cache = {}
pending_requests = set()
CACHE_EXPIRY = 3600  # Cache explanations for 1 hour

# 🔽 ВСТАВЬ СЮДА PROMPT_TEMPLATE
PROMPT_TEMPLATE = """
Ты врач-аналитик. Проанализируй результаты анализов и дай краткое, понятное объяснение.

Результаты анализов:
{raw_text}

Структурируй ответ так:
1. **Общая оценка:** (норма/требует внимания/срочно к врачу)
2. **Отклонения:** (перечисли основные отклонения)  
3. **Рекомендации:** (что делать)

Отвечай простым языком, избегай медицинской терминологии.
"""

# New template for individual metric explanations
METRIC_EXPLANATION_TEMPLATE = """
Объясни простым языком один показатель анализа:

Показатель: {metric_name}
Значение: {value} {unit}
Норма: {reference_range}
Статус: {status}

Дай краткое объяснение (1-2 предложения):
- Что означает этот показатель
- Нормально ли значение
- Что делать, если есть отклонения

Отвечай понятно, без медицинских терминов.
"""

# Placeholder response when model is taking too long
FALLBACK_RESPONSE = """
Основываясь на вашем анализе, я могу предоставить предварительное объяснение:

1. Обратите внимание на показатели, выходящие за пределы нормы (указаны в скобках после значений).
2. Небольшие отклонения могут быть вариантом нормы или временными изменениями.
3. Для точной интерпретации результатов рекомендуется проконсультироваться с врачом.

Более подробный анализ ваших результатов еще обрабатывается и будет доступен вскоре.
"""

# Disease explanation template
DISEASE_EXPLANATION_TEMPLATE = """
Ты врач, который объясняет результаты AI-анализа рисков заболеваний пациенту.

Результаты прогнозирования:
- Общий уровень риска: {overall_risk}
- Обнаруженные риски: {predicted_diseases}

Объясни пациенту простым языком:
1. **Что означают эти результаты**
2. **Какие показатели вызывают беспокойство**
3. **Практические рекомендации**
4. **Когда обратиться к врачу**

Важно:
- Используй простой, понятный язык
- Не пугай, но подчеркни важность медицинской консультации
- Объясни, что это только предварительная оценка
- Дай конкретные, практичные советы

Ответ должен быть успокаивающим, но информативным.
"""

def generate_explanation_async(raw_text: str) -> str:
    """
    Return cached explanation if available, otherwise start async processing
    and return a placeholder response
    """
    # Check cache first
    cache_key = hash(raw_text)
    if cache_key in explanation_cache:
        cached_item = explanation_cache[cache_key]
        # Check if cache is still valid
        if time.time() - cached_item["timestamp"] < CACHE_EXPIRY:
            return cached_item["explanation"]
        else:
            # Remove expired cache entry
            del explanation_cache[cache_key]
    
    # Check if we're already processing this request
    if cache_key in pending_requests:
        # If it's taking too long, return fallback
        if time.time() - pending_requests[cache_key] > 5:  # 5 seconds threshold
            return FALLBACK_RESPONSE
        else:
            # Just started processing, return fallback
            return FALLBACK_RESPONSE
    
    # Start processing in background
    pending_requests.add(cache_key)
    threading.Thread(
        target=_process_explanation_in_background,
        args=(raw_text, cache_key),
        daemon=True
    ).start()
    
    # Return placeholder immediately
    return FALLBACK_RESPONSE

def _process_explanation_in_background(raw_text: str, cache_key: int) -> None:
    """Process the explanation in background and store result in cache"""
    try:
        # Generate the actual explanation
        explanation = _call_groq_api(raw_text)
        
        # Store in cache
        explanation_cache[cache_key] = {
            "explanation": explanation,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Background processing error: {e}")
    finally:
        # Remove from pending list
        if cache_key in pending_requests:
            pending_requests.remove(cache_key)

def _call_groq_api(raw_text: str, timeout: int = 30) -> str:
    """Call the Groq API with timeout handling"""
    formatted_text = raw_text.replace("\\n", "\n")  # чтобы \n стали реальными переводами строк
    prompt = PROMPT_TEMPLATE.format(raw_text=formatted_text)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "Ты — медицинский помощник, который помогает людям понять результаты анализов."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json=payload, 
            headers=headers,
            timeout=timeout  # Add timeout parameter
        )

        if response.status_code != 200:
            print(f"[ERROR] Groq API response: {response.status_code} — {response.text}")
            raise Exception(f"Groq API error: {response.status_code} — {response.text}")

        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        print("[ERROR] Groq API request timed out")
        return "Извините, запрос к модели занял слишком много времени. Пожалуйста, попробуйте позже."
    except Exception as e:
        print(f"[ERROR] Groq API request failed: {e}")
        return f"Произошла ошибка при обработке запроса: {str(e)}"

# Legacy synchronous function - keep for backward compatibility
def generate_explanation(raw_text: str) -> str:
    """
    Generate explanation for medical text - this now uses the async version
    with immediate fallback response
    """
    return generate_explanation_async(raw_text)

def generate_individual_metric_explanations(metrics: List[Dict]) -> List[Dict]:
    """
    Generate individual explanations for each health metric
    
    Args:
        metrics: List of metric dictionaries with name, value, unit, reference_range, status
        
    Returns:
        List of metrics with added 'explanation' field
    """
    if not metrics:
        return metrics
    
    explained_metrics = []
    
    for metric in metrics:
        try:
            # Generate explanation for this specific metric
            explanation = _generate_single_metric_explanation(metric)
            
            # Add explanation to the metric dictionary
            metric_with_explanation = metric.copy()
            metric_with_explanation['explanation'] = explanation
            explained_metrics.append(metric_with_explanation)
            
        except Exception as e:
            print(f"Error generating explanation for metric {metric.get('name', 'Unknown')}: {e}")
            # Add fallback explanation
            metric_with_explanation = metric.copy()
            metric_with_explanation['explanation'] = f"Анализ показателя {metric.get('name', 'данного')} в процессе обработки."
            explained_metrics.append(metric_with_explanation)
    
    return explained_metrics

def _generate_single_metric_explanation(metric: Dict) -> str:
    """Generate explanation for a single metric"""
    # Create cache key for this specific metric
    cache_key = hash(f"{metric.get('name', '')}_{metric.get('value', '')}_{metric.get('status', '')}")
    
    # Check cache first
    if cache_key in explanation_cache:
        cached_item = explanation_cache[cache_key]
        if time.time() - cached_item["timestamp"] < CACHE_EXPIRY:
            return cached_item["explanation"]
        else:
            del explanation_cache[cache_key]
    
    # Prepare prompt for individual metric
    prompt = METRIC_EXPLANATION_TEMPLATE.format(
        metric_name=metric.get('name', 'Неизвестный показатель'),
        value=metric.get('value', 'Н/Д'),
        unit=metric.get('unit', ''),
        reference_range=metric.get('reference_range', 'Не указана'),
        status=_translate_status(metric.get('status', 'normal'))
    )
    
    try:
        # Call API to get explanation
        explanation = _call_groq_api_for_metric(prompt)
        
        # Cache the result
        explanation_cache[cache_key] = {
            "explanation": explanation,
            "timestamp": time.time()
        }
        
        return explanation
        
    except Exception as e:
        print(f"Error calling API for metric explanation: {e}")
        return _get_fallback_metric_explanation(metric)

def _translate_status(status: str) -> str:
    """Translate status to Russian for better prompt context"""
    status_translations = {
        'normal': 'норма',
        'low': 'ниже нормы', 
        'high': 'выше нормы',
        'elevated': 'повышен'
    }
    return status_translations.get(status.lower(), status)

def _get_fallback_metric_explanation(metric: Dict) -> str:
    """Generate a simple fallback explanation when API fails"""
    name = metric.get('name', 'Данный показатель')
    status = metric.get('status', 'normal')
    value = metric.get('value', '')
    unit = metric.get('unit', '')
    
    if status == 'normal':
        return f"{name} ({value} {unit}) находится в пределах нормы."
    elif status == 'low':
        return f"{name} ({value} {unit}) ниже нормы. Рекомендуется консультация врача."
    elif status in ['high', 'elevated']:
        return f"{name} ({value} {unit}) выше нормы. Рекомендуется консультация врача."
    else:
        return f"{name} ({value} {unit}) требует дополнительного анализа."

def _call_groq_api_for_metric(prompt: str, timeout: int = 15) -> str:
    """Call the Groq API specifically for metric explanations with shorter timeout"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "Ты — медицинский помощник, который помогает людям понять результаты анализов. Отвечай кратко и понятно."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 200  # Shorter responses for individual metrics
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json=payload, 
            headers=headers,
            timeout=timeout
        )

        if response.status_code != 200:
            print(f"[ERROR] Groq API response: {response.status_code} — {response.text}")
            raise Exception(f"Groq API error: {response.status_code}")

        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        print("[ERROR] Groq API request timed out for metric explanation")
        raise Exception("Request timeout")
    except Exception as e:
        print(f"[ERROR] Groq API request failed for metric: {e}")
        raise e

async def generate_disease_explanation(predicted_diseases: List[DiseaseRisk], 
                                     overall_risk: RiskLevel) -> str:
    """
    Generate AI explanation for disease risk predictions.
    
    Args:
        predicted_diseases: List of disease risk predictions
        overall_risk: Overall risk level
        
    Returns:
        Human-readable explanation of the disease risks
    """
    if not api_key:
        return _get_fallback_disease_explanation(predicted_diseases, overall_risk)
    
    try:
        # Format diseases for prompt
        disease_descriptions = []
        for disease in predicted_diseases:
            disease_descriptions.append(
                f"- {disease.disease_name}: {disease.risk_level.value} риск "
                f"(уверенность: {disease.confidence:.0%})"
            )
        
        diseases_text = "\n".join(disease_descriptions) if disease_descriptions else "Риски не обнаружены"
        
        # Create prompt
        prompt = DISEASE_EXPLANATION_TEMPLATE.format(
            overall_risk=_translate_risk_level(overall_risk),
            predicted_diseases=diseases_text
        )
        
        # Generate explanation
        explanation = await _call_groq_api_for_disease(prompt)
        
        return explanation
        
    except Exception as e:
        print(f"[ERROR] Failed to generate disease explanation: {e}")
        return _get_fallback_disease_explanation(predicted_diseases, overall_risk)

async def _call_groq_api_for_disease(prompt: str, timeout: int = 30) -> str:
    """Call the Groq API specifically for disease explanations"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "system", 
                "content": "Ты — опытный врач, который помогает пациентам понять результаты медицинских анализов. Объясняй сложные вещи простым языком, успокаивай пациентов, но подчеркивай важность профессиональной медицинской консультации."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 800  # Longer explanations for disease risks
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            json=payload, 
            headers=headers,
            timeout=timeout
        )

        if response.status_code != 200:
            print(f"[ERROR] Groq API response: {response.status_code} — {response.text}")
            raise Exception(f"Groq API error: {response.status_code}")

        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        print("[ERROR] Groq API request timed out for disease explanation")
        raise Exception("Request timeout")
    except Exception as e:
        print(f"[ERROR] Groq API request failed for disease explanation: {e}")
        raise e

def _translate_risk_level(risk_level: RiskLevel) -> str:
    """Translate risk level to Russian"""
    translations = {
        RiskLevel.LOW: "низкий",
        RiskLevel.MODERATE: "умеренный", 
        RiskLevel.HIGH: "высокий"
    }
    return translations.get(risk_level, risk_level.value)

def _get_fallback_disease_explanation(predicted_diseases: List[DiseaseRisk], 
                                    overall_risk: RiskLevel) -> str:
    """Generate fallback explanation when AI is unavailable"""
    if overall_risk == RiskLevel.HIGH:
        base_message = "⚠️ **Обнаружены показатели, требующие внимания**\n\n"
        base_message += "Анализ ваших результатов показал отклонения, которые могут указывать на определенные риски для здоровья. "
        base_message += "Рекомендуется как можно скорее обратиться к врачу для детальной консультации.\n\n"
    elif overall_risk == RiskLevel.MODERATE:
        base_message = "ℹ️ **Некоторые показатели заслуживают внимания**\n\n"
        base_message += "В ваших анализах есть значения, которые стоит обсудить с врачом. "
        base_message += "Это не обязательно означает серьезные проблемы, но профессиональная консультация поможет разобраться.\n\n"
    else:
        base_message = "✅ **Показатели в целом в пределах нормы**\n\n"
        base_message += "Анализ не выявил серьезных отклонений. Продолжайте следить за своим здоровьем и регулярно проходите обследования.\n\n"
    
    if predicted_diseases:
        base_message += "**Обнаруженные области для внимания:**\n"
        for disease in predicted_diseases:
            disease_name_ru = _translate_disease_name(disease.disease_name)
            base_message += f"• {disease_name_ru} (уровень риска: {_translate_risk_level(disease.risk_level)})\n"
        base_message += "\n"
    
    base_message += "**Важно помнить:**\n"
    base_message += "• Это предварительная оценка, основанная на анализе данных\n"
    base_message += "• Окончательный диагноз может поставить только врач\n"
    base_message += "• При любых симптомах или беспокойствах обращайтесь к специалисту\n"
    base_message += "• Регулярные профилактические осмотры важны для поддержания здоровья"
    
    return base_message

def _translate_disease_name(disease_name: str) -> str:
    """Translate disease names to Russian"""
    translations = {
        "anemia": "Анемия",
        "diabetes": "Сахарный диабет", 
        "liver_dysfunction": "Нарушение функции печени",
        "kidney_disease": "Заболевания почек",
        "thyroid_disorders": "Нарушения щитовидной железы",
        "cardiovascular_risk": "Сердечно-сосудистые риски"
    }
    return translations.get(disease_name, disease_name.replace("_", " ").title())
