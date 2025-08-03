import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";

export const SearchPage = ({ showResults }) => {
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
    <div className="flex flex-col items-center justify-center h-screen">
      <div className="relative flex items-center w-full max-w-md">
        <FaSearch className="absolute left-3 text-gray-400" />
        <input
          className="w-full py-2 pl-10 pr-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Type to search..."
          value={searchInput}
          onChange={(e) => handleSubmit(e.target.value)}
        />
      </div>
    </div>
  );
};

export default SearchPage;
