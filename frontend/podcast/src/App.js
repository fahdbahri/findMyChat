import React, { useState, useEffect } from "react";

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
    <div>
      {(typeof data.Name === 'undefined') ? (
        <p>Loading...</p>
      ) : (
        data.Name.map((member, i) => <p key={i}>{member}</p>)
      )}
    </div>
  );
}

export default App;
