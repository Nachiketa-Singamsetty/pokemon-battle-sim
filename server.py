"""
Pokémon Battle Simulation MCP Server
Main FastAPI server implementing Model Context Protocol for Pokémon battles.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

from resources.pokemon_resource import PokemonResource
from tools.battle_tool import BattleTool

app = FastAPI(
    title="Pokémon Battle Simulation MCP Server",
    description="MCP server for Pokémon data and battle simulation",
    version="1.0.0"
)

# Initialize resources and tools
pokemon_resource = PokemonResource()
battle_tool = BattleTool()

# MCP Protocol Models
class MCPResource(BaseModel):
    uri: str
    name: str
    description: str
    mimeType: str

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPResourceResponse(BaseModel):
    resources: List[MCPResource]

class MCPToolResponse(BaseModel):
    tools: List[MCPTool]

class MCPResourceContent(BaseModel):
    uri: str
    mimeType: str
    text: str

class MCPToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class MCPToolResult(BaseModel):
    content: List[Dict[str, Any]]
    isError: Optional[bool] = False

@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Pokémon Battle Simulation MCP Server",
        "version": "1.0.0",
        "description": "MCP server for Pokémon data and battle simulation using PokéAPI",
        "endpoints": {
            "resources": "/resources",
            "tools": "/tools",
            "resources/read": "/resources/read",
            "tools/call": "/tools/call"
        }
    }

@app.get("/resources", response_model=MCPResourceResponse)
async def list_resources():
    """List available MCP resources."""
    resources = [
        MCPResource(
            uri="pokemon://stats/{pokemon_name}",
            name="pokemon_stats",
            description="Get Pokémon base stats, types, abilities, and moves",
            mimeType="application/json"
        ),
        MCPResource(
            uri="pokemon://evolution/{pokemon_name}",
            name="pokemon_evolution",
            description="Get Pokémon evolution chain information",
            mimeType="application/json"
        )
    ]
    return MCPResourceResponse(resources=resources)

@app.post("/resources/read")
async def read_resource(request: Dict[str, str]):
    """Read a specific resource."""
    uri = request.get("uri", "")
    
    try:
        if uri.startswith("pokemon://stats/"):
            pokemon_name = uri.split("/")[-1]
            data = await pokemon_resource.get_pokemon_stats(pokemon_name)
            return MCPResourceContent(
                uri=uri,
                mimeType="application/json",
                text=str(data)
            )
        elif uri.startswith("pokemon://evolution/"):
            pokemon_name = uri.split("/")[-1]
            data = await pokemon_resource.get_evolution_chain(pokemon_name)
            return MCPResourceContent(
                uri=uri,
                mimeType="application/json",
                text=str(data)
            )
        else:
            raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools", response_model=MCPToolResponse)
async def list_tools():
    """List available MCP tools."""
    tools = [
        MCPTool(
            name="pokemon_battle",
            description="Simulate a battle between two Pokémon",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon1": {
                        "type": "string",
                        "description": "Name of the first Pokémon"
                    },
                    "pokemon2": {
                        "type": "string",
                        "description": "Name of the second Pokémon"
                    },
                    "moves1": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of moves for first Pokémon",
                        "maxItems": 4
                    },
                    "moves2": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of moves for second Pokémon",
                        "maxItems": 4
                    }
                },
                "required": ["pokemon1", "pokemon2"]
            }
        )
    ]
    return MCPToolResponse(tools=tools)

@app.post("/tools/call")
async def call_tool(request: MCPToolCall):
    """Execute a tool call."""
    try:
        if request.name == "pokemon_battle":
            result = await battle_tool.simulate_battle(
                pokemon1_name=request.arguments["pokemon1"],
                pokemon2_name=request.arguments["pokemon2"],
                moves1=request.arguments.get("moves1"),
                moves2=request.arguments.get("moves2")
            )
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": result
                }]
            )
        else:
            raise HTTPException(status_code=404, detail="Tool not found")
    except Exception as e:
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"Error: {str(e)}"
            }],
            isError=True
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
