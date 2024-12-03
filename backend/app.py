import os

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from pymongo import MongoClient, errors
from models.battle import Battle
from models.tournament import Tournament, Tournament_Data
from models.user import Operator, User, Administrator
from models.logger import Logger
from models.dbservice import DbService
from models.pokemon import Pokemon
from models.skill import AttackSkill, DefenseSkill
from models.battlemanager import BattleManager

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3001"],
)
app.secret_key = "secret-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True if using HTTPS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
battle_id = 0  # Global battle ID counter

# TODO: Set Admin logs for like everything
# TODO: ensure ownership relationships are maintained from documentation
# TODO: ensure that stops can work at any point and return control -- currently only checks in ongoing battle and tournament
# TODO: address PR comments (https://github.gatech.edu/jsh6/flask-pokemon-tournament/pull/7/files#diff-a29ff322ddbacd468fea10dfb6857e1026da13b23b9ae94e4c4d0e7d2c794dad) and fix db insert stuff
# TODO: display stop message to user when stop is input

# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.pokemon_database
# collection = db.pokemon
pokemon_collection = db.pokemon
battle_collection = db.battle
tournament_collection = db.tournament
user_collection = db.user

db_service = DbService()
# previously was referencing the module, not initializing an object
logger = Logger()
# previously was referencing the module, not initializing an object
operator = Operator("operator", "password2")
# Authoritative source for battle and tournament creation
battlemanager = BattleManager()


def create_unique_index(collection: str, field: str) -> None:

    collection_obj = db[collection]

    try:
        # Create the index if it doesn't already exist
        collection_obj.create_index([(field, 1)], unique=True)
        print(f"Unique index on '{field}' field created successfully for collection.")
    except errors.DuplicateKeyError:
        # If the index already exists and there are duplicates, handle it here
        print(f"Duplicate key error: The '{field}' field must be unique.")
    except Exception as e:
        print(f"Error creating index: {e}")


def initialize() -> None:
    create_unique_index("pokemon", "name")
    create_unique_index("battle", "battle id")
    create_unique_index("tournament", "tournament id")
    create_unique_index("user", "username")


# Create uniqueness constraints on tables
initialize()


