from models.skill import Skill, AttackSkill, DefenseSkill
from models.logger import Logger, DbCollection

import random
from enum import Enum
from typing import List, Optional, Tuple

from models.skill import Skill, AttackSkill, DefenseSkill

logger = Logger()


class Ratio(Enum):
    AGGRESSIVE = 1
    BALANCED = 2
    DEFENSIVE = 3


# should we have a global pokeid to use instead of having name as unique?
# TODO: consider setting up pokemon id system and changing pokemon lookups to id instead of name


class Pokemon:
    def __init__(
        self,
        name: str,
        max_hp: int,
        image: str,
        battle_wins: int = 0,
        battle_losses: int = 0,
        tournament_wins: int = 0,
        tournament_losses: int = 0,
        attack_skills: Optional[List[AttackSkill]] = None,
        defense_skills: Optional[List[DefenseSkill]] = None,
    ):
        self.__name: str = name
        self.__max_hp: int = max_hp
        self.__current_hp: int = max_hp
        self.__image: str = image
        self.__battle_wins: int = battle_wins
        self.__battle_losses: int = battle_losses
        self.__tournament_wins: int = tournament_wins
        self.__tournament_losses: int = tournament_losses
        self.__defense_active: bool = False
        self.__active_defense: Optional[DefenseSkill] = None
        self.__attack_skills: List[AttackSkill] = attack_skills if attack_skills else []
        self.__defense_skills: List[DefenseSkill] = (
            defense_skills if defense_skills else []
        )

        # create a local seed object set to no seed at first
        self.__poke_random: random = random.Random()
        self.__poke_seed: int

    def get_name(self) -> str:
        return self.__name

    def get_max_hp(self) -> int:
        return self.__max_hp

    def get_current_hp(self) -> int:
        return self.__current_hp

    def get_image(self) -> str:
        return self.__image

    def get_battle_wins(self) -> int:
        return self.__battle_wins

    def get_battle_losses(self) -> int:
        return self.__battle_losses

    def get_touranment_wins(self) -> int:
        return self.__tournament_wins

    def get_tournament_losses(self) -> int:
        return self.__tournament_losses

    def get_battle_win_loss_ratio(self) -> float:
        return (
            self.__battle_wins / self.__battle_losses if self.__battle_losses > 0 else 0
        )

    def get_tournament_win_loss_ratio(self) -> float:
        return (
            self.__tournament_wins / self.__tournament_losses
            if self.__tournament_losses > 0
            else 0
        )

    def increment_battle_wins(self) -> int:
        self.__battle_wins += 1
        return self.__battle_wins

    def increment_battle_losses(self) -> int:
        self.__battle_losses += 1
        return self.__battle_losses

    def increment_tournament_wins(self) -> int:
        self.__tournament_wins += 1
        return self.__tournament_wins

    def increment_tournament_losses(self) -> int:
        self.__tournament_losses += 1
        return self.__tournament_losses

    def get_attack_skills(self) -> List[AttackSkill]:
        return self.__attack_skills

    def get_defense_skills(self) -> List[DefenseSkill]:
        return self.__defense_skills

    def get_all_skills(self) -> List[Skill]:
        return self.__attack_skills + self.__defense_skills

    def get_active_defense(self) -> DefenseSkill:
        return self.__active_defense

    def get_hp_ratio(self) -> Ratio:
        if self.__max_hp > 0:
            ratio = self.__current_hp / self.__max_hp
            if ratio >= 0.7:
                return Ratio.AGGRESSIVE
            elif ratio >= 0.3:
                return Ratio.BALANCED
        return Ratio.DEFENSIVE

    def get_seed(self) -> int:
        return self.__poke_seed

    def set_seed(self, value: int = None) -> None:
        # set this pokemon's seed
        self.__poke_seed = value
        self.__poke_random.seed(value)
        return

    def rest(self) -> None:
        self.__current_hp = self.__max_hp

    def add_skill(self, skill: Skill) -> List[Skill]:
        if isinstance(skill, DefenseSkill):
            self.__defense_skills.append(skill)
            return self.__defense_skills
        elif isinstance(skill, AttackSkill):
            self.__attack_skills.append(skill)
            return self.__attack_skills
        else:
            return self.get_all_skills()

    def remove_skill(self, skill: Skill) -> List[Skill]:
        if isinstance(skill, AttackSkill):
            for s in self.__attack_skills:
                if s.get_name() == skill.get_name():
                    self.__attack_skills.remove(s)
                    return self.__attack_skills
        elif isinstance(skill, DefenseSkill):
            for s in self.__defense_skills:
                if s.get_name() == skill.get_name():
                    self.__defense_skills.remove(s)
                    return self.__defense_skills
        else:
            return self.get_all_skills()

    def set_defense_skills(
        self, defense_skills: List[DefenseSkill]
    ) -> List[DefenseSkill]:
        if isinstance(defense_skills, List[DefenseSkill]):
            self.__defense_skills = defense_skills
        else:
            return defense_skills
        return defense_skills

    def set_attack_skills(self, attack_skills: List[AttackSkill]) -> List[AttackSkill]:
        if isinstance(attack_skills, List[DefenseSkill]):
            self.__attack_skills = attack_skills
        else:
            return attack_skills
        return attack_skills

    def get_random_skill(self, skills: List[Skill]) -> Skill:
        if not skills:
            raise ValueError("Skill list must not be empty.")
        # pick a random skill based on this pokemon's seed
        return self.__poke_random.choice(skills)

    def choose_skill(self) -> Skill:

        ratio = self.get_hp_ratio()
        # Make sure to use that set seed!
        threshold = self.__poke_random.randint(0, 9)  # Random value between 0 and 9

        # Determine action based on HP ratio and threshold
        if ratio == Ratio.AGGRESSIVE:
            if threshold < 7:
                chosen_skill = self.get_random_skill(self.get_attack_skills())
            else:
                chosen_skill = self.get_random_skill(self.get_defense_skills())
        elif ratio == Ratio.BALANCED:
            if threshold < 5:
                chosen_skill = self.get_random_skill(self.get_attack_skills())
            else:
                chosen_skill = self.get_random_skill(self.get_defense_skills())
        else:  # Ratio.DEFENSIVE
            if threshold < 3:
                chosen_skill = self.get_random_skill(self.get_attack_skills())
            else:
                chosen_skill = self.get_random_skill(self.get_defense_skills())
        return chosen_skill

    # Battle handles damage, so 'defend' more logical than 'use'
    def defend(self, skill: Skill) -> None:
        if self.__defense_active:
            self.__defense_active = False
            self.__active_defense = None

        if isinstance(skill, DefenseSkill):
            self.__defense_active = True
            self.__active_defense = skill

        return

    def take_damage(self, damage: int) -> List[int]:

        # res[0] is damage actually taken, res[1] is damage reduction amt
        res = [0, 0]
        damage_to_take = damage
        # Make sure defense_active. If it is None, will not reduce at all
        if self.__defense_active:
            # return true damage after it has been reduced
            damage_to_take = self.__active_defense.reduce_damage(damage)
            res[1] = damage - damage_to_take
            self.__defense_active = False
            self.__active_defense = None

        # for logging, pokemon either takes current hp or damage
        res[0] = min(self.__current_hp, damage_to_take)
        # Set health to 0 if health would be negative
        self.__current_hp = max(0, self.__current_hp - damage_to_take)
        return res


