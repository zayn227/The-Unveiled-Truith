import os
import random
import cloudinary
import cloudinary.uploader
import requests
import json

# Cloudinary Configuration (from GitHub Secrets)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Facebook Page Details (from GitHub Secrets)
PAGE_ID = os.getenv("PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

POSTED_IMAGES_FILE = "posted_images.json"

def get_posted_images():
    """Loads the list of previously posted image URLs."""
    if os.path.exists(POSTED_IMAGES_FILE):
        with open(POSTED_IMAGES_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_posted_image(image_url):
    """Saves a new image URL to the list of posted images."""
    posted_images = get_posted_images()
    posted_images.append(image_url)
    with open(POSTED_IMAGES_FILE, 'w') as f:
        json.dump(posted_images, f)

def get_random_unposted_image_from_cloudinary():
    """Fetches a random unposted image from the 'Quotes' folder in Cloudinary."""
    resources = cloudinary.api.resources(type="upload", prefix="Quotes/", max_results=500)['resources']
    if not resources:
        print("No images found in the 'Quotes' folder.")
        return None

    all_image_urls = [res['secure_url'] for res in resources]
    posted_images = get_posted_images()

    unposted_images = [url for url in all_image_urls if url not in posted_images]

    if not unposted_images:
        print("All images from 'Quotes' folder have been posted. Consider adding new images or resetting the posted_images.json file.")
        return None

    return random.choice(unposted_images)

def post_image_to_facebook(image_url):
    """Posts an image to the Facebook page."""
    if not PAGE_ID or not FB_ACCESS_TOKEN:
        print("Error: Facebook PAGE_ID or FB_ACCESS_TOKEN not set.")
        return False

    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    params = {
        "url": image_url,
        "access_token": FB_ACCESS_TOKEN
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Image successfully posted to Facebook!")
        print(response.json())
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting image to Facebook: {e}")
        print(f"Response content: {response.text}")
        return False

if __name__ == "__main__":
    selected_image_url = get_random_unposted_image_from_cloudinary()

    if selected_image_url:
        print(f"Attempting to post: {selected_image_url}")
        if post_image_to_facebook(selected_image_url):
            save_posted_image(selected_image_url)
            print(f"Image {selected_image_url} marked as posted.")
        else:
            print("Failed to post image.")
    else:
        print("No image available to post at this time.")
