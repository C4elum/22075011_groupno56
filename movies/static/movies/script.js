// script.js
document.querySelectorAll('.movie-details-button').forEach(function(button) {
    button.addEventListener('click', function() {
        const movieId = button.getAttribute('data-movie-id');
        // Fetch movie details using AJAX or other method
        // Display the details and navigate to a new view
        // You can use an overlay or modal to show movie details
    });
});
