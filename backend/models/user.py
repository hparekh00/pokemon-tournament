import os
from enum import Enum
from flask import jsonify
from typing import Tuple, List, Optional
from cryptography.fernet import Fernet  # Using Fernet for password encryption
from models.tournament import Tournament
from models.pokemon import Pokemon, Pokemon_Data
from models.battle import Battle
from models.battlemanager import BattleManager
from models.logger import Logger, DbCollection
from models.dbservice import DbService
from models.skill import AttackSkill, DefenseSkill

logger = Logger()
db_service = DbService()

""" This class should be your entry point into starting battles and tournaments,
  or setting and removing seeds, rather than doing that directly!"""


class Authorization(Enum):
    UNKNOWN = 0
    ADMINISTRATOR = 1
    OPERATOR = 2


class User:
    def __init__(
        self, username: str, password: str
    ) -> None:
        self.__username = username
        self.__password = password
        self.__authorization = Authorization.UNKNOWN
        self.__active = False

    def get_username(self) -> str:
        return self.__username

    def get_password(self) -> str:
        return self.__password

    def get_authorization(self) -> Authorization:
        return self.__authorization
    
    def is_active(self) -> bool:
        return self.__active

    def activate(self) -> None:
        self.__active = True

    def deactivate(self) -> None:
        self.__active = False

    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        key = os.getenv("ENCRYPTION_KEY")
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_password.encode()).decode()
    
    def logout(self) -> Authorization:
        self.deactivate()
        logger.admin_log("logged out")
        return Authorization.UNKNOWN


