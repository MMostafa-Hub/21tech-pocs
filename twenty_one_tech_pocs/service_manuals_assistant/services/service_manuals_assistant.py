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
from langchain_openai import ChatOpenAI
from ..schemas import TaskPlan, TaskPlanListContainer # Added TaskPlanListContainer

logger = logging.getLogger(__name__)


class ServiceManualsAssistantService:
    """Service for processing service manual documents and extracting structured data."""

    def __init__(self):
        self.temp_file_path: Optional[str] = None
        self.temp_dir: str = "temp_documents"
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_document(
        self, file: UploadedFile, llm: BaseChatModel
    ) -> List[TaskPlan]: 
        """
        Process a service manual document using LangChain and generate structured output.

        Args:
            file: The uploaded PDF file to process
            llm: The language model to use for processing

        Returns:
            List[TaskPlan]: A list of structured task plans extracted from document

        Raises:
            ValueError: If file format is not supported
            IOError: If file cannot be read or processed
        """
        if not file.name.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported")

        try:
            file_path = self._save_temp_file(file)
            self.temp_file_path = file_path

            loader = UnstructuredPDFLoader(file_path)
            documents = loader.load()

            if not documents:
                raise ValueError("No content could be extracted from the PDF")

            processed_data_container = self._process_task_plan_data(llm, documents)
            return processed_data_container.task_plans # Extract list from container

        except Exception as e:
            logger.error(f"Error processing document {file.name}: {str(e)}")
            raise
        finally:
            self.cleanup()

    def _save_temp_file(self, file: UploadedFile) -> str:
        """
        Save the uploaded file to a temporary location.
        Args:
            file: The uploaded file to save
        Returns:
            str: Path to the saved temporary file
        """
        file_path = os.path.join(self.temp_dir, file.name)
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        logger.info(f"Saved temporary file: {file_path}")
        return file_path

    def _create_task_plan_prompt(self) -> ChatPromptTemplate: 
        """
        Create the prompt template for task plan data extraction.
        Returns:
            ChatPromptTemplate: The configured prompt template
        """
        system_template = self._get_system_prompt_template()
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = """Please analyze the following service manual document and extract the required information:
        
        {text}
        
        Respond with ONLY the JSON structure containing the extracted task plan data, matching the schema provided in the system instructions.
        """
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    def _get_system_prompt_template(self) -> str:
        """
        Get the system prompt template for task plan data extraction.
        Returns:
            str: The system prompt template
        """
        return """You are an expert AI system designed to transform equipment service manuals, technical bulletins, and historical repair logs into standardized work orders.
Your primary goal is to generate structured Task Plans and detailed Checklists for equipment troubleshooting and maintenance.

Key Objectives:
1.  **Ingest Technical Documentation:** Analyze the provided text from equipment manuals or related documents.
2.  **Identify Maintenance Procedures:** Recognize patterns indicating troubleshooting sequences, repair steps, safety precautions, and required resources.
3.  **Extract Contextual Relationships:** Understand links between symptoms, potential causes, and corresponding resolution actions.
4.  **Prioritize Safety:** Identify and clearly call out all safety warnings, cautions, required Personal Protective Equipment (PPE), and safety-critical steps.

Output Requirements:
-   Generate standardized Task Plans in a logical, step-by-step format.
-   Create comprehensive Checklists associated with each Task Plan. Checklists MUST include:
    -   Required tools and parts.
    -   All relevant safety procedures and PPE requirements.
    -   Clear, sequential troubleshooting or maintenance instructions.
    -   Verification steps to confirm successful completion.
-   Organize tasks considering safety, logical flow, and operational efficiency.

For each entity (Task Plan, Checklist), generate codes and IDs that are:
-   Descriptive: Incorporate key terms or abbreviations from the equipment, procedure, or task (e.g., 'PUMP_REPLACE_SEAL', 'CHK_BEARING_INSPECT').
-   Unique: Ensure each code/ID is distinct, potentially using a combination of the manual's name, task type, and sequence.
-   Human-readable: Prefer meaningful identifiers over random strings.

Format your response STRICTLY as a raw JSON object with a single key "task_plans".
The value of "task_plans" should be a list, where each item in the list is a Task Plan object.
Do NOT use any markdown formatting (e.g., do NOT use ```json ... ```).
The output must be directly parsable as JSON. 

The schema for the overall JSON object is:
{{
    "task_plans": [
        {{
            "task_code": string, // Task plan code, descriptive and unique (e.g., 'TP_PUMP_OVERHAUL') max length 20
            "description": string, // Task plan description (e.g., 'Complete overhaul of Pump Model X') max length 80
            "checklist": [
                {{
                    "checklist_id": string, // Checklist ID, descriptive and unique (e.g., 'CL_DISASSEMBLY') max length 20
                    "description": string // Checklist item description (e.g., 'Step 1: Verify pump is isolated and LOTO is applied') max length 80
                }},
                {{
                    "checklist_id": string, // (e.g., 'CL_INSPECT_SHAFT') max length 20
                    "description": string // (e.g., 'Step 2: Inspect shaft for wear and runout. Required tools: Micrometer') max length 80
                }}
                // ... more checklist items ...
            ]
        }}
        // ... more task plans if applicable ...
    ]
}}

Extract all relevant task plans and their checklist steps from the document.
If specific details (like tool names, part numbers) are mentioned for a step, include them in the checklist item's description.
Ensure every step is actionable and clear for a maintenance technician.
For any missing required fields in the schema (task_code, description, checklist_id), use reasonable, descriptive defaults based on the content.
"""

    def _process_task_plan_data(
        self, llm: ChatOpenAI, documents: list[Document]
    ) -> TaskPlanListContainer: # Changed return type to the container
        """
        Process the document chunks to extract task plan information.
        Args:
            llm: The language model to use for processing
            documents: The document chunks to process
        Returns:
            TaskPlanListContainer: Container with structured task plan data
        """
        logger.info(f"Processing {len(documents)} document chunks")
        chat_prompt = self._create_task_plan_prompt()
        parser = PydanticOutputParser(pydantic_object=TaskPlanListContainer) # Use the container model

        summarize_chain = load_summarize_chain(
            llm,
            chain_type="stuff",
            verbose=True,
            prompt=chat_prompt,
        )

        try:
            response = summarize_chain.invoke({"input_documents": documents})
            output_text = response["output_text"]
            # Strip markdown JSON fences if present - keeping this as a safeguard
            if output_text.startswith("```json\n"):
                output_text = output_text[7:]
            if output_text.endswith("\n```"):
                output_text = output_text[:-4]
            
            parsed_response = parser.invoke(output_text)
            logger.info("Successfully extracted task plan data container")
            return parsed_response
        except Exception as e:
            logger.error(f"Error extracting task plan data: {str(e)}")
            raise ValueError(f"Failed to extract structured data from document: {str(e)}")

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.remove(self.temp_file_path)
                logger.info(f"Cleaned up temporary file: {self.temp_file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {str(e)}") 