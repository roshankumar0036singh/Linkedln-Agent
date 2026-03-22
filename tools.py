import os
from crewai.tools import BaseTool
from pydantic import Field
from firecrawl import FirecrawlApp

class FirecrawlSearchTool(BaseTool):
    name: str = "Firecrawl Search Tool"
    description: str = "Searches the web for the latest information on a given topic using Firecrawl. Useful for finding recent news or internship postings."
    
    def _run(self, query: str) -> str:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key or api_key == "your_firecrawl_key_here":
            return "Error: FIRECRAWL_API_KEY environment variable not set or is invalid."
            
        try:
            app = FirecrawlApp(api_key=api_key)
            result = app.search(query=query)
            
            if not result or 'data' not in result:
                return "No useful results found."
                
            summaries = []
            for item in result['data']:
                title = item.get('title', 'Unknown Title')
                url = item.get('url', '')
                description = item.get('description', '')
                summaries.append(f"Title: {title}\nURL: {url}\nSummary: {description}\n")
                
            return "\n".join(summaries)
        except Exception as e:
            return f"Error performing search: {str(e)}"
