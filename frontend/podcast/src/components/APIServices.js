class APIService{

    // sending the search query to the backend
    static SendSearchInput(search){
        return fetch("/home", {
            'method': 'POST',
             headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({"search-input": search})
        })
        .then(response => response.json())
        .catch(error => console.log(error))
    }
}

export default APIService