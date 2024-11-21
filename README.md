# Food and Recipes Web Application

## Video Demo:  https://youtu.be/iZrxJhOQRcE?si=liBAcYtcuxjbfH8s

## Description:
Recipe Planner Web Application is a comprehensive tool designed to simplify meal planning for users by enabling them to search for recipes, save their favorites, and generate personalized meal plans. The project focuses on usability and functionality, offering an intuitive interface and features tailored to user needs.

This project was built using Flask for the backend, SQLite for the database, and standard web technologies (HTML, CSS, JavaScript) for the frontend. The application is responsive, easy to navigate, and offers a seamless experience for users interested in optimizing their meal preparation.

## Project Structure

### 1. **`app.py`**
This is the main application file. It initializes the Flask app, defines routes, and handles both backend logic and communication between the frontend and the database. Major features include:
- Managing user authentication (login, logout, and registration).
- Handling recipe search requests and displaying results.
- Managing user interactions with saved recipes and meal plans.

### 2. **`templates/`**
This folder contains HTML templates that define the structure and layout of the web pages. Key files include:
- **`index.html`**: The start page of the application, where the user is provided with an attractive display of several random recipes, and also has the opportunity to log in to the application or register to be able to use the full functionality of the application.
- **`home.html`**: The home page of the logged-in user, where he can search for recipes, and from which all the functionality of the application is generally available.
- **`favorites.html`**: Displays a list of recipes saved by the user.
- **`create_meal_plan.html`**: A page for creating and managing personalized meal plans.
- **`login.html`** and **`registration.html`**: Forms for user authentication.
- **`about_us.html`**: A page to introduce the user to my application and its goals.
- **`contacts.html`**: An example page for submitting company contact information.
- **`plan_results.html`**: A page for displaying the results of creating a meal plan or is also used to display the user's saved meal plan.
- **`recipe.html`**: A page for displaying a detailed version of a particular recipe.
- **`results.html`**: Page for displaying recipe search results.

Each file uses Flask's template rendering engine to dynamically inject data, making pages interactive and personalized.

### 3. **`static/`**
This folder contains all static assets, including CSS, JavaScript, and images:
- **CSS (`styles.css`)**: Defines the application's visual appearance, such as layout, fonts, and colors.
- **JavaScript (`favorite.js`, `meal_plan.js`)**: Contains client-side logic to manage interactions, such as adding recipes to favorites and handling dynamic updates to meal plans.
- It also stores images used on the welcome page and error handling pages.

### 4. **`additional_functions.py`**
This module includes helper functions for managing the core logic of the application. Examples:
- Querying recipes from the database.
- Handling user-specific operations, such as saving recipes or generating meal plans.
- Performing input validation to ensure data integrity.

### 5. **`requirements.txt`**
A text file listing all Python dependencies needed to run the project, including Flask and other libraries. This allows developers to replicate the environment quickly using:
```bash
pip install -r requirements.txt

### 6. **`users.db`**
An SQLite database that stores all application data. Key tables include:
- user: Stores user credentials.
- favorite_recipes: Stores unique recipe IDs for easy identification and display, saved recipe data and images.
- temp_planner: This is where responses from the meal planner are temporarily stored until the user's next request or until the completed meal plan is saved to the meal_plan table.
- meal_plan: This is where the user's meal plans are saved, which include days, meal type (breakfast, lunch, dinner), dish type, recipe data, recipe image and its ID.

## Design Decisions

### Framework and Database
Flask was chosen for its simplicity and flexibility, which is ideal for small to medium-sized projects. SQLite was selected as the database due to its lightweight nature and easy integration with Flask.

### User Interface
The interface was designed to be minimalistic and user-friendly, with intuitive navigation and responsive design for access across devices. Dynamic elements, such as interactive forms and AJAX-powered updates, enhance the user experience.

### Modular Design
The project is structured to separate concerns:
- Backend logic is handled in app.py.
- Frontend templates are in templates/, keeping the UI and backend independent.
- Reusable helper functions in additional_functions.py improve maintainability.

## Features

- **Recipe Search**: Search for recipes by keywords, categories, or ingredients.
- **Save Favorites**: Save recipes to your favorites list for quick access.
- **Meal Planning**: Generate personalized meal plans tailored to individual preferences and goals.
- **User Authentication**: Register and log in to manage saved recipes and meal plans.

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript (with some static assets)
- **Database**: SQLite

#### Installation

1. Clone the repository:
   ```bash
   git clone <https://github.com/code50/83469567/blob/3d99dd3a04fe77956d74ebec01f012928323446f/Project>
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   flask run
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage

- **Indexpage**: The first page, which provides the user with several random recipes with an attractive display. Most of the application's functions are limited here, but it is possible to access them after registration and login.
- **Homepage**: Here you have the opportunity to search for recipes and use the full functionality of the application.
- **Favorites**: Save recipes to your favorites for easy access.
- **Meal Planner**: Create a meal plan by selecting recipes and setting preferences. You can also always save your favorite meal plan and use it in the future.
