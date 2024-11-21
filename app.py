from flask import Flask, redirect, render_template, request, session, jsonify, flash
from flask_session import Session
import json
from cs50 import SQL
import requests
import base64

from additional_functions import login_required, hash_password, check_password, \
    searchRecipes, find_recipe_by_id, meal_planner, extract_plan_from_db, save_temp_planner, \
    request_from_user, health_conditions, diet_conditions, dish_types

# Configure application
app = Flask(__name__)
app.secret_key = 'supersecretkey'


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///users.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/', methods=['GET'])
def index():

    session.clear()

    recipes = searchRecipes(random=True)
    return render_template('index.html', recipes=recipes)


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE user_name = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password(password, rows[0]["password"]):
            return render_template("incorrect_entry.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        try:
            return redirect("/home")
        except Exception as e:
            print(f"Error redirecting to home page: {e}")
            return ("Error redirecting to home page", 500)

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # The correctness of the input data is checked in HTML at the input stage.
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if confirmation != password:
            return render_template("apology.html")

        # We hash the password using the function "hash_password"
        hash = hash_password(password)

        existing_user = db.execute(
            "SELECT * FROM user WHERE user_name = ?", (username,))

        if existing_user:
            existing_user = existing_user[0]
            return render_template("userexist.html", message="Username already exists.")

        try:
            db.execute(
                "INSERT INTO user (user_name, password) VALUES (?, ?)", username, hash)
            return render_template("successful_registration.html")
        except Exception as e:
            print(f"Error inserting user into database: {e}")
            return render_template("dberror.html", message="A database error occurred.")

    else:
        return render_template("registration.html")


@app.route("/about_us")
def about_us():
    return render_template("about_us.html")


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/home")
@login_required
def home():

    user_id = session["user_id"]
    plan_exists = bool(db.execute(
        "SELECT * FROM meal_plan WHERE user_id = ?", user_id))

    recipes = searchRecipes(random=True)
    return render_template('home.html', recipes=recipes, plan_exists=plan_exists)


@app.route("/search", methods=["GET"])
@login_required
def search_recipes():

    if request.method == "GET":

        query = request.args.get('query')
        recipes = searchRecipes(query)
        return render_template('results.html', recipes=recipes)


@app.route("/recipe/<recipe_id>")
@login_required
def recipe_detail(recipe_id):

    user_id = session["user_id"]
    plan_exists = bool(db.execute(
        "SELECT * FROM meal_plan WHERE user_id = ?", user_id))

    # Check if this recipe is in the user's favorites
    recipe_exists = bool(db.execute(
        "SELECT 1 FROM favorite_recipes WHERE user_id = ? AND recipe_id = ?", user_id, recipe_id))

    # Check if this recipe is in session
    recipe = find_recipe_by_id(recipe_id)

    if not recipe:
        try:
            recipe_data = db.execute("SELECT recipe_data, image FROM favorite_recipes\
                            WHERE user_id = ? AND recipe_id = ?", user_id, recipe_id)
        except Exception as e:
            print(f"Error retrieving recipe data: {e}")
            return "Error retrieving recipe data", 500
        if recipe_data:
            recipe = json.loads(recipe_data[0]["recipe_data"])

            # Extract the image and convert it to base64
            image_blob = recipe_data[0]["image"]
            recipe["image"] = f"data:image/png;base64,{
                base64.b64encode(image_blob).decode('utf-8')}"

    if recipe:
        return render_template('recipe.html', recipe=recipe, recipe_id=recipe_id, recipe_exists=recipe_exists, plan_exists=plan_exists)
    else:
        return "Recipe not found", 404


