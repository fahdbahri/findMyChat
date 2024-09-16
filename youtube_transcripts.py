from youtube_transcript_api import YouTubeTranscriptApi


urls = ['https://www.youtube.com/watch?v=xUNx_PxNHrY&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=2', 'https://www.youtube.com/watch?v=C_78DM8fG6E&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=2', 'https://www.youtube.com/watch?v=hJP5GqnTrNo&list=PLQcmLf7MkOOb3czkZ7HvLKW3Gtg_TPOhI&index=3']


video_ids = []
for url in urls:
    video_id = url.replace('https://www.youtube.com/watch?v=', '')
    video_ids.append(video_id)
    


def get_transcripts(video_ids):
    transcripts = []
    for video_id in video_ids:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcripts.append(transcript)
    print(transcripts)


if __name__ == '__main__':
    get_transcripts(video_ids)