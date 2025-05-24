"""
Doctor Recommendation Service - AI Agent for Medical Specialist Recommendations

This service analyzes health metrics from OCR analysis and recommends appropriate
medical specialists based on detected abnormalities and medical conditions.

IMPORTANT: This service provides recommendations only and does not diagnose.
All recommendations include disclaimers directing users to consult licensed physicians.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DoctorRecommendationService:
    """
    Intelligent agent that maps health metric abnormalities to medical specialist recommendations.
    """
    
    def __init__(self):
        """Initialize the recommendation service with medical knowledge bases."""
        self.metric_condition_map = self._build_metric_condition_map()
        self.condition_specialist_map = self._build_condition_specialist_map()
        self.specialist_info = self._build_specialist_info()
    
    def analyze_and_recommend(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main method to analyze health metrics and generate specialist recommendations.
        
        Args:
            metrics: List of health metric dictionaries from OCR analysis
            
        Returns:
            Dict containing recommended specialists, reasons, and next steps
        """
        try:
            # Filter abnormal metrics
            abnormal_metrics = self._filter_abnormal_metrics(metrics)
            
            if not abnormal_metrics:
                return self._generate_normal_response()
            
            # Map metrics to conditions
            conditions = self._map_metrics_to_conditions(abnormal_metrics)
            
            # Map conditions to specialists
            specialist_recommendations = self._map_conditions_to_specialists(conditions, abnormal_metrics)
            
            # Generate next steps
            next_steps = self._generate_next_steps(conditions, specialist_recommendations)
            
            # Build final response
            return self._build_recommendation_response(
                specialist_recommendations, 
                next_steps, 
                abnormal_metrics
            )
            
        except Exception as e:
            logger.error(f"Error in doctor recommendation analysis: {e}")
            return self._generate_error_response()
    
    def _filter_abnormal_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter metrics to only include abnormal values."""
        abnormal_statuses = ['high', 'low', 'elevated', 'decreased', 'positive', 'detected']
        
        abnormal_metrics = []
        for metric in metrics:
            status = metric.get('status', '').lower()
            if status in abnormal_statuses:
                abnormal_metrics.append(metric)
        
        logger.info(f"Found {len(abnormal_metrics)} abnormal metrics out of {len(metrics)} total")
        return abnormal_metrics
    
    def _map_metrics_to_conditions(self, abnormal_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map abnormal metrics to potential medical conditions."""
        conditions = []
        
        for metric in abnormal_metrics:
            metric_name = metric.get('name', '').lower()
            status = metric.get('status', '').lower()
            value = metric.get('value', 0)
            
            # Find matching conditions for this metric
            for pattern, condition_info in self.metric_condition_map.items():
                if self._matches_metric_pattern(metric_name, pattern):
                    condition = condition_info.copy()
                    condition['triggering_metrics'] = [metric]
                    condition['severity'] = self._assess_severity(metric, condition_info)
                    conditions.append(condition)
        
        # Merge related conditions
        return self._merge_related_conditions(conditions)
    
    def _map_conditions_to_specialists(self, conditions: List[Dict[str, Any]], metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map medical conditions to specialist recommendations."""
        recommendations = []
        
        for condition in conditions:
            condition_type = condition['type']
            
            if condition_type in self.condition_specialist_map:
                specialist_types = self.condition_specialist_map[condition_type]
                
                for specialist_type in specialist_types:
                    if specialist_type in self.specialist_info:
                        specialist_info = self.specialist_info[specialist_type]
                        
                        recommendation = {
                            'type': specialist_type,
                            'reason': self._generate_recommendation_reason(condition, metrics),
                            'priority': condition.get('severity', 'medium'),
                            'metrics_involved': [m['name'] for m in condition.get('triggering_metrics', [])],
                            'description': specialist_info.get('description', ''),
                            'when_to_consult': specialist_info.get('when_to_consult', '')
                        }
                        recommendations.append(recommendation)
        
        # Remove duplicates and prioritize
        return self._deduplicate_and_prioritize(recommendations)
    
    def _generate_next_steps(self, conditions: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable next steps based on conditions and recommendations."""
        steps = []
        
        # High priority conditions first
        high_priority = [c for c in conditions if c.get('severity') == 'high']
        if high_priority:
            steps.append("Schedule urgent consultation with recommended specialists for elevated values")
        
        # Specific recommendations based on specialist types
        specialist_types = [r['type'] for r in recommendations]
        
        if 'Gastroenterologist' in specialist_types:
            steps.append("Consider liver function panel and abdominal ultrasound")
        
        if 'Endocrinologist' in specialist_types:
            steps.append("Monitor blood glucose levels and consider HbA1c testing")
        
        if 'Cardiologist' in specialist_types:
            steps.append("Evaluate cardiovascular risk factors and consider ECG")
        
        if 'Hematologist' in specialist_types:
            steps.append("Complete blood count with differential and iron studies may be needed")
        
        # General recommendations
        steps.extend([
            "Follow up with your primary care physician to discuss these results",
            "Bring all previous lab results to specialist consultations",
            "Consider lifestyle modifications as recommended by specialists"
        ])
        
        return steps[:5]  # Limit to top 5 most relevant steps
    
    def _build_recommendation_response(self, recommendations: List[Dict[str, Any]], 
                                     next_steps: List[str], 
                                     abnormal_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build the final recommendation response."""
        return {
            'recommended_specialists': recommendations,
            'next_steps': next_steps,
            'abnormal_metrics_count': len(abnormal_metrics),
            'priority_level': self._determine_overall_priority(recommendations),
            'disclaimer': (
                "This is not a medical diagnosis. These recommendations are based on "
                "laboratory value patterns and should not replace professional medical "
                "evaluation. Please consult a licensed physician for proper diagnosis "
                "and treatment planning."
            ),
            'emergency_note': (
                "If you experience severe symptoms or feel unwell, seek immediate "
                "medical attention regardless of these recommendations."
            )
        }
    
    def _build_metric_condition_map(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive mapping from health metrics to medical conditions."""
        return {
            # Liver Function Tests
            'alt': {
                'type': 'liver_function',
                'condition_name': 'Elevated Liver Enzymes',
                'description': 'May indicate liver stress, hepatitis, or liver damage',
                'base_severity': 'medium'
            },
            'ast': {
                'type': 'liver_function',
                'condition_name': 'Elevated Liver Enzymes',
                'description': 'May indicate liver or muscle damage',
                'base_severity': 'medium'
            },
            'alp': {
                'type': 'liver_function',
                'condition_name': 'Elevated Alkaline Phosphatase',
                'description': 'May indicate liver or bone disorders',
                'base_severity': 'medium'
            },
            'ggt': {
                'type': 'liver_function',
                'condition_name': 'Elevated Gamma-GT',
                'description': 'May indicate liver dysfunction or bile duct issues',
                'base_severity': 'medium'
            },
            'total_bilirubin': {
                'type': 'liver_function',
                'condition_name': 'Elevated Bilirubin',
                'description': 'May indicate liver dysfunction or hemolysis',
                'base_severity': 'medium'
            },
            
            # Metabolic/Endocrine
            'glucose': {
                'type': 'metabolic',
                'condition_name': 'Glucose Abnormality',
                'description': 'May indicate diabetes or metabolic dysfunction',
                'base_severity': 'high'
            },
            'glycated_hemoglobin': {
                'type': 'metabolic',
                'condition_name': 'Elevated HbA1c',
                'description': 'May indicate poor long-term glucose control',
                'base_severity': 'high'
            },
            
            # Lipid Panel
            'total_cholesterol': {
                'type': 'lipid',
                'condition_name': 'Cholesterol Abnormality',
                'description': 'May indicate cardiovascular risk',
                'base_severity': 'medium'
            },
            'ldl_cholesterol': {
                'type': 'lipid',
                'condition_name': 'Elevated LDL Cholesterol',
                'description': 'May indicate increased cardiovascular risk',
                'base_severity': 'medium'
            },
            'hdl_cholesterol': {
                'type': 'lipid',
                'condition_name': 'HDL Cholesterol Abnormality',
                'description': 'May affect cardiovascular protection',
                'base_severity': 'medium'
            },
            'triglycerides': {
                'type': 'lipid',
                'condition_name': 'Elevated Triglycerides',
                'description': 'May indicate metabolic syndrome or cardiovascular risk',
                'base_severity': 'medium'
            },
            
            # Kidney Function
            'creatinine': {
                'type': 'kidney_function',
                'condition_name': 'Creatinine Abnormality',
                'description': 'May indicate kidney dysfunction',
                'base_severity': 'high'
            },
            'urea': {
                'type': 'kidney_function',
                'condition_name': 'Elevated Urea',
                'description': 'May indicate kidney dysfunction or dehydration',
                'base_severity': 'medium'
            },
            
            # Blood Count
            'hemoglobin': {
                'type': 'blood_count',
                'condition_name': 'Hemoglobin Abnormality',
                'description': 'May indicate anemia or polycythemia',
                'base_severity': 'medium'
            },
            'white_blood_cells': {
                'type': 'blood_count',
                'condition_name': 'White Blood Cell Abnormality',
                'description': 'May indicate infection, inflammation, or blood disorder',
                'base_severity': 'medium'
            },
            'platelets': {
                'type': 'blood_count',
                'condition_name': 'Platelet Abnormality',
                'description': 'May indicate bleeding or clotting disorders',
                'base_severity': 'high'
            },
            
            # Thyroid Function
            'thyroid_stimulating_hormone': {
                'type': 'thyroid',
                'condition_name': 'Thyroid Dysfunction',
                'description': 'May indicate hyperthyroidism or hypothyroidism',
                'base_severity': 'medium'
            },
            'free_t3': {
                'type': 'thyroid',
                'condition_name': 'Thyroid Hormone Abnormality',
                'description': 'May indicate thyroid dysfunction',
                'base_severity': 'medium'
            },
            'free_t4': {
                'type': 'thyroid',
                'condition_name': 'Thyroid Hormone Abnormality',
                'description': 'May indicate thyroid dysfunction',
                'base_severity': 'medium'
            },
            
            # Inflammatory Markers
            'c_reactive_protein': {
                'type': 'inflammation',
                'condition_name': 'Elevated Inflammatory Markers',
                'description': 'May indicate inflammation or infection',
                'base_severity': 'medium'
            },
            
            # Coagulation
            'international_normalized_ratio': {
                'type': 'coagulation',
                'condition_name': 'Coagulation Abnormality',
                'description': 'May indicate bleeding or clotting disorders',
                'base_severity': 'high'
            },
            
            # Infectious Disease Markers
            'hepatitis_c_antibodies': {
                'type': 'infectious_disease',
                'condition_name': 'Hepatitis C Exposure',
                'description': 'May indicate past or current hepatitis C infection',
                'base_severity': 'high'
            },
            'hepatitis_b_surface_antigen': {
                'type': 'infectious_disease',
                'condition_name': 'Hepatitis B Infection',
                'description': 'May indicate active hepatitis B infection',
                'base_severity': 'high'
            }
        }
    
    def _build_condition_specialist_map(self) -> Dict[str, List[str]]:
        """Map medical conditions to appropriate specialists."""
        return {
            'liver_function': ['Gastroenterologist', 'Hepatologist'],
            'metabolic': ['Endocrinologist', 'Internal Medicine'],
            'lipid': ['Cardiologist', 'Endocrinologist'],
            'kidney_function': ['Nephrologist', 'Internal Medicine'],
            'blood_count': ['Hematologist', 'Internal Medicine'],
            'thyroid': ['Endocrinologist'],
            'inflammation': ['Internal Medicine', 'Rheumatologist'],
            'coagulation': ['Hematologist'],
            'infectious_disease': ['Infectious Disease Specialist', 'Gastroenterologist']
        }
    
    def _build_specialist_info(self) -> Dict[str, Dict[str, str]]:
        """Build information about medical specialists."""
        return {
            'Gastroenterologist': {
                'description': 'Specialist in digestive system and liver disorders',
                'when_to_consult': 'For liver enzyme abnormalities, digestive issues, or abdominal symptoms'
            },
            'Hepatologist': {
                'description': 'Specialist specifically focused on liver diseases',
                'when_to_consult': 'For complex liver enzyme abnormalities or suspected liver disease'
            },
            'Endocrinologist': {
                'description': 'Specialist in hormones, metabolism, and endocrine disorders',
                'when_to_consult': 'For diabetes, thyroid disorders, or metabolic abnormalities'
            },
            'Cardiologist': {
                'description': 'Specialist in heart and cardiovascular system',
                'when_to_consult': 'For cholesterol abnormalities or cardiovascular risk factors'
            },
            'Nephrologist': {
                'description': 'Specialist in kidney diseases and disorders',
                'when_to_consult': 'For kidney function abnormalities or suspected kidney disease'
            },
            'Hematologist': {
                'description': 'Specialist in blood disorders and diseases',
                'when_to_consult': 'For blood count abnormalities or bleeding/clotting disorders'
            },
            'Internal Medicine': {
                'description': 'General internal medicine physician',
                'when_to_consult': 'For overall health assessment and coordination of care'
            },
            'Rheumatologist': {
                'description': 'Specialist in autoimmune and inflammatory diseases',
                'when_to_consult': 'For elevated inflammatory markers or suspected autoimmune conditions'
            },
            'Infectious Disease Specialist': {
                'description': 'Specialist in infectious diseases and infections',
                'when_to_consult': 'For suspected infections or positive infectious disease markers'
            }
        }
    
    def _matches_metric_pattern(self, metric_name: str, pattern: str) -> bool:
        """Check if a metric name matches a condition pattern."""
        metric_name = metric_name.lower().replace('_', ' ')
        pattern = pattern.lower().replace('_', ' ')
        
        # Direct match
        if pattern in metric_name or metric_name in pattern:
            return True
        
        # Common aliases
        aliases = {
            'alt': ['alanine aminotransferase', 'alat'],
            'ast': ['aspartate aminotransferase', 'asat'],
            'alp': ['alkaline phosphatase'],
            'ggt': ['gamma glutamyl transferase', 'ggtp'],
            'glucose': ['blood glucose', 'sugar'],
            'total cholesterol': ['cholesterol'],
            'ldl cholesterol': ['ldl', 'low density lipoprotein'],
            'hdl cholesterol': ['hdl', 'high density lipoprotein'],
            'creatinine': ['serum creatinine'],
            'hemoglobin': ['hgb', 'hb'],
            'white blood cells': ['wbc', 'leukocytes'],
            'platelets': ['plt', 'thrombocytes'],
            'thyroid stimulating hormone': ['tsh'],
            'c reactive protein': ['crp'],
            'international normalized ratio': ['inr']
        }
        
        if pattern in aliases:
            return any(alias in metric_name for alias in aliases[pattern])
        
        return False
    
    def _assess_severity(self, metric: Dict[str, Any], condition_info: Dict[str, Any]) -> str:
        """Assess the severity of an abnormal metric."""
        base_severity = condition_info.get('base_severity', 'medium')
        status = metric.get('status', '').lower()
        value = metric.get('value', 0)
        
        # High severity conditions
        if status in ['high', 'elevated'] and base_severity == 'high':
            return 'high'
        
        # Special cases for very abnormal values
        metric_name = metric.get('name', '').lower()
        if 'glucose' in metric_name and value > 11.0:  # Very high glucose
            return 'high'
        if 'creatinine' in metric_name and status == 'high':
            return 'high'
        if 'hepatitis' in metric_name and status in ['positive', 'detected']:
            return 'high'
        
        return base_severity
    
    def _merge_related_conditions(self, conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge related conditions to avoid redundancy."""
        merged = {}
        
        for condition in conditions:
            condition_type = condition['type']
            
            if condition_type in merged:
                # Merge triggering metrics
                existing_metrics = merged[condition_type].get('triggering_metrics', [])
                new_metrics = condition.get('triggering_metrics', [])
                merged[condition_type]['triggering_metrics'] = existing_metrics + new_metrics
                
                # Update severity to highest
                current_severity = merged[condition_type].get('severity', 'low')
                new_severity = condition.get('severity', 'low')
                severity_order = {'low': 1, 'medium': 2, 'high': 3}
                if severity_order.get(new_severity, 0) > severity_order.get(current_severity, 0):
                    merged[condition_type]['severity'] = new_severity
            else:
                merged[condition_type] = condition
        
        return list(merged.values())
    
    def _generate_recommendation_reason(self, condition: Dict[str, Any], metrics: List[Dict[str, Any]]) -> str:
        """Generate a detailed reason for specialist recommendation."""
        condition_name = condition.get('condition_name', 'abnormal values')
        triggering_metrics = condition.get('triggering_metrics', [])
        
        if not triggering_metrics:
            return f"{condition_name} detected in laboratory results."
        
        metric_details = []
        for metric in triggering_metrics:
            name = metric.get('name', 'Unknown')
            value = metric.get('value', 'N/A')
            unit = metric.get('unit', '')
            status = metric.get('status', 'abnormal')
            
            detail = f"{name}: {value} {unit} ({status})"
            metric_details.append(detail)
        
        metrics_text = ", ".join(metric_details)
        return f"{condition_name} detected: {metrics_text}. {condition.get('description', '')}"
    
    def _deduplicate_and_prioritize(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate specialists and prioritize by importance."""
        seen_specialists = set()
        unique_recommendations = []
        
        # Sort by priority first
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_recommendations = sorted(
            recommendations, 
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 2),
            reverse=True
        )
        
        for rec in sorted_recommendations:
            specialist_type = rec['type']
            if specialist_type not in seen_specialists:
                seen_specialists.add(specialist_type)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:4]  # Limit to top 4 specialists
    
    def _determine_overall_priority(self, recommendations: List[Dict[str, Any]]) -> str:
        """Determine overall priority level based on recommendations."""
        if any(r.get('priority') == 'high' for r in recommendations):
            return 'high'
        elif any(r.get('priority') == 'medium' for r in recommendations):
            return 'medium'
        else:
            return 'low'
    
    def _generate_normal_response(self) -> Dict[str, Any]:
        """Generate response when all metrics are normal."""
        return {
            'recommended_specialists': [],
            'next_steps': [
                "All laboratory values appear to be within normal ranges",
                "Continue regular check-ups with your primary care physician",
                "Maintain healthy lifestyle habits"
            ],
            'abnormal_metrics_count': 0,
            'priority_level': 'low',
            'disclaimer': (
                "While your current laboratory values appear normal, this analysis "
                "is not a substitute for professional medical interpretation. "
                "Please discuss these results with your healthcare provider."
            ),
            'emergency_note': (
                "If you experience any concerning symptoms, seek medical attention "
                "regardless of laboratory results."
            )
        }
    
    def _generate_error_response(self) -> Dict[str, Any]:
        """Generate response when an error occurs."""
        return {
            'recommended_specialists': [],
            'next_steps': [
                "Unable to analyze laboratory results due to technical error",
                "Please consult your healthcare provider for result interpretation"
            ],
            'abnormal_metrics_count': 0,
            'priority_level': 'medium',
            'disclaimer': (
                "Technical error occurred during analysis. Please consult a "
                "healthcare professional for proper interpretation of your results."
            ),
            'emergency_note': (
                "If you have any health concerns, please contact your healthcare "
                "provider immediately."
            )
        }


# Global service instance
doctor_recommendation_service = DoctorRecommendationService() 