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
    <div className="App">
      <div className="search-bar-container">
        <SearchInput showResults={showResults} />
        <VideoList videos={videos} />
      </div>
    </div>
  );
}

export default App;
