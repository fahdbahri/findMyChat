// SearchInput.js
import React, { useState } from "react";
import { FaSearch } from "react-icons/fa"

import "./SearchInput.css";

const SearchInput = ({ showResults }) => {
  const [searchInput, setSearchInput] = useState("");

  const SendSearchInput = (value) => {
    fetch("/home", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "search-input": value })
    })
    .then((response) => response.json())
    .then((json) => {
      const results = json.filter((videos) => {
        return (
          videos.video_id && videos.title
        );
      });
      showResults(results);
    })
    .catch(error => console.error('Error:', error));
  };

  const handleSubmit = (value) => {
    try {
      setSearchInput(value);
      SendSearchInput(value);
    } catch (error) {
      console.log("There is an error in here", error);
    }
  };

  return (
    <div className="main">
      <FaSearch id="search-icon" />
      <input
        placeholder="Type to search..."
        value={searchInput}
        onChange={(e) => handleSubmit(e.target.value)}
      />
    </div>
  );
};

export default SearchInput;