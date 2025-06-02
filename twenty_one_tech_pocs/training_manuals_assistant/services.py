import logging
import os
from typing import Optional, List

from django.core.files.uploadedfile import UploadedFile
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from .schemas import (
    TrainingManualAnalysisOutput,
    EquipmentQualificationProfile,
    MaintenanceTask,
    TechnicalSkill,
    RequiredCertification,
    SafetyRequirement,
    SkillLevelChoices,
    CertificationTypeChoices,
    QualificationCategoryChoices
)

logger = logging.getLogger(__name__)

class TrainingManualsAssistantService:
    """
    Service for processing equipment training and operation manuals to extract structured qualification requirements.
    """

    def __init__(self):
        self.temp_file_path: Optional[str] = None
        self.temp_dir: str = "temp_documents/training_assistant"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_document(
        self, file: UploadedFile, llm: BaseChatModel
    ) -> Optional[TrainingManualAnalysisOutput]:
        """
        Process a training manual document and generate structured qualification analysis.
        
        Args:
            file: The uploaded training manual file.
            llm: The language model.
            
        Returns:
            Optional[TrainingManualAnalysisOutput]: Structured analysis or None if error.
        """
        try:
            file_path = self._save_temp_file(file)
            self.temp_file_path = file_path
            loader = UnstructuredPDFLoader(file_path)
            documents = loader.load()

            if not documents:
                logger.warning(f"No content extracted from {file.name}")
                return None

            analysis_output = self._extract_qualification_analysis(llm, documents)
            
            if analysis_output:
                logger.info(f"Successfully extracted qualification analysis. Identified {len(analysis_output.equipment_qualification_profiles)} equipment profiles.")
            else:
                logger.info("No structured qualification analysis was extracted by the LLM.")
            return analysis_output

        except Exception as e:
            logger.error(f"Error processing training manual {file.name}: {str(e)}")
            raise
        finally:
            self.cleanup()

    def _save_temp_file(self, file: UploadedFile) -> str:
        file_path = os.path.join(self.temp_dir, file.name)
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        logger.info(f"Saved temporary training manual file: {file_path}")
        return file_path

    def _get_system_prompt_template(self) -> str:
        skill_level_options = ", ".join([f'"{e.value}"' for e in SkillLevelChoices])
        cert_type_options = ", ".join([f'"{e.value}"' for e in CertificationTypeChoices])
        qualification_category_options = ", ".join([f'"{e.value}"' for e in QualificationCategoryChoices])

        return f"""
You are an expert AI system specialized in analyzing equipment training manuals, operation manuals, and technical documentation to extract technician qualification requirements. Your goal is to transform complex technical documentation into structured qualification profiles that ensure only properly trained personnel operate and maintain equipment.

Primary Objectives:
1. **Extract Equipment Information:** Identify specific equipment types, models, and manufacturers mentioned in the documentation.
2. **Identify Qualification Requirements:** Recognize patterns indicating required skills, certifications, experience levels, and safety protocols.
3. **Analyze Task Complexity:** Determine the skill level required for different maintenance and operation tasks.
4. **Extract Safety Requirements:** Identify all safety protocols, PPE requirements, and safety training needs.
5. **Structure Qualification Data:** Organize findings into comprehensive qualification profiles for each equipment type.

Analysis Focus Areas:
- **Technical Skills:** Look for mentions of specific technical competencies (electrical, mechanical, hydraulic, etc.)
- **Certifications:** Identify required manufacturer certifications, industry standards, safety certifications
- **Experience Requirements:** Extract minimum experience levels or years required for different tasks
- **Safety Protocols:** Identify all safety procedures, lockout/tagout requirements, confined space protocols
- **Tool Proficiency:** Note specialized tools or equipment that technicians must be qualified to use
- **Training Requirements:** Identify specific training programs or hours required

Output Requirements:
Generate a single JSON object with three top-level keys: "equipment_qualification_profiles", "general_safety_requirements", and "general_certifications".

1. **equipment_qualification_profiles**: A LIST of EquipmentQualificationProfile objects.
   - Each profile represents a specific equipment type or model with its qualification requirements
   - Include all maintenance tasks identified for that equipment
   - Each maintenance task should include required skills, certifications, and safety requirements

2. **general_safety_requirements**: A LIST of SafetyRequirement objects that apply across all equipment.

3. **general_certifications**: A LIST of RequiredCertification objects that are generally required.

Schema Details:

**SkillLevelChoices**: {skill_level_options}
**CertificationTypeChoices**: {cert_type_options}  
**QualificationCategoryChoices**: {qualification_category_options}

Example JSON structure:
{{
    "equipment_qualification_profiles": [
        {{
            "equipment_type": "Centrifugal Pump Model CP-500",
            "equipment_manufacturer": "ABC Industrial",
            "qualification_profile_code": "QUAL-CP500-001",
            "profile_description": "Qualification requirements for operating and maintaining CP-500 centrifugal pumps",
            "minimum_experience_years": 2,
            "maintenance_tasks": [
                {{
                    "task_code": "TASK-CP500-MAINT",
                    "task_name": "Routine Maintenance",
                    "task_description": "Perform routine maintenance including lubrication, inspection, and minor adjustments",
                    "complexity_level": "Intermediate",
                    "estimated_duration": 120,
                    "required_skills": [
                        {{
                            "skill_code": "SKILL-MECH-001",
                            "skill_name": "Mechanical Assembly",
                            "skill_category": "Mechanical",
                            "skill_level": "Intermediate",
                            "description": "Ability to disassemble and reassemble pump components",
                            "tools_required": ["Torque wrench", "Bearing puller", "Dial indicator"]
                        }}
                    ],
                    "required_certifications": [
                        {{
                            "certification_code": "CERT-ABC-001",
                            "certification_name": "ABC Pump Technician Certification",
                            "certification_type": "Manufacturer Certification",
                            "issuing_authority": "ABC Industrial Training Center",
                            "renewal_period": 24,
                            "is_mandatory": true
                        }}
                    ],
                    "safety_requirements": [
                        {{
                            "safety_code": "SAFE-LOTO-001",
                            "requirement_name": "Lockout/Tagout Procedures",
                            "description": "Proper isolation and lockout of electrical and mechanical energy sources",
                            "ppe_required": ["Safety glasses", "Hard hat", "Steel-toed boots"],
                            "training_hours": 8
                        }}
                    ]
                }}
            ]
        }}
    ],
    "general_safety_requirements": [
        {{
            "safety_code": "SAFE-GEN-001",
            "requirement_name": "General PPE Requirements",
            "description": "Basic personal protective equipment required for all maintenance activities",
            "ppe_required": ["Safety glasses", "Hard hat", "Steel-toed boots", "Work gloves"],
            "training_hours": 4
        }}
    ],
    "general_certifications": [
        {{
            "certification_code": "CERT-OSHA-001",
            "certification_name": "OSHA 10-Hour Safety Training",
            "certification_type": "Safety Certification",
            "issuing_authority": "OSHA",
            "renewal_period": 36,
            "is_mandatory": true
        }}
    ]
}}

Instructions:
- Generate unique, descriptive codes for all entities
- Extract ALL qualification requirements mentioned in the document
- Organize tasks by complexity level and required qualifications
- Include specific tool requirements when mentioned
- Capture both mandatory and recommended certifications
- If no specific experience requirements are mentioned, you may omit minimum_experience_years
- Ensure all codes are unique and descriptive based on equipment type and task
- Strictly adhere to this JSON structure without markdown formatting
"""

    def _create_extraction_prompt(self) -> ChatPromptTemplate:
        system_template = self._get_system_prompt_template()
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = """Please analyze the following training manual document and extract the structured qualification requirements based on the requirements provided.

Training Manual Content:
{text}

Respond with ONLY the JSON object adhering to the schema described in the system prompt.
"""
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    def _extract_qualification_analysis(
        self, llm: BaseChatModel, documents: List[Document]
    ) -> Optional[TrainingManualAnalysisOutput]:
        logger.info(f"Starting qualification analysis extraction from {len(documents)} document chunks.")
        extraction_prompt = self._create_extraction_prompt()
        parser = PydanticOutputParser(pydantic_object=TrainingManualAnalysisOutput)

        chain = load_summarize_chain(
            llm, chain_type="stuff", verbose=True, prompt=extraction_prompt
        )
        try:
            response = chain.invoke({"input_documents": documents})
            output_text = response.get("output_text", "")
            if not output_text:
                logger.warning("LLM returned empty output for qualification analysis.")
                return None
            
            parsed_response = parser.invoke(output_text)
            logger.info("Successfully parsed LLM response into TrainingManualAnalysisOutput.")
            return parsed_response
        except Exception as e:
            logger.error(f"Failed to parse LLM response for qualification analysis. Error: {str(e)}. Raw output: '{output_text[:500]}...'")
            return None

    def cleanup(self) -> None:
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.remove(self.temp_file_path)
                logger.info(f"Cleaned up temporary training manual file: {self.temp_file_path}")
            except OSError as e:
                logger.error(f"Error cleaning up temporary file {self.temp_file_path}: {str(e)}")
        self.temp_file_path = None 