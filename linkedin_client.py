import os
import requests
import tempfile

def download_image(image_url: str) -> str:
    """Downloads an image from a URL and saves it to a temp file. Returns the file path."""
    try:
        response = requests.get(image_url, timeout=180, stream=True)
        response.raise_for_status()

        # Save to a temporary file
        suffix = ".png"
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
        tmp_file.close()
        print(f"Image downloaded to: {tmp_file.name}")
        return tmp_file.name
    except Exception as e:
        print(f"Failed to download image: {e}")
        return ""


def register_image_upload(access_token: str, author_urn: str) -> dict:
    """
    Registers an image upload with LinkedIn. Returns the upload URL and asset URN.
    """
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset = data["value"]["asset"]
    return {"upload_url": upload_url, "asset": asset}


def upload_image_to_linkedin(upload_url: str, image_path: str, access_token: str) -> bool:
    """Uploads an image binary to LinkedIn's upload endpoint."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
    }
    with open(image_path, "rb") as f:
        response = requests.put(upload_url, headers=headers, data=f)

    if response.status_code in [200, 201]:
        print("Image uploaded to LinkedIn successfully.")
        return True
    else:
        print(f"Image upload failed: {response.status_code} - {response.text}")
        return False


def post_to_linkedin(text_content: str, image_url: str = None) -> str:
    """
    Posts content to LinkedIn using the REST API.
    If an image_url is provided, downloads it and attaches it to the post.
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")

    if not access_token or not author_urn or access_token == "your_linkedin_access_token":
        print("--- DRY RUN / MISSING KEYS ---")
        print("Would have posted to LinkedIn:")
        print(text_content)
        if image_url:
            print(f"With image: {image_url}")
        print("------------------------------")
        return "DRY RUN: Post successfully simulated."

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    # Determine if we should attach an image
    media_asset = None
    if image_url:
        print("Downloading generated image...")
        image_path = download_image(image_url)
        if image_path:
            try:
                print("Registering image upload with LinkedIn...")
                upload_info = register_image_upload(access_token, author_urn)

                print("Uploading image to LinkedIn...")
                success = upload_image_to_linkedin(
                    upload_info["upload_url"], image_path, access_token
                )
                if success:
                    media_asset = upload_info["asset"]
                    print(f"Image asset registered: {media_asset}")
            except Exception as e:
                print(f"Image upload process failed: {e}. Posting without image.")

            # Clean up temp file
            try:
                os.remove(image_path)
            except Exception:
                pass

    # Build the payload
    if media_asset:
        # Post WITH image
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text_content
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": media_asset,
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    else:
        # Post WITHOUT image (text only)
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
        error_msg = str(e)
        if "401" in error_msg:
            error_msg += (
                "\n\n*** YOUR ACCESS TOKEN HAS EXPIRED OR IS INVALID. ***"
                "\nGo to https://developer.linkedin.com -> Your App -> Auth -> Token Generator"
                "\nGenerate a new token with the required scopes and update your .env file."
            )
        return f"Failed to post to LinkedIn. Error: {error_msg}"


def post_carousel_to_linkedin(text_content: str, pdf_path: str) -> str:
    """
    Posts a carousel (document) to LinkedIn by uploading a PDF.
    Uses the same register → upload → post flow as images.
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")

    if not access_token or not author_urn or access_token == "your_linkedin_access_token":
        print("--- DRY RUN / MISSING KEYS ---")
        print("Would have posted carousel to LinkedIn:")
        print(f"Text: {text_content[:100]}...")
        print(f"PDF: {pdf_path}")
        print("------------------------------")
        return "DRY RUN: Carousel post successfully simulated."

    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at {pdf_path}"

    headers_auth = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Step 1: Register document upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
            "owner": author_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    try:
        reg_response = requests.post(register_url, headers=headers_auth, json=register_payload)
        reg_response.raise_for_status()
        reg_data = reg_response.json()

        upload_url = reg_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = reg_data["value"]["asset"]
        print(f"Document asset registered: {asset_urn}")

    except Exception as e:
        return f"Failed to register document upload: {str(e)}"

    # Step 2: Upload PDF binary
    try:
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/octet-stream",
        }
        with open(pdf_path, "rb") as f:
            upload_response = requests.put(upload_url, headers=upload_headers, data=f)

        if upload_response.status_code not in [200, 201]:
            return f"Failed to upload PDF: {upload_response.status_code} - {upload_response.text}"
        print("PDF uploaded successfully.")

    except Exception as e:
        return f"Failed to upload PDF: {str(e)}"

    # Step 3: Create the post with the document
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    post_headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    post_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "NATIVE_DOCUMENT",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                        "title": {
                            "text": "Career Launchpad Guide"
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(post_url, headers=post_headers, json=post_payload)
        response.raise_for_status()
        return f"Successfully posted carousel to LinkedIn! ID: {response.json().get('id')}"
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if "401" in error_msg:
            error_msg += "\n\n*** ACCESS TOKEN EXPIRED. Regenerate at developer.linkedin.com ***"
        return f"Failed to post carousel. Error: {error_msg}"

    finally:
        # Clean up temp PDF
        try:
            os.remove(pdf_path)
        except Exception:
            pass

