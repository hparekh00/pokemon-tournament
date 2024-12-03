from models.user import User, Authorization
from models.pokemon import Pokemon
from models.battle import Battle
from models.tournament import Tournament
from models.skill import AttackSkill, DefenseSkill
from models.logger import Logger

import os
from typing import List, Optional

from pymongo import MongoClient
from cryptography.fernet import Fernet  # Using Fernet for password encryption


# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.pokemon_database
# collection = db.pokemon


# TODO: Rename to DbService, and move logger functionality here. They serve similar purpose
class DbFetch:
    def __init__(self) -> None:
        self.__logger = Logger()

    def get_user(self, username: str, password: str) -> Optional[User]:
        key = os.getenv("ENCRYPTION_KEY")

        if key is None:
            raise ValueError("Encryption key not set in environment variables")

        retrieved_user = db.user.find_one({"username": username})
        if retrieved_user is None:
            self.__logger.admin_log(f"No such user: {username}")
            return None
        encrypted_password = retrieved_user["password"]

        cipher = Fernet(key)

        decrypted_password = cipher.decrypt(encrypted_password)

        if password == decrypted_password:
            auth = (
                Authorization.ADMINISTRATOR.value
                if retrieved_user["authorization"] == 1
                else Authorization.OPERATOR.value
            )
            return User(retrieved_user["username"], password, auth)
        else:
            # Password didn't match
            self.__logger.admin_log(f"Incorrect password for {username}")
            return None

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
                name,
                pokemon["max hp"],
                pokemon["current hp"],
                pokemon["battle wins"],
                pokemon["battle losses"],
                pokemon["tournament wins"],
                pokemon["tournament losses"],
                attackSkills,
                defenseSkills,
            )
        else:
            return None

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

    def get_battle_events(self, battleid: int) -> List[str]:
        events: List[str] = []
        retrieved_battle = db.battle.find_one({"battle id": battleid})

        if retrieved_battle is None:
            return None

        for event in retrieved_battle["events"]:
            events.append(event)
        return events

    def get_all_battles(self) -> List:
        all_documents = db.battle.find()
        return list(all_documents)

    def get_tournament(self, tournamentid: int) -> Optional[Tournament]:
        retrieved_tourney = db.battle.find_one({"tournament id": tournamentid})

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

    def get_tournament_events(self, tournamentid: int) -> List[str]:
        retrieved_tourney = db.battle.find_one({"tournament id": tournamentid})

        if retrieved_tourney is None:
            return None

        events: List[str] = []

        for event in retrieved_tourney["events"]:
            events.append_event(event)

        return events

    def get_admin_logs(self) -> Optional[List[str]]:
        # Just have one super admin log to find and retrieve
        admin_logs = db.admin.find_one()
        return admin_logs["events"] if admin_logs else None