class Operator(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.__authorization = Authorization.OPERATOR
        self.__active = False
        self.__battle_manager = BattleManager()
        self.__active_seed = None

    def get_username(self) -> str:
        return super().get_username()

    def get_password(self) -> str:
        return super().get_password()

    def get_authorization(self) -> Authorization:
        return self.__authorization

    def is_active(self) -> bool:
        return self.__active

    # def login(self, username: str, password: str) -> Authorization:
    #     # self.__active = True
    #     user_data = db_service.fetch_user_data(username)

    #     if not user_data:
    #         logger.admin_log(f"No such user: {username}")
    #         return Authorization.UNKNOWN
        
    #     # Decrypt the password stored in MongoDB (assume it's encrypted with Fernet)
    #     decrypted_password = User.decrypt_password(user_data["password"])

    #     if password == decrypted_password and user_data["authorization"] == 2:
    #         self.activate()
    #         logger.admin_log(f"Operator '{username}' logged in successfully.")
    #         return jsonify({
    #             "message": "Login successful",
    #             "authorization": "OPERATOR"
    #         }), 200
    #     else:
    #         logger.admin_log(f"Incorrect password for {username}")
    #         return Authorization.UNKNOWN

    # Fetch whole battle object
    def get_battle(self, battle_id) -> Optional[Battle]:
        return db_service.get_battle(battle_id)

    # Fetch all whole battle objects
    def get_all_battles(self) -> List:
        return db_service.get_all_battles()

    # Fetch only events from battle object (not extraneous fields)
    def get_battle_log(self, battle_id: int) -> List[str]:
        return db_service.get_battle_events(battle_id)

    # Fetch whole pokemon object
    def lookup_pokemon_info(self, name: str) -> Optional[Pokemon]:
        return db_service.get_pokemon(name)

    # Update or insert pokemon with "name" to the information held in dict
    # Parse the fields to tell user whether there was an insert or update
    def modify_pokemon(self, data: dict) -> None:
        try:
            pokemon = Pokemon(**data)
        except TypeError:
            logger.admin_log("Data could be parsed as pokemon")

        poke_data = Pokemon_Data(pokemon)
        poke_data.save()

    def create_pokemon(self, data: dict) -> None:
        try:
            required_fields = ["name", "max_hp", "image", "attack_skills", "defense_skills"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            attack_skills = [
                AttackSkill(name, damage)
                for name, damage in data["attack_skills"].items()
                if isinstance(name, str) and isinstance(damage, int)
            ]

            defense_skills = [
                DefenseSkill(name, damage)
                for name, damage in data["defense_skills"].items()
                if isinstance(name, str) and isinstance(damage, int)
            ]

            if not attack_skills or not defense_skills:
                raise ValueError("Invalid attack or defense skills provided")

            pokemon = Pokemon(
                name=data["name"],
                max_hp=data["max_hp"],
                image=data["image"],
                attack_skills=attack_skills,
                defense_skills=defense_skills,
            )

        except Exception as e:
            logger.admin_log(f"Error creating Pokémon: {str(e)}")
            raise ValueError(f"Validation error: {str(e)}")

        poke_data = Pokemon_Data(pokemon)
        poke_data.save()

    # Update active seed for user to propogate to events started by user
    def set_seed(self, seed: int = None):
        self.__battle_manager.set_seed(seed)
        self.__active_seed = seed

    def remove_seed(self):
        self.__battle_manager.set_seed(None)
        self.__active_seed = None

    # create tournament when passed list of pokemon names
    def start_tournament(
        self, participants: List[str], seed: int = None
    ) -> Optional[Tournament]:
        logger.admin_log("Attempting to create tournament")

        # Fetch pokemon participants by name
        pokemon = list(db_service.get_pokemon(participant) for participant in participants)

        # Found all pokemon successfully
        if None not in pokemon:
            return self.__battle_manager.start_tournament(pokemon)

        # Fetched failed for whatever reason, so can't create tournament
        else:
            logger.admin_log(
                "create_tournament Failed: Improper attempt to create tournament"
            )
            return None

    # Start a battle between two pokemon
    def execute_battle(self, pokemon1: Pokemon, pokemon2: Pokemon):
        # Battle can manage passing seeds to pokemon
        return self.__battle_manager.start_battle(pokemon1, pokemon2)


class Administrator(Operator):
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)
        self.__authorization = Authorization.ADMINISTRATOR
        self.__active = False

    def get_username(self) -> str:
        return super().get_username()

    def get_password(self) -> str:
        return super().get_password()

    def get_authorization(self) -> Authorization:
        return self.__authorization

    def is_active(self) -> bool:
        return self.__active

    # def login(self, username: str, password: str) -> Authorization:
    #     # self.__active = True
    #     user_data = db_service.fetch_user_data(username)

    #     if not user_data:
    #         logger.admin_log(f"Login failed: Username '{username}' not found.")
    #         return Authorization.UNKNOWN

    #     # Decrypt the password stored in MongoDB (assume it's encrypted with Fernet)
    #     decrypted_password = User.decrypt_password(user_data["password"])

    #     if password == decrypted_password and user_data["authorization"] == 1:
    #         self.activate()
    #         logger.admin_log(f"Administrator '{username}' logged in successfully.")
    #         return jsonify({
    #             "message": "Login successful",
    #             "authorization": "ADMINISTRATOR"
    #         }), 200
    #     else: 
    #         logger.admin_log(f"Login failed: Incorrect credentials for '{username}'.")
    #         return Authorization.UNKNOWN

    def logout(self) -> Authorization:
        self.__active = False
        logger.admin_log("Administrator logged out")
        return Authorization.UNKNOWN

    # Fetch whole battle object
    def get_battle(self, battle_id: int) -> Battle:
        return super().get_battle(battle_id)

    # Fetch all whole battle objects
    def get_all_battles(self) -> List:
        return super().get_all_battles()

    # Fetch only events from battle object (not extraneous fields)
    def get_battle_log(self, battle_id: int) -> List[str]:
        return super().get_battle_log(battle_id)

    # Fetch whole pokemon object
    def lookup_pokemon_info(self, name: str) -> Pokemon:
        return super().lookup_pokemon_info(name)

    # Update or insert pokemon with "name" to the information held in dict
    def modify_pokemon(self, data: dict) -> None:
        return super().modify_pokemon(data)

    # create tournament when passed list of pokemon names
    def start_tournament(self, participants: List[str], seed: int) -> Tournament:
        return super().start_tournament(participants, seed)

    # Start a battle between two pokemon
    def execute_battle(
        self, pokemon1: Pokemon, pokemon2: Pokemon, seed: int = None
    ) -> Battle:
        # Battle can manage passing seeds to pokemon
        return super().execute_battle(pokemon1, pokemon2, seed)

    def view_internal_logs(self) -> Optional[List[str]]:
        return db_service.get_admin_logs()


class User_Data:
    def __init__(self, user: User) -> None:
        # automatically build loggable object
        self.__data = {}
        self.build_data(user)

    def get_user_data(self) -> dict:
        return self.__data

    def save(self) -> None:
        logger.log(self.__data, DbCollection.USER)
        logger.admin_log(f"User {self.__data['username']} logged")

    def deconstruct_user(self, user: User) -> Tuple[str, str, int]:
        return tuple(
            [user.get_username(), user.get_password(), user.get_authorization()]
        )

    def build_data(self, user: User) -> None:
        deconstructed = self.deconstruct_user(user)
        self.__data = {
            "username": deconstructed[0],
            "password": deconstructed[1],
            "privilege": deconstructed[2],
        }
