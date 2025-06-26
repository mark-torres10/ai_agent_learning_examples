from pydantic import BaseModel, Field

class ProposedIdea(BaseModel):
    idea: str
    audience: str
    campaign_message: str
    concept: str

class ProposedIdeasWrapper(BaseModel):
    ideas: list[ProposedIdea]

class IdeaEvaluation(BaseModel):
    idea_name: str = Field(..., description="Name or title of the campaign idea")
    audience_fit: int = Field(..., ge=0, le=5)
    clarity: int = Field(..., ge=0, le=5)
    creativity: int = Field(..., ge=0, le=5)
    channel_suitability: int = Field(..., ge=0, le=5)
    comments: str

class IdeaEvaluationOutput(BaseModel):
    evaluations: list[IdeaEvaluation]
