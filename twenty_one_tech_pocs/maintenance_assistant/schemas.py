from pydantic import BaseModel, Field
from typing import List


class ChecklistItem(BaseModel):
    checklist_id: str
    description: str


class TaskPlan(BaseModel):
    task_code: str
    description: str
    checklist: List[ChecklistItem]


class MaintenanceSchedule(BaseModel):
    code: str = Field(..., max_length=20)
    description: str = Field(..., max_length=80)
    duration: int
    task_plans: List[TaskPlan]
