class Skill:
    def __init__(self, name: str, damage_level: int) -> None:
        self.name: str = name
        self.damage_level: int = damage_level

    def get_name(self) -> str:
        return self.name

    def get_damage(self) -> int:
        return self.damage_level


class AttackSkill(Skill):
    def __init__(self, name: str, damage_level: int) -> None:
        super().__init__(name, damage_level)

    def calculate_damage(self) -> int:
        return self.get_damage()  # Attack skill's damage is simply its damage level


class DefenseSkill(Skill):
    def __init__(self, name: str, damage_level: int) -> None:
        super().__init__(name, damage_level)

    # Reduces the incoming damage by the skill's damage level.
    def reduce_damage(self, damage: int) -> int:
        return max(0, damage - self.get_damage())  # Prevent negative damage
