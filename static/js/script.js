// Get the search input field
var searchInput = document.getElementById('search');

// Automatically focus the search bar when the page loads
searchInput.focus();

document.getElementById('searchForm').addEventListener('submit', function(event) {
    // Prevent the form from being submitted in the standard way
    event.preventDefault();

    // Get the value from the search input field
    var searchTerm = searchInput.value;

    // Send a GET request to the /search endpoint on the server
    fetch('/search?term=' + encodeURIComponent(searchTerm))
        .then(response => response.json())
        .then(data => {
            // Remove any previously displayed images
            var imageContainer = document.getElementById('imageContainer');
            while (imageContainer.firstChild) {
                imageContainer.removeChild(imageContainer.firstChild);
            }

            // For each image path returned by the server...
            data.forEach(filePath => {
                // Create a new div element with class 'card'
                var card = document.createElement('div');
                card.className = 'card';

                // Create a new img element
                var img = document.createElement('img');

                // Set the src attribute of the img element to the image path
                img.src = "/image" + filePath;

                // Set the title attribute to the filePath for the tooltip
                img.title = filePath;

                // Add the img element to the 'card'
                card.appendChild(img);

                // Add the 'card' to the imageContainer
                imageContainer.appendChild(card);
            });
        })
        .catch(error => console.error('Error:', error));
});


document.getElementById('directoryPickerButton').addEventListener('click', function(){
    fetch('/open_directory_dialog')
    .then(response => response.json())
    .then(data => {
        alert('Selected folder: ' + data.folder_selected);
    });
});

// Dark mode
document.addEventListener('DOMContentLoaded', (event) => {
    const bodyElement = document.body;
    const darkModeToggle = document.getElementById('darkModeToggle');

    // Check for saved user preference, if any, on page load
    if (localStorage.getItem('darkMode') === 'enabled') {
        bodyElement.classList.add('dark-mode');
    }

    // Toggle dark mode
    darkModeToggle.addEventListener('click', () => {
        bodyElement.classList.toggle('dark-mode');
        // Save the user preference in localStorage
        if (bodyElement.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
        } else {
            localStorage.setItem('darkMode', 'disabled');
        }
    });
});