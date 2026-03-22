import os
import requests

def post_to_linkedin(text_content: str) -> str:
    """
    Posts content to LinkedIn using the REST API.
    Returns the URL of the created post or an error message.
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")
    
    if not access_token or not author_urn or access_token == "your_linkedin_access_token":
        print("--- DRY RUN / MISSING KEYS ---")
        print("Would have posted to LinkedIn:")
        print(text_content)
        print("------------------------------")
        return "DRY RUN: Post successfully simulated."
        
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Successfully posted to LinkedIn! ID: {response.json().get('id')}"
    except requests.exceptions.RequestException as e:
        return f"Failed to post to LinkedIn. Error: {str(e)}"
