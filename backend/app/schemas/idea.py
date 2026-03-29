from pydantic import BaseModel


class IdeaBase(BaseModel):
    name: str
    description: str
    failure_reason: str | None = None
    industry: str | None = None
    year: int | None = None
    source_url: str | None = None


class IdeaCreate(IdeaBase):
    pass


class AnalysisOut(BaseModel):
    id: int
    problem: str | None
    failure_type: str | None
    current_opportunity: str | None
    pain_score: int | None
    paying_capacity: int | None
    mvp_ease: int | None
    tech_advantage: int | None
    total_score: float | None

    class Config:
        from_attributes = True


class ExecutionOut(BaseModel):
    id: int
    mvp_plan: str | None
    stack: str | None
    monetization: str | None
    estimated_days: int | None
    status: str

    class Config:
        from_attributes = True


class IdeaOut(IdeaBase):
    id: int
    analysis: AnalysisOut | None = None
    execution: ExecutionOut | None = None

    class Config:
        from_attributes = True
