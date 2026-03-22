import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("LINKEDIN_ACCESS_TOKEN")
urn = os.getenv("LINKEDIN_AUTHOR_URN")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

# 1. Register Image Upload
print("\n--- Testing Multi-Image Post Registration ---")
register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
payload_reg = {
    "registerUploadRequest": {
        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
        "owner": urn,
        "serviceRelationships": [
            {
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }
        ]
    }
}

try:
    # We won't actually upload a binary here, just test if we can register 2 assets 
    # and if the final ugcPosts payload with multiple READY assets is accepted.
    # Note: In a real run, we'd need to upload the binary before READY status works, 
    # but we can test the UGC Post structure.
    
    # Let's just try to create a post with a dummy READY asset (it might fail if not uploaded, but let's see the error)
    print("Testing UGC Post payload structure with multiple media items...")
    
    ugc_url = "https://api.linkedin.com/v2/ugcPosts"
    payload_ugc = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Testing Multi-Image Post from Python script"
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": "urn:li:digitalmediaAsset:dummy1",
                        "title": {"text": "Slide 1"}
                    },
                    {
                        "status": "READY",
                        "media": "urn:li:digitalmediaAsset:dummy2",
                        "title": {"text": "Slide 2"}
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    resp = requests.post(ugc_url, headers=headers, json=payload_ugc)
    print(f"Status: {resp.status_code}")
    print("Response details:", resp.text)
    # If it says "Asset not found" or "Asset is not READY", that's GOOD, 
    # it means the *structure* was accepted and it reached the validation phase.
except Exception as e:
    print(e)


