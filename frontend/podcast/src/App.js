import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField"


function App() {
  const [data, setData] = useState([{}]);

  useEffect(() => {
    fetch("/home")
      .then((res) => res.json())
      .then((data) => {

        setData(data);
        console.log(data);
      });
  }, []);
  return (
    <div className="main">
      <h1>Search Your Favourite Podcast</h1>
      <div className="search">
        <TextField 
        id="outlined-basic"
        variant="outlined"
        fullWidth
        label="Seach"
        />
      </div>
    </div>
  );
}

export default App;
