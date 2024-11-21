document.getElementById('like-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Stopping Form Submission by Default
    const form = event.target;
    const button = document.getElementById('like-button');
    const flashMessage = document.getElementById('flash-message');
    const recipeId = button.getAttribute('data-recipe-id');

    if (button.classList.contains('active')) {
        // If the button is active (the recipe is already in favorites), we delete the recipe
        fetch(`/delete_favorite/${recipeId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => {
            if (response.ok) {
                // Successful removal - update the appearance of the button
                button.classList.remove('active');
                button.querySelector('.far.fa-heart').classList.remove('d-none');
                button.querySelector('.fas.fa-heart').classList.add('d-none');

                // Show notification of successful deletion
                flashMessage.textContent = "Recipe removed from favorites!";
                flashMessage.classList.remove('d-none', 'alert-danger');
                flashMessage.classList.add('alert-success');
                flashMessage.style.opacity = 1;
            } else {
                throw new Error('Deletion failed');
            }
        })
        .catch(error => {
            console.error(error);
            // Error notification
            flashMessage.textContent = "Error removing recipe. Please try again.";
            flashMessage.classList.remove('d-none', 'alert-success');
            flashMessage.classList.add('alert-danger');
            flashMessage.style.opacity = 1;
        });
    } else {
        // If the button is inactive (the recipe is not in the favorites), we add the recipe
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => {
            if (response.ok) {
                // Successful save - update the button appearance
                button.classList.add('active');
                button.querySelector('.far.fa-heart').classList.add('d-none');
                button.querySelector('.fas.fa-heart').classList.remove('d-none');

                // Show notification of successful saving
                flashMessage.textContent = "Recipe saved successfully in favorites!";
                flashMessage.classList.remove('d-none', 'alert-danger');
                flashMessage.classList.add('alert-success');
                flashMessage.style.opacity = 1;
            } else {
                throw new Error('Saving failed');
            }
        })
        .catch(error => {
            console.error(error);
            // Show error notification
            flashMessage.textContent = "Error saving recipe. Please try again.";
            flashMessage.classList.remove('d-none', 'alert-success');
            flashMessage.classList.add('alert-danger');
            flashMessage.style.opacity = 1;
        });
    }

    // Remove notification after 2.5 seconds
    setTimeout(() => {
        flashMessage.style.opacity = 0;
    }, 2500);
});
