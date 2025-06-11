# Add your service classes here. 
from django.core.files.base import ContentFile
from typing import List, Optional
from langchain_core.language_models.base import BaseLanguageModel
import logging
import os

from django.core.files.uploadedfile import UploadedFile
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from .schemas import JobSafetyAnalysis
from common.eam_api import EAMApiService
from ...common.utils import get_llm

logger = logging.getLogger(__name__)

class SafetyProcedureAssistantService:
    """
    A service to analyze equipment incident reports and extract a Job Safety Analysis (JSA).
    It identifies hazards, required precautions, and links them to the involved equipment.
    """

    def __init__(self):
        self.temp_file_path: Optional[str] = None
        self.temp_dir: str = "temp_documents/safety_assistant"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.eam_api_service = EAMApiService()

    def process_document(
        self, file: UploadedFile, llm: BaseChatModel
    ) -> Optional[JobSafetyAnalysis]:
        """
        Processes an uploaded incident report to extract a Job Safety Analysis.

        Args:
            file: The uploaded incident report file.
            llm: The language model to use for extraction.

        Returns:
            An optional JobSafetyAnalysis object or None if extraction fails.
        """
        try:
            file_path = self._save_temp_file(file)
            self.temp_file_path = file_path

            # Use PyMuPDF to extract text from the PDF
            doc = fitz.open(file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            # Create a single LangChain Document
            documents = [Document(page_content=full_text)]

            if not documents or not documents[0].page_content.strip():
                logger.warning(f"No content extracted from {file.name}")
                return None

            job_safety_analysis = self._extract_job_safety_analysis(llm, documents)
            
            if job_safety_analysis:
                logger.info(f"Successfully extracted {len(job_safety_analysis.identified_hazards)} hazards from incident report.")
            else:
                logger.info("No job safety analysis could be extracted from the incident report.")
            return job_safety_analysis

        except Exception as e:
            logger.error(f"Error processing incident report {file.name}: {str(e)}")
            raise
        finally:
            self.cleanup()

    def _save_temp_file(self, file: UploadedFile) -> str:
        """Saves the uploaded file to a temporary location."""
        file_path = os.path.join(self.temp_dir, file.name)
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        logger.info(f"Saved temporary incident report file: {file_path}")
        return file_path

    def _get_system_prompt_template(self) -> str:
        # This prompt is extensive and defines the entire extraction logic for the LLM.
        # It includes schemas, constraints, and examples for the expected JSON output.
        return """
You are an expert AI system for analyzing equipment incident reports and generating a Job Safety Analysis (JSA). Your primary goal is to extract hazards, precautions, and their links to specific equipment from the provided incident report.

## CORE TASK
Analyze the incident report to identify:
1.  **Hazards**: What potential dangers or risks were present or contributed to the incident?
2.  **Precautions**: What safety measures or controls could prevent such incidents?
3.  **Equipment Links**: Which specific precautions apply to which pieces of equipment?

## JSON OUTPUT STRUCTURE
You must return a single JSON object with two main keys: `identified_hazards` and `equipment_safety_links`.

```json
{
    "identified_hazards": [
        {
            "hazard_code": "HAZ-UNIQUE-CODE-001",
            "description": "A clear, concise description of the hazard.",
            "hazard_type": "One of the allowed hazard types",
            "precautions": [
                {
                    "precaution_code": "PREC-UNIQUE-CODE-001",
                    "description": "A specific, actionable safety measure.",
                    "timing": "When the precaution should be taken"
                }
            ]
        }
    ],
    "equipment_safety_links": [
        {
            "equipment_details": {
                "equipment_id": "Specific model or ID of the equipment",
                "class_code": "A valid equipment class code",
                "category": "A valid equipment category"
            },
            "linked_precaution": {
                "precaution_code": "PREC-UNIQUE-CODE-001",
                "description": "A specific, actionable safety measure.",
                "timing": "When the precaution should be taken"
            }
        }
    ]
}
```

### 1. `identified_hazards`
A list of all hazards identified in the report. Each hazard object must contain:
-   `hazard_code`: A unique identifier for the hazard (e.g., `HAZ-FALL-001`).
-   `description`: A detailed description of the risk.
-   `hazard_type`: Must be one of: "Biological", "Chemical", "Ergonomic", "Physical", "Psychosocial", "Safety".
-   `precautions`: A list of all safety measures related to this hazard. Each precaution object must contain:
    -   `precaution_code`: A unique identifier for the precaution (e.g., `PREC-FALL001-HARNESS01`).
    -   `description`: A specific, actionable instruction.
    -   `timing`: When the action should be taken. Must be one of: "Pre-Work", "During Work", "Post-Work".

### 2. `equipment_safety_links`
A list linking specific precautions to specific pieces of equipment mentioned in the report.
-   `equipment_details`: Information about the equipment.
    -   `equipment_id`: The specific name, model, or identifier of the equipment.
    -   `class_code`: The equipment's class code. Must be one of: "FLEET", "FACILITY", "TOOL", "HVAC".
    -   `category` (optional): Must be one of: "Heavy Machinery", "Power Tools", "Hand Tools", "Lifting Equipment", "Vehicles", "Safety Gear".
-   `linked_precaution`: A Precaution object. This precaution MUST BE an exact copy of one of the precautions listed under the corresponding hazard in the `identified_hazards` list.

Strictly adhere to this JSON structure. Do not use markdown formatting for the JSON output.
"""

    def _create_extraction_prompt(self) -> ChatPromptTemplate:
        system_template = self._get_system_prompt_template()
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        )
        human_template = """Please analyze the following incident report document and extract the structured safety analysis based on the requirements provided.

Incident Report Text:
{text}

Respond with ONLY the JSON object adhering to the schema described in the system prompt.
"""
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        return ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

    def _extract_job_safety_analysis(
        self, llm: BaseChatModel, documents: List[Document]
    ) -> Optional[JobSafetyAnalysis]:
        logger.info(
            f"Starting job safety analysis extraction from {len(documents)} document chunks."
        )
        extraction_prompt = self._create_extraction_prompt()
        parser = PydanticOutputParser(pydantic_object=JobSafetyAnalysis)

        chain = load_summarize_chain(
            llm, chain_type="stuff", verbose=True, prompt=extraction_prompt
        )
        
        # We are passing the single document with all the text.
        # The 'stuff' chain type will put it all into the context.
        input_data = {"input_documents": documents}
        output_text = ""
        try:
            response = chain.invoke(input_data)
            output_text = response.get("output_text", "")
            if not output_text:
                logger.warning("LLM returned empty output for job safety analysis.")
                return None
            
            parsed_response = parser.invoke(output_text)
            logger.info("Successfully parsed LLM response into JobSafetyAnalysis.")
            return parsed_response
        except Exception as e:
            logger.error(
                f"Failed to parse LLM response for job safety analysis. Error: {str(e)}. Raw output: '{output_text[:500]}...'"
            )
            return None

    def cleanup(self) -> None:
        """Removes the temporary file if it exists."""
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.remove(self.temp_file_path)
                logger.info(
                    f"Cleaned up temporary incident report file: {self.temp_file_path}"
                )
            except OSError as e:
                logger.error(
                    f"Error cleaning up temporary file {self.temp_file_path}: {str(e)}"
                )
        self.temp_file_path = None