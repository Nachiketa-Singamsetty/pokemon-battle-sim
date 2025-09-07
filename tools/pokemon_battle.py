"""
Pokémon Battle System
Core classes and mechanics for Pokémon battle simulation.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

class StatusEffect(Enum):
    NONE = "none"
    PARALYSIS = "paralysis"
    BURN = "burn"
    POISON = "poison"

class DamageClass(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

class PokemonType(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"

class Move:
    def __init__(self, name: str, power: int, accuracy: int, pp: int, 
                 move_type: str, damage_class: str, effect: Optional[str] = None):
        self.name = name
        self.power = power if power else 0
        self.accuracy = accuracy if accuracy else 100
        self.pp = pp
        self.current_pp = pp
        self.type = move_type
        self.damage_class = damage_class
        self.effect = effect
    
    def can_use(self) -> bool:
        return self.current_pp > 0
    
    def use(self):
        if self.can_use():
            self.current_pp -= 1

class Pokemon:
    def __init__(self, name: str, stats: Dict[str, int], types: List[str], 
                 moves: List[Move], level: int = 50):
        self.name = name
        self.level = level
        self.types = types
        self.moves = moves
        
        # Base stats
        self.base_hp = stats.get('hp', 100)
        self.base_attack = stats.get('attack', 100)
        self.base_defense = stats.get('defense', 100)
        self.base_special_attack = stats.get('special_attack', 100)
        self.base_special_defense = stats.get('special_defense', 100)
        self.base_speed = stats.get('speed', 100)
        
        # Calculate actual stats (simplified formula)
        self.max_hp = self._calculate_hp()
        self.current_hp = self.max_hp
        self.attack = self._calculate_stat(self.base_attack)
        self.defense = self._calculate_stat(self.base_defense)
        self.special_attack = self._calculate_stat(self.base_special_attack)
        self.special_defense = self._calculate_stat(self.base_special_defense)
        self.speed = self._calculate_stat(self.base_speed)
        
        # Status
        self.status = StatusEffect.NONE
        self.status_turns = 0
        self.is_fainted = False
    
    def _calculate_hp(self) -> int:
        """Calculate HP using simplified Pokémon formula."""
        return int(((2 * self.base_hp + 31) * self.level) / 100) + self.level + 10
    
    def _calculate_stat(self, base_stat: int) -> int:
        """Calculate other stats using simplified Pokémon formula."""
        return int(((2 * base_stat + 31) * self.level) / 100) + 5
    
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted = True
        return actual_damage
    
    def apply_status_effect(self, status: StatusEffect, turns: int = 3):
        """Apply a status effect."""
        if self.status == StatusEffect.NONE:
            self.status = status
            self.status_turns = turns
    
    def process_status_effects(self) -> Tuple[bool, str]:
        """Process status effects at the end of turn. Returns (can_act, message)."""
        if self.status == StatusEffect.NONE:
            return True, ""
        
        message = ""
        can_act = True
        
        if self.status == StatusEffect.PARALYSIS:
            if random.random() < 0.25:  # 25% chance to be paralyzed
                can_act = False
                message = f"{self.name} is paralyzed and can't move!"
        
        elif self.status == StatusEffect.BURN:
            # Burn damage (1/16 of max HP)
            burn_damage = max(1, self.max_hp // 16)
            actual_damage = self.take_damage(burn_damage)
            message = f"{self.name} is hurt by burn! ({actual_damage} damage)"
        
        elif self.status == StatusEffect.POISON:
            # Poison damage (1/8 of max HP)
            poison_damage = max(1, self.max_hp // 8)
            actual_damage = self.take_damage(poison_damage)
            message = f"{self.name} is hurt by poison! ({actual_damage} damage)"
        
        # Reduce status duration
        self.status_turns -= 1
        if self.status_turns <= 0:
            old_status = self.status.value
            self.status = StatusEffect.NONE
            if message:
                message += f" {self.name} recovered from {old_status}!"
            else:
                message = f"{self.name} recovered from {old_status}!"
        
        return can_act, message

class TypeEffectiveness:
    """Handles type effectiveness calculations."""
    
    # Type effectiveness chart (attacking type -> defending type -> multiplier)
    EFFECTIVENESS = {
        "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
        "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0},
        "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
        "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "flying": 2.0, "dragon": 0.5},
        "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5, "steel": 0.5},
        "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5},
        "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0, "dark": 2.0, "steel": 2.0, "fairy": 0.5},
        "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0, "fairy": 2.0},
        "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
        "flying": {"electric": 0.5, "grass": 2.0, "ice": 0.5, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "steel": 0.5},
        "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0, "steel": 0.5},
        "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0, "steel": 0.5, "fairy": 0.5},
        "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5, "flying": 2.0, "bug": 2.0, "steel": 0.5},
        "ghost": {"normal": 0.0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5},
        "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
        "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5, "fairy": 0.5},
        "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0, "rock": 2.0, "steel": 0.5, "fairy": 2.0},
        "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "dragon": 2.0, "dark": 2.0, "steel": 0.5}
    }
    
    @classmethod
    def get_multiplier(cls, attack_type: str, defend_types: List[str]) -> float:
        """Calculate type effectiveness multiplier."""
        multiplier = 1.0
        
        for defend_type in defend_types:
            if attack_type in cls.EFFECTIVENESS:
                type_chart = cls.EFFECTIVENESS[attack_type]
                if defend_type in type_chart:
                    multiplier *= type_chart[defend_type]
        
        return multiplier

class BattleCalculator:
    """Handles battle damage calculations."""
    
    @staticmethod
    def calculate_damage(attacker: Pokemon, defender: Pokemon, move: Move) -> Tuple[int, bool, float]:
        """
        Calculate damage using Pokémon damage formula.
        Returns (damage, is_critical, type_effectiveness)
        """
        if move.power == 0:
            return 0, False, 1.0
        
        # Check if move hits
        if random.randint(1, 100) > move.accuracy:
            return 0, False, 1.0  # Move missed
        
        # Determine attack and defense stats
        if move.damage_class == "physical":
            attack_stat = attacker.attack
            defense_stat = defender.defense
            # Burn halves physical attack
            if attacker.status == StatusEffect.BURN:
                attack_stat = attack_stat // 2
        else:  # special
            attack_stat = attacker.special_attack
            defense_stat = defender.special_defense
        
        # Critical hit check (6.25% chance)
        is_critical = random.random() < 0.0625
        critical_multiplier = 1.5 if is_critical else 1.0
        
        # Type effectiveness
        type_multiplier = TypeEffectiveness.get_multiplier(move.type, defender.types)
        
        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.type in attacker.types else 1.0
        
        # Random factor (85-100%)
        random_factor = random.randint(85, 100) / 100
        
        # Damage formula: ((((2 * level / 5 + 2) * power * (Attack/Defense)) / 50) + 2) * modifiers
        level_factor = (2 * attacker.level / 5 + 2)
        base_damage = (level_factor * move.power * (attack_stat / defense_stat)) / 50 + 2
        
        final_damage = int(base_damage * critical_multiplier * stab * type_multiplier * random_factor)
        
        return max(1, final_damage), is_critical, type_multiplier
