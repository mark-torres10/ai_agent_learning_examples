from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

from marketing_agent_examples.models import (
    BlogPost,
    BlogPostEvaluation,
    BlogPostWithEvaluation,
    EmailBlastDraft,
    EmailBlastDraftEvaluation,
    EmailBlastDraftWithEvaluation,
    IdeaEvaluation,
    IdeaEvaluationOutput,
    IdeaWithEvaluation,
    ProposedIdea,
    ProposedIdeasWrapper,
    SocialMediaPost,
    SocialMediaPostEvaluation,
    SocialMediaPostWithEvaluation,
    SocialMediaPostsWrapper,
)

class SocialMediaCampaignIdeaGenerationAgent:
    """AI agent that creates ideas for a social media campaign.
    
    It will, given a spec for a social media campaign:
    1. Creates ideas to promote.
    2. Evaluates the ideas and selects the best one.
    """
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    def generate_ideas(self) -> ProposedIdeasWrapper:
        parser = PydanticOutputParser(pydantic_object=ProposedIdeasWrapper)
        idea_generation_instructions = parser.get_format_instructions()
        prompt = PromptTemplate(
            template="""
                You are an expert marketing agent helping a neighborhood American-style brunch restaurant design a creative and targeted marketing campaign. You will be given product offerings and a target audience. Your job is to generate 5–7 campaign ideas that highlight the value of the offerings and appeal to the specific interests of the audience segments.

                Client: Independent American-style brunch restaurant known for quality and community.

                Product offerings to highlight:
                1. Budget-friendly $9.99 full breakfast combo — includes 2 eggs, choice of meat (bacon, sausage, or veggie patty), breakfast potatoes, fresh fruit, and coffee.
                2. Hearty and nutritious Mediterranean wrap — packed with veggies and lean protein, great for health-conscious diners.
                3. Popular $20.99 all-you-can-eat Sunday brunch buffet — includes full breakfast classics (eggs, pancakes, waffles, bacon, sausage, hash browns, omelets) and lunch options (salad bar, seasonal meats, and sides).

                Target audience:
                - Families looking for weekend outings
                - Health-conscious individuals seeking nutritious, flavorful options
                - Social brunch groups celebrating milestones or gathering casually

                Output:
                - A list of 5-7 specific marketing campaign ideas
                - Each idea should include a title and a 2-3 sentence explanation
                - Tailor each idea to one or more of the audience segments
                - Highlight value, experience, or emotional appeal

                {format_instructions}
            """,
            input_variables=[],
            partial_variables={
                "format_instructions": idea_generation_instructions            }
        )
        prompt_text = prompt.format()
        messages = [
            SystemMessage(content="You are a helpful social media marketing agent."),
            HumanMessage(content=prompt_text)
        ]
        response = self.llm.invoke(messages)
        return parser.parse(response.content)

    def evaluate_ideas(self, ideas: ProposedIdeasWrapper) -> IdeaEvaluationOutput:
        parser = PydanticOutputParser(pydantic_object=IdeaEvaluationOutput)
        idea_evaluation_instructions = parser.get_format_instructions()
        prompt = PromptTemplate(
            template="""
                You are a senior marketing strategist evaluating proposed campaign ideas for an American-style brunch restaurant.

                Evaluate each idea on the following criteria (score from 0-5):
                - **Audience Fit**: Does it match the needs or preferences of the specified audience?
                - **Clarity**: Is the idea easy to understand and well-articulated?
                - **Creativity**: How original or compelling is the campaign concept?
                - **Channel Suitability**: Does the distribution method or concept fit real-world marketing channels (e.g., Instagram, flyers, email)?

                Also include brief **comments** on the strengths or weaknesses of each idea.

                Here are the proposed ideas to review:
                {idea_text}

                {evaluation_instructions}
            """,
            input_variables=["idea_text"],
            partial_variables={"evaluation_instructions": idea_evaluation_instructions}
        )
        idea_text = self.format_ideas_for_evaluation(ideas.ideas)
        prompt_text = prompt.format(idea_text=idea_text)
        messages = [
            SystemMessage(content="You are a helpful social media marketing agent."),
            HumanMessage(content=prompt_text)
        ]
        response = self.llm.invoke(messages)
        return parser.parse(response.content)

    def format_ideas_for_evaluation(self, ideas: list[ProposedIdea]) -> str:
        result = []
        for i, idea in enumerate(ideas, 1):
            result.append(f"""
                Idea {i}:
                Audience: {idea.audience}
                Name: {idea.idea}
                Message: {idea.campaign_message}
                Concept: {idea.concept}
            """
            )
        return "\n\n".join(result)

    def save_ideas_and_evaluations(self, ideas: ProposedIdeasWrapper, evaluations: IdeaEvaluationOutput):
        self.ideas_with_evaluations: list[IdeaWithEvaluation] = []
        ideas: list[ProposedIdea] = ideas.ideas
        evaluations: list[IdeaEvaluation] = evaluations.evaluations
        for (idea, evaluation) in zip(ideas, evaluations):
            self.ideas_with_evaluations.append(IdeaWithEvaluation(idea=idea, evaluation=evaluation))

    def score_ideas(self) -> list[int]:
        scores = []
        for idea_with_evaluation in self.ideas_with_evaluations:
            score = (
                idea_with_evaluation.evaluation.audience_fit +
                idea_with_evaluation.evaluation.clarity +
                idea_with_evaluation.evaluation.creativity +
                idea_with_evaluation.evaluation.channel_suitability
            )
            scores.append(score)
        return scores

    def select_best_ideas(self, total_ideas: int) -> ProposedIdea:
        scores = self.score_ideas()
        best_ideas = []
        for _ in range(total_ideas):
            best_idea = max(self.ideas_with_evaluations, key=lambda x: scores[x.index])
            best_ideas.append(best_idea)
            self.ideas_with_evaluations.remove(best_idea)
        return best_ideas

    def generate_and_return_best_ideas(self, total_ideas: int = 1) -> ProposedIdea:
        ideas = self.generate_ideas()
        evaluations = self.evaluate_ideas(ideas)
        self.save_ideas_and_evaluations(ideas, evaluations)
        return self.select_best_ideas(total_ideas)
    
