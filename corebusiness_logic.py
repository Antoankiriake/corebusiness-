from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ActionId(str, Enum):
    ATTACK = "attack"
    HEAL = "heal"
    ABILITY = "ability"


@dataclass
class Item:
    name: str
    bonus_flat: float = 0.0
    res_pen: float = 0.0


@dataclass
class Ability:
    name: str
    dmg_flat: float
    bonus_flat: float = 0.0
    res_pen: float = 0.0


@dataclass
class CharacterProfile:
    items: list[Item] = field(default_factory=list)
    abilities: list[Ability] = field(default_factory=list)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def add_ability(self, ability: Ability) -> None:
        self.abilities.append(ability)


class DamageCalculator(ABC):
    @abstractmethod
    def calculate_magic_damage(
        self,
        ability: Ability,
        target_res: float,
        bonus_prof: float,
        debuffs: list[float],
    ) -> float:
        pass


class StandardDamageCalculator(DamageCalculator):
    def calculate_magic_damage(
        self,
        ability: Ability,
        target_res: float,
        bonus_prof: float,
        debuffs: list[float],
    ) -> float:
        dmg_ability = sum(debuffs)
        res_factor = max(0.0, 1.0 - target_res + ability.res_pen)
        prof_factor = max(0.0, bonus_prof - dmg_ability)
        raw_damage = (ability.dmg_flat * res_factor + ability.bonus_flat) * prof_factor
        return max(0.0, raw_damage)


@dataclass
class Character:
    name: str
    health: float
    damage: float
    magic_res: float = 0.0
    bonus_prof: float = 0.0
    debuffs: list[float] = field(default_factory=list)
    profile: CharacterProfile = field(default_factory=CharacterProfile)

    def check_status(self) -> str:
        return "ALIVE" if self.health > 0 else "DEFEATED"

    def is_alive(self) -> bool:
        return self.health > 0

    def receive_damage(self, amount: float) -> None:
        self.health = max(0.0, self.health - max(0.0, amount))

    def attack(self, target: "Character") -> float:
        if not self.is_alive() or not target.is_alive():
            return 0.0
        target.receive_damage(self.damage)
        return self.damage

    def heal(self, target: "Character", amount: float = 15.0) -> float:
        if not self.is_alive() or not target.is_alive():
            return 0.0
        target.health += max(0.0, amount)
        return amount

    def action(
        self,
        action_id: int,
        target: "Character",
        calculator: DamageCalculator,
    ) -> float:
        if not self.is_alive() or not target.is_alive():
            return 0.0
        if action_id < 0 or action_id >= len(self.profile.abilities):
            raise ValueError("Invalid ability index")

        ability = self.profile.abilities[action_id]
        item_bonus_flat = sum(i.bonus_flat for i in self.profile.items)
        item_res_pen = sum(i.res_pen for i in self.profile.items)

        effective_ability = Ability(
            name=ability.name,
            dmg_flat=ability.dmg_flat,
            bonus_flat=ability.bonus_flat + item_bonus_flat,
            res_pen=ability.res_pen + item_res_pen,
        )
        dmg = calculator.calculate_magic_damage(
            ability=effective_ability,
            target_res=target.magic_res,
            bonus_prof=self.bonus_prof,
            debuffs=self.debuffs,
        )
        target.receive_damage(dmg)
        return dmg


@dataclass
class GameConfig:
    characters: list[Character]
    max_turns: int = 20


class GameConfigRepository(ABC):
    @abstractmethod
    def load_config(self) -> GameConfig:
        pass


class Turn:
    def __init__(self, calculator: DamageCalculator) -> None:
        self.calculator = calculator
        self.turn_number = 0

    def begin_turn(self) -> int:
        self.turn_number += 1
        return self.turn_number

    def act(
        self,
        action_id: ActionId,
        actor: Character,
        target: Character,
        ability_index: int = 0,
    ) -> str:
        if not actor.is_alive():
            return f"{actor.name} cannot act (status: {actor.check_status()})."

        if action_id == ActionId.ATTACK:
            dealt = actor.attack(target)
            return f"{actor.name} attacks {target.name} for {dealt:.1f} damage (target HP: {target.health:.1f})."

        if action_id == ActionId.HEAL:
            healed = actor.heal(target)
            return f"{actor.name} heals {target.name} for {healed:.1f} HP (target HP: {target.health:.1f})."

        if action_id == ActionId.ABILITY:
            dmg = actor.action(ability_index, target, self.calculator)
            return f"{actor.name} uses ability on {target.name} for {dmg:.1f} damage (target HP: {target.health:.1f})."

        raise ValueError(f"Unknown action: {action_id}")


class Game:
    def __init__(self, calculator: DamageCalculator | None = None) -> None:
        self.calculator = calculator or StandardDamageCalculator()
        self.config: GameConfig | None = None
        self.turn = Turn(self.calculator)
        self.is_running = False

    def setup_game(self) -> GameConfig:
        c1 = Character(name="Hero", health=100.0, damage=20.0, magic_res=0.1, bonus_prof=1.5)
        c1.profile.add_item(Item(name="Mage Ring", bonus_flat=5.0, res_pen=0.1))
        c1.profile.add_ability(Ability(name="Fireball", dmg_flat=25.0, bonus_flat=5.0, res_pen=0.1))

        c2 = Character(name="Enemy", health=100.0, damage=15.0, magic_res=0.2, bonus_prof=1.2)
        self.config = GameConfig(characters=[c1, c2], max_turns=10)
        return self.config

    def start_game(self, config: GameConfig) -> None:
        self.config = config
        self.turn = Turn(self.calculator)
        self.is_running = True

    def is_game_over(self) -> bool:
        if not self.config:
            return True
        alive_count = sum(1 for c in self.config.characters if c.is_alive())
        return alive_count <= 1 or self.turn.turn_number >= self.config.max_turns


if __name__ == "__main__":
    game = Game()
    config = game.setup_game()
    game.start_game(config)

    hero, enemy = config.characters[0], config.characters[1]

    game.turn.begin_turn()
    print(game.turn.act(ActionId.ATTACK, hero, enemy))

    game.turn.begin_turn()
    print(game.turn.act(ActionId.ABILITY, hero, enemy, ability_index=0))
