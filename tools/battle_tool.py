"""
Battle Tool Module
MCP tool implementation for Pokémon battle simulation.
"""

import json
import random
from typing import Dict, List, Optional, Any
from resources.pokemon_resource import PokemonResource
from tools.pokemon_battle import Pokemon, Move, BattleCalculator, StatusEffect

class BattleTool:
    """MCP tool for simulating Pokémon battles."""
    
    def __init__(self):
        self.pokemon_resource = PokemonResource()
        self.battle_calculator = BattleCalculator()
    
    async def simulate_battle(self, pokemon1_name: str, pokemon2_name: str, 
                            moves1: Optional[List[str]] = None, 
                            moves2: Optional[List[str]] = None) -> str:
        """
        Simulate a battle between two Pokémon.
        Returns a detailed battle log as a string.
        """
        try:
            # Fetch Pokémon data
            pokemon1_data = await self.pokemon_resource.get_pokemon_stats(pokemon1_name)
            pokemon2_data = await self.pokemon_resource.get_pokemon_stats(pokemon2_name)
            
            # Create Pokémon instances
            pokemon1 = self._create_pokemon_from_data(pokemon1_data, moves1)
            pokemon2 = self._create_pokemon_from_data(pokemon2_data, moves2)
            
            # Start battle simulation
            battle_log = []
            battle_log.append("=== POKÉMON BATTLE SIMULATION ===")
            battle_log.append(f"{pokemon1.name.title()} vs {pokemon2.name.title()}")
            battle_log.append("")
            
            # Display initial stats
            battle_log.append("Initial Stats:")
            battle_log.append(f"{pokemon1.name.title()}: HP {pokemon1.current_hp}/{pokemon1.max_hp}, "
                            f"ATK {pokemon1.attack}, DEF {pokemon1.defense}, "
                            f"SP.ATK {pokemon1.special_attack}, SP.DEF {pokemon1.special_defense}, "
                            f"SPD {pokemon1.speed}")
            battle_log.append(f"{pokemon2.name.title()}: HP {pokemon2.current_hp}/{pokemon2.max_hp}, "
                            f"ATK {pokemon2.attack}, DEF {pokemon2.defense}, "
                            f"SP.ATK {pokemon2.special_attack}, SP.DEF {pokemon2.special_defense}, "
                            f"SPD {pokemon2.speed}")
            battle_log.append("")
            
            # Battle loop
            turn = 1
            max_turns = 50  # Prevent infinite battles
            
            while not pokemon1.is_fainted and not pokemon2.is_fainted and turn <= max_turns:
                battle_log.append(f"--- Turn {turn} ---")
                
                # Determine turn order based on speed
                if pokemon1.speed >= pokemon2.speed:
                    first, second = pokemon1, pokemon2
                else:
                    first, second = pokemon2, pokemon1
                
                # First Pokémon's turn
                if not first.is_fainted:
                    turn_result = self._execute_turn(first, second, battle_log)
                    if turn_result:
                        battle_log.extend(turn_result)
                
                # Second Pokémon's turn (if still alive)
                if not second.is_fainted and not first.is_fainted:
                    turn_result = self._execute_turn(second, first, battle_log)
                    if turn_result:
                        battle_log.extend(turn_result)
                
                # Process status effects
                for pokemon in [pokemon1, pokemon2]:
                    if not pokemon.is_fainted:
                        can_act, status_msg = pokemon.process_status_effects()
                        if status_msg:
                            battle_log.append(status_msg)
                
                battle_log.append("")
                turn += 1
            
            # Determine winner
            battle_log.append("=== BATTLE RESULT ===")
            if pokemon1.is_fainted and pokemon2.is_fainted:
                battle_log.append("It's a draw! Both Pokémon fainted!")
            elif pokemon1.is_fainted:
                battle_log.append(f"{pokemon2.name.title()} wins!")
            elif pokemon2.is_fainted:
                battle_log.append(f"{pokemon1.name.title()} wins!")
            else:
                battle_log.append("Battle ended due to turn limit!")
            
            battle_log.append("")
            battle_log.append("Final HP:")
            battle_log.append(f"{pokemon1.name.title()}: {pokemon1.current_hp}/{pokemon1.max_hp}")
            battle_log.append(f"{pokemon2.name.title()}: {pokemon2.current_hp}/{pokemon2.max_hp}")
            
            return "\n".join(battle_log)
            
        except Exception as e:
            return f"Battle simulation failed: {str(e)}"
    
    def _create_pokemon_from_data(self, pokemon_data: Dict[str, Any], 
                                custom_moves: Optional[List[str]] = None) -> Pokemon:
        """Create a Pokemon instance from API data."""
        stats = pokemon_data['stats']
        types = [t['name'] for t in pokemon_data['types']]
        
        # Create moves
        moves = []
        available_moves = pokemon_data['moves']
        
        if custom_moves:
            # Use custom moves if provided
            for move_name in custom_moves[:4]:  # Max 4 moves
                move_data = next((m for m in available_moves if m['name'] == move_name.lower().replace(' ', '-')), None)
                if move_data:
                    moves.append(self._create_move_from_data(move_data))
                else:
                    # Create a basic move if not found
                    moves.append(Move(move_name, 60, 100, 20, types[0], "physical"))
        else:
            # Use first 4 available moves
            for move_data in available_moves[:4]:
                moves.append(self._create_move_from_data(move_data))
        
        # Ensure at least one move
        if not moves:
            moves.append(Move("tackle", 40, 100, 35, "normal", "physical"))
        
        return Pokemon(
            name=pokemon_data['name'],
            stats=stats,
            types=types,
            moves=moves
        )
    
    def _create_move_from_data(self, move_data: Dict[str, Any]) -> Move:
        """Create a Move instance from API data."""
        return Move(
            name=move_data['name'],
            power=move_data.get('power', 60),
            accuracy=move_data.get('accuracy', 100),
            pp=move_data.get('pp', 20),
            move_type=move_data.get('type', 'normal'),
            damage_class=move_data.get('damage_class', 'physical'),
            effect=move_data.get('effect')
        )
    
    def _execute_turn(self, attacker: Pokemon, defender: Pokemon, battle_log: List[str]) -> List[str]:
        """Execute a single turn for a Pokémon."""
        turn_log = []
        
        # Check if Pokémon can act (status effects)
        can_act, status_msg = attacker.process_status_effects()
        if status_msg:
            turn_log.append(status_msg)
        
        if not can_act or attacker.is_fainted:
            return turn_log
        
        # Choose a random move
        available_moves = [move for move in attacker.moves if move.can_use()]
        if not available_moves:
            turn_log.append(f"{attacker.name.title()} has no moves left!")
            return turn_log
        
        chosen_move = random.choice(available_moves)
        chosen_move.use()
        
        # Calculate damage
        damage, is_critical, type_effectiveness = self.battle_calculator.calculate_damage(
            attacker, defender, chosen_move
        )
        
        if damage == 0:
            turn_log.append(f"{attacker.name.title()} used {chosen_move.name.title()}, but it missed!")
            return turn_log
        
        # Apply damage
        actual_damage = defender.take_damage(damage)
        
        # Build attack message
        attack_msg = f"{attacker.name.title()} used {chosen_move.name.title()}!"
        if is_critical:
            attack_msg += " Critical hit!"
        
        turn_log.append(attack_msg)
        
        # Type effectiveness message
        if type_effectiveness > 1.0:
            turn_log.append("It's super effective!")
        elif type_effectiveness < 1.0 and type_effectiveness > 0:
            turn_log.append("It's not very effective...")
        elif type_effectiveness == 0:
            turn_log.append("It has no effect!")
        
        if actual_damage > 0:
            turn_log.append(f"{defender.name.title()} took {actual_damage} damage! "
                          f"({defender.current_hp}/{defender.max_hp} HP remaining)")
        
        # Check for status effect application (simplified)
        if chosen_move.name in ["thunder-wave", "thunderbolt"] and random.random() < 0.3:
            defender.apply_status_effect(StatusEffect.PARALYSIS)
            turn_log.append(f"{defender.name.title()} is paralyzed!")
        elif chosen_move.name in ["flamethrower", "fire-blast"] and random.random() < 0.1:
            defender.apply_status_effect(StatusEffect.BURN)
            turn_log.append(f"{defender.name.title()} is burned!")
        elif chosen_move.name in ["poison-powder", "sludge-bomb"] and random.random() < 0.3:
            defender.apply_status_effect(StatusEffect.POISON)
            turn_log.append(f"{defender.name.title()} is poisoned!")
        
        # Check if defender fainted
        if defender.is_fainted:
            turn_log.append(f"{defender.name.title()} fainted!")
        
        return turn_log
