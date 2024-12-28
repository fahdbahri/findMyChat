const VideoList = ({ videos }) => {
  videos = Array.from(videos)
    return (
      <div className="mt-2">
        {videos && videos.map(video => (
          <div key={video.video_id} className="mb-4">
            <h2 className="text-primary">{video.title}</h2>
            <iframe
              width="560"
              height="315"
              src={`https://www.youtube.com/embed/${video.video_id}`}
              title={video.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        ))}
      </div>
    );
  };

export default VideoList;