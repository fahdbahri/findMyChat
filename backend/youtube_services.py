import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    
    def search_podcast(self, query, top_k=2):

        # Extract the information from the database
        cursor = self.db_connection.cursor()
        cursor.execute('''SELECT video_id, title, transcript FROM podcasts''')
        podcasts = cursor.fetchall()

        # Append the query with the array
        texts = [podcast[2] for podcast in podcasts]
        texts.append(query)


        # Vectorization
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(texts)

        # COmpute similarity
        similarity_score = cosine_similarity(tfidf_matrix[-1] ,tfidf_matrix[:-1])[0]


        top_indices = similarity_score.argsort()[-top_k:][::-1]

        results = [
            {
                'video_id': podcasts[idx][0],
                'title': podcasts[idx][1]

            } for idx in top_indices
        ] 

        return results 


        

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

    results  = search_engine.search_podcast("can we use AI to study")

    for result in results:
        print(f"{result['title']} and {result['video_id']}")


if __name__ == "__main__":
    main()