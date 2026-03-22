import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("LINKEDIN_ACCESS_TOKEN")
urn = os.getenv("LINKEDIN_AUTHOR_URN")

print(f"Testing Token (starts with): {token[:15]}...")
print(f"Testing URN: {urn}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

# 1. Test basic profile access to verify token isn't expired
print("\n--- Testing Basic Token Validity ---")
try:
    resp = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Token is valid! Connected as:", resp.json().get("localizedFirstName"))
    else:
        print("Error details:", resp.text)
except Exception as e:
    print(e)

# 2. Test Organization Access
print("\n--- Testing Organization Access ---")
org_id = urn.split(":")[-1]
try:
    resp = requests.get(f"https://api.linkedin.com/v2/organizations/{org_id}", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("Successfully read Organization Profile!")
    else:
        print("Error details:", resp.text)
except Exception as e:
    print(e)

# 3. Test Register Upload for Document
print("\n--- Testing Document Register Upload ---")
register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
payload = {
    "registerUploadRequest": {
        "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
        "owner": urn,
        "serviceRelationships": [
            {
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }
        ]
    }
}

print("\n--- Testing Image Register Upload ---")
payload_image = {
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
    resp = requests.post(register_url, headers=headers, json=payload_image)
    print(f"Status: {resp.status_code}")
    print("Response:", resp.text)
except Exception as e:
    print(e)
