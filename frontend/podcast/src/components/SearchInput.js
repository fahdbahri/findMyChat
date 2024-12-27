import React, { useState } from "react";
import TextField from "@mui/material/TextField";
import APIService from "../components/APIServices";

const SearchInput = ({ onSearch }) => {
  const [searchInput, setSearchInput] = useState("");

  const handleSumbit = async (event) => {
    event.preventDefault();
    try {
      const response = await APIService.SendSearchInput(searchInput);
      onsearch(response);
      setSearchInput("");
    } catch (error) {
      console.log("erorr", error);
    }
  };

  return (
    <div className="main">
      <h1>Search Your Favourite Podcast</h1>
      <form onSubmit={handleSumbit}>
        <div className="search">
          <TextField
            id="outlined-basic"
            value={searchInput}
            variant="outlined"
            onChange={(e) => setSearchInput(e.target.value)}
            fullWidth
            label="Search"
          />
        </div>
        <button className="btn btn-primary mt-2">Search</button>
      </form>
    </div>
  );
};

export default SearchInput;