class BlogPostAgent:
    """AI agent that creates a blog post.
    
    It will, given a spec for a blog post:
    1. Create a blog post.
    2. Evaluate the blog post.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

        self.blog_post_parser = PydanticOutputParser(pydantic_object=BlogPost)
        self.blog_post_evaluation_parser = PydanticOutputParser(pydantic_object=BlogPostEvaluation)

        self.blog_post = None
        self.blog_post_evaluation = None

    def create_blog_post(self, idea: ProposedIdea) -> BlogPost:
        blog_prompt = PromptTemplate(
            template="""
                You are a content marketer creating a blog post for an American-style brunch restaurant.

                Your job is to write an SEO-optimized blog post based on the following campaign idea:

                <idea>
                Name: {idea_name}
                Target Audience: {audience}
                Campaign Message: {message}
                Concept: {concept}
                </idea>

                You must optimize this blog post for:
                - **Search Engine Visibility**: Use high-intent brunch-related keywords naturally throughout.
                - **Click-Through Rate**: Title and excerpt should be emotionally compelling, clear, and benefit-driven.
                - **Engagement**: Structure the content with subheadings, short paragraphs, and a clear flow.
                - **Audience Fit**: Make the tone match the specified audience. You may include humor, warmth, or health-focused language if appropriate.

                Output Format:
                {format_instructions}

                Success is defined as:
                - The title is both SEO-relevant and emotionally appealing.
                - The excerpt would make a reader want to click through.
                - The content clearly communicates the campaign idea while being useful, fun, and on-brand.
                - Keywords are relevant and well-targeted to brunch-goers and local audiences.
        """,
            input_variables=["idea_name", "audience", "message", "concept"],
            partial_variables={"format_instructions": self.blog_post_parser.get_format_instructions()}
        )
        blog_post_full_prompt = blog_prompt.format(
            idea_name=idea.idea,
            audience=idea.audience,
            message=idea.campaign_message,
            concept=idea.concept
        )
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=blog_post_full_prompt)
        ]
        response = self.llm.invoke(messages)
        return self.blog_post_parser.parse(response.content)

    def evaluate_blog_post(self, blog_post: BlogPost) -> BlogPostEvaluation:
        blog_post_evaluation_prompt = PromptTemplate(
            template="""
                You are a senior SEO content editor evaluating a blog post for an American-style brunch restaurant.

                Evaluate the post based on the following 5 criteria (0-5 scale):
                - **SEO Optimization**: Does the post use relevant keywords naturally? Is the title and excerpt search-friendly? Are metadata fields filled?
                - **Clickability**: Does the title and excerpt compel users to click? Is there emotional or benefit-driven language?
                - **Readability**: Is the post well-structured with good formatting (headings, paragraph length, etc)?
                - **Audience Fit**: Is the tone and language tailored to the intended audience?
                - **Content Quality**: Is it engaging, informative, and clear?

                Also provide 2-3 sentences of comments on strengths and areas for improvement.

                Blog post to evaluate:

                Title: {title}
                Slug: {slug}
                Excerpt: {excerpt}
                Content: {content}
                Keywords: {keywords}

                {format_instructions}
        """,
            input_variables=["title", "slug", "excerpt", "content", "keywords"],
            partial_variables={"format_instructions": self.blog_post_evaluation_parser.get_format_instructions()}
        )
        prompt_text = blog_post_evaluation_prompt.format(
            title=blog_post.title,
            slug=blog_post.slug,
            excerpt=blog_post.excerpt,
            content=blog_post.content,
            keywords=", ".join(blog_post.keywords),
        )

        messages = [
            SystemMessage(content="You are a helpful evaluator of marketing content."),
            HumanMessage(content=prompt_text)
        ]

        response = self.llm.invoke(messages)
        return self.blog_post_evaluation_parser.parse(response.content)

    def create_and_evaluate_blog_post(self, idea: ProposedIdea) -> BlogPostEvaluation:
        self.blog_post = self.create_blog_post(idea)
        self.blog_post_evaluation = self.evaluate_blog_post(self.blog_post)
        self.blog_post_with_evaluation = BlogPostWithEvaluation(blog_post=self.blog_post, evaluation=self.blog_post_evaluation)
        return self.blog_post_with_evaluation
    
class EmailBlastDraftAgent:
    """AI agent that creates an email blast draft.

    It will, given a spec for an email blast draft:
    1. Create an email blast draft.
    2. Evaluate the email blast draft.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

        self.email_blast_draft_parser = PydanticOutputParser(pydantic_object=EmailBlastDraft)
        self.email_blast_draft_evaluation_parser = PydanticOutputParser(pydantic_object=EmailBlastDraftEvaluation)

        self.email_blast_draft = None
        self.email_blast_draft_evaluation = None

    def create_email_blast_draft(self, idea: ProposedIdea, blog_post: BlogPost) -> EmailBlastDraft:
        email_blast_draft_prompt = PromptTemplate(
            template="""
                You are an email marketing expert creating a launch email for a brunch restaurant's new campaign.

                You are provided with:
                <idea>
                Name: {idea_name}
                Audience: {audience}
                Campaign Message: {campaign_message}
                Concept: {concept}
                </idea>

                <blog_post>
                Title: {title}
                Excerpt: {excerpt}
                Content: {content}
                Keywords: {keywords}
                </blog_post>

                Write a short, emotionally engaging email blast targeted at the given audience. It should:
                - Grab attention in the subject line and preview text
                - Use a warm, persuasive tone that matches the audience
                - Summarize the blog post clearly and concisely
                - Lead to a strong call to action (CTA)
                - Be optimized for both desktop and mobile readers

                {format_instructions}

                Also include an explanation of why this CTA was chosen for this audience and what kind of behavioral response is expected.
        """,
            input_variables=["idea_name", "audience", "campaign_message", "concept", "title", "excerpt", "content", "keywords"],
            partial_variables={"format_instructions": self.email_blast_draft_parser.get_format_instructions()}
        )
        prompt_text = email_blast_draft_prompt.format(
            idea_name=idea.idea,
            audience=idea.audience,
            campaign_message=idea.campaign_message,
            concept=idea.concept,
            title=blog_post.title,
            excerpt=blog_post.excerpt,
            content=blog_post.content,
            keywords=", ".join(blog_post.keywords)
        )

        messages = [
            SystemMessage(content="You are a skilled marketing copywriter and strategist."),
            HumanMessage(content=prompt_text)
        ]

        response = self.llm.invoke(messages)
        return self.email_blast_draft_parser.parse(response.content)

    def evaluate_email_blast_draft(self, email_blast_draft: EmailBlastDraft) -> EmailBlastDraftEvaluation:
        email_blast_draft_evaluation_prompt = PromptTemplate(
            template="""
                You are a senior email marketing strategist evaluating the quality of a marketing email blast.

                Evaluate the email based on the following criteria (0-5 scale):

                - **Subject Effectiveness**: Is the subject line likely to drive opens?
                - **Preview Quality**: Does the preview text complement the subject and generate curiosity?
                - **Message Clarity**: Is the message clear, persuasive, and well-structured?
                - **CTA Strength**: Is the call-to-action obvious, relevant, and likely to convert?
                - **Tone Fit**: Does the tone match the target audience and campaign intent?

                Also provide 2-3 sentences of overall comments on strengths and areas for improvement.

                Here is the email blast to evaluate:

                Subject: {subject_line}  
                Preview: {preview_text}  
                Body: {body}  
                Call to Action: {cta}  
                Explanation: {explanation}

                {format_instructions}
            """,
            input_variables=["subject_line", "preview_text", "body", "cta", "explanation"],
            partial_variables={"format_instructions": self.email_blast_draft_evaluation_parser.get_format_instructions()}
        )
        prompt_text = email_blast_draft_evaluation_prompt.format(
            subject_line=email_blast_draft.subject_line,
            preview_text=email_blast_draft.preview_text,
            body=email_blast_draft.body,
            cta=email_blast_draft.call_to_action,
            explanation=email_blast_draft.explanation
        )

        messages = [
            SystemMessage(content="You are a helpful evaluator of email marketing content."),
            HumanMessage(content=prompt_text)
        ]

        response = self.llm.invoke(messages)
        return self.email_blast_draft_evaluation_parser.parse(response.content)
    
    def create_and_evaluate_email_blast_draft(self, idea: ProposedIdea) -> EmailBlastDraftWithEvaluation:
        self.email_blast_draft: EmailBlastDraft = self.create_email_blast_draft(idea)
        self.email_blast_draft_evaluation: EmailBlastDraftEvaluation = self.evaluate_email_blast_draft(self.email_blast_draft)
        self.email_blast_draft_with_evaluation = EmailBlastDraftWithEvaluation(
            email_blast_draft=self.email_blast_draft,
            evaluation=self.email_blast_draft_evaluation
        )
        return self.email_blast_draft_with_evaluation

