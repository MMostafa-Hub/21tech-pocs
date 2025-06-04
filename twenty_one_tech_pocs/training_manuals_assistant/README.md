# Training Manuals Assistant

## Overview

The Training Manuals Assistant is a Django app that uses Large Language Models (LLMs) to extract technician qualification codes and descriptions from equipment training manuals, with integrated EAM (Enterprise Asset Management) system support for automatically creating qualifications.

## Features

### Document Processing

- **PDF Training Manual Analysis**: Processes equipment training manuals and technical documentation
- **EAM Integration**: Fetches documents directly from EAM document management system
- **Multi-source Input**: Supports both direct file upload and EAM document codes

### Qualification Extraction

- **Simple Qualification Structure**: Extracts qualification codes and concise descriptions (max 80 characters)
- **Comprehensive Coverage**: Captures all qualification requirements mentioned in training materials
- **Standardized Coding**: Uses consistent naming conventions for qualification codes
- **Concise Descriptions**: Focused, abbreviated descriptions optimized for EAM system constraints

### EAM Integration

- **Automatic Qualification Creation**: Creates qualifications directly in EAM when requested
- **Batch Processing**: Processes multiple qualifications in a single request
- **Error Handling**: Provides detailed status and error information for each qualification
- **Success Tracking**: Reports successful and failed creations with detailed results

## API Endpoints

### Process Training Manual

**POST** `/api/training-manuals/process-training-manual/`

Processes a training manual document to extract qualification requirements and optionally create them in EAM.

#### Request Parameters

- `document_code` (optional): EAM document code to fetch document from EAM system
- `training_manual_file` (optional): Direct file upload (PDF format)
- `create_in_eam` (optional, boolean): Flag to create qualifications in EAM (default: false)

#### Response Format

**Basic Extraction (create_in_eam=false):**

```json
{
    "qualification_extraction": {
        "qualifications": [
            {
                "qualification_code": "QUAL-WELD-STRUCT-001",
                "qualification_description": "AWS D1.1 structural welding cert, 2+ yrs exp, MIG/TIG techniques"
            }
        ]
    },
    "summary": {
        "total_qualifications": 1,
        "qualification_codes": ["QUAL-WELD-STRUCT-001"]
    }
}
```

**With EAM Integration (create_in_eam=true):**

```json
{
    "qualification_extraction": {
        "qualifications": [...]
    },
    "summary": {
        "total_qualifications": 1,
        "qualification_codes": ["QUAL-WELD-STRUCT-001"]
    },
    "qualification_summary_for_eam": [
        {
            "qualification_code": "QUAL-WELD-STRUCT-001",
            "qualification_description": "...",
            "eam_integration_status": "success",
            "eam_creation_result": {
                "status": "success",
                "qualification_code": "QUAL-WELD-STRUCT-001",
                "eam_response": {...}
            }
        }
    ],
    "eam_creation_summary": {
        "total_qualifications_processed": 1,
        "successful_creations": 1,
        "failed_creations": 0,
        "creation_results": [...]
    }
}
```

## Data Schema

### Qualification

```python
{
    "qualification_code": "QUAL-WELD-STRUCT-001",
    "qualification_description": "AWS D1.1 structural welding cert, 2+ yrs exp, MIG/TIG techniques"
}
```

**Description Constraints:**

- Maximum 80 characters
- Uses abbreviations for efficiency: "cert", "exp", "maint", "req", "proc"
- Focuses on core requirements and skills
- Omits articles ("the", "a", "an") to save space

## Qualification Code Convention

The system uses a standardized naming convention for qualification codes:

- **Format**: `QUAL-[CATEGORY]-[SPECIFIC]-[NUMBER]`
- **Categories**: WELD, ELEC, MECH, SAFETY, HVAC, HYDRAUL, PNEUM, etc.
- **Examples**:
  - `QUAL-WELD-STRUCT-001` - Structural welding qualification
  - `QUAL-SAFETY-CONFINED-001` - Confined space entry qualification
  - `QUAL-ELEC-HV-001` - High voltage electrical qualification

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

### Extract Qualifications Only

```bash
curl -X POST http://localhost:8000/api/training-manuals/process-training-manual/ \
  -F "training_manual_file=@training_manual.pdf"
```

### Extract and Create in EAM

```bash
curl -X POST http://localhost:8000/api/training-manuals/process-training-manual/ \
  -F "training_manual_file=@training_manual.pdf" \
  -F "create_in_eam=true"
```

### From EAM Document Code

```bash
curl -X POST http://localhost:8000/api/training-manuals/process-training-manual/ \
  -H "Content-Type: application/json" \
  -d '{
    "document_code": "DOC-TRAINING-MANUAL-001",
    "create_in_eam": true
  }'
```

## EAM Integration Details

### Qualification Creation

When `create_in_eam=true`, the system:

1. Extracts qualifications from the training manual
2. For each qualification, creates an EAM qualification record using:
   - **Qualification Code**: From extracted data
   - **Description**: From extracted data
   - **Organization Code**: "*" (default)
   - **Class Code**: "*" (default)
   - **Active Flag**: "true"
   - **Training Record**: "false"

### EAM API Endpoint

- **URL**: `https://us1.eam.hxgnsmartcloud.com:443/axis/restservices/qualifications`
- **Method**: POST
- **Headers**: Content-Type, tenant, organization, Authorization
- **Authentication**: Basic authentication with 21Tech credentials

### Error Handling

The system provides detailed error information for failed EAM creations:

- **Status**: "success" or "failed"
- **Error Details**: Specific error messages from EAM
- **Payload Information**: What was sent to EAM
- **Response Text**: Raw response from EAM API

## Testing

Run the app tests:

```bash
python manage.py test training_manuals_assistant
```

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

## Benefits

1. **Simplified Structure**: Easy-to-understand qualification codes and descriptions
2. **Comprehensive Extraction**: Captures all qualification requirements from training manuals
3. **Standardized Format**: Consistent qualification code naming and structure
4. **Automated EAM Integration**: Direct creation of qualifications in EAM system
5. **Time Efficiency**: Reduces qualification identification and setup time from days to hours
6. **Error Handling**: Robust error handling and reporting for EAM integration
7. **Batch Processing**: Handle multiple qualifications efficiently
