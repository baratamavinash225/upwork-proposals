from pydantic import BaseModel
from typing import Optional, List

class ClientInfo(BaseModel):
    payment_verified: bool
    past_hires: int
    total_spent: float
    country: str
    rating: Optional[float] = None

class Job(BaseModel):
    id: str
    title: str
    description: str
    budget: Optional[float] = None
    skills: List[str]
    client: ClientInfo
    proposal_count: str # e.g., "Less than 5"
    url: str

class JobEvaluation(BaseModel):
    job_id: str
    is_match: bool
    match_score: int
    reason: str
    proposal_draft: Optional[str] = None
