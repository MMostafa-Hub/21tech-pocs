from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class HazardTypeChoices(str, Enum):
    ALL_HAZARDS = "All Hazards"
    BIOLOGICAL_HAZARDS = "Biological Hazards"
    CHEMICAL_HAZARDS = "Chemical Hazards"
    PHYSICAL_HAZARDS = "Physical Hazards"
    RADIOLOGICAL_HAZARDS = "Radiological Hazards"
    
class PrecautionTimingChoices(str, Enum):
    ALL_TIME = "All Time"
    DURING = "During"
    POST_WORK = "Post Work"
    PRE_WORK = "Pre Work"

class Precaution(BaseModel):
    precaution_code: str = Field(..., description="Unique code for the precaution, proposed by LLM (e.g., PREC-SAFETY-001).")
    description: str = Field(..., description="Detailed description of the precautionary measure.")
    timing: Optional[PrecautionTimingChoices] = Field(None, description="When the precaution should be applied.")

class Hazard(BaseModel):
    hazard_code: str = Field(..., description="Unique code for the hazard, proposed by LLM (e.g., HAZ-BLOWTORCH-001).")
    description: str = Field(..., description="Detailed description of the hazard observed or inferred from the incident.")
    hazard_type: HazardTypeChoices = Field(..., description="Type of hazard.")
    precautions: List[Precaution] = Field(default_factory=list, description="Comprehensive list of precautionary measures identified for this hazard.")

class EquipmentDetails(BaseModel):
    class_code: Optional[str] = Field(None, description="Class code of the equipment if known (e.g., 'BLWTRCH').")
    category: Optional[str] = Field(None, description="Category of the equipment (e.g., 'Welding Tools').")
    equipment_id: str = Field(..., description="Specific identifier of the equipment involved (e.g., 'Blowtorch Model X'). This is mandatory if equipment is linked.")

class EquipmentSafetyLink(BaseModel):
    equipment_details: EquipmentDetails = Field(..., description="The specific equipment involved in this link.")
    linked_precaution: Precaution = Field(..., description="The specific precaution that is critically linked to the equipment and incident.")
    parent_hazard_code: str = Field(..., description="The hazard_code of the parent Hazard to which the linked_precaution belongs. This code must match one of the hazard_codes in the 'identified_hazards' list.")

class IncidentAnalysisOutput(BaseModel):
    identified_hazards: List[Hazard] = Field(default_factory=list, description="A list of all unique hazards identified from the incident report, each with its associated precautions.")
    equipment_safety_links: List[EquipmentSafetyLink] = Field(default_factory=list, description="A list of specific links associating equipment with a critical precaution and its parent hazard, derived from the incident details.")