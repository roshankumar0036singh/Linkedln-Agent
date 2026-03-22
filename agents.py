import os
from crewai import Agent, LLM
from tools import FirecrawlSearchTool

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
    
    head_agent = Agent(
        role="Lead Content Strategist",
        goal="Determine the optimal topic and structure for today's LinkedIn post for the 'Career Launchpad' channel.",
        backstory="""You are the lead strategist for 'Career Launchpad', a channel dedicated to students. 
        You decide whether today's post should be about new internship opportunities, career growth courses, 
        or general student advice. You also generate relevant hashtags.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    profiler_agent = Agent(
        role="Audience Engagement Analyst",
        goal="Analyze past performance and provide guidelines on what tone and formatting works best for students.",
        backstory="""You are a data-driven analyst. You know that students prefer clear, actionable advice, 
        bullet points, and encouraging tones. You provide guidelines to the writer on how to structure the post 
        for maximum engagement.""",
        verbose=True,
        allow_delegation=False,
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
        backstory="""You are a master copywriter. You take the research data, apply the audience guidelines, 
        and write a compelling LinkedIn post. You use appropriate emojis, whitespace, and end with an engaging question.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    publisher_agent = Agent(
        role="Publishing QA",
        goal="Review the final draft for quality and execute the publishing process.",
        backstory="""You are the final gatekeeper. You ensure the post has no placeholder text, contains the 
        correct hashtags, and is ready for LinkedIn. You return the absolute final text to be posted.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return {
        "head": head_agent,
        "profiler": profiler_agent,
        "researcher": researcher_agent,
        "writer": writer_agent,
        "publisher": publisher_agent
    }
