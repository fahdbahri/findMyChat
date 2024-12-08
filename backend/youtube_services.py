import os
from dotenv import load_dotenv
import googleapiclient.discovery
import pprint as pp
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

#API information 
api_service_name = "youtube"
api_version = "v3"
DELEVOPER_KEY = youtube_api_key

# Create an API client
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DELEVOPER_KEY)

# Request body
def get_video_title(video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response['items'][0]['snippet']['title']


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        return None
    


video_id = "xUNx_PxNHrY"
title = get_video_title(video_id)
transcript = get_transcript(video_id)

podcast_data = {
    "title": title,
    "transcript": transcript
}

print(podcast_data)