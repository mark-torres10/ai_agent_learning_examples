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

class BlogPostEvaluation(BaseModel):
    seo_optimization: int = Field(..., ge=0, le=5)
    clickability: int = Field(..., ge=0, le=5)
    readability: int = Field(..., ge=0, le=5)
    audience_fit: int = Field(..., ge=0, le=5)
    content_quality: int = Field(..., ge=0, le=5)
    comments: str

class EmailBlastDraft(BaseModel):
    subject_line: str = Field(..., description="The email's subject line, optimized for opens")
    preview_text: str = Field(..., description="Short preview text shown in email clients")
    body: str = Field(..., description="Main email body, in simple HTML or plain text format")
    call_to_action: str = Field(..., description="Clear and concise call-to-action phrase")
    explanation: str = Field(..., description="Explanation of why this CTA was chosen for this audience and what user response is expected")

class EmailBlastDraftEvaluation(BaseModel):
    subject_effectiveness: int = Field(..., ge=0, le=5)
    preview_quality: int = Field(..., ge=0, le=5)
    message_clarity: int = Field(..., ge=0, le=5)
    cta_strength: int = Field(..., ge=0, le=5)
    tone_fit: int = Field(..., ge=0, le=5)
    comments: str
