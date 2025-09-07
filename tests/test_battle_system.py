"""
Tests for Battle System Components
"""

import pytest
from tools.pokemon_battle import Pokemon, Move, BattleCalculator, TypeEffectiveness, StatusEffect

class TestMove:
    
    def test_move_creation(self):
        move = Move("thunderbolt", 90, 100, 15, "electric", "special", "May paralyze target")
        assert move.name == "thunderbolt"
        assert move.power == 90
        assert move.accuracy == 100
        assert move.pp == 15
        assert move.current_pp == 15
        assert move.type == "electric"
        assert move.damage_class == "special"
    
    def test_move_usage(self):
        move = Move("tackle", 40, 100, 35, "normal", "physical")
        assert move.can_use() is True
        
        # Use move multiple times
        for _ in range(35):
            move.use()
        
        assert move.current_pp == 0
        assert move.can_use() is False

class TestPokemon:
    
    def test_pokemon_creation(self):
        stats = {
            'hp': 35, 'attack': 55, 'defense': 40,
            'special_attack': 50, 'special_defense': 50, 'speed': 90
        }
        moves = [Move("thunderbolt", 90, 100, 15, "electric", "special")]
        
        pokemon = Pokemon("pikachu", stats, ["electric"], moves, level=50)
        
        assert pokemon.name == "pikachu"
        assert pokemon.level == 50
        assert pokemon.types == ["electric"]
        assert len(pokemon.moves) == 1
        assert pokemon.current_hp == pokemon.max_hp
        assert pokemon.is_fainted is False
    
    def test_hp_calculation(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        pokemon = Pokemon("test", stats, ["normal"], moves, level=50)
        
        # HP should be calculated using the formula
        expected_hp = int(((2 * 100 + 31) * 50) / 100) + 50 + 10
        assert pokemon.max_hp == expected_hp
    
    def test_take_damage(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        pokemon = Pokemon("test", stats, ["normal"], moves)
        initial_hp = pokemon.current_hp
        
        damage_taken = pokemon.take_damage(50)
        
        assert damage_taken == 50
        assert pokemon.current_hp == initial_hp - 50
        assert pokemon.is_fainted is False
    
    def test_fainting(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        pokemon = Pokemon("test", stats, ["normal"], moves)
        
        # Deal more damage than current HP
        damage_taken = pokemon.take_damage(pokemon.current_hp + 50)
        
        assert damage_taken == pokemon.max_hp  # Should only take actual HP
        assert pokemon.current_hp == 0
        assert pokemon.is_fainted is True
    
    def test_status_effects(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        pokemon = Pokemon("test", stats, ["normal"], moves)
        
        # Apply paralysis
        pokemon.apply_status_effect(StatusEffect.PARALYSIS, 3)
        assert pokemon.status == StatusEffect.PARALYSIS
        assert pokemon.status_turns == 3
        
        # Process status effects
        can_act, message = pokemon.process_status_effects()
        assert pokemon.status_turns == 2  # Should decrease

class TestTypeEffectiveness:
    
    def test_super_effective(self):
        # Water vs Fire should be 2x
        multiplier = TypeEffectiveness.get_multiplier("water", ["fire"])
        assert multiplier == 2.0
    
    def test_not_very_effective(self):
        # Water vs Grass should be 0.5x
        multiplier = TypeEffectiveness.get_multiplier("water", ["grass"])
        assert multiplier == 0.5
    
    def test_no_effect(self):
        # Electric vs Ground should be 0x
        multiplier = TypeEffectiveness.get_multiplier("electric", ["ground"])
        assert multiplier == 0.0
    
    def test_normal_effectiveness(self):
        # Normal vs Normal should be 1x
        multiplier = TypeEffectiveness.get_multiplier("normal", ["normal"])
        assert multiplier == 1.0
    
    def test_dual_type_effectiveness(self):
        # Fire vs Grass/Ice should be 2x * 2x = 4x
        multiplier = TypeEffectiveness.get_multiplier("fire", ["grass", "ice"])
        assert multiplier == 4.0

class TestBattleCalculator:
    
    def test_damage_calculation_basic(self):
        # Create test Pokémon
        stats1 = {'hp': 100, 'attack': 100, 'defense': 100, 
                 'special_attack': 100, 'special_defense': 100, 'speed': 100}
        stats2 = {'hp': 100, 'attack': 100, 'defense': 100, 
                 'special_attack': 100, 'special_defense': 100, 'speed': 100}
        
        moves1 = [Move("tackle", 40, 100, 35, "normal", "physical")]
        moves2 = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        attacker = Pokemon("attacker", stats1, ["normal"], moves1)
        defender = Pokemon("defender", stats2, ["normal"], moves2)
        
        move = moves1[0]
        
        damage, is_critical, type_effectiveness = BattleCalculator.calculate_damage(
            attacker, defender, move
        )
        
        # Damage should be > 0 for a valid attack
        assert damage > 0
        assert isinstance(is_critical, bool)
        assert type_effectiveness == 1.0  # Normal vs Normal
    
    def test_zero_power_move(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("status-move", 0, 100, 35, "normal", "status")]
        
        attacker = Pokemon("attacker", stats, ["normal"], moves)
        defender = Pokemon("defender", stats, ["normal"], moves)
        
        damage, is_critical, type_effectiveness = BattleCalculator.calculate_damage(
            attacker, defender, moves[0]
        )
        
        assert damage == 0
        assert is_critical is False
        assert type_effectiveness == 1.0
    
    def test_burn_reduces_physical_attack(self):
        stats = {'hp': 100, 'attack': 100, 'defense': 100, 
                'special_attack': 100, 'special_defense': 100, 'speed': 100}
        moves = [Move("tackle", 40, 100, 35, "normal", "physical")]
        
        attacker = Pokemon("attacker", stats, ["normal"], moves)
        defender = Pokemon("defender", stats, ["normal"], moves)
        
        # Calculate normal damage
        normal_damage, _, _ = BattleCalculator.calculate_damage(attacker, defender, moves[0])
        
        # Apply burn and calculate again
        attacker.apply_status_effect(StatusEffect.BURN)
        burned_damage, _, _ = BattleCalculator.calculate_damage(attacker, defender, moves[0])
        
        # Burned damage should be less than normal damage
        assert burned_damage < normal_damage
