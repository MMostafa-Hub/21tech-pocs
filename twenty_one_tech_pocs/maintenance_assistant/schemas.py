from pydantic import BaseModel
from typing import List


class Checklist(BaseModel):
    checklist_id: str
    checklist_type: str
    description: str
    required_tools: List[str]
    safety_requirements: List[str]
    frequency: str
    estimated_duration: str
    steps: List[str]


class TaskPlan(BaseModel):
    plan_id: str
    checklists: List[Checklist]


class MaintenanceSchedule(BaseModel):
    equipment_id: str
    equipment_name: str
    maintenance_frequency: str
    task_plans: List[TaskPlan]
