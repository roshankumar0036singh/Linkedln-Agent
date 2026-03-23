from crewai import Task

def create_tasks(agents):
    strategize_task = Task(
        description="""Decide on ONE specific topic for today's post based on the Content Calendar data in your backstory.
        IMPORTANT: Choose a topic that has NOT been posted recently. Check the calendar data carefully.
        Available topic categories: Software Engineering Internships, Free AI/Tech Courses, Resume Building Tips,
        Interview Preparation, Career Growth Mindset, Hackathons & Competitions, Freelancing & Side Projects,
        LinkedIn Profile Optimization.
        
        Also decide: Should this be a REGULAR post (text + image) or a CAROUSEL post (multi-slide images)?
        Use CAROUSEL for listicle content like "Top 5..." or "3 Tips for...".
        Use REGULAR for news, announcements, or single-topic deep dives.
        
        Output: The chosen topic, 3-5 hashtags, and whether it should be REGULAR or CAROUSEL.""",
        expected_output="A short paragraph with: chosen topic, list of hashtags, and post format (REGULAR or CAROUSEL).",
        agent=agents["head"]
    )

    profiling_task = Task(
        description="""Use the LinkedIn Analytics Tool to fetch engagement data from recent posts. 
        Analyze patterns and provide 4-5 specific, data-backed writing guidelines for the Writer Agent.""",
        expected_output="A bulleted list of 4-5 data-backed writing recommendations based on real analytics.",
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
        Follow the strict data-backed formatting rules provided by the Engagement Analyst.
        Include the hashtags provided by the Lead Strategist.
        The post MUST be formatted nicely with emojis, newlines, and a call to action at the end.
        CRITICAL: DO NOT use any Markdown formatting (no asterisks ** for bold, no hash # for headings, no markdown links). 
        LinkedIn only supports plain unicode text. If you want to emphasize something, use ALL CAPS or emojis.
        
        If the Strategist chose CAROUSEL format, structure the content as a series of clear, 
        numbered points (4-6 points) that can be split across carousel slides.""",
        expected_output="The full plain text of the tailored LinkedIn post without any markdown.",
        agent=agents["writer"],
        context=[strategize_task, profiling_task, research_task]
    )

    carousel_task = Task(
        description="""Check the Strategist's output to see if this should be a CAROUSEL post.
        
        IF the format is CAROUSEL:
        Take the Writer's content and EXTRACT the most important 4-6 points to create a unique 'Quick Guide' or 'Cheat Sheet'. 
        The slides MUST provide extra value and NOT just repeat the post text verbatim.
        Structure it into a JSON format for the carousel generator.
        The JSON must follow this exact format:
        {"title": "Main Title", "subtitle": "Optional subtitle", 
         "slides": [{"heading": "Slide 1 Title", "body": "Slide 1 details..."}, 
                     {"heading": "Slide 2 Title", "body": "Slide 2 details..."}],
         "cta": "Like & Follow for more!", "hashtags": "#relevant #hashtags"}
        Then use the Carousel Image Generator Tool with this JSON string.
        Output ONLY the comma-separated file paths of the generated images.
        
        IF the format is REGULAR:
        Output exactly: "SKIP_CAROUSEL - Regular post format selected."
        """,
        expected_output="Either a comma-separated string of file paths or 'SKIP_CAROUSEL - Regular post format selected.'",
        agent=agents["carousel_designer"],
        context=[strategize_task, writing_task]
    )

    image_task = Task(
        description="""Check the Strategist's output to see if this is a REGULAR or CAROUSEL post.
        
        IF REGULAR: Read the post text and craft a detailed image prompt, then use the Image Generator Tool.
        Return ONLY the final image URL.
        
        IF CAROUSEL: The carousel images already provide visuals. Output exactly: "SKIP_IMAGE - Carousel post uses its own slide visuals."
        """,
        expected_output="Either an image URL or 'SKIP_IMAGE - Carousel post uses its own slide visuals.'",
        agent=agents["creative_director"],
        context=[strategize_task, writing_task]
    )

    qa_task = Task(
        description="""Review the drafted post. Ensure it is complete, has no weird artifacts, 
        and reads perfectly. Ensure there is absolutely NO Markdown text like **bold** or ## headings anywhere in the output.
        Output ONLY the final edited post plain text, nothing else. 
        Do NOT include image URLs or file paths in your output; those are handled separately.""",
        expected_output="The absolute final plain text of the LinkedIn post, ready to be sent to the API.",
        agent=agents["publisher"],
        context=[writing_task]
    )

    return [strategize_task, profiling_task, research_task, writing_task, carousel_task, image_task, qa_task]
