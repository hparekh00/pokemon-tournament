from models.pokemon import Pokemon
from models.skill import Skill


class Target:
    def __init__(self, pokemon: "Pokemon", skill: "Skill") -> None:
        self.__pokemon = pokemon
        self.__skill = skill

    def get_pokemon(self) -> Pokemon:
        return self.__pokemon

    def get_skill(self) -> Skill:
        return self.__skill
