// SearchInput.js
import React, { useState } from "react";
import "./SearchInput.css";

const SearchInput = () => {
  const [searchInput, setSearchInput] = useState("");

  const SendSearchInput = (value) => {
    console.log("Sending value:", value);  // Add this
    console.log("Sending body:", JSON.stringify({ "search-input": value }));
    fetch("/home", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "search-input": value })
    })
    .then((response) => response.json())
    .then((json) => {
      console.log(json)
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
      <h1>Search Your Favourite Podcast</h1>
      <input
        placeholder="Search here"
        value={searchInput}
        onChange={(e) => handleSubmit(e.target.value)}
      />
    </div>
  );
};

export default SearchInput;