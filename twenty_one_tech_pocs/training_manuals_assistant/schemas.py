from pydantic import BaseModel, Field
from typing import List


class Qualification(BaseModel):
    qualification_code: str = Field(
        ...,
        max_length=20,
        description="Unique code for the qualification (max 20 characters, e.g., QUAL-WELD-001, QUAL-SAFE-002).")
    qualification_description: str = Field(
        ...,
        max_length=80,
        description="Concise description of the qualification (max 80 characters). Focus on core skills/requirements.")


class TrainingManualQualificationExtraction(BaseModel):
    qualifications: List[Qualification] = Field(
        default_factory=list,
        description="List of qualifications extracted from the training manual."
    )