class SocialMediaPostAgent:
    def __init__(self, num_posts: int = 10):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

        self.social_media_posts_parser = PydanticOutputParser(pydantic_object=SocialMediaPostsWrapper)
        self.social_media_post_evaluation_parser = PydanticOutputParser(pydantic_object=SocialMediaPostEvaluation)

        self.social_media_posts = None
        self.social_media_post_evaluations = None

        self.num_posts = num_posts


    def create_social_media_posts(self, idea: ProposedIdea, blog_post: BlogPost, email_blast_draft: EmailBlastDraft, num_posts: Optional[int] = None) -> SocialMediaPostsWrapper:
        if num_posts is None:
            num_posts = self.num_posts

        social_media_posts_prompt = PromptTemplate(
            template="""
                You are a social media strategist creating platform-specific posts for an American-style brunch restaurant.

                You are given:
                <idea>
                Name: {idea_name}
                Audience: {audience}
                Message: {campaign_message}
                Concept: {concept}
                </idea>

                <blog_post>
                Title: {title}
                Excerpt: {excerpt}
                Content: {content}
                Keywords: {keywords}
                </blog_post>

                <email_blast>
                Subject: {subject_line}
                Preview: {preview_text}
                Body: {body}
                Call to Action: {call_to_action}
                </email_blast>

                Create {num_posts} social media posts that are:
                - Optimized for either Facebook or Instagram
                - Tailored to the campaign audience
                - Emotionally compelling, easy to skim, and visually suggestive
                - Short enough for quick consumption
                - Include relevant and popular hashtags
                - Include the *intended ad targeting audience* (e.g., young professionals in urban areas, families with kids, health-conscious millennials, etc.)

                Output format:
                {format_instructions}
        """,
            input_variables=[
                "idea_name", "audience", "campaign_message", "concept",
                "title", "excerpt", "content", "keywords",
                "subject_line", "preview_text", "body", "call_to_action",
                "num_posts"
            ],
            partial_variables={"format_instructions": self.social_media_posts_parser.get_format_instructions()}
        )
        prompt_text = social_media_posts_prompt.format(
            idea_name=idea.idea,
            audience=idea.audience,
            campaign_message=idea.campaign_message,
            concept=idea.concept,
            title=blog_post.title,
            excerpt=blog_post.excerpt,
            content=blog_post.content,
            keywords=", ".join(blog_post.keywords),
            subject_line=email_blast_draft.subject_line,
            preview_text=email_blast_draft.preview_text,
            body=email_blast_draft.body,
            call_to_action=email_blast_draft.call_to_action,
            num_posts=num_posts
        )
        messages = [
            SystemMessage(content="You are a creative social media strategist."),
            HumanMessage(content=prompt_text)
        ]
        response = self.llm.invoke(messages)
        return self.social_media_posts_parser.parse(response.content)

    def evaluate_social_media_post(self, post: SocialMediaPost) -> SocialMediaPostEvaluation:
        social_media_post_evaluation_prompt = PromptTemplate(
            template="""
                You are a social media marketing expert evaluating a post for a brunch restaurant campaign.

                Rate the post on a 0-5 scale for each of the following criteria:

                - **Platform Fit**: Does it suit the norms of the target platform?
                - **Audience Alignment**: Does the tone, message, and offer resonate with the specified audience?
                - **Engagement Potential**: Is it likely to attract likes, comments, shares, or clicks?
                - **Hashtag Relevance**: Are the hashtags appropriate, effective, and not overused?
                - **Clarity & Appeal**: Is the message understandable and emotionally appealing?

                Also provide a few sentences of feedback on what works and what could be improved.

                Here is the post:

                Platform: {platform}  
                Content: {content}  
                Hashtags: {hashtags}  
                Targeting Audience: {audience}

                {format_instructions}
        """,
            input_variables=["platform", "content", "hashtags", "audience"],
            partial_variables={"format_instructions": self.social_media_post_evaluation_parser.get_format_instructions()}
        )
        prompt_text = social_media_post_evaluation_prompt.format(
            platform=post.platform,
            content=post.content,
            hashtags=", ".join(post.hashtags),
            audience=post.intended_audience
        )

        messages = [
            SystemMessage(content="You are a helpful evaluator of social media content."),
            HumanMessage(content=prompt_text)
        ]

        response = self.llm.invoke(messages)
        return self.social_media_post_evaluation_parser.parse(response.content)

    def evaluate_social_media_posts(self, posts: SocialMediaPostsWrapper) -> list[SocialMediaPostEvaluation]:
        result: list[SocialMediaPostEvaluation] = []
        for i, post in enumerate(posts.posts):
            total_posts = len(posts.posts)
            if i % 5 == 0:
                print(f"Evaluating post {i} of {total_posts}")
            result.append(self.evaluate_social_media_post(post))
        return result

    def create_and_evaluate_social_media_posts(self, idea: ProposedIdea, blog_post: BlogPost, email_blast_draft: EmailBlastDraft) -> list[SocialMediaPostWithEvaluation]:
        self.social_media_posts = self.create_social_media_posts(idea, blog_post, email_blast_draft)
        self.social_media_post_evaluations = self.evaluate_social_media_posts(self.social_media_posts)
        return [
            SocialMediaPostWithEvaluation(
                social_media_post=post,
                evaluation=evaluation
            ) for post, evaluation in zip(self.social_media_posts.posts, self.social_media_post_evaluations)
        ]

