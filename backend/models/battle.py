import random
from typing import List, Optional, Tuple
from enum import Enum

from models.pokemon import Pokemon
from models.skill import Skill, AttackSkill, DefenseSkill
from models.target import Target
from models.logger import Logger, DbCollection


class turn(Enum):
    POKE_ONE = False
    POKE_TWO = True


logger = Logger()


class Battle:
    def __init__(
        self,
        pokemon1: Pokemon,
        pokemon2: Pokemon,
        battle_id: int = 1,
        seed: Optional[int] = None,
    ):
        self.__pokemon1 = pokemon1
        self.__pokemon2 = pokemon2
        self.__battle_id = battle_id
        self.__battle_random = random.Random()
        self.__battle_seed = seed
        self.__turn = turn.POKE_ONE
        self.__events: List[str] = []

        # random.seed accepts None and just acts as normal random
        self.set_seed(seed)

    def get_pokemon(self) -> List[Pokemon]:
        return list([self.__pokemon1, self.__pokemon2])

    def get_id(self) -> int:
        return self.__battle_id

    def get_events(self) -> List[str]:
        return self.__events

    def get_seed(self) -> int:
        return self.__battle_seed

    def append_event(self, event: str) -> None:
        self.__events.append(event)

    # Track seed and pass on to pokemon
    def set_seed(self, value: int = None) -> None:
        self.__battle_random.seed(value)
        self.__battle_seed = value
        self.set_pokemon_seeds()
        return

    def set_pokemon_seeds(self):
        if self.__battle_seed is not None:
            self.__pokemon1.set_seed(self.__battle_seed)
            self.__pokemon2.set_seed(self.__battle_seed + 1)
        else:
            self.__pokemon1.set_seed()
            self.__pokemon2.set_seed()

    # Check if a Pokémon has fainted.
    def check_if_fainted(self, pokemon: Pokemon) -> bool:
        return pokemon.get_current_hp() == 0

    # Change turn from pokeone to poketwo, or vice versa
    def change_turn(self) -> None:
        if self.__turn == turn.POKE_ONE:
            self.__turn = turn.POKE_TWO
        else:
            self.__turn = turn.POKE_ONE

    # Get action based on pokemon decision tree (seed)
    def get_action_from_pokemon(self, pokemon: Pokemon) -> Target:
        """
        TODO: consider moving target Pokemon choosing into Pokemon class
        """
        # Decide which action a Pokémon should take based on its HP ratio.
        chosen_skill: Skill = pokemon.choose_skill()

        # what to do depends which pokemon is going
        if pokemon.get_name() == self.__pokemon1.get_name():
            # Give self defenses or attack enemy
            if isinstance(chosen_skill, DefenseSkill):
                target_pokemon = self.__pokemon1
            else:
                target_pokemon = self.__pokemon2
        else:
            if isinstance(chosen_skill, DefenseSkill):
                target_pokemon = self.__pokemon2
            else:
                target_pokemon = self.__pokemon1

        return Target(target_pokemon, chosen_skill)

    def execute_skill(self, user: Pokemon, target: Target) -> None:

        # Execute the chosen skill on the target Pokémon.
        target_pokemon = target.get_pokemon()
        skill = target.get_skill()

        if isinstance(skill, AttackSkill):
            # Apply attack damage to the target Pokémon
            damage = skill.get_damage()
            self.append_event(
                f"{user.get_name()} is attacking with {skill.get_name()} "
                f"for {damage} damage to {target_pokemon.get_name()}"
            )

            # take_damage handles damage reduction
            # if pokemon is defending and returns [damage taken, damage reduced]
            """I know it's ugly but I gots a project to complete atp"""
            active_defense = target_pokemon.get_active_defense()
            if active_defense:
                active_defense_name = active_defense.get_name()
            damage_taken_and_reduced = target_pokemon.take_damage(damage)
            damage_taken = damage_taken_and_reduced[0]
            damage_reduced = damage_taken_and_reduced[1]

            if damage_reduced > 0:
                self.append_event(
                    f"{target_pokemon.get_name()} successfully reduced "
                    f"{user.get_name()}'s damage by {damage_reduced} "
                    f"with {active_defense_name}"
                )

            self.append_event(
                f"{target_pokemon.get_name()} has received {damage_taken} damage, "
                f"remaining hp is {target_pokemon.get_current_hp()}"
            )

        elif isinstance(skill, DefenseSkill):
            user.defend(skill)
            self.append_event(
                f"{user.get_name()} is attempting to defend with {skill.get_name()}"
            )

        return

    # Start the battle between two teams of Pokémon.
    def start_battle(self) -> Optional[List[Pokemon]]:
        logger.admin_log(f"battle started: {self.__battle_id}")
        self.append_event("Welcome to the thunderdome!")

        # loop until pokemon faints
        while not self.is_battle_over():
            # Determine which Pokémon's turn it is
            if self.__turn == turn.POKE_ONE:
                pokemon = self.__pokemon1
            else:
                pokemon = self.__pokemon2

            # Execute action
            target: Target = self.get_action_from_pokemon(pokemon)
            self.execute_skill(pokemon, target)
            # Change turn for next round
            self.change_turn()

        # Determine the outcome
        outcome = (
            [self.__pokemon1, self.__pokemon2]
            if not self.check_if_fainted(self.__pokemon1)
            else [self.__pokemon2, self.__pokemon1]
        )

        # Announce outcome and log
        self.append_event(f"{outcome[1].get_name()} has lost")
        self.append_event(f"{outcome[0].get_name()} has won the battle")
        battle_data = Battle_Data(self)
        battle_data.save()
        return outcome

    # Check if the battle is over
    def is_battle_over(self) -> bool:

        team_1_fainted = self.check_if_fainted(self.__pokemon1)
        team_2_fainted = self.check_if_fainted(self.__pokemon2)

        return team_1_fainted or team_2_fainted


class Battle_Data:
    def __init__(self, battle: Battle) -> None:
        # automatically generate loggable data
        self.__data = {}
        self.build_data(battle)

    def get_battle_data(self) -> dict:
        return self.__data

    def save(self) -> None:
        logger.log(self.__data, DbCollection.BATTLE)
        logger.admin_log(f"Battle {self.__data['battle id']} logged")

    def deconstruct_battle(
        self, battle: Battle
    ) -> Tuple[int, List[str], str, str, int]:
        return tuple(
            [
                battle.get_id(),
                battle.get_events(),
                battle.get_pokemon()[0].get_name(),
                battle.get_pokemon()[1].get_name(),
                battle.get_seed(),
            ]
        )

    def build_data(self, battle: Battle) -> None:
        deconstructed = self.deconstruct_battle(battle)
        self.__data = {
            "battle id": deconstructed[0],
            "events": deconstructed[1],
            "pokemon1": deconstructed[2],
            "pokemon2": deconstructed[3],
            "seed": deconstructed[4],
        }
        return
