# Training Manuals Assistant

## Overview

The Training Manuals Assistant is a Django app that uses Large Language Models (LLMs) to transform equipment operation and maintenance manuals into structured technician qualification requirements. This solves the challenge of manually reviewing hundreds of pages of technical documentation to determine what qualifications technicians need to safely operate and maintain equipment.

## Use Case

### The Challenge
When new equipment arrives at a facility, maintenance leaders must:
1. **Identify required skills** by manually reviewing extensive operation and maintenance manuals
2. **Determine qualification criteria** for different maintenance tasks based on technical complexity and safety requirements
3. **Create standardized qualification records** in the Enterprise Asset Management (EAM) system
4. **Ensure compliance** with safety regulations and manufacturer recommendations

### The Solution
This LLM-powered system automatically:
1. **Processes technical documentation** including operation manuals, maintenance manuals, and technical bulletins
2. **Extracts qualification requirements** including technical skills, certifications, safety protocols, and experience levels
3. **Generates structured qualification profiles** organized by equipment type and maintenance task
4. **Creates EAM-ready data** for integration with qualification management systems

## Features

### Document Processing
- **PDF Document Analysis**: Processes equipment manuals, operation guides, and technical documentation
- **EAM Integration**: Fetches documents directly from EAM document management system
- **Multi-source Input**: Supports both direct file upload and EAM document codes

### Qualification Extraction
- **Technical Skills Analysis**: Identifies required technical competencies (electrical, mechanical, hydraulic, etc.)
- **Certification Requirements**: Extracts manufacturer certifications, industry standards, and safety certifications
- **Safety Protocol Identification**: Captures safety procedures, PPE requirements, and training needs
- **Experience Level Assessment**: Determines minimum experience requirements for different tasks

### Structured Output
- **Equipment Qualification Profiles**: Comprehensive qualification requirements per equipment type
- **Maintenance Task Breakdown**: Task-specific skill and certification requirements
- **Safety Requirements**: Detailed safety protocols and PPE specifications
- **Certification Mapping**: Links between tasks and required certifications

## API Endpoints

### Process Training Manual
**POST** `/api/training-manuals/process-training-manual/`

Processes a training manual document to extract qualification requirements.

#### Request Parameters
- `document_code` (optional): EAM document code to fetch document from EAM system
- `training_manual_file` (optional): Direct file upload (PDF format)
- `create_qualifications_in_eam` (optional, boolean): Flag for future EAM integration

#### Response Format
```json
{
    "qualification_analysis": {
        "equipment_qualification_profiles": [...],
        "general_safety_requirements": [...],
        "general_certifications": [...]
    },
    "summary": {
        "total_equipment_profiles": 2,
        "total_general_safety_requirements": 5,
        "total_general_certifications": 3,
        "equipment_types": ["Centrifugal Pump Model CP-500", "Motor Control Center"]
    }
}
```

## Data Schemas

### Equipment Qualification Profile
```python
{
    "equipment_type": "Centrifugal Pump Model CP-500",
    "equipment_manufacturer": "ABC Industrial",
    "qualification_profile_code": "QUAL-CP500-001",
    "profile_description": "Qualification requirements for CP-500 pumps",
    "minimum_experience_years": 2,
    "maintenance_tasks": [...]
}
```

### Technical Skill
```python
{
    "skill_code": "SKILL-MECH-001",
    "skill_name": "Mechanical Assembly",
    "skill_category": "Mechanical",
    "skill_level": "Intermediate",
    "description": "Ability to disassemble and reassemble pump components",
    "tools_required": ["Torque wrench", "Bearing puller", "Dial indicator"]
}
```

### Required Certification
```python
{
    "certification_code": "CERT-ABC-001",
    "certification_name": "ABC Pump Technician Certification",
    "certification_type": "Manufacturer Certification",
    "issuing_authority": "ABC Industrial Training Center",
    "renewal_period": 24,
    "is_mandatory": true
}
```

### Safety Requirement
```python
{
    "safety_code": "SAFE-LOTO-001",
    "requirement_name": "Lockout/Tagout Procedures",
    "description": "Proper isolation and lockout of electrical and mechanical energy sources",
    "ppe_required": ["Safety glasses", "Hard hat", "Steel-toed boots"],
    "training_hours": 8
}
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- Django 4.2+
- Required Python packages (see project requirements.txt)

### Environment Variables
Configure the following in your `.env` file:
```
LLM_NAME=gpt-4o
LLM_API_KEY=your_openai_api_key
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000
```

### Adding to Django Project
1. Add `'training_manuals_assistant'` to `INSTALLED_APPS` in settings.py
2. Include URLs in main urlpatterns:
   ```python
   path('api/training-manuals/', include('training_manuals_assistant.urls')),
   ```

## Usage Examples

### Processing a Training Manual from EAM
```bash
curl -X POST http://localhost:8000/api/training-manuals/process-training-manual/ \
  -H "Content-Type: application/json" \
  -d '{
    "document_code": "DOC-PUMP-MANUAL-001",
    "create_qualifications_in_eam": false
  }'
```

### Direct File Upload
```bash
curl -X POST http://localhost:8000/api/training-manuals/process-training-manual/ \
  -F "training_manual_file=@pump_manual.pdf" \
  -F "create_qualifications_in_eam=false"
```

## Future Enhancements

### EAM Integration
- **Qualification Profile Creation**: Automatically create qualification profiles in EAM
- **Skill Matrix Setup**: Configure skill requirements and assessment criteria
- **Certification Tracking**: Link certification requirements to equipment records
- **Training Program Generation**: Create structured training programs based on qualification requirements

### Advanced Analysis
- **Multi-Document Analysis**: Process multiple related documents for comprehensive qualification profiles
- **Skill Gap Analysis**: Compare current technician qualifications against requirements
- **Training Path Recommendations**: Suggest optimal training sequences for technicians

## Dependencies

### Key Python Packages
- `langchain` - LLM orchestration and document processing
- `langchain-openai` - OpenAI LLM integration
- `langchain-community` - Community document loaders
- `unstructured` - PDF processing and text extraction
- `pydantic` - Data validation and serialization
- `requests` - HTTP client for EAM API integration

### System Dependencies
- `poppler-utils` - PDF processing support (install via system package manager)

## Testing

Run the app tests:
```bash
python manage.py test training_manuals_assistant
```

## Architecture

### Service Layer
- `TrainingManualsAssistantService`: Core document processing logic
- PDF document loading and text extraction
- LLM prompt engineering and response parsing
- Temporary file management and cleanup

### API Layer
- `ProcessTrainingManualView`: REST API endpoint for document processing
- Request validation and error handling
- Response formatting and summary generation
- EAM integration for document retrieval

### Data Layer
- Pydantic schemas for structured data validation
- Type-safe data models for qualification requirements
- Enumerated choices for standardized values

## Benefits

1. **Enhanced Safety Compliance**: Ensures all manufacturer-recommended safety qualifications are captured
2. **Consistent Standards**: Creates uniform qualification requirements across similar equipment
3. **Time Efficiency**: Reduces qualification setup time from days to hours
4. **Comprehensive Coverage**: Captures nuanced requirements that might be missed manually
5. **Improved Maintenance Quality**: Ensures only properly qualified technicians perform maintenance tasks 