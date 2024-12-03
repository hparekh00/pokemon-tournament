from models.pokemon import Pokemon
from models.battle import Battle
from models.tournament import Tournament
from models.dbservice import DbService

from typing import List, Optional


class BattleManager:
    def __init__(self, seed: int = None) -> None:
        self.__seed = seed
        self.__battle_id = 0
        self.__tournament_id = 0

    """ This seed will act as global seed passed to everything beneath it when
    SetSeed or RemoveSeed is called by user"""

    def set_seed(self, seed: int = None) -> None:
        self.__seed = seed

    """ Same idea, whenever you create a new tournament or battle with the
    now None seed, it will propogate down to all random decisions """

    def remove_seed(self) -> None:
        self.__seed = None

    """ Fetch battle id to pass down -- needs to be persistent, and
    responsibility given to BattleManager because DbService imports battle and tournament"""

    def get_next_battle_id(self) -> int:
        dbfetch = DbService()
        return dbfetch.get_next_battle_id()

    """ Fetch tournament id to pass down -- needs to be persistent, and
    responsibility given to BattleManager because DbService imports battle and tournament"""

    def get_next_tournament_id(self) -> int:
        dbfetch = DbService()
        return dbfetch.get_next_tournament_id()

    def create_battle(self, pokemon1: Pokemon, pokemon2: Pokemon) -> Battle:
        next_id = self.get_next_battle_id()
        battle = Battle(pokemon1, pokemon2, next_id, self.__seed)
        return battle

    def start_battle(self, battle: Battle) -> Optional[List[Pokemon]]:
        outcome = battle.start_battle()
        return outcome

    # Just initializes a tournament object
    def create_tournament(
        self,
        participants: List[Pokemon],
    ) -> Tournament:
        self.__battle_id = self.get_next_battle_id()
        self.__tournament_id = self.get_next_tournament_id()
        return Tournament(
            participants, self.__tournament_id, self.__battle_id, self.__seed
        )

    # If none was returned, then the tournament was created with invalid participant length or entries
    def start_tournament(self, tournament: Tournament) -> Optional[Pokemon]:
        result = tournament.run_tournament()
        # tournament will increment it's local battle id and we can just fetch it to keep ours updated
        if not result:
            return None
        self.__battle_id = tournament.get_battle_id()
        return result
