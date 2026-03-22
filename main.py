import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_agents
from tasks import create_tasks
from linkedin_client import post_to_linkedin

# Load environment variables
load_dotenv()

def run_agentic_workflow():
    print("Initiating LinkedIn Agentic Workflow...")
    
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
    
    raw_result = result.raw
    print(raw_result)
    
    print("\nAttempting to post to LinkedIn...")
    # Attempt to post (will fallback to DRY RUN if keys are missing)
    post_response = post_to_linkedin(raw_result)
    print(post_response)

if __name__ == "__main__":
    run_agentic_workflow()
