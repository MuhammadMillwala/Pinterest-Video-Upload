import requests
import time

# Constants
ACCESS_TOKEN = ''
BOARD_ID = ''
VIDEO_FILE_PATH = 'https://dl5hm3xr9o0pk.cloudfront.net/instagram/smfiuh_1718025091397.mp4'
COVER_IMAGE_URL = 'https://dl5hm3xr9o0pk.cloudfront.net/instagram/thunder.jpg'
# TITLE = 'Your Pin Title'
DESCRIPTION = 'Your Pin Description'

# Step 1: Register your intent to upload a video
def register_media_upload():
    url = "https://api.pinterest.com/v5/media"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "media_type": "video"
    }
    
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    media_id = response_data.get("media_id")
    upload_url = response_data.get("upload_url")
    upload_parameters = response_data.get("upload_parameters")
    
    return media_id, upload_url, upload_parameters

# Step 2: Upload the video file to the Pinterest Media AWS bucket
def upload_video(upload_url, upload_parameters, video_url):
    # Download video from the URL
    video_response = requests.get(video_url, stream=True)
    video_response.raise_for_status()
    
    # Prepare the files and data for upload
    files = {
        'file': ('video.mp4', video_response.raw, 'video/mp4')
    }
    response = requests.post(upload_url, files=files, data=upload_parameters)
    return response.status_code

# Step 3: Confirm upload
def confirm_upload(media_id):
    url = f"https://api.pinterest.com/v5/media/{media_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    while True:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        status = response_data.get("status")
        if status == "succeeded":
            return True
        elif status == "failed":
            print("Upload failed")
            return False
        print("Waiting for upload to complete...")
        time.sleep(5)  # Wait for 5 seconds before checking again

# Step 4: Create Pin
def create_pin(media_id, cover_image_url, board_id, description):
    url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        # "title": title,
        "description": description,
        "board_id": board_id,
        "media_source": {
            "source_type": "video_id",
            "cover_image_url": cover_image_url,
            "media_id": media_id
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Main function to execute the steps
def main():
    # Step 1
    media_id, upload_url, upload_parameters = register_media_upload()
    if not media_id or not upload_url or not upload_parameters:
        print("Failed to register media upload")
        return
    
    # Step 2
    status_code = upload_video(upload_url, upload_parameters, VIDEO_FILE_PATH)
    if status_code != 204:
        print(f"Video upload failed with status code: {status_code}")
        return
    
    # Step 3
    if not confirm_upload(media_id):
        print("Video upload confirmation failed")
        return
    
    # Step 4
    pin_data = create_pin(media_id, COVER_IMAGE_URL, BOARD_ID, DESCRIPTION)
    print("Pin created:", pin_data)

if __name__ == "__main__":
    main()