@app.route("/pokemon", methods=["POST"])
def add_pokemon():
    try:
        # Ensure the user is logged in
        if "user" not in session:
            return jsonify({"error": "Unauthorized. Please log in first."}), 401
        # Get user role and username from the session
        user_role = session["user"]["role"]
        username = session["user"]["username"]

        data = request.json

        # Create the appropriate user object dynamically based on role
        if user_role == "admin":
            user = Administrator(username, "N/A")
        elif user_role == "operator":
            user = Operator(username, "N/A")
        else:
            return jsonify({"error": "Invalid user role."}), 403

        user.create_pokemon(data)
        return (
            jsonify({"message": f"Pokemon '{data['name']}' created successfully."}),
            201,
        )

    except ValueError as ve:
        return jsonify({"error": f"Validation error: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Get all Pokemon
@app.route("/pokemon", methods=["GET"])
def list_pokemon():
    try:
        pokemon_name = request.args.get("name")

        if pokemon_name:
            pokemon = db_service.get_pokemon(pokemon_name)
            if not pokemon:
                return jsonify({"error": f"Pokémon '{pokemon_name}' not found"}), 404

            pokemon_data = {
                "name": pokemon.get_name(),
                "max hp": pokemon.get_max_hp(),
                "image": pokemon.get_image(),
                "attack skills": [
                    {"name": skill.get_name(), "damage": skill.get_damage()}
                    for skill in pokemon.get_attack_skills()
                ],
                "defense skills": [
                    {"name": skill.get_name(), "damage": skill.get_damage()}
                    for skill in pokemon.get_defense_skills()
                ],
            }
            return jsonify(pokemon_data), 200
        else:
            # TODO: ideally we would move this logic to dbservice for same reason but whatever
            pokemon_list = list(pokemon_collection.find({}))
            for p in pokemon_list:
                p["_id"] = str(p["_id"])
            return jsonify(pokemon_list), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Battle Routes


# Start battle
@app.route("/battle", methods=["POST"])
def start_battle():
    try:
        # Parse request data
        data = request.json

        # Validate required fields
        required_fields = ["pokemon1", "pokemon2"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        pokemon1_name = data["pokemon1"]
        pokemon2_name = data["pokemon2"]
        seed = data.get("seed")  # Optional seed for deterministic behavior

        # Fetch Pokémon objects from the database
        pokemon1 = db.pokemon.find_one({"name": pokemon1_name})
        pokemon2 = db.pokemon.find_one({"name": pokemon2_name})

        if not pokemon1 or not pokemon2:
            return (
                jsonify({"error": "One or both Pokémon not found in the database"}),
                404,
            )

        # Create Pokémon objects
        poke1 = Pokemon(
            name=pokemon1["name"],
            max_hp=pokemon1["max hp"],
            image=pokemon1["image"],
            attack_skills=[
                AttackSkill(name, damage)
                for name, damage in pokemon1["attack skills"].items()
            ],
            defense_skills=[
                DefenseSkill(name, damage)
                for name, damage in pokemon1["defense skills"].items()
            ],
        )

        poke2 = Pokemon(
            name=pokemon2["name"],
            max_hp=pokemon2["max hp"],
            image=pokemon2["image"],
            attack_skills=[
                AttackSkill(name, damage)
                for name, damage in pokemon2["attack skills"].items()
            ],
            defense_skills=[
                DefenseSkill(name, damage)
                for name, damage in pokemon2["defense skills"].items()
            ],
        )

        if seed:
            battlemanager.set_seed(seed)

        # Initialize the battle -- battlemanager handles seed tracking and incrementing battle_id
        battle = battlemanager.create_battle(pokemon1=poke1, pokemon2=poke2)

        # Get the unique battle ID
        battle_id = battle.get_id()

        # Start the battle and return outcome
        outcome = battlemanager.start_battle(battle)

        # Handle the response based on the outcome
        if outcome is None:
            return (
                jsonify({"message": "Battle terminated early", "battle_id": battle_id}),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "message": "Battle completed",
                        "battle_id": battle_id,
                        "winner": outcome[0].get_name(),
                        "loser": outcome[1].get_name(),
                        "events": battle.get_events(),
                    }
                ),
                200,
            )

    except ValueError as ve:
        return jsonify({"error": f"Validation error: {str(ve)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Get battle
@app.route("/battle/<battle_id>", methods=["GET"])
def get_battle_logs(battle_id):
    # Use dbservice to reduce code redundancy and allow for one-stop function fixes
    battle = db_service.get_battle(int(battle_id))
    if not battle:
        return jsonify({"error": "Battle not found"}), 404

    # JSONify the entire battle result, but you can use whatever you want from it
    return (
        jsonify(
            {
                "message": "Battle Found",
                "battle_id": battle_id,
                "events": battle.get_events(),
            }
        ),
        200,
    )


# Tournament Routes


# Start tournament
@app.route("/tournament", methods=["POST"])
def start_tournament():
    data = request.json

    # Validate required fields
    required_fields = ["participants"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    participants = []

    # Fetch all participating pokemon by name from request
    for pokemon_name in data["participants"]:
        pokemon = db_service.get_pokemon(pokemon_name)
        if not pokemon:
            return (
                jsonify({"error": f"Pokémon {pokemon_name} not found in the database"}),
                404,
            )
        else:
            participants.append(pokemon)

    seed = data.get("seed")  # Optional seed for deterministic behavior

    if seed:
        battlemanager.set_seed(seed)

    # battlemanager will handle id tracking and seed passing
    tournament = battlemanager.create_tournament(participants)
    result = battlemanager.start_tournament(tournament)

    # Tournament will save itself so no need to worry about that

    # Tournament was invalid or ended early for some reason
    if not result:
        return (
            jsonify(
                {
                    "message": "Tournament terminated early",
                    "tournament_id": tournament.get_tournament_id(),
                }
            ),
            200,
        )
    return jsonify(
        {
            "message": "Tournament started",
            "tournament_id": tournament.get_tournament_id(),
        }
    )


# Get tournament
@app.route("/tournament/<tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    # Fetch the tournament data directly from the database
    retrieved_tourney = db.tournament.find_one({"tournament id": int(tournament_id)})

    if not retrieved_tourney:
        return jsonify({"error": "Tournament not found"}), 404

    # Extract relevant data from the retrieved tournament
    events = retrieved_tourney["events"]
    winner = retrieved_tourney.get("winner", "")

    # Prepare the response with the tournament details
    response = {
        "tournament_id": retrieved_tourney["tournament id"],
        "events": events,
        "winner": winner,
    }

    return jsonify(response), 200


# Users Routes


# Get user
@app.route("/login", methods=["POST"])
def login():
    try:
        # Extract username and password from the request body
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user_data = db_service.fetch_user_data(username)
        if not user_data:
            return jsonify({"error": "Invalid username or password."}), 401

        try:
            decrypted_password = User.decrypt_password(user_data["password"])
        except Exception as e:
            return jsonify({"error": "Error decrypting password."}), 500

        if password != decrypted_password:
            return jsonify({"error": "Invalid username or password."}), 401

        if user_data["authorization"] == 1:
            user = Administrator(username, password)
        elif user_data["authorization"] == 2:
            user = Operator(username, password)
        else:
            return jsonify({"error": "Invalid user authorization level."}), 403

        # Save user info to session
        user.activate()
        session["user"] = {
            "username": username,
            "role": "admin" if isinstance(user, Administrator) else "operator",
        }
        return jsonify({"message": f"{username} logged in successfully."}), 200

    except Exception as e:
        logger.admin_log(f"Login error: {str(e)}")
        return jsonify({"error": f"An error occurred during login: {str(e)}"}), 500


#Get the Admin Logs from the database
@app.route("/adminLogs", methods=["GET"])
def getAdminLogs():
    # Fetch the tournament data directly from the database
    retrieved_logs = db_service.get_admin_logs()

    # Prepare the response with the tournament details
    response = {
        "events": retrieved_logs,
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6035)
