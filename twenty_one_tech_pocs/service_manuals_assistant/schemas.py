from pydantic import BaseModel, Field
from typing import List


class ChecklistItem(BaseModel):
    checklist_id: str = Field(..., max_length=20)
    description: str = Field(..., max_length=80)


class TaskPlan(BaseModel):
    task_code: str = Field(..., max_length=20)
    description: str = Field(..., max_length=80)
    checklist: List[ChecklistItem]


class TaskPlanListContainer(BaseModel):
    task_plans: List[TaskPlan] = Field(..., description="A list of task plans extracted from the document.") 