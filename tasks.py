from crewai import Task

def create_tasks(agents):
    strategize_task = Task(
        description="""Decide on ONE specific topic for today's post. 
        Options: 1. Software Engineering Internships, 2. Free AI/Tech Courses, 3. Resume Building Tips.
        Output exactly what the topic is and 3-5 relevant hashtags.""",
        expected_output="A short paragraph declaring the chosen topic and a list of hashtags.",
        agent=agents["head"]
    )
    
    profiling_task = Task(
        description="""Provide 3-4 structural guidelines for how to write for the 'Career Launchpad' audience (students).
        Focus on readability and engagement.""",
        expected_output="A bulleted list of 3-4 writing guidelines (e.g., use emojis, keep paragraphs short).",
        agent=agents["profiler"]
    )
    
    research_task = Task(
        description="""Using the topic from the Lead Strategist, use your Firecrawl Search Tool 
        to find 2-3 real, recent opportunities, links, or facts related to the topic. 
        Provide the details and URLs so the writer can use them.
        Make sure you actually use the search tool to find recent information.""",
        expected_output="A compiled list of facts, links, or opportunities related to the active topic.",
        agent=agents["researcher"],
        context=[strategize_task]
    )
    
    writing_task = Task(
        description="""Write the final LinkedIn post. 
        Incorporate the research provided by the Researcher.
        Follow the strict formatting rules provided by the Audience Analyst.
        Include the hashtags provided by the Lead Strategist.
        The post MUST be formatted nicely with emojis, newlines, and a call to action at the end.
        CRITICAL: DO NOT use any Markdown formatting (no asterisks ** for bold, no hash # for headings, no markdown links). 
        LinkedIn only supports plain unicode text. If you want to emphasize something, use ALL CAPS or emojis.""",
        expected_output="The full plain text of the tailored LinkedIn post without any markdown.",
        agent=agents["writer"],
        context=[strategize_task, profiling_task, research_task]
    )
    
    qa_task = Task(
        description="""Review the drafted post. Ensure it is complete, has no weird artifacts, 
        and reads perfectly. Ensure there is absolutely NO Markdown text like **bold** or ## headings anywhere in the output.
        Output ONLY the final edited post plain text, nothing else.""",
        expected_output="The absolute final plain text of the LinkedIn post, ready to be sent to the API.",
        agent=agents["publisher"],
        context=[writing_task]
    )
    
    return [strategize_task, profiling_task, research_task, writing_task, qa_task]
