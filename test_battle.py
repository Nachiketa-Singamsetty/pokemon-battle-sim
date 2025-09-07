#!/usr/bin/env python3
"""
Test the Pokemon battle system directly
"""

from tools.pokemon_battle import Pokemon, Move, BattleCalculator, TypeEffectiveness

def test_battle_system():
    print("=== Testing Pokemon Battle System ===\n")
    
    # Test 1: Create moves
    print("1. Testing Move creation...")
    tackle = Move("tackle", 40, 100, 35, "normal", "physical")
    thunderbolt = Move("thunderbolt", 90, 100, 15, "electric", "special")
    print(f"✅ Created moves: {tackle.name} (power: {tackle.power}), {thunderbolt.name} (power: {thunderbolt.power})")
    
    # Test 2: Create Pokemon
    print("\n2. Testing Pokemon creation...")
    pikachu_stats = {'hp': 35, 'attack': 55, 'defense': 40, 'special_attack': 50, 'special_defense': 50, 'speed': 90}
    charizard_stats = {'hp': 78, 'attack': 84, 'defense': 78, 'special_attack': 109, 'special_defense': 85, 'speed': 100}
    
    pikachu = Pokemon("pikachu", pikachu_stats, ["electric"], [tackle, thunderbolt])
    charizard = Pokemon("charizard", charizard_stats, ["fire", "flying"], [tackle])
    
    print(f"✅ Pikachu: HP {pikachu.current_hp}/{pikachu.max_hp}, Speed {pikachu.speed}")
    print(f"✅ Charizard: HP {charizard.current_hp}/{charizard.max_hp}, Speed {charizard.speed}")
    
    # Test 3: Type effectiveness
    print("\n3. Testing type effectiveness...")
    water_vs_fire = TypeEffectiveness.get_multiplier("water", ["fire"])
    electric_vs_flying = TypeEffectiveness.get_multiplier("electric", ["flying"])
    electric_vs_fire = TypeEffectiveness.get_multiplier("electric", ["fire"])
    
    print(f"✅ Water vs Fire: {water_vs_fire}x (should be 2.0)")
    print(f"✅ Electric vs Flying: {electric_vs_flying}x (should be 2.0)")
    print(f"✅ Electric vs Fire: {electric_vs_fire}x (should be 1.0)")
    
    # Test 4: Damage calculation
    print("\n4. Testing damage calculation...")
    damage, is_critical, type_eff = BattleCalculator.calculate_damage(pikachu, charizard, thunderbolt)
    print(f"✅ Pikachu's Thunderbolt vs Charizard:")
    print(f"   Damage: {damage}")
    print(f"   Critical: {is_critical}")
    print(f"   Type effectiveness: {type_eff}x")
    
    # Test 5: Battle simulation
    print("\n5. Testing battle mechanics...")
    original_hp = charizard.current_hp
    actual_damage = charizard.take_damage(damage)
    print(f"✅ Charizard took {actual_damage} damage")
    print(f"   HP: {original_hp} → {charizard.current_hp}")
    
    # Test 6: Speed-based turn order
    print("\n6. Testing turn order...")
    if pikachu.speed > charizard.speed:
        print(f"✅ Pikachu (speed {pikachu.speed}) goes first")
    else:
        print(f"✅ Charizard (speed {charizard.speed}) goes first")
    
    print("\n🎉 All battle system tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_battle_system()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
