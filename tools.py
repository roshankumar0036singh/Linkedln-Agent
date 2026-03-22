import os
import requests
import urllib.parse
from crewai.tools import BaseTool
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


class LinkedInAnalyticsTool(BaseTool):
    name: str = "LinkedIn Analytics Tool"
    description: str = (
        "Fetches engagement analytics (likes, comments, impressions) for recent LinkedIn posts "
        "from the Career Launchpad page. Use this to understand what content performs best."
    )

    def _run(self, query: str = "recent") -> str:
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        author_urn = os.getenv("LINKEDIN_AUTHOR_URN")

        if not access_token or not author_urn:
            return self._fallback_analytics()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # Step 1: Fetch recent posts by the author
        encoded_urn = urllib.parse.quote(author_urn, safe='')
        posts_url = (
            f"https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List({encoded_urn})"
            f"&sortBy=LAST_MODIFIED&count=10"
        )

        try:
            posts_response = requests.get(posts_url, headers=headers)
            posts_response.raise_for_status()
            posts_data = posts_response.json()

            elements = posts_data.get("elements", [])
            if not elements:
                return self._fallback_analytics()

            analytics_report = []
            for i, post in enumerate(elements[:5]):
                post_id = post.get("id", "unknown")
                text = post.get("specificContent", {}).get(
                    "com.linkedin.ugc.ShareContent", {}
                ).get("shareCommentary", {}).get("text", "")
                preview = text[:80] + "..." if len(text) > 80 else text

                # Step 2: Fetch social actions (likes/comments) for each post
                stats = self._get_social_stats(post_id, headers)

                analytics_report.append(
                    f"Post {i+1}: \"{preview}\"\n"
                    f"  Likes: {stats['likes']} | Comments: {stats['comments']}\n"
                )

            summary = "\n".join(analytics_report)
            return (
                f"REAL ENGAGEMENT DATA FROM LAST 5 POSTS:\n\n{summary}\n"
                f"Use these numbers to guide your writing recommendations."
            )

        except requests.exceptions.RequestException as e:
            print(f"LinkedIn Analytics API error: {e}")
            return self._fallback_analytics()

    def _get_social_stats(self, post_urn: str, headers: dict) -> dict:
        """Fetch like and comment counts for a specific post."""
        try:
            encoded_urn = urllib.parse.quote(post_urn, safe='')
            stats_url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}"
            response = requests.get(stats_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
            }
        except Exception:
            return {"likes": "N/A", "comments": "N/A"}

    def _fallback_analytics(self) -> str:
        """Provide reasonable heuristic guidelines when the API is not available."""
        return (
            "ANALYTICS DATA UNAVAILABLE (API keys missing or insufficient permissions).\n"
            "Using heuristic best practices instead:\n"
            "- Posts with emojis get ~20% more engagement.\n"
            "- Posts under 150 words perform best.\n"
            "- Questions at the end increase comment rates by ~30%.\n"
            "- Posts about internships tend to get more shares than course posts.\n"
            "- Posting between 8-10 AM IST gets maximum visibility for Indian students.\n"
            "Use these guidelines to instruct the Writer Agent."
        )


class ImageGeneratorTool(BaseTool):
    name: str = "Image Generator Tool"
    description: str = (
        "Generates an image based on a text prompt. Provide a detailed visual description "
        "and the tool will return the URL of the generated image. Use for LinkedIn post images."
    )

    def _run(self, prompt: str) -> str:
        """
        Uses Pollinations.ai (free, no API key needed) to generate an image.
        Returns the URL of the generated image.
        """
        try:
            # Pollinations provides a direct URL-based image generation API
            encoded_prompt = urllib.parse.quote(prompt)
            image_url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1200&height=627&nologo=true"
            )

            # Verify the URL is accessible (use GET with stream to trigger generation)
            response = requests.get(image_url, timeout=120, stream=True)
            if response.status_code == 200:
                response.close()
                return (
                    f"IMAGE GENERATED SUCCESSFULLY!\n"
                    f"Image URL: {image_url}\n"
                    f"This image is 1200x627px (optimal LinkedIn size)."
                )
            else:
                response.close()
                return f"Image generation returned status {response.status_code}. URL: {image_url}"

        except Exception as e:
            return f"Error generating image: {str(e)}"


class CarouselImageGeneratorTool(BaseTool):
    name: str = "Carousel Image Generator Tool"
    description: str = (
        "Generates multiple separate slide images for a LinkedIn carousel post. "
        "Input must be a JSON string with this format: "
        '{"title": "Main Title", "subtitle": "Optional", '
        '"slides": [{"heading": "Slide Title", "body": "Slide content"}], '
        '"cta": "Follow for more!", "hashtags": "#Career #Internships"}. '
        "Returns a comma-separated string of file paths to the generated images."
    )

    def _run(self, slides_json: str) -> str:
        try:
            from carousel_generator import generate_carousel_pdf
            # Actually generates images now, returned as comma-separated paths
            image_paths = generate_carousel_pdf(slides_json)
            if image_paths.startswith("ERROR"):
                return image_paths
            return f"CAROUSEL IMAGES GENERATED SUCCESSFULLY!\nFile paths: {image_paths}"
        except Exception as e:
            return f"Error generating carousel images: {str(e)}"

