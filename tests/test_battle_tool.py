"""
Tests for Battle Tool MCP Implementation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from tools.battle_tool import BattleTool

class TestBattleTool:
    
    @pytest.fixture
    def battle_tool(self):
        return BattleTool()
    
    @pytest.fixture
    def mock_pokemon_data(self):
        return {
            'name': 'pikachu',
            'stats': {
                'hp': 35, 'attack': 55, 'defense': 40,
                'special_attack': 50, 'special_defense': 50, 'speed': 90
            },
            'types': [{'name': 'electric'}],
            'moves': [
                {
                    'name': 'thunderbolt',
                    'power': 90,
                    'accuracy': 100,
                    'pp': 15,
                    'type': 'electric',
                    'damage_class': 'special'
                },
                {
                    'name': 'quick-attack',
                    'power': 40,
                    'accuracy': 100,
                    'pp': 30,
                    'type': 'normal',
                    'damage_class': 'physical'
                }
            ]
        }
    
    @patch('tools.battle_tool.BattleTool._create_pokemon_from_data')
    @patch('resources.pokemon_resource.PokemonResource.get_pokemon_stats')
    def test_simulate_battle_success(self, mock_get_stats, mock_create_pokemon, battle_tool, mock_pokemon_data):
        # Mock the resource calls
        mock_get_stats.return_value = mock_pokemon_data
        
        # Mock Pokemon creation
        mock_pokemon1 = Mock()
        mock_pokemon1.name = 'pikachu'
        mock_pokemon1.current_hp = 100
        mock_pokemon1.max_hp = 100
        mock_pokemon1.attack = 55
        mock_pokemon1.defense = 40
        mock_pokemon1.special_attack = 50
        mock_pokemon1.special_defense = 50
        mock_pokemon1.speed = 90
        mock_pokemon1.is_fainted = False
        mock_pokemon1.process_status_effects.return_value = (True, "")
        
        mock_pokemon2 = Mock()
        mock_pokemon2.name = 'charizard'
        mock_pokemon2.current_hp = 150
        mock_pokemon2.max_hp = 150
        mock_pokemon2.attack = 84
        mock_pokemon2.defense = 78
        mock_pokemon2.special_attack = 109
        mock_pokemon2.special_defense = 85
        mock_pokemon2.speed = 100
        mock_pokemon2.is_fainted = True  # Make it faint to end battle quickly
        mock_pokemon2.process_status_effects.return_value = (True, "")
        
        mock_create_pokemon.side_effect = [mock_pokemon1, mock_pokemon2]
        
        # Run the battle simulation
        result = asyncio.run(battle_tool.simulate_battle('pikachu', 'charizard'))
        
        # Verify result is a string containing battle information
        assert isinstance(result, str)
        assert 'POKÉMON BATTLE SIMULATION' in result
        assert 'pikachu' in result.lower()
        assert 'charizard' in result.lower()
    
    def test_create_pokemon_from_data(self, battle_tool, mock_pokemon_data):
        pokemon = battle_tool._create_pokemon_from_data(mock_pokemon_data)
        
        assert pokemon.name == 'pikachu'
        assert pokemon.types == ['electric']
        assert len(pokemon.moves) >= 1
        assert pokemon.max_hp > 0
    
    def test_create_pokemon_with_custom_moves(self, battle_tool, mock_pokemon_data):
        custom_moves = ['thunderbolt', 'quick-attack']
        pokemon = battle_tool._create_pokemon_from_data(mock_pokemon_data, custom_moves)
        
        assert pokemon.name == 'pikachu'
        assert len(pokemon.moves) <= 4  # Max 4 moves
    
    def test_create_move_from_data(self, battle_tool):
        move_data = {
            'name': 'thunderbolt',
            'power': 90,
            'accuracy': 100,
            'pp': 15,
            'type': 'electric',
            'damage_class': 'special',
            'effect': 'May paralyze target'
        }
        
        move = battle_tool._create_move_from_data(move_data)
        
        assert move.name == 'thunderbolt'
        assert move.power == 90
        assert move.accuracy == 100
        assert move.pp == 15
        assert move.type == 'electric'
        assert move.damage_class == 'special'
    
    @patch('resources.pokemon_resource.PokemonResource.get_pokemon_stats')
    def test_simulate_battle_error_handling(self, mock_get_stats, battle_tool):
        # Mock an exception
        mock_get_stats.side_effect = Exception("API Error")
        
        result = asyncio.run(battle_tool.simulate_battle('invalid', 'pokemon'))
        
        assert isinstance(result, str)
        assert 'Battle simulation failed' in result
        assert 'API Error' in result
