document.getElementById('save-plan-button').addEventListener('click', function() {
    const flashMessage = document.getElementById('meal-plan-flash-message');

    fetch('/save_meal_plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: 'user_id_value' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            flashMessage.textContent = "Meal plan saved successfully!";
            flashMessage.classList.remove('d-none', 'alert-danger');
            flashMessage.classList.add('alert-success');
        } else {
            throw new Error(data.message || 'Saving failed');
        }
    })
    .catch(error => {
        console.error(error);
        flashMessage.textContent = "Error saving meal plan. Please try again.";
        flashMessage.classList.remove('d-none', 'alert-success');
        flashMessage.classList.add('alert-danger');
    });

    setTimeout(() => {
        flashMessage.style.opacity = 0;
    }, 2500);
});
