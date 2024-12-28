import React, { useState } from "react";
import "./App.css";
import VideoList from "./components/videoslist";
import SearchInput from "./components/SearchInput";


function App() {
  const [videos, setVideos] = useState([]);

  const showResults = (newVideos) => {
    setVideos(newVideos);
  };

  return (
    <div>
      <SearchInput onSearch={showResults} />
      <VideoList videos={videos} />
    </div>
  );
}

export default App;
