import hashlib
import requests
from argon2 import PasswordHasher
from flask import session
from requests.auth import HTTPBasicAuth
import json
from cs50 import SQL
import base64
import os
from dotenv import load_dotenv

from flask import redirect, request, session
from functools import wraps

load_dotenv()

ph = PasswordHasher()

db = SQL("sqlite:///users.db")


# Data arrays for creating selection forms
health_conditions = ['fat-free', 'low-fat-abs', 'sugar-conscious', 'low-sugar', 'low-potassium', 'kidney-friendly',
                     'keto-friendly', 'plant-based', 'vegan', 'vegetarian', 'pescatarian', 'paleo', 'specific-carbs',
                     'Mediterranean', 'DASH', 'dairy-free', 'gluten-free', 'wheat-free', 'egg-free', 'milk-free',
                     'peanut-free', 'tree-nut-free', 'soy-free', 'fish-free', 'shellfish-free', 'pork-free', 'red-meat-free',
                     'crustacean-free', 'celery-free', 'mustard-free', 'sesame-free', 'lupine-free', 'mollusk-free',
                     'alcohol-free', 'no-oil-added', 'no-sugar-added', 'sulfite-free', 'fodmap-free', 'kosher','immuno-supportive' ]

diet_conditions = ['balanced', 'high-protein', 'high-fiber', 'low-fat', 'low-carb', 'low-sodium']

dish_types = ['alcohol cocktail', 'biscuits and cookies', 'bread', 'cereals', 'condiments and sauces', 'desserts',
              'drinks', 'egg', 'ice cream and custard', 'main course', 'pancake', 'pasta', 'pastry', 'pies and tarts',
              'pizza', 'preps', 'preserve', 'salad', 'sandwiches', 'seafood', 'side dish', 'soup', 'special occasions', 'starter']


# Extracting the assigned URIs from the API response
def extract_assigned_urls(data):
    assigned_urls = []

    def recurse_sections(sections):
        for value in sections.items():
            if isinstance(value, dict):
                if 'assigned' in value:
                    assigned_urls.append(value['assigned'])
                if 'sections' in value:
                    recurse_sections(value['sections'])

    if 'selection' in data:
        for selection in data['selection']:
            recurse_sections(selection['sections'])
    else:
        print("Key 'selection' missing from response data")

    return assigned_urls


# Updated exception recipes for meal plan functionality
def update_exclude_recipes(data):

    exclude_recipes = session.get('exclude_recipes', [])

    new_recipes = extract_assigned_urls(data)

    # Add unique recipe URIs to exclude_recipes and save in session
    exclude_recipes.extend(uri for uri in new_recipes if uri not in exclude_recipes)
    session['exclude_recipes'] = exclude_recipes

    return exclude_recipes


# Appeal to API Meal Plan
def meal_planner(query_from_user):

    app_id = os.getenv("APP_ID_MEAL_PLANNER")
    app_key = os.getenv("APP_KEY_MEAL_PLANNER")
    url = os.getenv("URL_MEAL_PLANNER")

    if 'exclude_recipes' not in session:
        session['exclude_recipes'] = []

    headers = {
        'accept': 'application/json',
        'Edamam-Account-User': 'YevhenKhalin',
        'Content-Type': 'application/json'
    }

    # Executing a request
    response = requests.post(url, auth=HTTPBasicAuth(app_id, app_key), headers=headers, json=query_from_user)

    if response.status_code == 200:
        data = response.json()
        if data:
            # uris = extract_assigned_urls(data)
            update_exclude_recipes(data)
            return data
    else:
        print('Error:', response.status_code, response.text)
        return {'error': response.status_code, 'message': response.text}


