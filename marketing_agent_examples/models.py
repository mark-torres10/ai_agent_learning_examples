from pydantic import BaseModel

class ProposedIdea(BaseModel):
    idea: str
    audience: str
    campaign_message: str
    concept: str

class ProposedIdeasWrapper(BaseModel):
    ideas: list[ProposedIdea]
