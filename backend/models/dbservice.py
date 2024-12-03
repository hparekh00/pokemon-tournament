# from models.user import User, Authorization
from models.pokemon import Pokemon
from models.battle import Battle
from models.tournament import Tournament
from models.skill import AttackSkill, DefenseSkill
from pymongo import MongoClient
from typing import List, Optional
from cryptography.fernet import Fernet  # Using Fernet for password encryption
import os
from enum import Enum

# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.pokemon_database
collection = db.pokemon


class DbCollection(Enum):
    BATTLE = "BATTLE"
    TOURNAMENT = "TOURNAMENT"
    POKEMON = "POKEMON"
    USER = "USER"


class DbService:

    # Return password encrypted with Fernet key from .env
    def encrypt_password(self, password: str) -> str:
        key = os.getenv("ENCRYPTION_KEY")

        if key is None:
            raise ValueError("Encryption key not set in environment variables")

        cipher = Fernet(key)
        encrypted_password = cipher.encrypt(password.encode())
        return encrypted_password

    # Fetch user by username
    def fetch_user_data(self, username: str) -> Optional[dict]:
        user = db.user.find_one({"username": username})
        if not user:
            print(f"User '{username}' not found in the database.")
            return None
        return user

    # Fetches pokemon object by name
    def get_pokemon(self, name: str) -> Optional[Pokemon]:
        pokemon = db.pokemon.find_one({"name": name})
        if pokemon is not None:
            defenseSkills = [
                DefenseSkill(name, damage)
                for name, damage in pokemon["defense skills"].items()
            ]
            attackSkills = [
                AttackSkill(name, damage)
                for name, damage in pokemon["attack skills"].items()
            ]
            return Pokemon(
                name=name,
                max_hp=pokemon["max hp"],
                image=pokemon["image"],
                battle_wins=pokemon["battle wins"],
                battle_losses=pokemon["battle losses"],
                tournament_wins=pokemon["tournament wins"],
                tournament_losses=pokemon["tournament losses"],
                attack_skills=attackSkills,
                defense_skills=defenseSkills,
            )
        else:
            return None

    # Fetches battle object by id
    def get_battle(self, battleid: int) -> Optional[Battle]:
        retrieved_battle = db.battle.find_one({"battle id": battleid})

        if retrieved_battle is None:
            return None

        pokemon1: Pokemon = self.get_pokemon(retrieved_battle["pokemon1"])
        pokemon2: Pokemon = self.get_pokemon(retrieved_battle["pokemon1"])

        if pokemon1 is not None and pokemon2 is not None:
            battle = Battle(pokemon1, pokemon2, retrieved_battle["battle id"], None)
        else:
            return None

        for event in retrieved_battle["events"]:
            battle.append_event(event)
        return battle

    # Fetches battle log that just holds events
    def get_battle_events(self, battleid: int) -> List[str]:
        events: List[str] = []
        retrieved_battle = db.battle.find_one({"battle id": battleid})

        if retrieved_battle is None:
            return None

        for event in retrieved_battle["events"]:
            events.append(event)
        return events

    # Fetches all battle objects in collection
    def get_all_battles(self) -> List:
        # Returns them in sorted (Ascending) order for ease of use
        all_documents = db.battle.find().sort("battle id", 1)
        return list(all_documents)

    # Fetches most recent battle id and increments for next go
    def get_next_battle_id(self) -> int:
        # Generate unique battle ID
        return db.battle.count_documents({}) + 1

    # Fetches most recent battle id and increments for next go
    def get_next_tournament_id(self) -> int:
        return db.tournament.count_documents({}) + 1

    # Fetch tournament object by id
    def get_tournament(self, tournamentid: int) -> Optional[Tournament]:
        retrieved_tourney = db.tournament.find_one({"tournament id": tournamentid})

        if retrieved_tourney is None:
            return None

        participants: List[Pokemon] = []

        for participant in retrieved_tourney["participants"]:
            pokemon: Pokemon = self.get_pokemon(participant)
            if pokemon is None:
                return None

            participants.append(pokemon)

        tournament = Tournament(participants, retrieved_tourney["tournament id"])

        for event in retrieved_tourney["events"]:
            tournament.append_event(event)

        return tournament

    # Fetches tournament log by id -- list of battle victors who move on to next round
    def get_tournament_events(self, tournamentid: int) -> List[str]:
        retrieved_tourney = db.battle.find_one({"tournament id": tournamentid})

        if retrieved_tourney is None:
            return None

        events: List[str] = []

        for event in retrieved_tourney["events"]:
            events.append_event(event)

        return events

    # Fetches the grow-only admin log that stores administrative events
    def get_admin_logs(self) -> Optional[List[str]]:
        # Just have one super admin log to find and retrieve
        admin_logs = db.admin.find_one()
        return admin_logs["events"] if admin_logs else None
