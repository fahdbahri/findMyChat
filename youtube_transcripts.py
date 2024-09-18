from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import numpy as np


urls = ['https://www.youtube.com/watch?v=xUNx_PxNHrY&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=2', 'https://www.youtube.com/watch?v=C_78DM8fG6E&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=2', 'https://www.youtube.com/watch?v=hJP5GqnTrNo&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=3']


video_ids = []
for url in urls:
    video_id = url.replace('https://www.youtube.com/watch?v=', '')
    video_ids.append(video_id)



def get_transcripts(video_ids):
    transcripts = {}

    for i, video_id in enumerate(video_ids):
        print(f'Getting transcript for video {i+1}/{len(video_ids)}')
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcripts[video_id] = " ".join([entry['text'] for entry in transcript])
    return transcripts

transcripts = get_transcripts(video_ids)

full_transcript = list(transcripts.values())

model = SentenceTransformer('all-MiniLM-L6-v2')

video_embeddings = model.encode(full_transcript)

np.save('video_embeddings.npy', video_embeddings)

print('Embeddings shape:', video_embeddings.shape)

