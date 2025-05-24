import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.schemas import (
    MetricInput, DiseaseRisk, RiskFactor, DiseasePredictionCreate, 
    DiseasePredictionResponse, RiskLevel
)

logger = logging.getLogger(__name__)

class DiseasePredictionService:
    """
    Service for predicting disease risks based on health metrics.
    Uses rule-based algorithms with medical knowledge base.
    """
    
    def __init__(self):
        self.medical_disclaimer = (
            "IMPORTANT MEDICAL DISCLAIMER: This AI-generated prediction is for informational "
            "purposes only and should not be used as a substitute for professional medical "
            "advice, diagnosis, or treatment. Always seek the advice of your physician or "
            "other qualified health provider with any questions you may have regarding a "
            "medical condition. Never disregard professional medical advice or delay seeking "
            "it because of information provided by this AI system. In case of emergency, "
            "contact emergency services immediately."
        )
        
        # Disease knowledge base with normal ranges and thresholds
        self.disease_definitions = {
            "anemia": {
                "description": "A condition where you lack enough healthy red blood cells or hemoglobin",
                "primary_indicators": ["hemoglobin", "hematocrit", "rbc_count"],
                "secondary_indicators": ["mcv", "mch", "iron", "ferritin"],
                "thresholds": {
                    "hemoglobin": {
                        "normal_min": {"male": 13.8, "female": 12.1, "general": 12.0},
                        "mild_anemia": {"male": 11.0, "female": 10.0, "general": 10.5},
                        "moderate_anemia": {"male": 8.0, "female": 8.0, "general": 8.0},
                        "severe_anemia": {"male": 6.5, "female": 6.5, "general": 6.5}
                    },
                    "hematocrit": {
                        "normal_min": {"male": 40.7, "female": 36.1, "general": 36.0},
                        "mild_anemia": {"male": 30.0, "female": 30.0, "general": 30.0}
                    }
                },
                "symptoms": ["fatigue", "weakness", "pale skin", "shortness of breath", "dizziness"]
            },
            "diabetes": {
                "description": "A group of metabolic disorders characterized by high blood sugar",
                "primary_indicators": ["glucose", "fasting_glucose", "hba1c"],
                "secondary_indicators": ["random_glucose", "glucose_tolerance"],
                "thresholds": {
                    "glucose": {
                        "normal_max": 99,
                        "prediabetic": 125,
                        "diabetic": 126
                    },
                    "fasting_glucose": {
                        "normal_max": 99,
                        "prediabetic": 125,
                        "diabetic": 126
                    },
                    "hba1c": {
                        "normal_max": 5.6,
                        "prediabetic": 6.4,
                        "diabetic": 6.5
                    }
                },
                "symptoms": ["increased thirst", "frequent urination", "unexplained weight loss", "fatigue", "blurred vision"]
            },
            "liver_dysfunction": {
                "description": "Impaired liver function affecting metabolism and detoxification",
                "primary_indicators": ["alt", "ast", "bilirubin"],
                "secondary_indicators": ["alkaline_phosphatase", "albumin", "ggt"],
                "thresholds": {
                    "alt": {
                        "normal_max": 40,
                        "mild_elevation": 80,
                        "moderate_elevation": 200,
                        "severe_elevation": 400
                    },
                    "ast": {
                        "normal_max": 40,
                        "mild_elevation": 80,
                        "moderate_elevation": 200,
                        "severe_elevation": 400
                    },
                    "bilirubin": {
                        "normal_max": 1.2,
                        "mild_elevation": 2.0,
                        "moderate_elevation": 5.0,
                        "severe_elevation": 10.0
                    }
                },
                "symptoms": ["jaundice", "abdominal pain", "fatigue", "nausea", "dark urine"]
            },
            "kidney_disease": {
                "description": "Chronic kidney disease affecting filtration and waste removal",
                "primary_indicators": ["creatinine", "bun", "gfr"],
                "secondary_indicators": ["protein_urine", "albumin_urine", "urea"],
                "thresholds": {
                    "creatinine": {
                        "normal_max": {"male": 1.3, "female": 1.1, "general": 1.2},
                        "mild_elevation": 1.5,
                        "moderate_elevation": 3.0,
                        "severe_elevation": 5.0
                    },
                    "bun": {
                        "normal_max": 20,
                        "mild_elevation": 40,
                        "moderate_elevation": 80,
                        "severe_elevation": 100
                    },
                    "gfr": {
                        "normal_min": 90,
                        "mild_reduction": 60,
                        "moderate_reduction": 30,
                        "severe_reduction": 15
                    }
                },
                "symptoms": ["swelling", "fatigue", "decreased urination", "nausea", "shortness of breath"]
            },
            "thyroid_disorders": {
                "description": "Thyroid gland dysfunction affecting metabolism regulation",
                "primary_indicators": ["tsh", "t3", "t4"],
                "secondary_indicators": ["free_t4", "free_t3", "thyroid_antibodies"],
                "thresholds": {
                    "tsh": {
                        "normal_min": 0.4,
                        "normal_max": 4.0,
                        "mild_abnormal": 10.0,
                        "severe_abnormal": 20.0
                    },
                    "t4": {
                        "normal_min": 4.5,
                        "normal_max": 11.2
                    },
                    "t3": {
                        "normal_min": 3.1,
                        "normal_max": 6.8
                    }
                },
                "symptoms": ["weight changes", "fatigue", "temperature sensitivity", "mood changes", "heart palpitations"]
            },
            "cardiovascular_risk": {
                "description": "Increased risk of heart disease and stroke",
                "primary_indicators": ["total_cholesterol", "ldl_cholesterol", "hdl_cholesterol", "triglycerides"],
                "secondary_indicators": ["blood_pressure_systolic", "blood_pressure_diastolic"],
                "thresholds": {
                    "total_cholesterol": {
                        "desirable": 200,
                        "borderline": 239,
                        "high": 240
                    },
                    "ldl_cholesterol": {
                        "optimal": 100,
                        "near_optimal": 129,
                        "borderline": 159,
                        "high": 189,
                        "very_high": 190
                    },
                    "hdl_cholesterol": {
                        "low": 40,
                        "normal_min": 40,
                        "good": 60
                    },
                    "triglycerides": {
                        "normal": 150,
                        "borderline": 199,
                        "high": 499,
                        "very_high": 500
                    }
                },
                "symptoms": ["chest pain", "shortness of breath", "leg pain", "numbness", "fatigue"]
            }
        }
    
    def predict_diseases(self, metrics: List[MetricInput]) -> DiseasePredictionCreate:
        """
        Main method to predict diseases based on input metrics.
        
        Args:
            metrics: List of health metrics with values
            
        Returns:
            DiseasePredictionCreate object with predictions and recommendations
        """
        logger.info(f"Starting disease prediction for {len(metrics)} metrics")
        
        # Convert metrics to dictionary for easier processing
        metric_dict = {metric.name: metric for metric in metrics}
        
        # Analyze each disease
        disease_predictions = []
        all_risk_factors = []
        overall_risk_level = RiskLevel.LOW
        
        for disease_name, disease_info in self.disease_definitions.items():
            prediction = self._analyze_disease_risk(disease_name, disease_info, metric_dict)
            if prediction:
                disease_predictions.append(prediction)
                all_risk_factors.extend(prediction.contributing_factors)
                
                # Update overall risk level
                if prediction.risk_level == RiskLevel.HIGH:
                    overall_risk_level = RiskLevel.HIGH
                elif prediction.risk_level == RiskLevel.MODERATE and overall_risk_level != RiskLevel.HIGH:
                    overall_risk_level = RiskLevel.MODERATE
        
        # Generate recommendations
        recommendations = self._generate_recommendations(disease_predictions, overall_risk_level)
        
        # Create confidence scores dictionary
        confidence_scores = {pred.disease_name: pred.confidence for pred in disease_predictions}
        
        logger.info(f"Disease prediction completed. Found {len(disease_predictions)} potential risks")
        
        return DiseasePredictionCreate(
            predicted_diseases=disease_predictions,
            risk_factors=all_risk_factors,
            confidence_scores=confidence_scores,
            overall_risk_level=overall_risk_level,
            recommendations=recommendations,
            medical_disclaimer=self.medical_disclaimer
        )
    
    def _analyze_disease_risk(self, disease_name: str, disease_info: Dict, 
                            metric_dict: Dict[str, MetricInput]) -> Optional[DiseaseRisk]:
        """
        Analyze risk for a specific disease based on available metrics.
        
        Args:
            disease_name: Name of the disease to analyze
            disease_info: Disease definition and thresholds
            metric_dict: Dictionary of available metrics
            
        Returns:
            DiseaseRisk object or None if insufficient data
        """
        available_indicators = []
        risk_factors = []
        
        # Check primary indicators
        for indicator in disease_info["primary_indicators"]:
            if indicator in metric_dict:
                available_indicators.append(indicator)
        
        # Check secondary indicators
        for indicator in disease_info["secondary_indicators"]:
            if indicator in metric_dict:
                available_indicators.append(indicator)
        
        # Need at least one primary indicator for prediction
        primary_available = any(ind in metric_dict for ind in disease_info["primary_indicators"])
        if not primary_available:
            return None
        
        # Analyze each available indicator
        total_risk_score = 0.0
        max_risk_level = RiskLevel.LOW
        
        for indicator in available_indicators:
            metric = metric_dict[indicator]
            risk_factor, risk_score, risk_level = self._analyze_metric_risk(
                indicator, metric, disease_info["thresholds"].get(indicator, {})
            )
            
            if risk_factor:
                risk_factors.append(risk_factor)
                total_risk_score += risk_score
                
                # Update maximum risk level
                if risk_level == RiskLevel.HIGH:
                    max_risk_level = RiskLevel.HIGH
                elif risk_level == RiskLevel.MODERATE and max_risk_level != RiskLevel.HIGH:
                    max_risk_level = RiskLevel.MODERATE
        
        if not risk_factors:
            return None
        
        # Calculate confidence based on number of indicators and their weights
        confidence = min(0.95, (len(risk_factors) / len(disease_info["primary_indicators"])) * 0.8 + 
                        (total_risk_score / len(risk_factors)) * 0.2)
        
        return DiseaseRisk(
            disease_name=disease_name,
            risk_level=max_risk_level,
            confidence=round(confidence, 2),
            contributing_factors=risk_factors,
            description=disease_info["description"],
            symptoms_to_watch=disease_info["symptoms"]
        )
    
    def _analyze_metric_risk(self, metric_name: str, metric: MetricInput, 
                           thresholds: Dict) -> Tuple[Optional[RiskFactor], float, RiskLevel]:
        """
        Analyze risk for a specific metric based on thresholds.
        
        Args:
            metric_name: Name of the metric
            metric: Metric data
            thresholds: Disease-specific thresholds for this metric
            
        Returns:
            Tuple of (RiskFactor, risk_score, risk_level)
        """
        if not thresholds:
            return None, 0.0, RiskLevel.LOW
        
        value = metric.value
        risk_score = 0.0
        risk_level = RiskLevel.LOW
        deviation_severity = "normal"
        weight = 0.5  # Default weight
        
        # Handle different threshold patterns
        if "normal_max" in thresholds:
            normal_max = thresholds["normal_max"]
            if isinstance(normal_max, dict):
                normal_max = normal_max.get("general", normal_max.get("male", normal_max.get("female", 100)))
            
            if value > normal_max:
                if value > thresholds.get("severe_elevation", normal_max * 3):
                    risk_level = RiskLevel.HIGH
                    risk_score = 0.9
                    deviation_severity = "severe"
                    weight = 0.9
                elif value > thresholds.get("moderate_elevation", normal_max * 2):
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.7
                    deviation_severity = "moderate"
                    weight = 0.7
                elif value > thresholds.get("mild_elevation", normal_max * 1.5):
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.5
                    deviation_severity = "mild"
                    weight = 0.6
                else:
                    return None, 0.0, RiskLevel.LOW
        
        elif "normal_min" in thresholds:
            normal_min = thresholds["normal_min"]
            if isinstance(normal_min, dict):
                normal_min = normal_min.get("general", normal_min.get("male", normal_min.get("female", 0)))
            
            if value < normal_min:
                if value < thresholds.get("severe_reduction", normal_min * 0.5):
                    risk_level = RiskLevel.HIGH
                    risk_score = 0.9
                    deviation_severity = "severe"
                    weight = 0.9
                elif value < thresholds.get("moderate_reduction", normal_min * 0.7):
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.7
                    deviation_severity = "moderate"
                    weight = 0.7
                elif value < thresholds.get("mild_reduction", normal_min * 0.85):
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.5
                    deviation_severity = "mild"
                    weight = 0.6
                else:
                    return None, 0.0, RiskLevel.LOW
        
        elif "normal_min" in thresholds and "normal_max" in thresholds:
            # Range-based analysis (e.g., TSH)
            normal_min = thresholds["normal_min"]
            normal_max = thresholds["normal_max"]
            
            if value < normal_min or value > normal_max:
                deviation = max(abs(value - normal_min), abs(value - normal_max))
                range_size = normal_max - normal_min
                
                if deviation > range_size * 2:
                    risk_level = RiskLevel.HIGH
                    risk_score = 0.8
                    deviation_severity = "severe"
                    weight = 0.8
                elif deviation > range_size:
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.6
                    deviation_severity = "moderate"
                    weight = 0.7
                else:
                    risk_level = RiskLevel.MODERATE
                    risk_score = 0.4
                    deviation_severity = "mild"
                    weight = 0.5
            else:
                return None, 0.0, RiskLevel.LOW
        
        else:
            return None, 0.0, RiskLevel.LOW
        
        # Create normal range string
        normal_range = metric.reference_range or self._get_normal_range_string(thresholds)
        
        risk_factor = RiskFactor(
            metric_name=metric_name,
            metric_value=value,
            normal_range=normal_range,
            deviation_severity=deviation_severity,
            contribution_weight=weight
        )
        
        return risk_factor, risk_score, risk_level
    
    def _get_normal_range_string(self, thresholds: Dict) -> str:
        """Generate a normal range string from thresholds."""
        if "normal_min" in thresholds and "normal_max" in thresholds:
            min_val = thresholds["normal_min"]
            max_val = thresholds["normal_max"]
            if isinstance(min_val, dict):
                min_val = min_val.get("general", "varies")
            if isinstance(max_val, dict):
                max_val = max_val.get("general", "varies")
            return f"{min_val}-{max_val}"
        elif "normal_max" in thresholds:
            max_val = thresholds["normal_max"]
            if isinstance(max_val, dict):
                max_val = max_val.get("general", "varies")
            return f"<{max_val}"
        elif "normal_min" in thresholds:
            min_val = thresholds["normal_min"]
            if isinstance(min_val, dict):
                min_val = min_val.get("general", "varies")
            return f">{min_val}"
        return "varies"
    
    def _generate_recommendations(self, predictions: List[DiseaseRisk], 
                                overall_risk: RiskLevel) -> str:
        """
        Generate medical recommendations based on predictions.
        
        Args:
            predictions: List of disease risk predictions
            overall_risk: Overall risk level
            
        Returns:
            String with recommendations
        """
        recommendations = []
        
        if overall_risk == RiskLevel.HIGH:
            recommendations.append("🚨 HIGH RISK DETECTED: Seek immediate medical attention.")
            recommendations.append("Contact your healthcare provider as soon as possible.")
        elif overall_risk == RiskLevel.MODERATE:
            recommendations.append("⚠️ MODERATE RISK: Schedule an appointment with your healthcare provider.")
            recommendations.append("Discuss these results with a medical professional.")
        else:
            recommendations.append("✅ LOW RISK: Continue regular health monitoring.")
            recommendations.append("Maintain healthy lifestyle habits.")
        
        # Disease-specific recommendations
        disease_names = [pred.disease_name for pred in predictions if pred.risk_level != RiskLevel.LOW]
        
        if "diabetes" in disease_names:
            recommendations.append("• Monitor blood sugar levels regularly")
            recommendations.append("• Consider dietary modifications to manage glucose")
        
        if "anemia" in disease_names:
            recommendations.append("• Consider iron-rich foods or supplements")
            recommendations.append("• Evaluate for underlying causes of anemia")
        
        if "liver_dysfunction" in disease_names:
            recommendations.append("• Avoid alcohol and hepatotoxic medications")
            recommendations.append("• Consider liver function follow-up testing")
        
        if "kidney_disease" in disease_names:
            recommendations.append("• Monitor kidney function closely")
            recommendations.append("• Consider dietary protein and sodium restrictions")
        
        if "thyroid_disorders" in disease_names:
            recommendations.append("• Consider thyroid function evaluation")
            recommendations.append("• Monitor for thyroid-related symptoms")
        
        if "cardiovascular_risk" in disease_names:
            recommendations.append("• Consider cardiovascular risk assessment")
            recommendations.append("• Focus on heart-healthy lifestyle changes")
        
        recommendations.append("\n⚠️ IMPORTANT: These recommendations are informational only. Always consult with healthcare professionals for proper medical care.")
        
        return "\n".join(recommendations) 