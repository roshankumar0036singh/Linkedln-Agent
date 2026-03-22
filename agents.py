import os
from crewai import Agent, LLM
from tools import (
    FirecrawlSearchTool, LinkedInAnalyticsTool,
    ImageGeneratorTool, CarouselImageGeneratorTool
)
from content_calendar import get_topic_summary

def get_mistral_llm():
    key = os.getenv("MISTRAL_API_KEY")
    if not key or key == "your_mistral_key_here":
        print("WARNING: MISTRAL_API_KEY is not set correctly in your environment.")

    return LLM(
        model="mistral/mistral-large-latest",
        temperature=0.7,
        api_key=key
    )

def create_agents():
    llm = get_mistral_llm()
    search_tool = FirecrawlSearchTool()
    analytics_tool = LinkedInAnalyticsTool()
    image_tool = ImageGeneratorTool()
    carousel_tool = CarouselImageGeneratorTool()

    # Fetch content calendar context for the Head Agent
    calendar_context = get_topic_summary()

    head_agent = Agent(
        role="Lead Content Strategist",
        goal="Determine the optimal topic for today's LinkedIn post for the 'Career Launchpad' channel, avoiding recently covered topics.",
        backstory=f"""You are the lead strategist for 'Career Launchpad', a channel dedicated to students. 
        You decide the topic based on the Content Calendar below, which shows what was posted recently.
        ALWAYS pick a FRESH topic that hasn't been posted in the last few days.
        You also generate relevant hashtags and decide whether today's post should be a 
        REGULAR post (text + image) or a CAROUSEL post (multi-slide PDF document).
        Carousel posts work best for listicle content like "Top 5 Internships" or "3 Resume Tips".
        
        CONTENT CALENDAR DATA:
        {calendar_context}""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    profiler_agent = Agent(
        role="Data-Driven Engagement Analyst",
        goal="Fetch real engagement analytics from past LinkedIn posts and provide data-backed guidelines to the Writer.",
        backstory="""You are a data-driven analyst with access to LinkedIn Analytics. 
        Your job is to use the LinkedIn Analytics Tool to fetch real engagement data (likes, comments, impressions) 
        from recent posts. You analyze patterns and output specific, data-backed 
        writing recommendations for the Writer Agent to follow.""",
        verbose=True,
        allow_delegation=False,
        tools=[analytics_tool],
        llm=llm
    )

    researcher_agent = Agent(
        role="Career Opportunities Researcher",
        goal="Find the latest news, internships, or courses related to the topic provided by the Strategist.",
        backstory="""You are an expert web researcher. Using the Firecrawl tool, you find actual, up-to-date 
        links and details about internships or courses to include in the post.""",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=llm
    )

    writer_agent = Agent(
        role="Content Curator and Writer",
        goal="Draft an engaging, highly-readable LinkedIn post tailored for students.",
        backstory="""You are a master copywriter. You take the research data, apply the data-backed audience 
        guidelines from the Analyst, and write a compelling LinkedIn post. You use appropriate emojis, 
        whitespace, and end with an engaging question. You NEVER use Markdown formatting.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    carousel_designer = Agent(
        role="Carousel Content Designer",
        goal="Design and generate multiple slide images for a LinkedIn carousel post when requested.",
        backstory="""You are a content designer who specializes in creating LinkedIn carousel posts.
        When the Strategist decides a CAROUSEL format is best, you take the Writer's content and 
        restructure it into a slide-by-slide JSON format, then use the Carousel Image Generator Tool 
        to create the actual image files. You output ONLY the comma-separated file paths of the generated images.""",
        verbose=True,
        allow_delegation=False,
        tools=[carousel_tool],
        llm=llm
    )

    creative_director = Agent(
        role="Creative Director",
        goal="Generate a stunning, eye-catching image to accompany the LinkedIn post.",
        backstory="""You are a visual creative director. After the Writer produces the post text, 
        you read it and craft a detailed image generation prompt. The image should be professional, 
        vibrant, and relevant to the post topic. 
        Use the Image Generator Tool to create the image and return ONLY the image URL.""",
        verbose=True,
        allow_delegation=False,
        tools=[image_tool],
        llm=llm
    )

    publisher_agent = Agent(
        role="Publishing QA",
        goal="Review the final draft for quality and execute the publishing process.",
        backstory="""You are the final gatekeeper. You ensure the post has no placeholder text, contains the 
        correct hashtags, no Markdown formatting, and is ready for LinkedIn. You return the absolute final text to be posted.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return {
        "head": head_agent,
        "profiler": profiler_agent,
        "researcher": researcher_agent,
        "writer": writer_agent,
        "carousel_designer": carousel_designer,
        "creative_director": creative_director,
        "publisher": publisher_agent
    }