@app.route("/save_favorite/<recipe_id>", methods=['POST'])
@login_required
def save_favorite(recipe_id):

    if request.method == "POST":

        user_id = session["user_id"]

        recipe = find_recipe_by_id(recipe_id)

        if not recipe:
            return render_template("error.html", message="Recipe not found."), 404

        recipe_data = {
            'label': recipe.get('label'),
            'yield': recipe.get('yield'),
            'url': recipe.get('url'),
            'source': recipe.get('source'),
            'ingredientLines': recipe.get('ingredientLines', []),
            'totalNutrients': recipe.get('totalNutrients', {}),
            'totalTime': recipe.get('totalTime'),
            'dietLabels': recipe.get('dietLabels', []),
            'healthLabels': recipe.get('healthLabels', []),
            'cuisineType': recipe.get('cuisineType', []),
            'mealType': recipe.get('mealType', []),
            'dishType': recipe.get('dishType', []),
        }

        # Prepare image for saving as bytes
        image_url = recipe.get('image')
        print("Image url: ", image_url)
        if image_url:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_data = image_response.content  # Save as bytes
                else:
                    print("Error loading image:", image_response.status_code)
                    image_data = None
            except Exception as e:
                print(f"Error loading image: {e}")
                image_data = None
        else:
            image_data = None

        try:
            db.execute("INSERT INTO favorite_recipes (user_id, recipe_id, recipe_data, image) VALUES (?, ?, ?, ?)",
                       user_id, recipe_id, json.dumps(recipe_data), image_data)
            flash("Recipe saved successfully!", "success")
            return redirect(request.referrer)
        except:
            flash("A database error occurred.", "danger")
            return redirect(request.referrer)


@app.route("/favorites")
@login_required
def favorites():

    user_id = session["user_id"]
    plan_exists = bool(db.execute(
        "SELECT * FROM meal_plan WHERE user_id = ?", user_id))

    rows = db.execute(
        "SELECT recipe_id, recipe_data, image FROM favorite_recipes WHERE user_id = ?", user_id)

    # Let's parse the JSON data for each recipe
    recipes = []
    for row in rows:
        recipe_data = json.loads(row['recipe_data'])
        recipe_data['recipe_id'] = row['recipe_id']

        # Encode the image to base64 for displaying in HTML
        if row['image']:
            recipe_data['image'] = base64.b64encode(
                row['image']).decode('utf-8')
        else:
            recipe_data['image'] = None  # Set to None if no image is available

        recipes.append(recipe_data)

    return render_template("favorites.html", recipes=recipes, plan_exists=plan_exists)


@app.route("/delete_favorite/<recipe_id>", methods=['POST'])
@login_required
def delete_favorite(recipe_id):

    if request.method == "POST":

        user_id = session["user_id"]

        try:
            db.execute(
                "DELETE FROM favorite_recipes WHERE user_id = ? AND recipe_id = ?", user_id, recipe_id)
            return jsonify(success=True)
        except Exception as e:
            print(f"Error deleting recipe from database: {e}")
            return jsonify(success=False, message="A database error occurred.")


@app.route('/create_meal_plan')
@login_required
def meal_plan():

    return render_template('create_meal_plan.html', health_conditions=health_conditions,
                           diet_conditions=diet_conditions, dish_types=dish_types)


@app.route('/request_from_user', methods=["POST"])
@login_required
def temp_plan():

    # We receive a meal plan upon request from the user
    meal_plan = meal_planner(request_from_user())

    if "error" in meal_plan:
        return f"Error: {meal_plan['message']}", meal_plan['error']

    save_temp_planner(meal_plan)
    # Generate data for page rendering from a temporary table
    recipes = extract_plan_from_db("temp_planner")
    recipes.sort(key=lambda x: {"Breakfast": 1,
                 "Lunch": 2, "Dinner": 3}.get(x["meal"], 0))

    return render_template('plan_results.html', recipes=recipes)


@app.route('/save_meal_plan', methods=["POST"])
@login_required
def save_meal_plan():
    user_id = session["user_id"]

    try:
        db.execute("DELETE FROM meal_plan WHERE user_id = ?", user_id)

        db.execute("INSERT INTO meal_plan (user_id, day_number, meal, dish, recipe, recipe_id, image)\
                    SELECT user_id, day_number, meal, dish, recipe, recipe_id, image \
                    FROM temp_planner WHERE user_id = ?", user_id)

        return jsonify(success=True)

    except Exception as e:
        print(f"Error saving meal plan: {e}")
        return jsonify(success=False, message="An error occurred while saving the meal plan.")


@app.route('/my_meal_plan')
@login_required
def my_plan():

    recipes = extract_plan_from_db("meal_plan")
    recipes.sort(key=lambda x: {"Breakfast": 1,
                 "Lunch": 2, "Dinner": 3}.get(x["meal"], 0))

    return render_template('plan_results.html', recipes=recipes)


if __name__ == '__main__':
    app.run(debug=True)
