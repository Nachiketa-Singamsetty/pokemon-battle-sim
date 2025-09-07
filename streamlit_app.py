"""
Pokémon Battle Simulation - Enhanced Streamlit UI
Interactive web interface for the Pokémon Battle Simulation system.
"""

import streamlit as st
import asyncio
import json
import requests
from typing import List, Dict, Any, Optional
import time

# Import our battle system components
from resources.pokemon_resource import PokemonResource
from tools.battle_tool import BattleTool

# Page configuration
st.set_page_config(
    page_title="Pokémon Battle Simulator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Pokemon-themed CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Nunito:wght@400;600;700;800&display=swap');
    
    .main {
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 25%, #45b7d1 50%, #f9ca24 75%, #f0932b 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-header {
        text-align: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 2rem;
        color: #fff;
        text-shadow: 3px 3px 0px #000, -1px -1px 0px #000, 1px -1px 0px #000, -1px 1px 0px #000;
        margin: 2rem 0;
        padding: 1rem;
        background: rgba(0,0,0,0.3);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .pokemon-card {
        background: linear-gradient(145deg, #fff 0%, #f8f9fa 100%);
        border: 4px solid #333;
        border-radius: 25px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 2px 8px rgba(255,255,255,0.8);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .pokemon-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24);
        border-radius: 25px;
        z-index: -1;
        animation: cardGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes cardGlow {
        from { opacity: 0.7; }
        to { opacity: 1; }
    }
    
    .pokemon-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }
    
    .battle-arena {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border: 3px solid #ecf0f1;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .battle-arena::before {
        content: '⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡';
        position: absolute;
        top: 10px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 1.5rem;
        color: #f1c40f;
        animation: sparkle 1.5s infinite;
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .battle-log {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
        color: #00ff41;
        padding: 1.5rem;
        border-radius: 15px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
        border: 3px solid #00ff41;
        box-shadow: 0 0 20px rgba(0,255,65,0.5), inset 0 0 20px rgba(0,255,65,0.1);
        position: relative;
    }
    
    .battle-log::before {
        content: '> BATTLE SYSTEM ONLINE';
        position: absolute;
        top: -15px;
        left: 20px;
        background: #0c0c0c;
        padding: 0 10px;
        color: #00ff41;
        font-weight: bold;
    }
    
    .pokemon-name {
        font-family: 'Press Start 2P', cursive;
        font-size: 1.2rem;
        text-align: center;
        margin: 1rem 0;
        color: #2c3e50;
        text-shadow: 2px 2px 0px #fff;
    }
    
    .vs-container {
        text-align: center;
        font-family: 'Press Start 2P', cursive;
        font-size: 1.8rem;
        color: #e74c3c;
        text-shadow: 2px 2px 0px #fff;
        margin: 2rem 0;
        animation: pulse 2s infinite;
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 15px;
        border: 3px solid #333;
    }
    
    .type-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        margin: 0.2rem;
        border-radius: 25px;
        font-family: 'Nunito', sans-serif;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        color: white;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        border: 2px solid #fff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Pokemon type colors */
    .type-normal { background: linear-gradient(45deg, #A8A878, #BCBC7A); }
    .type-fire { background: linear-gradient(45deg, #F08030, #F5AC78); }
    .type-water { background: linear-gradient(45deg, #6890F0, #9DB7F5); }
    .type-electric { background: linear-gradient(45deg, #F8D030, #FAE078); color: #333; }
    .type-grass { background: linear-gradient(45deg, #78C850, #A7DB8D); }
    .type-ice { background: linear-gradient(45deg, #98D8D8, #BCE6E6); color: #333; }
    .type-fighting { background: linear-gradient(45deg, #C03028, #D67873); }
    .type-poison { background: linear-gradient(45deg, #A040A0, #C183C1); }
    .type-ground { background: linear-gradient(45deg, #E0C068, #EBD69D); color: #333; }
    .type-flying { background: linear-gradient(45deg, #A890F0, #C6B7F5); }
    .type-psychic { background: linear-gradient(45deg, #F85888, #FA92B2); }
    .type-bug { background: linear-gradient(45deg, #A8B820, #C6D16E); }
    .type-rock { background: linear-gradient(45deg, #B8A038, #D1C17D); }
    .type-ghost { background: linear-gradient(45deg, #705898, #A292BC); }
    .type-dragon { background: linear-gradient(45deg, #7038F8, #A27DFA); }
    .type-dark { background: linear-gradient(45deg, #705848, #A29288); }
    .type-steel { background: linear-gradient(45deg, #B8B8D0, #D1D1E0); color: #333; }
    .type-fairy { background: linear-gradient(45deg, #EE99AC, #F4BDC9); color: #333; }
    
    .stat-bar-container {
        background: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #333;
    }
    
    .stat-bar {
        background: #ddd;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.3rem 0;
        height: 20px;
        position: relative;
        border: 1px solid #333;
    }
    
    .stat-fill {
        height: 100%;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: 'Nunito', sans-serif;
        font-weight: bold;
        font-size: 0.8rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        transition: width 1s ease-in-out;
    }
    
    .hp-bar { background: linear-gradient(90deg, #e74c3c, #c0392b); }
    .attack-bar { background: linear-gradient(90deg, #e67e22, #d35400); }
    .defense-bar { background: linear-gradient(90deg, #3498db, #2980b9); }
    .sp-attack-bar { background: linear-gradient(90deg, #9b59b6, #8e44ad); }
    .sp-defense-bar { background: linear-gradient(90deg, #1abc9c, #16a085); }
    .speed-bar { background: linear-gradient(90deg, #f39c12, #e67e22); }
    
    .stButton > button {
        background: linear-gradient(45deg, #e74c3c, #c0392b);
        color: white;
        border: 3px solid #fff;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-family: 'Nunito', sans-serif;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(231, 76, 60, 0.6);
        background: linear-gradient(45deg, #c0392b, #a93226);
    }
    
    .sidebar .stSelectbox > div > div {
        background: linear-gradient(145deg, #fff, #f8f9fa);
        border: 2px solid #333;
        border-radius: 10px;
    }
    
    .battle-turn {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        font-family: 'Nunito', sans-serif;
    }
    
    .damage-text { color: #e74c3c; font-weight: bold; animation: shake 0.5s; }
    .heal-text { color: #2ecc71; font-weight: bold; animation: pulse 0.5s; }
    .status-text { color: #f39c12; font-weight: bold; }
    .critical-text { color: #e67e22; font-weight: bold; animation: flash 0.5s; }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .pokemon-sprite {
        filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3));
        transition: transform 0.3s ease;
    }
    
    .pokemon-sprite:hover {
        transform: scale(1.1) rotate(5deg);
    }
    
    .tab-header {
        font-family: 'Press Start 2P', cursive;
        font-size: 1.2rem;
        color: #2c3e50;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        border: 3px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'battle_log' not in st.session_state:
    st.session_state.battle_log = ""
if 'pokemon_data' not in st.session_state:
    st.session_state.pokemon_data = {}
if 'battle_history' not in st.session_state:
    st.session_state.battle_history = []

# Initialize resources
@st.cache_resource
def get_pokemon_resource():
    return PokemonResource()

@st.cache_resource
def get_battle_tool():
    return BattleTool()

pokemon_resource = get_pokemon_resource()
battle_tool = get_battle_tool()

# Helper functions
async def fetch_pokemon_data(pokemon_name: str) -> Optional[Dict[str, Any]]:
    """Fetch Pokémon data asynchronously."""
    try:
        return await pokemon_resource.get_pokemon_stats(pokemon_name.lower())
    except Exception as e:
        st.error(f"Error fetching {pokemon_name}: {str(e)}")
        return None

def display_pokemon_stats(pokemon_data: Dict[str, Any], col):
    """Display Pokémon stats in a Pokemon-themed card."""
    with col:
        if pokemon_data:
            #st.markdown('<div class="pokemon-card">', unsafe_allow_html=True)
            
            # Pokemon name
            st.markdown(f'<div class="pokemon-name">{pokemon_data["name"].title()}</div>', unsafe_allow_html=True)
            
            
            # Display types
            types_html = ""
            for pokemon_type in pokemon_data['types']:
                type_name = pokemon_type['name'].lower()
                types_html += f'<span class="type-badge type-{type_name}">{type_name}</span>'
            st.markdown(f'<div style="text-align: center; margin: 1rem 0;">{types_html}</div>', unsafe_allow_html=True)
            
            # Display stats
            # Load retro font
            st.markdown(
                """
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

                .stat-bar-container {
                    font-family: 'Press Start 2P', cursive;
                    font-size: 16px;
                    color: black;
                    text-align: center;
                    padding: 8px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Apply it to your text
            st.markdown(
                '<div class="stat-bar-container">Base Stats</div>',
                unsafe_allow_html=True
            )
            
            stats = pokemon_data['stats']
            stat_colors = {
                'hp': 'hp-bar', 'attack': 'attack-bar', 'defense': 'defense-bar',
                'special_attack': 'sp-attack-bar', 'special_defense': 'sp-defense-bar', 'speed': 'speed-bar'
            }
            
            for stat_name, value in stats.items():
                percentage = min(value / 200 * 100, 100)
                color_class = stat_colors.get(stat_name, 'hp-bar')
                display_name = stat_name.replace('_', ' ').title()
                
                st.markdown(f"""
                <div style="margin: 0.3rem 0;">
                    <div style="display: flex; justify-content: space-between; font-family: 'Nunito', sans-serif; font-weight: bold;">
                        <span>{display_name}:</span>
                        <span>{value}</span>
                    </div>
                    <div class="stat-bar">
                        <div class="stat-fill {color_class}" style="width: {percentage}%;">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)

def format_battle_log(battle_log: str) -> str:
    """Format battle log with Pokemon-themed HTML styling."""
    lines = battle_log.split('\n')
    formatted_lines = []
    
    for line in lines:
        if not line.strip():
            continue
            
        if line.startswith('==='):
            formatted_lines.append(f'<div style="color: #f1c40f; font-weight: bold; text-align: center; margin: 1rem 0;">🏆 {line} 🏆</div>')
        elif ' vs ' in line and not line.startswith(' '):
            formatted_lines.append(f'<div style="color: #e74c3c; font-weight: bold; text-align: center; margin: 1rem 0;">⚔️ {line} ⚔️</div>')
        elif ' used ' in line:
            formatted_lines.append(f'<div class="status-text">💫 {line}</div>')
        elif ' took ' in line and ' damage' in line:
            formatted_lines.append(f'<div class="damage-text">💥 {line}</div>')
        elif ' fainted!' in line:
            formatted_lines.append(f'<div style="color: #e74c3c; font-weight: bold;">💀 {line}</div>')
        elif ' wins!' in line:
            formatted_lines.append(f'<div style="color: #2ecc71; font-weight: bold; font-size: 1.2em; text-align: center;">🎉 {line} 🎉</div>')
        else:
            formatted_lines.append(f'<div style="color: #ecf0f1;">{line}</div>')
    
    return '<br>'.join(formatted_lines)

def run_async_battle(pokemon1_name: str, pokemon2_name: str, moves1: List[str] = None, moves2: List[str] = None):
    """Run battle simulation asynchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            battle_tool.simulate_battle(pokemon1_name, pokemon2_name, moves1, moves2)
        )
    finally:
        loop.close()

# Main UI
st.markdown('<h1 class="main-header">⚔️ POKÉMON BATTLE SIMULATOR ⚔️</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="tab-header">🎮 BATTLE SETUP</div>', unsafe_allow_html=True)
    
    # Pokemon selection with both custom input and popular options
    st.markdown("**Choose Pokémon:**")
    
    # Toggle between custom input and popular selections
    input_mode = st.radio("Selection Mode:", ["🔍 Custom Search", "⭐ Popular Picks"], horizontal=True)
    
    if input_mode == "🔍 Custom Search":
        pokemon1_name = st.text_input("🔴 Player 1 Pokémon", value="pikachu", placeholder="Enter any Pokémon name...")
        pokemon2_name = st.text_input("🔵 Player 2 Pokémon", value="charizard", placeholder="Enter any Pokémon name...")
        
        # Show some examples
        st.markdown("💡 **Examples:** *lucario, garchomp, rayquaza, dialga, palkia, giratina, arceus, reshiram, zekrom, kyurem*")
    else:
        pokemon_options = ["pikachu", "charizard", "blastoise", "venusaur", "mewtwo", "mew", "gyarados", "dragonite", "alakazam", "machamp", "lucario", "garchomp", "rayquaza", "dialga", "palkia"]
        
        pokemon1_name = st.selectbox("🔴 Player 1 Pokémon", options=pokemon_options, index=0)
        pokemon2_name = st.selectbox("🔵 Player 2 Pokémon", options=pokemon_options, index=1)
    
    # Quick battle button
    battle_button = st.button("🥊 START EPIC BATTLE!", type="primary", use_container_width=True)
    
    st.markdown("---")
    

# Main content
tab1, tab2, tab3 = st.tabs(["🏟️ **BATTLE ARENA**", "📊 **POKÉMON STATS**", "📜 **BATTLE HISTORY**"])

with tab1:
    st.markdown('<div class="tab-header">🏟️ BATTLE ARENA</div>', unsafe_allow_html=True)
    
    # Battle matchup display
    st.markdown('<div class="battle-arena">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f'<div class="pokemon-name" style="color: #e74c3c;">🔴 {pokemon1_name.upper()}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="vs-container">VS</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="pokemon-name" style="color: #3498db;">🔵 {pokemon2_name.upper()}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Battle execution
    if battle_button:
        with st.spinner("⚔️ Epic battle in progress..."):
            battle_result = run_async_battle(pokemon1_name, pokemon2_name)
            st.session_state.battle_log = battle_result
            
            # Add to history
            st.session_state.battle_history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "pokemon1": pokemon1_name.title(),
                "pokemon2": pokemon2_name.title(),
                "result": battle_result
            })
            
            st.success("🎉 Battle completed!")
    
    # Battle log display
    if st.session_state.battle_log:
        st.markdown("---")
        formatted_log = format_battle_log(st.session_state.battle_log)
        st.markdown(f'<div class="battle-log">{formatted_log}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-header">📊 POKÉMON STATISTICS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Display Pokemon stats
    if pokemon1_name:
        with st.spinner(f"Loading {pokemon1_name}..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                pokemon1_data = loop.run_until_complete(fetch_pokemon_data(pokemon1_name))
                if pokemon1_data:
                    display_pokemon_stats(pokemon1_data, col1)
            except Exception as e:
                with col1:
                    st.error(f"Could not load {pokemon1_name}")
            finally:
                loop.close()
    
    if pokemon2_name:
        with st.spinner(f"Loading {pokemon2_name}..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                pokemon2_data = loop.run_until_complete(fetch_pokemon_data(pokemon2_name))
                if pokemon2_data:
                    display_pokemon_stats(pokemon2_data, col2)
            except Exception as e:
                with col2:
                    st.error(f"Could not load {pokemon2_name}")
            finally:
                loop.close()

with tab3:
    st.markdown('<div class="tab-header">📜 BATTLE HISTORY</div>', unsafe_allow_html=True)
    
    if st.session_state.battle_history:
        for i, battle in enumerate(reversed(st.session_state.battle_history)):
            with st.expander(f"⚔️ Battle {len(st.session_state.battle_history) - i}: {battle['pokemon1']} vs {battle['pokemon2']} - {battle['timestamp']}"):
                st.code(battle['result'])
        
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.battle_history = []
            st.success("History cleared!")
            st.rerun()
    else:
        st.info("🎯 No battles recorded yet! Start your first epic battle!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #2c3e50; font-family: 'Nunito', sans-serif; font-weight: bold; padding: 1rem; background: rgba(255,255,255,0.8); border-radius: 15px; margin: 2rem 0;">
    <p>🎮 POKÉMON BATTLE SIMULATOR | Built with ❤️ using Streamlit & PokéAPI</p>
    <p>⚡ Powered by Model Context Protocol (MCP) Server</p>
</div>
""", unsafe_allow_html=True)