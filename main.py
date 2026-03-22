import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_agents
from tasks import create_tasks
from linkedin_client import post_to_linkedin, post_carousel_to_linkedin
from content_calendar import log_post

# Load environment variables
load_dotenv()


def extract_image_url(crew_result) -> str:
    """Extract the image URL from the Creative Director task output."""
    try:
        tasks_output = crew_result.tasks_output
        # Image task is index 5 (strategy=0, profiling=1, research=2, writing=3, carousel=4, image=5, qa=6)
        image_output = tasks_output[5].raw if len(tasks_output) > 5 else ""

        if "SKIP_IMAGE" in image_output:
            return ""

        for line in image_output.split("\n"):
            line = line.strip()
            if "image.pollinations.ai" in line:
                start = line.find("https://image.pollinations.ai")
                if start != -1:
                    url = line[start:].split(" ")[0].split(")")[0]
                    return url
            elif line.startswith("http"):
                return line.split(" ")[0]

        return ""
    except Exception as e:
        print(f"Could not extract image URL: {e}")
        return ""


def extract_carousel_path(crew_result) -> str:
    """Extract the carousel PDF file path from the Carousel Designer task output."""
    try:
        tasks_output = crew_result.tasks_output
        # Carousel task is index 4
        carousel_output = tasks_output[4].raw if len(tasks_output) > 4 else ""

        if "SKIP_CAROUSEL" in carousel_output:
            return ""

        for line in carousel_output.split("\n"):
            line = line.strip()
            if line.endswith(".pdf") or ".pdf" in line:
                # Extract file path
                for word in line.split():
                    if ".pdf" in word:
                        return word
        return ""
    except Exception as e:
        print(f"Could not extract carousel path: {e}")
        return ""


def extract_topic_from_strategy(crew_result) -> str:
    """Extract the chosen topic from the Strategist's output for the content calendar."""
    try:
        tasks_output = crew_result.tasks_output
        strategy_output = tasks_output[0].raw if len(tasks_output) > 0 else ""
        # Return first 50 chars as topic identifier
        return strategy_output[:50].strip()
    except Exception:
        return "Unknown Topic"


def run_agentic_workflow():
    print("=" * 60)
    print("LinkedIn Agentic Workflow v3")
    print("Features: Analytics + Image Gen + Content Calendar + Carousel")
    print("=" * 60)

    # Initialize agents and tasks
    agents_dict = create_agents()
    tasks_list = create_tasks(agents_dict)

    # Form the crew
    linkedin_crew = Crew(
        agents=list(agents_dict.values()),
        tasks=tasks_list,
        process=Process.sequential,
        verbose=True
    )

    # Execute workflow
    result = linkedin_crew.kickoff()

    print("\n==================================")
    print("WORKFLOW COMPLETE. FINAL POST DRAFT:")
    print("==================================\n")

    # The QA task (last task) gives us the final post text
    final_post = result.raw
    print(final_post)

    # Extract carousel PDF path (if any)
    carousel_path = extract_carousel_path(result)
    # Extract image URL (if any)
    image_url = extract_image_url(result)

    if carousel_path and os.path.exists(carousel_path):
        print(f"\nCarousel PDF detected: {carousel_path}")
        print("Posting as a LinkedIn Document post...")
        post_response = post_carousel_to_linkedin(final_post, carousel_path)
    elif image_url:
        print(f"\nGenerated Image URL: {image_url}")
        print("Posting with image...")
        post_response = post_to_linkedin(final_post, image_url=image_url)
    else:
        print("\nNo image or carousel. Posting text-only.")
        post_response = post_to_linkedin(final_post)

    print(post_response)

    # Log to content calendar
    topic = extract_topic_from_strategy(result)
    log_post(topic, final_post)
    print(f"\nLogged to content calendar: {topic}")


if __name__ == "__main__":
    run_agentic_workflow()
