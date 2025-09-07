"""
Tests for FastAPI MCP Server
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from server import app

class TestMCPServer:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Pokémon Battle Simulation MCP Server"
        assert "endpoints" in data
    
    def test_list_resources(self, client):
        response = client.get("/resources")
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert len(data["resources"]) >= 2
        
        # Check for expected resources
        resource_names = [r["name"] for r in data["resources"]]
        assert "pokemon_stats" in resource_names
        assert "pokemon_evolution" in resource_names
    
    def test_list_tools(self, client):
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) >= 1
        
        # Check for battle tool
        tool_names = [t["name"] for t in data["tools"]]
        assert "pokemon_battle" in tool_names
    
    @patch('resources.pokemon_resource.PokemonResource.get_pokemon_stats')
    def test_read_pokemon_stats_resource(self, mock_get_stats, client):
        # Mock the resource response
        mock_stats = {
            "name": "pikachu",
            "stats": {"hp": 35, "attack": 55},
            "types": [{"name": "electric"}]
        }
        mock_get_stats.return_value = mock_stats
        
        response = client.post("/resources/read", json={"uri": "pokemon://stats/pikachu"})
        assert response.status_code == 200
        data = response.json()
        assert data["uri"] == "pokemon://stats/pikachu"
        assert data["mimeType"] == "application/json"
    
    @patch('resources.pokemon_resource.PokemonResource.get_evolution_chain')
    def test_read_pokemon_evolution_resource(self, mock_get_evolution, client):
        # Mock the evolution response
        mock_evolution = {
            "id": 10,
            "evolution_chain": {"species_name": "pichu"}
        }
        mock_get_evolution.return_value = mock_evolution
        
        response = client.post("/resources/read", json={"uri": "pokemon://evolution/pikachu"})
        assert response.status_code == 200
        data = response.json()
        assert data["uri"] == "pokemon://evolution/pikachu"
    
    def test_read_invalid_resource(self, client):
        response = client.post("/resources/read", json={"uri": "invalid://resource"})
        assert response.status_code == 404
    
    @patch('tools.battle_tool.BattleTool.simulate_battle')
    def test_call_battle_tool(self, mock_simulate, client):
        # Mock the battle simulation
        mock_simulate.return_value = "Battle completed! Pikachu wins!"
        
        tool_call = {
            "name": "pokemon_battle",
            "arguments": {
                "pokemon1": "pikachu",
                "pokemon2": "charizard"
            }
        }
        
        response = client.post("/tools/call", json=tool_call)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert len(data["content"]) > 0
        assert "Battle completed!" in data["content"][0]["text"]
    
    def test_call_invalid_tool(self, client):
        tool_call = {
            "name": "invalid_tool",
            "arguments": {}
        }
        
        response = client.post("/tools/call", json=tool_call)
        assert response.status_code == 404
    
    @patch('tools.battle_tool.BattleTool.simulate_battle')
    def test_call_battle_tool_with_error(self, mock_simulate, client):
        # Mock an error in battle simulation
        mock_simulate.side_effect = Exception("Battle error")
        
        tool_call = {
            "name": "pokemon_battle",
            "arguments": {
                "pokemon1": "pikachu",
                "pokemon2": "charizard"
            }
        }
        
        response = client.post("/tools/call", json=tool_call)
        assert response.status_code == 200
        data = response.json()
        assert data["isError"] is True
        assert "Error:" in data["content"][0]["text"]
