
$(document).ready(function() {
    $('.movie-poster').on('click', function() {
        const movieId = $(this).find('img').data('movie-id');
        const movieDetailsContainer = $('#movie-details-overlay');

        // Fetch movie details including the poster and display them in the pop-up box
        $.get('/movies/movie_details/' + movieId + '/', function(data) {
            const movieDetails = $(data);
           

            // Append the movie poster and the rest of the movie details to the pop-up box
            movieDetailsContainer.empty().append(movieDetails).show();
        });

        // Close the pop-up when clicking outside the movie details box or on the close button
        $(document).on('mouseup', function(e) {
            if (!movieDetailsContainer.is(e.target) && movieDetailsContainer.has(e.target).length === 0) {
                movieDetailsContainer.hide();
            }
        });

        
    });
});



