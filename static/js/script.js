document.getElementById('searchForm').addEventListener('submit', function (event) {
    // Prevent the form from being submitted in the standard way
    event.preventDefault();

    // Get the value from the search input field
    var searchTerm = document.getElementById('search').value;

    // Send a GET request to the /search endpoint on the server
    fetch('/search?term=' + encodeURIComponent(searchTerm))
        .then(response => response.json())
        .then(data => {
            data.forEach(filePath => {
                console.log(filePath);
                // Add code here to handle each file path
            });
        })
        .catch(error => console.error('Error:', error));
});