# Easier than passing Mongo type hints if our data structure changes tbh
# Stores all relevant information about a pokemon -- search mongo by name
class Pokemon_Data:
    def __init__(self, pokemon: Pokemon) -> None:
        # automatically generate object for storage
        self.__data = {}
        self.build_data(pokemon)

    def get_pokemon_data(self) -> dict:
        return self.__data

    def save(self) -> None:
        logger.log(self.__data, DbCollection.POKEMON)
        logger.admin_log(f"Pokemon {self.__data['name']} upserted")

    def insert(self) -> None:
        logger.insert("pokemon", self.__data)
        logger.admin_log(f"Pokemon {self.__data['name']} inserted")

    def skills_to_dict(self, skills: List[Skill]) -> dict:
        res = {}
        for skill in skills:
            """
            res dict looks like:
            {
            "name": damage,
            "name": damage,
            .
            .
            .
            }
            """
            res[skill.get_name()] = skill.get_damage()
        return res

    def deconstruct_pokemon(
        self, pokemon: Pokemon
    ) -> Tuple[str, int, int, int, int, int, int, float, float, dict, dict]:
        return tuple(
            [
                pokemon.get_name(),
                pokemon.get_max_hp(),
                pokemon.get_image(),
                pokemon.get_battle_wins(),
                pokemon.get_battle_losses(),
                pokemon.get_touranment_wins(),
                pokemon.get_tournament_losses(),
                pokemon.get_battle_win_loss_ratio(),
                pokemon.get_tournament_win_loss_ratio(),
                self.skills_to_dict(pokemon.get_attack_skills()),
                self.skills_to_dict(pokemon.get_defense_skills()),
            ]
        )

    def build_data(self, pokemon: Pokemon) -> None:
        deconstructed = self.deconstruct_pokemon(pokemon)
        self.__data = {
            "name": deconstructed[0],
            "max hp": deconstructed[1],
            "image": deconstructed[2],
            "battle wins": deconstructed[3],
            "battle losses": deconstructed[4],
            "tournament wins": deconstructed[5],
            "tournament losses": deconstructed[6],
            "battle W/L": deconstructed[7],
            "tournament W/L": deconstructed[8],
            "attack skills": deconstructed[9],
            "defense skills": deconstructed[10],
        }
        return
