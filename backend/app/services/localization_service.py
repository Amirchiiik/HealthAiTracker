"""
Localization Service

Provides multilingual support for the AI Health Tracker system.
Currently supports English (en) and Russian (ru).
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    RUSSIAN = "ru"

class LocalizationService:
    """Service for handling translations and localized text."""
    
    def __init__(self):
        self.translations = {
            "en": {
                # Doctor recommendations
                "glucose_abnormality": "Glucose Abnormality detected: {metric_name}: {value} {unit} ({status}). May indicate diabetes or metabolic dysfunction",
                "liver_enzymes_elevated": "Elevated Liver Enzymes detected: {metrics}. May indicate liver stress, hepatitis, or liver damage",
                "kidney_function_abnormal": "Kidney Function Abnormality detected: {metrics}. May indicate kidney dysfunction or disease",
                "blood_count_abnormal": "Blood Count Abnormality detected: {metrics}. May require hematological evaluation",
                "cholesterol_abnormal": "Cholesterol Abnormality detected: {metrics}. May indicate cardiovascular risk",
                
                # Specialist types
                "endocrinologist": "Endocrinologist",
                "gastroenterologist": "Gastroenterologist", 
                "hepatologist": "Hepatologist",
                "nephrologist": "Nephrologist",
                "hematologist": "Hematologist",
                "cardiologist": "Cardiologist",
                "internal_medicine": "Internal Medicine",
                
                # Specialist descriptions
                "endocrinologist_desc": "Specialist in hormones, metabolism, and endocrine disorders",
                "gastroenterologist_desc": "Specialist in digestive system and liver disorders",
                "hepatologist_desc": "Specialist specifically focused on liver diseases",
                "nephrologist_desc": "Specialist in kidney diseases and disorders",
                "hematologist_desc": "Specialist in blood disorders and diseases",
                "cardiologist_desc": "Specialist in heart and cardiovascular diseases",
                "internal_medicine_desc": "General internal medicine physician",
                
                # When to consult
                "endocrinologist_when": "For diabetes, thyroid disorders, or metabolic abnormalities",
                "gastroenterologist_when": "For liver enzyme abnormalities, digestive issues, or abdominal symptoms",
                "hepatologist_when": "For complex liver enzyme abnormalities or suspected liver disease",
                "nephrologist_when": "For kidney function abnormalities or urinary symptoms",
                "hematologist_when": "For blood count abnormalities or bleeding disorders",
                "cardiologist_when": "For cholesterol abnormalities or cardiovascular risk factors",
                "internal_medicine_when": "For overall health assessment and coordination of care",
                
                # Agent reasoning
                "clinical_significance": "Clinical Significance of Abnormal Values:",
                "interconnections": "Potential Interconnections Between Abnormal Metrics:",
                "urgency_level": "Urgency Level for Medical Consultation:",
                "patterns_suggest": "Specific Conditions Suggested by Patterns:",
                "high_priority": "High Priority",
                "medium_priority": "Medium Priority", 
                "low_priority": "Low Priority",
                "immediate_consultation": "Immediate consultation with {specialist} is recommended due to {reason}",
                
                # Next steps
                "schedule_urgent_consultation": "Schedule urgent consultation with recommended specialists for elevated values",
                "consider_liver_function": "Consider liver function panel and abdominal ultrasound",
                "monitor_glucose": "Monitor blood glucose levels and consider HbA1c testing",
                "follow_up_primary": "Follow up with your primary care physician to discuss these results",
                "bring_previous_results": "Bring all previous lab results to specialist consultations",
                "routine_monitoring": "Continue routine monitoring of health metrics",
                "healthy_lifestyle": "Maintain healthy diet and exercise routine",
                "regular_checkups": "Continue regular check-ups with your primary care physician",
                
                # Actions and booking
                "auto_booked_appointment": "Automatically booked urgent appointment (ID: {appointment_id})",
                "booking_attempted": "Attempted auto-booking: {message}",
                "no_available_doctors": "No available {specialist} doctors found",
                "earliest_appointment": "Earliest available appointment with {doctor_name} is on {datetime}. Please book manually if acceptable.",
                "successfully_booked": "Successfully booked appointment with {doctor_name} on {datetime}",
                "booking_error": "Error occurred while booking appointment: {error}",
                "no_appropriate_specialist": "No appropriate specialist determined for auto-booking",
                "urgent_consultation_required": "Urgent consultation required due to critical health metrics: {metrics}",
                "auto_booking_failed": "Auto-booking failed due to error: {error}",
                "automated_analysis_detected": "Automated analysis detected {metrics} critical metrics requiring {priority} priority attention",
                "no_health_metrics_found": "No health metrics found in analysis",
                "upload_medical_report": "Upload a medical report with health metrics for analysis",
                "no_actions_taken": "No actions taken - no metrics found",
                
                # Analysis summary
                "total_metrics": "Total metrics analyzed",
                "abnormal_metrics": "Abnormal metrics found", 
                "critical_metrics": "Critical metrics requiring attention",
                "priority_level": "Overall priority level",
                "no_metrics_found": "No health metrics found in analysis",
                "all_normal": "All values fall within normal reference ranges",
                "continue_monitoring": "Continue regular health monitoring and maintain healthy lifestyle",
                
                # Error messages
                "analysis_not_found": "Health analysis not found or unauthorized",
                "patient_not_found": "Patient not found",
                "unable_to_analyze": "Unable to complete intelligent analysis. Please try again later.",
                "doctor_not_available": "Doctor not found or not available",
                "time_slot_conflict": "Time slot conflict for the requested appointment time",
                
                # Notifications
                "critical_alert": "Important Health Alert - Critical Values Detected",
                "appointment_confirmation": "Appointment Confirmation - AI Health Tracker",
                "analysis_complete": "Health Analysis Complete - {count} Recommendations"
            },
            
            "ru": {
                # Doctor recommendations
                "glucose_abnormality": "Обнаружено нарушение глюкозы: {metric_name}: {value} {unit} ({status}). Может указывать на диабет или метаболическую дисфункцию",
                "liver_enzymes_elevated": "Обнаружено повышение печёночных ферментов: {metrics}. Может указывать на стресс печени, гепатит или повреждение печени",
                "kidney_function_abnormal": "Обнаружено нарушение функции почек: {metrics}. Может указывать на дисфункцию или заболевание почек",
                "blood_count_abnormal": "Обнаружено нарушение показателей крови: {metrics}. Может потребоваться гематологическое обследование",
                "cholesterol_abnormal": "Обнаружено нарушение холестерина: {metrics}. Может указывать на сердечно-сосудистый риск",
                
                # Specialist types
                "endocrinologist": "Эндокринолог",
                "gastroenterologist": "Гастроэнтеролог",
                "hepatologist": "Гепатолог", 
                "nephrologist": "Нефролог",
                "hematologist": "Гематолог",
                "cardiologist": "Кардиолог",
                "internal_medicine": "Терапевт",
                
                # Specialist descriptions
                "endocrinologist_desc": "Специалист по гормонам, метаболизму и эндокринным расстройствам",
                "gastroenterologist_desc": "Специалист по заболеваниям пищеварительной системы и печени",
                "hepatologist_desc": "Специалист, специализирующийся на заболеваниях печени",
                "nephrologist_desc": "Специалист по заболеваниям и расстройствам почек",
                "hematologist_desc": "Специалист по заболеваниям и расстройствам крови",
                "cardiologist_desc": "Специалист по сердечным и сердечно-сосудистым заболеваниям",
                "internal_medicine_desc": "Врач общей терапии",
                
                # When to consult
                "endocrinologist_when": "При диабете, заболеваниях щитовидной железы или метаболических нарушениях",
                "gastroenterologist_when": "При нарушениях печёночных ферментов, проблемах с пищеварением или симптомах в области живота",
                "hepatologist_when": "При сложных нарушениях печёночных ферментов или подозрении на заболевание печени",
                "nephrologist_when": "При нарушениях функции почек или симптомах мочеполовой системы",
                "hematologist_when": "При нарушениях показателей крови или расстройствах свёртываемости",
                "cardiologist_when": "При нарушениях холестерина или факторах сердечно-сосудистого риска",
                "internal_medicine_when": "Для общей оценки состояния здоровья и координации лечения",
                
                # Agent reasoning
                "clinical_significance": "Клиническое значение аномальных показателей:",
                "interconnections": "Потенциальные взаимосвязи между аномальными показателями:",
                "urgency_level": "Уровень срочности для медицинской консультации:",
                "patterns_suggest": "Конкретные состояния, предполагаемые паттернами:",
                "high_priority": "Высокий приоритет",
                "medium_priority": "Средний приоритет",
                "low_priority": "Низкий приоритет", 
                "immediate_consultation": "Рекомендуется немедленная консультация с {specialist} по причине {reason}",
                
                # Next steps
                "schedule_urgent_consultation": "Запланируйте срочную консультацию с рекомендованными специалистами по поводу повышенных показателей",
                "consider_liver_function": "Рассмотрите проведение панели функций печени и УЗИ брюшной полости",
                "monitor_glucose": "Контролируйте уровень глюкозы в крови и рассмотрите тестирование HbA1c",
                "follow_up_primary": "Обратитесь к своему лечащему врачу для обсуждения этих результатов",
                "bring_previous_results": "Принесите все предыдущие результаты анализов на консультации к специалистам",
                "routine_monitoring": "Продолжайте регулярный мониторинг показателей здоровья",
                "healthy_lifestyle": "Поддерживайте здоровое питание и режим физических упражнений",
                "regular_checkups": "Продолжайте регулярные осмотры у своего лечащего врача",
                
                # Actions and booking
                "auto_booked_appointment": "Автоматически забронирован срочный приём (ID: {appointment_id})",
                "booking_attempted": "Попытка автоматического бронирования: {message}",
                "no_available_doctors": "Не найдено доступных врачей специальности {specialist}",
                "earliest_appointment": "Ближайший доступный приём к врачу {doctor_name} возможен {datetime}. Пожалуйста, забронируйте вручную, если подходит.",
                "successfully_booked": "Успешно забронирован приём к врачу {doctor_name} на {datetime}",
                "booking_error": "Произошла ошибка при бронировании приёма: {error}",
                "no_appropriate_specialist": "Не определен подходящий специалист для автоматического бронирования",
                "urgent_consultation_required": "Необходима срочная консультация из-за критических показателей здоровья: {metrics}",
                "auto_booking_failed": "Автоматическое бронирование не удалось из-за ошибки: {error}",
                "automated_analysis_detected": "Обнаружена автоматическая аналитика {metrics} критических показателей, требующих {priority} приоритета внимания",
                "no_health_metrics_found": "В анализе не найдено показателей здоровья",
                "upload_medical_report": "Загрузите медицинский отчёт с показателями здоровья для анализа",
                "no_actions_taken": "Действий не выполнено - не найдено показателей",
                
                # Analysis summary
                "total_metrics": "Всего проанализировано показателей",
                "abnormal_metrics": "Найдено аномальных показателей",
                "critical_metrics": "Критических показателей, требующих внимания",
                "priority_level": "Общий уровень приоритета",
                "no_metrics_found": "В анализе не найдено показателей здоровья",
                "all_normal": "Все значения находятся в пределах нормальных референтных диапазонов",
                "continue_monitoring": "Продолжайте регулярный мониторинг здоровья и поддерживайте здоровый образ жизни",
                
                # Error messages
                "analysis_not_found": "Анализ здоровья не найден или нет доступа",
                "patient_not_found": "Пациент не найден",
                "unable_to_analyze": "Невозможно завершить интеллектуальный анализ. Пожалуйста, попробуйте позже.",
                "doctor_not_available": "Врач не найден или недоступен",
                "time_slot_conflict": "Конфликт временного слота для запрашиваемого времени приёма",
                
                # Notifications
                "critical_alert": "Важное уведомление о здоровье - Обнаружены критические значения",
                "appointment_confirmation": "Подтверждение приёма - AI Health Tracker",
                "analysis_complete": "Анализ здоровья завершён - {count} рекомендаций"
            }
        }
    
    def get_text(self, key: str, language: Language = Language.RUSSIAN, **kwargs) -> str:
        """Get localized text by key with optional formatting parameters."""
        try:
            lang_dict = self.translations.get(language.value, self.translations["en"])
            text = lang_dict.get(key, self.translations["en"].get(key, key))
            
            if kwargs:
                return text.format(**kwargs)
            return text
            
        except Exception as e:
            logger.error(f"Error getting localized text for key '{key}': {e}")
            return key
    
    def get_specialist_info(self, specialist_type: str, language: Language = Language.RUSSIAN) -> Dict[str, str]:
        """Get complete specialist information (name, description, when to consult)."""
        specialist_key = specialist_type.lower().replace(" ", "_")
        
        return {
            "type": self.get_text(specialist_key, language),
            "description": self.get_text(f"{specialist_key}_desc", language),
            "when_to_consult": self.get_text(f"{specialist_key}_when", language)
        }
    
    def get_priority_text(self, priority: str, language: Language = Language.RUSSIAN) -> str:
        """Get localized priority level text."""
        priority_key = f"{priority.lower()}_priority"
        return self.get_text(priority_key, language)
    
    def get_recommendation_reason(self, condition_type: str, metrics: List[str], language: Language = Language.RUSSIAN) -> str:
        """Get localized recommendation reason based on condition type."""
        metrics_str = ", ".join(metrics)
        
        condition_map = {
            "glucose": "glucose_abnormality",
            "liver": "liver_enzymes_elevated", 
            "kidney": "kidney_function_abnormal",
            "blood": "blood_count_abnormal",
            "cholesterol": "cholesterol_abnormal"
        }
        
        key = condition_map.get(condition_type, "glucose_abnormality")
        return self.get_text(key, language, metrics=metrics_str)

# Global instance
localization_service = LocalizationService() 