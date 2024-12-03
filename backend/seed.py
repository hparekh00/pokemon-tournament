from pymongo import MongoClient
from cryptography.fernet import Fernet
from models.pokemon import Pokemon, Pokemon_Data
from models.skill import AttackSkill, DefenseSkill
import os

client = MongoClient("mongodb://mongo:27017")
db = client.pokemon_database


def clear_tables():
    db.pokemon.delete_many({})
    db.battle.delete_many({})
    db.tournament.delete_many({})
    db.user.delete_many({})
    db.admin.delete_many({})
    print("All tables cleared.")


def initialize_users():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in environment variables")

    cipher = Fernet(key)

    users = [
        {
            "username": "admin",
            "password": cipher.encrypt("password1".encode()).decode(),
            "authorization": 1,  # 1 = ADMINISTRATOR
        },
        {
            "username": "operator",
            "password": cipher.encrypt("password2".encode()).decode(),
            "authorization": 2,  # 2 = OPERATOR
        },
    ]

    db.user.insert_many(users)
    print("Sample users added.")


def initialize_pokemon():
    try:
        starters = [
            {
                "name": "Pikachu",
                "max_hp": 25,
                "image": "@/assets/pikachu.png",
                "attack_skills": [
                    AttackSkill("Growl", 1),
                    AttackSkill("Tail Whip", 2),
                    AttackSkill("Thunder Shock", 3),
                    AttackSkill("Thunder", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Charmander",
                "max_hp": 25,
                "image": "@/assets/charmander.png",
                "attack_skills": [
                    AttackSkill("Attack", 1),
                    AttackSkill("Scratch", 2),
                    AttackSkill("Ember", 3),
                    AttackSkill("Flamethrower", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Squirtle",
                "max_hp": 25,
                "image": "@/assets/squirtle.png",
                "attack_skills": [
                    AttackSkill("Attack", 1),
                    AttackSkill("Tackle", 2),
                    AttackSkill("Water Gun", 3),
                    AttackSkill("Hydro Pump", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Bulbasaur",
                "max_hp": 25,
                "image": "@/assets/bulbasaur.png",
                "attack_skills": [
                    AttackSkill("Tackle", 1),
                    AttackSkill("Vine Whip", 2),
                    AttackSkill("Razor Leaf", 3),
                    AttackSkill("Leaf Storm", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Snorlax",
                "max_hp": 40,
                "image": "@/assets/snorlax.png",
                "attack_skills": [
                    AttackSkill("Rest", 0),
                    AttackSkill("Snore", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Ditto",
                "max_hp": 35,
                "image": "@/assets/ditto.png",
                "attack_skills": [
                    AttackSkill("Transform", 0),
                    AttackSkill("Attack", 2),
                    AttackSkill("Attack", 3),
                    AttackSkill("Attack", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Mew",
                "max_hp": 25,
                "image": "@/assets/mew.png",
                "attack_skills": [
                    AttackSkill("Charm", 0),
                    AttackSkill("Pound", 1),
                    AttackSkill("Imprison", 2),
                    AttackSkill("Psychic", 15),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Geodude",
                "max_hp": 25,
                "image": "@/assets/geodude.png",
                "attack_skills": [
                    AttackSkill("Tackle", 1),
                    AttackSkill("Rock Throw", 2),
                    AttackSkill("Earth Quake", 3),
                    AttackSkill("Rock Slide", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Jigglypuff",
                "max_hp": 25,
                "image": "@/assets/jigglypuff.png",
                "attack_skills": [
                    AttackSkill("Sharpie", 0),
                    AttackSkill("Sing", 1),
                    AttackSkill("Pound", 2),
                    AttackSkill("Double Slap", 10),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Butterfree",
                "max_hp": 40,
                "image": "@/assets/butterfree.png",
                "attack_skills": [
                    AttackSkill("Poison", 0),
                    AttackSkill("Gust", 1),
                    AttackSkill("Whirlwind", 3),
                    AttackSkill("Solar Beam", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Abra",
                "max_hp": 25,
                "image": "@/assets/abra.png",
                "attack_skills": [
                    AttackSkill("Mega Punch", 1),
                    AttackSkill("Mega Kick", 2),
                    AttackSkill("Seismic Toss", 3),
                    AttackSkill("Psychic", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
            {
                "name": "Lapras",
                "max_hp": 25,
                "image": "@/assets/lapras.png",
                "attack_skills": [
                    AttackSkill("Mist", 1),
                    AttackSkill("Ice Shard", 2),
                    AttackSkill("Ice Beam", 3),
                    AttackSkill("Sheer Cold", 6),
                ],
                "defense_skills": [
                    DefenseSkill("Endure", 1),
                    DefenseSkill("Block", 2),
                    DefenseSkill("Protect", 3),
                ],
            },
        ]

        for starter in starters:
            pokemon = Pokemon(
                name=starter["name"],
                max_hp=starter["max_hp"],
                image=starter["image"],
                attack_skills=starter["attack_skills"],
                defense_skills=starter["defense_skills"],
            )
            pokemon_data = Pokemon_Data(pokemon)
            pokemon_data.save()
            print(f"Seeded pokemon: {starter['name']}")
    except Exception as e:
        print(f"Error initializing pokemon: {e}")


def initialize_admin():
    adminData = [
        {
            "events": ["Initialized Admin."],
        },
    ]

    db.admin.insert_many(adminData)
    print(f"Sample Admin table initialized.")


if __name__ == "__main__":
    clear_tables()
    initialize_users()
    initialize_pokemon()
    initialize_admin()