class SocialMediaCampaignAgent:
    """AI agent that creates a social media campaign.
    
    It will, given a spec for a social media campaign:
    1. Creates a blog post for the best idea.
    2. Evaluate the blog post.
    3. Create a draft of an email blast given the idea and blog post.
    4. Evaluate the email blast draft.
    5. Create social media posts given the idea, blog post, and email blast draft.
    6. Evaluate the social media posts.
    """
    def __init__(self):
        self.blog_post_agent = BlogPostAgent()
        self.email_blast_draft_agent = EmailBlastDraftAgent()
        self.social_media_campaign_agent = SocialMediaCampaignAgent()

    def run(self, idea: ProposedIdea):
        # 1. Create and evaluate blog post
        blog_post_with_eval: BlogPostWithEvaluation = self.blog_post_agent.create_and_evaluate_blog_post(idea)

        # 2. Create and evaluate email blast draft
        email_blast_with_eval: EmailBlastDraftWithEvaluation = self.email_blast_draft_agent.create_and_evaluate_email_blast_draft(
            idea=idea,
            blog_post=blog_post_with_eval.blog_post
        )

        # 3. Create and evaluate social media posts
        social_posts_with_eval: list[SocialMediaPostWithEvaluation] = self.social_media_post_agent.create_and_evaluate_social_media_posts(
            idea=idea,
            blog_post=blog_post_with_eval.blog_post,
            email_blast_draft=email_blast_with_eval.email_blast_draft
        )

        return {
            "blog_post": blog_post_with_eval,
            "email_blast": email_blast_with_eval,
            "social_posts": social_posts_with_eval
        }
    
class SocialMediaManager:
    """Orchestrator that runs the full social media campaign pipeline."""
    def __init__(self):
        self.idea_generator = SocialMediaCampaignIdeaGenerationAgent()
        self.campaign_agent = SocialMediaCampaignAgent()

    def run_full_campaign(self):
        # 1. Generate and select best idea
        best_idea: ProposedIdea = self.idea_generator.generate_and_return_best_ideas(total_ideas=1)[0]

        # 2. Run full campaign creation pipeline for that idea
        campaign_outputs = self.campaign_agent.run(best_idea)

        return {
            "idea": best_idea,
            **campaign_outputs
        }
