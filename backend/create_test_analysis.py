#!/usr/bin/env python3
"""
Script to create a test health analysis for testing the intelligent agent
"""

from app.database import get_db
from app.models import HealthAnalysis
from sqlalchemy.orm import Session
import json

# Test metrics with critical values
test_metrics = [
    {
        "name": "Glucose",
        "value": 66.19,
        "unit": "mmol/L",
        "reference_range": "3.9 - 6.1",
        "status": "high"
    },
    {
        "name": "ALT",
        "value": 150,
        "unit": "U/L", 
        "reference_range": "3 - 45",
        "status": "high"
    },
    {
        "name": "GGT",
        "value": 200,
        "unit": "U/L",
        "reference_range": "5 - 55",
        "status": "high"
    }
]

def create_test_analysis():
    """Create a test health analysis for user ID 10"""
    db = next(get_db())
    
    try:
        # Create health analysis
        health_analysis = HealthAnalysis(
            user_id=10,  # The test patient we created
            filename="test_critical_results.txt",
            extracted_text="Glucose: 66.19 mmol/L (High), ALT: 150 U/L (High), GGT: 200 U/L (High)",
            metrics=test_metrics,
            overall_summary="Critical glucose and liver enzyme levels detected",
            analysis_data={
                "total_metrics": 3,
                "abnormal_metrics": 3,
                "critical_metrics": 3,
                "analysis_type": "critical_health_metrics"
            }
        )
        
        db.add(health_analysis)
        db.commit()
        db.refresh(health_analysis)
        
        print(f"✅ Created test health analysis with ID: {health_analysis.id}")
        print(f"   User ID: {health_analysis.user_id}")
        print(f"   Metrics: {len(health_analysis.metrics)} critical values")
        print(f"   Summary: {health_analysis.overall_summary}")
        
        return health_analysis.id
        
    except Exception as e:
        print(f"❌ Error creating test analysis: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 Creating test health analysis...")
    analysis_id = create_test_analysis()
    
    if analysis_id:
        print(f"\n🎯 Test analysis created successfully!")
        print(f"   Analysis ID: {analysis_id}")
        print(f"\n💡 Now you can test the intelligent agent with:")
        print(f"   POST /agent/analyze-and-act")
        print(f"   {{\"health_analysis_id\": {analysis_id}, \"language\": \"ru\"}}") 