from models.pokemon import Pokemon
from models.battle import Battle
from models.logger import Logger, DbCollection

import random
from typing import List, Optional, Tuple

logger = Logger()


class Tournament:
    def __init__(
        self,
        participants: List[Pokemon],
        tournament_id: int = 1,
        battle_id: int = 1,
        seed: int = None,
    ):
        self.__participants = participants
        self.__remaining = participants
        self.__tournament_random = random.Random()

        # Set tournament seed
        self.__tournament_random.seed(seed)
        self.__tournament_seed = seed

        self.__tournament_id = tournament_id
        self.__battle_id = battle_id
        self.__events: List[str] = []
        self.__victors: List[List[str]] = []

    def get_seed(self) -> int:
        return self.__tournament_seed

    def set_seed(self, value: int) -> None:
        self.__tournament_random.seed(value)
        self.__tournament_seed = value

        return

    def get_victors(self):
        return self.__victors

    def get_participants(self) -> List[Pokemon]:
        return self.__participants

    def get_events(self) -> List[str]:
        return self.__events

    def get_tournament_id(self):
        return self.__tournament_id

    def get_battle_id(self):
        return self.__battle_id

    def append_event(self, event: str):
        self.__events.append(event)

    def conduct_round(self) -> None:
        next_round = []

        if len(self.__remaining) % 2 == 1:
            bye_pokemon: Pokemon = self.__tournament_random.choice(self.__remaining)
            self.__remaining.remove(bye_pokemon)
            next_round.append(bye_pokemon)

        round_events = []  # Holds events for this round

        for i in range(0, len(self.__remaining), 2):
            pokemon1: Pokemon = self.__remaining[i]
            pokemon2: Pokemon = self.__remaining[i + 1]

            battle = Battle(
                pokemon1, pokemon2, self.__battle_id, self.__tournament_seed
            )
            self.__battle_id += 1
            outcome = battle.start_battle()

            # Add battle results to the round's events
            round_events.append(
                {
                    "battle_id": self.__battle_id - 1,
                    "winner": outcome[0].get_name(),
                    "loser": outcome[1].get_name(),
                }
            )

            next_round.append(outcome[0])  # Winner proceeds
            outcome[0].increment_battle_wins()
            outcome[1].increment_battle_losses()

        self.__remaining = next_round
        self.__events.append(
            {
                "round": len(self.__events) + 1,
                "events": round_events,
            }
        )
        return None

    def run_tournament(self) -> Optional[Pokemon]:
        logger.admin_log(f"tournament started: {self.__tournament_id}")

        if not self.validate_participants() or len(self.__participants) < 4:
            logger.admin_log(f"Invalid tournament: {self.__tournament_id}")
            return None

        while len(self.__remaining) > 1:
            self.conduct_round()

            # Append victors from this round for logging
            self.__victors.append(
                list(participant.get_name() for participant in self.__remaining)
            )

        winner = self.__remaining[0]
        winner.increment_tournament_wins()

        tourney_data = Tournament_Data(self)
        tourney_data.save()
        return winner

    def validate_participants(self) -> bool:
        return all(isinstance(entry, Pokemon) for entry in self.__participants)


class Tournament_Data:
    def __init__(self, tournament: Tournament) -> None:
        self.__data = {}
        self.build_data(tournament)

    def get_tournament_data(self) -> dict:
        return self.__data

    def save(self) -> None:
        logger.log(self.__data, DbCollection.TOURNAMENT)
        logger.admin_log(f"Tournament {self.__data['tournament id']} logged")

    def deconstruct_tournament(
        self, tournament: Tournament
    ) -> Tuple[int, List[str], List[dict], str]:
        return tuple(
            [
                tournament.get_tournament_id(),
                list(
                    participant.get_name()
                    for participant in tournament.get_participants()
                ),
                tournament.get_events(),
                tournament.get_victors(),
            ]
        )

    def build_data(self, tournament: Tournament) -> None:
        deconstructed = self.deconstruct_tournament(tournament)
        self.__data = {
            "tournament id": deconstructed[0],
            "participants": deconstructed[1],
            "events": deconstructed[2],  # Events with round winners
            "winner": (
                deconstructed[3][-1][-1] if deconstructed[3] else ""
            ),  # Final winner's name
        }
        return None