# Receiving recipes by their URI
def receiving_recipes_via_URI(uris):

    url = os.getenv("URL_RECIPES_URI")
    app_id = os.getenv("APP_ID_RECIPES")
    app_key = os.getenv("APP_KEY_RECIPES")

    all_recipes = []

     # Function to split a list due to the API request limit of 20 values.
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    # We divide uris into lists of no more than 20 in length
    uri_chunks = list(chunk_list(uris, 20))

    for chunk in uri_chunks:
        params = {
            "type": "public",
            "uri": chunk,
            "app_id": app_id,
            "app_key": app_key
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            recipes = data.get('hits', [])
            all_recipes.extend(recipes)
        else:
            print('Error:', response.status_code, response.text)
            return {'error': response.status_code, 'message': response.text}

    return all_recipes if all_recipes else {'error': 'No recipes found'}


# Generate a unique recipe ID
def generate_recipe_id(recipe_data):

    # Use the label and list of ingredients to generate a unique ID
    recipe_name = recipe_data.get('label', '')
    ingredient_lines = recipe_data.get('ingredientLines', [])

    if not isinstance(ingredient_lines, list):
        raise TypeError("Expected ingredientLines to be a list")

    ingredients = ','.join(ingredient_lines)
    unique_string = recipe_name + ingredients

    # Generate a hash
    return hashlib.blake2b(unique_string.encode()).hexdigest()


# Saves recipes to session with duplicate check.
def save_recipes_to_session(recipes):

    results = session.get('api_results', [])

    for recipe in recipes:
        recipe_data = recipe['recipe']
        recipe_id = generate_recipe_id(recipe_data)

        # Check if a recipe with this ID exists
        if find_recipe_by_id(recipe_id) is None:
            results.append({
                'id': recipe_id,
                'recipe': recipe_data
            })

    # We update the session with new results
    session['api_results'] = results


# Checking login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Search recipes function
def searchRecipes(query = None, random = False):

    app_id = os.getenv("APP_ID_RECIPES")
    app_key = os.getenv("APP_KEY_RECIPES")
    url = os.getenv("URL_RECIPES")

    # Check that all environment variables are set
    if not app_id or not app_key or not url:
        raise ValueError("APP_ID_RECIPES, APP_KEY_RECIPES, and URL_RECIPES must be set in the environment variables")

    params = {
        "type": "public",
        "q": query if query else "random",
        "app_id": app_id,
        "app_key": app_key,
    }

    if random:
        params["random"] = True

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        recipes = data.get('hits', [])[:4] if random else data.get('hits', [])

        results = []
        for recipe in recipes:
            recipe_data = recipe['recipe'] # Recipe data from API response
            recipe_id = generate_recipe_id(recipe_data)  # Generate unique ID for each element

            results.append({
                'id': recipe_id,
                'recipe': recipe_data
            })

        # Saving recipes using a common function in a session
        save_recipes_to_session(results)

        return results if results else []
    else:
        print('Error:', response.status_code, response.text)
        return []

# Password Hashing function
def hash_password(plain_password):
    return ph.hash(plain_password)

# Check password
def check_password(plain_password, hashed_password):
    try:
        return ph.verify(hashed_password, plain_password)
    except:
        return False


# Search for a recipe by its ID
def find_recipe_by_id(recipe_id):

    api_results = session.get("api_results", [])

    for item in api_results:
        if item['id'] == recipe_id:
            return item['recipe']

    return None


# Request to the API and save the meal plan to a temporary table
def save_temp_planner(json_response):

    db.execute("DELETE FROM temp_planner")

    user_id = session["user_id"]
    uris = []
    uri_to_meal_info = []

    # Preparing a request to the API using recipe uri identifiers
    for day_number, day_data in enumerate(json_response.get('selection', []), start=1):
        sections = day_data.get('sections', {})

        for meal, meal_data in sections.items():
            if 'sections' not in meal_data:
                uri = meal_data.get('assigned')
                uris.append(uri)
                uri_to_meal_info.append((user_id, day_number, meal, None, uri))
            else:
                for dish_name, dish_data in meal_data['sections'].items():
                    uri = dish_data.get('assigned')
                    uris.append(uri)
                    uri_to_meal_info.append((user_id, day_number, meal, dish_name, uri))

    # Get recipes for all URIs from the API response
    recipes = receiving_recipes_via_URI(uris)

    # Create URI mapping to recipes
    if recipes:
        save_recipes_to_session(recipes)
        uri_to_recipe = {recipe["recipe"]["uri"]: recipe["recipe"] for recipe in recipes}

    # Prepare data for saving
    for user_id, day_number, meal, dish, uri in uri_to_meal_info:
        recipe = uri_to_recipe.get(uri, {})

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

        recipe_id = generate_recipe_id(recipe_data)

        # Prepare image for saving
        image_url  = recipe.get('image')
        if image_url:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    # Convert image to base64
                    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                else:
                    print("Error loading image:", image_response.status_code)
                    image_base64 = None
            except Exception as e:
                print(f"Error loading image: {e}")
                image_base64 = None
        else:
            image_base64 = None

        try:
            db.execute("INSERT INTO temp_planner (user_id, day_number, meal, dish, recipe, recipe_id, image)\
                        VALUES (?, ?, ?, ?, ?, ?, ?)",\
                        user_id, day_number, meal, dish, json.dumps(recipe_data), recipe_id, image_base64)
        except Exception as e:
            print(f"Error inserting user into database: {e}")


# Form a request to the API Meal Plan according to the data from the user
def request_from_user():
    # Receive data from the user
    days = int(request.form.get("days", 1))
    health_conditions = request.form.getlist("health_conditions") or []
    diet_conditions = request.form.getlist("diet_conditions") or []
    min_calories = int(request.form.get("min_calories") or 1500)
    max_calories = int(request.form.get("max_calories") or 2000)

    # Assembling breakfast subcategories
    health_breakfast = request.form.getlist("health_breakfast") or []
    breakfast_dish = request.form.getlist("breakfast_dish") or []

    health_lunch = request.form.getlist("health_lunch") or []
    lunch_dish = request.form.getlist("lunch_dish") or []

    # Assembling lunch subcategories
    lunch_sections = request.form.getlist('lunch_sections')
    lunch_subsections = {}
    if "Starter" in lunch_sections:
        starter_dish = request.form.getlist("starter_dish") or []
        lunch_subsections["Starter"] = {
            "accept": {"all": [{"dish": starter_dish}]}
        }
    if "Main" in lunch_sections:
        lunch_main_dish = request.form.getlist("lunch_main_dish") or []
        lunch_subsections["Main"] = {
            "accept": {"all": [{"dish": lunch_main_dish}]}
        }
    if "Dessert" in lunch_sections:
        lunch_dessert = request.form.getlist("lunch_dessert") or []
        lunch_subsections["Dessert"] = {
            "accept": {"all": [{"dish": lunch_dessert}]}
        }

    health_dinner = request.form.getlist("health_dinner") or []
    dinner_dish = request.form.getlist("dinner_dish") or []

    # Assembling dinner subcategories
    dinner_sections = request.form.getlist('dinner_sections')
    dinner_subsections = {}
    if "Main" in dinner_sections:
        dinner_main_dish = request.form.getlist("dinner_main_dish") or []
        dinner_subsections["Main"] = {
            "accept": {"all": [{"dish": dinner_main_dish}]}
        }
    if "Dessert" in dinner_sections:
        dinner_dessert = request.form.getlist("dinner_dessert") or []
        dinner_subsections["Dessert"] = {
            "accept": {"all": [{"dish": dinner_dessert}]}
        }

    # Generate a JSON template for the request
    data = {
        "size": days,
        "plan": {
            "accept": {
                "all": [{"health": health_conditions}, {"diet": diet_conditions}]
            },
            "fit": {
                "ENERC_KCAL": {"min": min_calories, "max": max_calories}
            },
            "exclude": session.get('exclude_recipes', []),
            "sections": {
                "Breakfast": {
                    "accept": {
                        "all": [
                            {"health": health_breakfast},
                            {"dish": breakfast_dish}
                        ]
                    }
                },
                "Lunch": {
                    "accept": {
                        "all": [
                            {"health": health_lunch},
                            {"dish": lunch_dish}
                        ]
                    },
                    "sections": lunch_subsections
                },
                "Dinner": {
                    "accept": {
                        "all": [
                            {"health": health_dinner},
                            {"dish": dinner_dish}
                        ]
                    },
                    "sections": dinner_subsections
                }
            }
        }
    }

    return data


# Getting a meal plan from the database
def extract_plan_from_db(table_name):
    user_id = session["user_id"]
    recipes = []

    try:
        rows = db.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", user_id)
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []

    # Parse the JSON data for each recipe
    for row in rows:
        try:
            recipe_data = json.loads(row['recipe'])
            recipe_data['recipe_id'] = row['recipe_id']
            recipe_data['day_number'] = row['day_number']
            recipe_data['meal'] = row['meal']
            recipe_data['dish'] = row['dish']
            recipe_data['image'] = row['image']
            recipes.append(recipe_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

    return recipes
