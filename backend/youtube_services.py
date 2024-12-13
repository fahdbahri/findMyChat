import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pprint as pp
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript
import sqlite3 

class PodcastSearchEngine:
    def __init__(self):
        load_dotenv()
        self.yotube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build("youtube", "v3", developerKey=self.yotube_api_key)
        self.db_connection = sqlite3.connect('podcast.db')
        self.create_database()
    
    def create_database(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS podcasts (
                        video_id TEXT PRIMARY KEY,
                        title TEXT,
                        transcript TEXT
                            )""")
        self.db_connection.commit()

    def extract_video_info(self, video_id):

        try:

        # Cet the video Title
            title_request = self.youtube.videos().list(
                part='snippet', id=video_id
            )
            title_response = title_request.execute()
            title = title_response['items'][0]['snippet']['title']

            try:

                # Get the Transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join(entry["text"] for entry in transcript)
                print("Transcript are available")
            except CouldNotRetrieveTranscript:
                print(f"Transcript not available for Video ID: {video_id}")
                transcript_text = ""
            return {
                'video_id': video_id,
                'title': title,
                'transcript': transcript_text
            }
        except Exception as e:
            print(f"Error processing video ID {video_id}: {e}")

    def store_podcast_info(self, podcast_info):
        try: 

            cursor = self.db_connection.cursor()
            cursor.execute('''
                            INSERT OR REPLACE INTO podcasts (video_id, title, transcript)
                            VALUES (?,?,?)''', (
                                podcast_info['video_id'],
                                podcast_info['title'],
                                podcast_info['transcript']
                            ))
            self.db_connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def bulk_and_store_all(self, video_ids):
        for video_id in video_ids:
            podcast_info = self.extract_video_info(video_id)
            if podcast_info:
                self.store_podcast_info(podcast_info)

    def __del__(self):
        if self.db_connection:
            self.db_connection.close()
        



def main():

    search_engine = PodcastSearchEngine()

    video_ids = [
        "xUNx_PxNHrY",
        "hJP5GqnTrNo",
        "fLMZAHyrpyo",
        "WX_vN1QYgmE",
        "Yd0yQ9yxSYY"
    ]

    search_engine.bulk_and_store_all(video_ids)


if __name__ == "__main__":
    main()