"""
Tests for Pokémon Resource Module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from resources.pokemon_resource import PokemonResource

class TestPokemonResource:
    
    @pytest.fixture
    def pokemon_resource(self):
        return PokemonResource()
    
    @pytest.fixture
    def mock_pokemon_data(self):
        return {
            'id': 25,
            'name': 'pikachu',
            'height': 4,
            'weight': 60,
            'base_experience': 112,
            'stats': [
                {'base_stat': 35, 'stat': {'name': 'hp'}},
                {'base_stat': 55, 'stat': {'name': 'attack'}},
                {'base_stat': 40, 'stat': {'name': 'defense'}},
                {'base_stat': 50, 'stat': {'name': 'special-attack'}},
                {'base_stat': 50, 'stat': {'name': 'special-defense'}},
                {'base_stat': 90, 'stat': {'name': 'speed'}}
            ],
            'types': [
                {'slot': 1, 'type': {'name': 'electric'}}
            ],
            'abilities': [
                {'ability': {'name': 'static'}, 'is_hidden': False},
                {'ability': {'name': 'lightning-rod'}, 'is_hidden': True}
            ],
            'moves': [
                {'move': {'name': 'thunder-shock'}},
                {'move': {'name': 'quick-attack'}},
                {'move': {'name': 'thunderbolt'}},
                {'move': {'name': 'agility'}}
            ]
        }
    
    @pytest.fixture
    def mock_move_data(self):
        return {
            'name': 'thunder-shock',
            'power': 40,
            'accuracy': 100,
            'pp': 30,
            'type': {'name': 'electric'},
            'damage_class': {'name': 'special'},
            'effect_entries': [
                {
                    'language': {'name': 'en'},
                    'short_effect': 'Has a 10% chance to paralyze the target.'
                }
            ]
        }
    
    @patch('requests.Session.get')
    def test_get_pokemon_stats_success(self, mock_get, pokemon_resource, mock_pokemon_data, mock_move_data):
        # Mock the API responses
        mock_pokemon_response = Mock()
        mock_pokemon_response.json.return_value = mock_pokemon_data
        mock_pokemon_response.raise_for_status.return_value = None
        
        mock_move_response = Mock()
        mock_move_response.json.return_value = mock_move_data
        mock_move_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_pokemon_response, mock_move_response, mock_move_response, mock_move_response, mock_move_response]
        
        # Test the method
        result = asyncio.run(pokemon_resource.get_pokemon_stats('pikachu'))
        
        # Assertions
        assert result['name'] == 'pikachu'
        assert result['id'] == 25
        assert result['stats']['hp'] == 35
        assert result['stats']['attack'] == 55
        assert result['stats']['speed'] == 90
        assert len(result['types']) == 1
        assert result['types'][0]['name'] == 'electric'
        assert len(result['abilities']) == 2
        assert result['abilities'][0]['name'] == 'static'
    
    @patch('requests.Session.get')
    def test_get_pokemon_stats_not_found(self, mock_get, pokemon_resource):
        # Mock 404 response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        
        # Test that exception is raised
        with pytest.raises(Exception) as exc_info:
            asyncio.run(pokemon_resource.get_pokemon_stats('nonexistent'))
        
        assert "Failed to fetch Pokémon data" in str(exc_info.value)
    
    def test_caching(self, pokemon_resource):
        # Test that results are cached
        pokemon_resource.cache['stats_pikachu'] = {'name': 'pikachu', 'cached': True}
        
        result = asyncio.run(pokemon_resource.get_pokemon_stats('pikachu'))
        assert result['cached'] is True
    
    @patch('requests.Session.get')
    def test_get_evolution_chain(self, mock_get, pokemon_resource):
        # Mock species response
        mock_species_data = {
            'evolution_chain': {
                'url': 'https://pokeapi.co/api/v2/evolution-chain/10/'
            }
        }
        
        # Mock evolution chain response
        mock_evolution_data = {
            'id': 10,
            'chain': {
                'species': {'name': 'pichu'},
                'evolution_details': [],
                'evolves_to': [
                    {
                        'species': {'name': 'pikachu'},
                        'evolution_details': [{'min_level': 16}],
                        'evolves_to': [
                            {
                                'species': {'name': 'raichu'},
                                'evolution_details': [{'trigger': {'name': 'use-item'}}],
                                'evolves_to': []
                            }
                        ]
                    }
                ]
            }
        }
        
        mock_species_response = Mock()
        mock_species_response.json.return_value = mock_species_data
        mock_species_response.raise_for_status.return_value = None
        
        mock_evolution_response = Mock()
        mock_evolution_response.json.return_value = mock_evolution_data
        mock_evolution_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_species_response, mock_evolution_response]
        
        result = asyncio.run(pokemon_resource.get_evolution_chain('pikachu'))
        
        assert result['id'] == 10
        assert result['evolution_chain']['species_name'] == 'pichu'
        assert len(result['evolution_chain']['evolves_to']) == 1
        assert result['evolution_chain']['evolves_to'][0]['species_name'] == 'pikachu'
