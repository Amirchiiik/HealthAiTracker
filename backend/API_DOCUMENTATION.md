# AI Health Tracker - Individual Metric Explanations API

## Overview
The AI Health Tracker now provides individual explanations for each health metric detected in medical reports, offering users clear, metric-specific insights.

## New Endpoints

### 1. Enhanced OCR with Individual Explanations
**GET** `/ocr/{filename}/with-explanations`

Process an uploaded medical document and return individual explanations for each detected metric.

**Response:**
```json
{
  "filename": "medical_report.pdf",
  "extracted_text": "Raw OCR text...",
  "metrics": [
    {
      "name": "Гемоглобин",
      "value": 140.0,
      "unit": "г/л",
      "reference_range": "120-160",
      "status": "normal",
      "explanation": "Ваш уровень гемоглобина 140.0 г/л находится в пределах нормы (120-160 г/л). Это указывает на здоровую способность крови переносить кислород."
    }
  ],
  "overall_summary": "3 показателей проанализировано. 2 в норме. 1 требуют внимания.",
  "analysis": {
    "valid": true,
    "validation_message": "Valid medical document detected"
  }
}
```

### 2. Analyze Text with Individual Explanations
**POST** `/explain/metrics`

Analyze raw text containing health metrics and return individual explanations.

**Request:**
```json
{
  "raw_text": "Гемоглобин: 140 г/л (норма: 120-160)\nГлюкоза: 110 мг/дл (норма: 70-99)"
}
```

**Response:**
```json
{
  "metrics": [
    {
      "name": "Гемоглобин", 
      "value": 140.0,
      "unit": "г/л",
      "reference_range": "120-160",
      "status": "normal",
      "explanation": "Individual explanation for this metric..."
    }
  ],
  "overall_summary": "Analysis summary...",
  "analysis": {
    "valid": true,
    "metrics": [...],
    "validation_message": "Valid medical data"
  },
  "processing": false
}
```

### 3. Advanced Analysis Endpoints

#### Analyze Text with Explanations
**POST** `/analysis/text`

```json
{
  "raw_text": "Medical report text..."
}
```

#### Explain Individual Metrics
**POST** `/analysis/metrics/explain`

```json
{
  "metrics": [
    {
      "name": "Glucose",
      "value": 110,
      "unit": "mg/dL",
      "reference_range": "70-99", 
      "status": "elevated"
    }
  ]
}
```

#### Generate Metrics Summary
**POST** `/analysis/summary`

Returns grouped metrics by status with counts and recommendations.

## Metric Status Values

- **normal**: Value within reference range
- **low**: Value below reference range  
- **high**: Value above reference range
- **elevated**: Value approaching upper limit

## Individual Explanation Features

### 1. Metric-Specific Context
Each explanation is tailored to the specific health metric:
- What the metric measures
- Whether the value is normal or abnormal
- Possible causes for abnormal values
- Recommended actions

### 2. Status-Based Explanations
Explanations vary based on the metric status:
- **Normal**: Reassurance and explanation of healthy values
- **Abnormal**: Possible causes and recommended actions

### 3. Fallback Explanations
If AI-generated explanations fail, the system provides simple fallback explanations based on the metric status.

## Backward Compatibility

All existing endpoints remain functional:
- **GET** `/ocr/{filename}` - Original OCR without explanations
- **POST** `/explain` - Original general explanation endpoint

## Example Usage

### Get Individual Explanations for Uploaded File
```bash
curl -X GET "http://localhost:8000/ocr/report.pdf/with-explanations"
```

### Analyze Text with Individual Explanations
```bash
curl -X POST "http://localhost:8000/explain/metrics" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "Гемоглобин: 140 г/л (норма: 120-160)"}'
```

### Explain Specific Metrics
```bash
curl -X POST "http://localhost:8000/analysis/metrics/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {
        "name": "Glucose",
        "value": 110,
        "unit": "mg/dL",
        "reference_range": "70-99",
        "status": "elevated"
      }
    ]
  }'
```

## Performance Considerations

- Individual explanations are cached to improve performance
- Parallel processing for multiple metrics
- Fallback explanations when API calls fail or timeout
- Shorter timeouts for individual metric explanations (15s vs 30s)

## Error Handling

The system gracefully handles various error scenarios:
- API timeouts → Fallback explanations
- Invalid metrics → Skipped with error logging
- Empty text → Appropriate error messages
- File not found → 404 errors

This enhanced system provides users with clear, actionable insights for each health metric while maintaining all existing functionality. 