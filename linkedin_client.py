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
def post_multiple_images_to_linkedin(text_content: str, image_paths: list) -> str:
    """
    Posts content to LinkedIn as a multi-image carousel.
    Takes a list of local file paths, uploads them all, and attaches them to a UGC Post.
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")

    if not access_token or not author_urn or access_token == "your_linkedin_access_token":
        print("--- DRY RUN / MISSING KEYS ---")
        print("Would have posted multi-image carousel to LinkedIn:")
        print(text_content)
        print(f"With {len(image_paths)} images: {image_paths}")
        print("------------------------------")
        return "DRY RUN: Carousel successfully simulated."

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    media_assets = []
    
    # Upload each image
    for i, img_path in enumerate(image_paths):
        print(f"Uploading image {i+1}/{len(image_paths)}...")
        try:
            upload_info = register_image_upload(access_token, author_urn)
            success = upload_image_to_linkedin(
                upload_info["upload_url"], img_path, access_token
            )
            if success:
                media_assets.append({
                    "status": "READY",
                    "media": upload_info["asset"],
                    "title": {"text": f"Slide {i+1}"}
                })
        except Exception as e:
            print(f"Failed to upload slide {i+1}: {e}")
            continue
            
        finally:
            # Clean up temp images
            try:
                os.remove(img_path)
            except Exception:
                pass

    if not media_assets:
        return "Failed to upload any images for the carousel."

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text_content
                },
                "shareMediaCategory": "IMAGE",
                "media": media_assets
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Successfully posted image carousel to LinkedIn! ID: {response.json().get('id')}"
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = e.response.text
        if status_code == 401:
            return f"Error: 401 Unauthorized. Access token expired or missing w_organization_social scope."
        elif status_code == 400:
            return f"Error: 400 Bad Request. Validation failed. {error_msg}"
        return f"Failed to post carousel: {status_code} - {error_msg}"
    except Exception as e:
        return f"An error occurred while posting carousel: {str(e)}"

