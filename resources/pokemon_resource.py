"""
Pokémon Resource Module
Handles fetching Pokémon data from PokéAPI and exposing it as MCP resources.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class PokemonType(BaseModel):
    name: str
    slot: int

class PokemonAbility(BaseModel):
    name: str
    is_hidden: bool

class PokemonMove(BaseModel):
    name: str
    power: Optional[int]
    accuracy: Optional[int]
    pp: int
    type: str
    damage_class: str
    effect: Optional[str]

class PokemonData(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    base_experience: int
    stats: PokemonStats
    types: List[PokemonType]
    abilities: List[PokemonAbility]
    moves: List[PokemonMove]

class EvolutionChain(BaseModel):
    species_name: str
    evolves_to: List['EvolutionChain']
    evolution_details: List[Dict[str, Any]]

class PokemonResource:
    """Handles Pokémon data fetching from PokéAPI."""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
    
    async def get_pokemon_stats(self, pokemon_name: str) -> Dict[str, Any]:
        """Get comprehensive Pokémon stats, types, abilities, and moves."""
        pokemon_name = pokemon_name.lower().strip()
        
        # Check cache first
        cache_key = f"stats_{pokemon_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Fetch basic Pokémon data
            pokemon_response = self.session.get(f"{self.BASE_URL}/pokemon/{pokemon_name}")
            pokemon_response.raise_for_status()
            pokemon_data = pokemon_response.json()
            
            # Parse stats
            stats = {}
            for stat in pokemon_data['stats']:
                stat_name = stat['stat']['name'].replace('-', '_')
                stats[stat_name] = stat['base_stat']
            
            # Parse types
            types = []
            for type_info in pokemon_data['types']:
                types.append({
                    'name': type_info['type']['name'],
                    'slot': type_info['slot']
                })
            
            # Parse abilities
            abilities = []
            for ability_info in pokemon_data['abilities']:
                abilities.append({
                    'name': ability_info['ability']['name'],
                    'is_hidden': ability_info['is_hidden']
                })
            
            # Parse moves (limit to first 20 for performance)
            moves = []
            for move_info in pokemon_data['moves'][:20]:
                move_name = move_info['move']['name']
                move_details = await self._get_move_details(move_name)
                moves.append(move_details)
            
            # Get sprite URL
            sprite_url = None
            if pokemon_data.get('sprites'):
                sprites = pokemon_data['sprites']
                # Try different sprite options in order of preference
                sprite_url = (sprites.get('other', {}).get('official-artwork', {}).get('front_default') or
                             sprites.get('front_default') or
                             sprites.get('other', {}).get('home', {}).get('front_default'))
            
            result = {
                'id': pokemon_data['id'],
                'name': pokemon_data['name'],
                'height': pokemon_data['height'],
                'weight': pokemon_data['weight'],
                'base_experience': pokemon_data['base_experience'],
                'sprite': sprite_url,
                'stats': {
                    'hp': stats.get('hp', 0),
                    'attack': stats.get('attack', 0),
                    'defense': stats.get('defense', 0),
                    'special_attack': stats.get('special_attack', 0),
                    'special_defense': stats.get('special_defense', 0),
                    'speed': stats.get('speed', 0)
                },
                'types': types,
                'abilities': abilities,
                'moves': moves
            }
            
            # Cache the result
            self.cache[cache_key] = result
            return result
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Pokémon data for {pokemon_name}: {str(e)}")
    
    async def _get_move_details(self, move_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific move."""
        cache_key = f"move_{move_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            move_response = self.session.get(f"{self.BASE_URL}/move/{move_name}")
            move_response.raise_for_status()
            move_data = move_response.json()
            
            # Get effect description
            effect = None
            if move_data.get('effect_entries'):
                for entry in move_data['effect_entries']:
                    if entry['language']['name'] == 'en':
                        effect = entry['short_effect']
                        break
            
            result = {
                'name': move_data['name'],
                'power': move_data['power'],
                'accuracy': move_data['accuracy'],
                'pp': move_data['pp'],
                'type': move_data['type']['name'],
                'damage_class': move_data['damage_class']['name'],
                'effect': effect
            }
            
            self.cache[cache_key] = result
            return result
            
        except requests.RequestException:
            # Return basic move info if detailed fetch fails
            return {
                'name': move_name,
                'power': None,
                'accuracy': None,
                'pp': 10,
                'type': 'normal',
                'damage_class': 'physical',
                'effect': None
            }
    
    async def get_evolution_chain(self, pokemon_name: str) -> Dict[str, Any]:
        """Get evolution chain information for a Pokémon."""
        pokemon_name = pokemon_name.lower().strip()
        
        cache_key = f"evolution_{pokemon_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # First get the Pokémon species data
            species_response = self.session.get(f"{self.BASE_URL}/pokemon-species/{pokemon_name}")
            species_response.raise_for_status()
            species_data = species_response.json()
            
            # Get the evolution chain URL
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # Fetch evolution chain data
            evolution_response = self.session.get(evolution_chain_url)
            evolution_response.raise_for_status()
            evolution_data = evolution_response.json()
            
            # Parse evolution chain
            def parse_evolution_chain(chain_data):
                result = {
                    'species_name': chain_data['species']['name'],
                    'evolves_to': [],
                    'evolution_details': chain_data.get('evolution_details', [])
                }
                
                for evolution in chain_data.get('evolves_to', []):
                    result['evolves_to'].append(parse_evolution_chain(evolution))
                
                return result
            
            evolution_chain = parse_evolution_chain(evolution_data['chain'])
            
            result = {
                'id': evolution_data['id'],
                'evolution_chain': evolution_chain
            }
            
            self.cache[cache_key] = result
            return result
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch evolution data for {pokemon_name}: {str(e)}")
    
    async def get_pokemon_by_name(self, pokemon_name: str) -> Dict[str, Any]:
        """Get basic Pokémon data for battle simulation."""
        return await self.get_pokemon_stats(pokemon_name)
