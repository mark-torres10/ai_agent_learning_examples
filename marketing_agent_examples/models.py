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

class BlogPost(BaseModel):
    title: str = Field(..., description="SEO-optimized title of the blog post")
    slug: str = Field(..., description="URL-friendly slug version of the title")
    excerpt: str = Field(..., description="1-2 sentence summary that entices the reader")
    content: str = Field(..., description="Main blog content (approx. 300-500 words), formatted with headings and paragraphs")
    keywords: list[str] = Field(..., description="List of SEO keywords relevant to the post")