from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SkillLevelChoices(str, Enum):
    ENTRY_LEVEL = "Entry Level"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

class CertificationTypeChoices(str, Enum):
    MANUFACTURER_CERTIFICATION = "Manufacturer Certification"
    INDUSTRY_CERTIFICATION = "Industry Certification"
    SAFETY_CERTIFICATION = "Safety Certification"
    TECHNICAL_CERTIFICATION = "Technical Certification"

class QualificationCategoryChoices(str, Enum):
    ELECTRICAL = "Electrical"
    MECHANICAL = "Mechanical"
    HYDRAULIC = "Hydraulic"
    PNEUMATIC = "Pneumatic"
    ELECTRONICS = "Electronics"
    SOFTWARE = "Software"
    SAFETY = "Safety"
    OPERATION = "Operation"
    MAINTENANCE = "Maintenance"

class RequiredCertification(BaseModel):
    certification_code: str = Field(..., description="Unique code for the certification requirement (e.g., CERT-ELEC-001).")
    certification_name: str = Field(..., description="Name of the required certification.")
    certification_type: CertificationTypeChoices = Field(..., description="Type of certification required.")
    issuing_authority: Optional[str] = Field(None, description="Organization that issues the certification.")
    renewal_period: Optional[int] = Field(None, description="Certification renewal period in months.")
    is_mandatory: bool = Field(True, description="Whether this certification is mandatory or recommended.")

class TechnicalSkill(BaseModel):
    skill_code: str = Field(..., description="Unique code for the technical skill (e.g., SKILL-WELD-001).")
    skill_name: str = Field(..., description="Name of the technical skill.")
    skill_category: QualificationCategoryChoices = Field(..., description="Category of the technical skill.")
    skill_level: SkillLevelChoices = Field(..., description="Required skill level.")
    description: str = Field(..., description="Detailed description of the skill requirement.")
    tools_required: List[str] = Field(default_factory=list, description="List of tools/equipment needed for this skill.")

class SafetyRequirement(BaseModel):
    safety_code: str = Field(..., description="Unique code for the safety requirement (e.g., SAFE-PPE-001).")
    requirement_name: str = Field(..., description="Name of the safety requirement.")
    description: str = Field(..., description="Detailed description of the safety requirement.")
    ppe_required: List[str] = Field(default_factory=list, description="Personal protective equipment required.")
    training_hours: Optional[int] = Field(None, description="Required training hours for this safety requirement.")

class MaintenanceTask(BaseModel):
    task_code: str = Field(..., description="Unique code for the maintenance task (e.g., TASK-INSP-001).")
    task_name: str = Field(..., description="Name of the maintenance task.")
    task_description: str = Field(..., description="Detailed description of the maintenance task.")
    complexity_level: SkillLevelChoices = Field(..., description="Complexity level of the task.")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes.")
    required_skills: List[TechnicalSkill] = Field(default_factory=list, description="Technical skills required for this task.")
    required_certifications: List[RequiredCertification] = Field(default_factory=list, description="Certifications required for this task.")
    safety_requirements: List[SafetyRequirement] = Field(default_factory=list, description="Safety requirements for this task.")

class EquipmentQualificationProfile(BaseModel):
    equipment_type: str = Field(..., description="Type or model of equipment.")
    equipment_manufacturer: Optional[str] = Field(None, description="Manufacturer of the equipment.")
    qualification_profile_code: str = Field(..., description="Unique code for this qualification profile (e.g., QUAL-PUMP-001).")
    profile_description: str = Field(..., description="Description of the qualification profile.")
    minimum_experience_years: Optional[int] = Field(None, description="Minimum years of experience required.")
    maintenance_tasks: List[MaintenanceTask] = Field(default_factory=list, description="List of maintenance tasks for this equipment.")

class TrainingManualAnalysisOutput(BaseModel):
    equipment_qualification_profiles: List[EquipmentQualificationProfile] = Field(
        default_factory=list, 
        description="List of qualification profiles extracted from the training manual."
    )
    general_safety_requirements: List[SafetyRequirement] = Field(
        default_factory=list, 
        description="General safety requirements that apply across all tasks."
    )
    general_certifications: List[RequiredCertification] = Field(
        default_factory=list, 
        description="General certifications required for working with this equipment."
    ) 