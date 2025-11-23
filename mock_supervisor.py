"""
Mock Supervisor/Registry Service
For testing agent registration and communication
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime
import uvicorn

app = FastAPI(title="Mock Supervisor Service", version="1.0.0")

# Store registered agents
registered_agents: Dict[str, Dict[str, Any]] = {}


class AgentRegistration(BaseModel):
    """Agent registration data"""
    agent_id: str
    name: str
    version: str
    capabilities: List[str]
    health_check_url: str
    api_url: str
    timestamp: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Mock Supervisor/Registry",
        "version": "1.0.0",
        "registered_agents": len(registered_agents),
        "endpoints": {
            "register": "/register",
            "agents": "/agents",
            "health": "/health"
        }
    }


@app.post("/register")
async def register_agent(registration: AgentRegistration):
    """Register a new agent"""
    agent_id = registration.agent_id
    
    registered_agents[agent_id] = {
        "agent_id": agent_id,
        "name": registration.name,
        "version": registration.version,
        "capabilities": registration.capabilities,
        "health_check_url": registration.health_check_url,
        "api_url": registration.api_url,
        "registered_at": datetime.utcnow().isoformat(),
        "last_heartbeat": datetime.utcnow().isoformat()
    }
    
    print(f"✅ Agent registered: {agent_id} ({registration.name})")
    
    return {
        "success": True,
        "message": f"Agent {agent_id} registered successfully",
        "agent_id": agent_id
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "total": len(registered_agents),
        "agents": list(registered_agents.values())
    }


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent info"""
    if agent_id in registered_agents:
        return registered_agents[agent_id]
    return {"error": "Agent not found"}, 404


@app.get("/health")
async def health_check():
    """Health check for supervisor"""
    return {
        "status": "healthy",
        "service": "supervisor",
        "registered_agents": len(registered_agents),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("="*70)
    print("MOCK SUPERVISOR/REGISTRY SERVICE")
    print("="*70)
    print("Starting on http://localhost:9000")
    print("\nThis is a mock service for testing agent registration")
    print("\nEndpoints:")
    print("  - POST /register - Register an agent")
    print("  - GET /agents - List all agents")
    print("  - GET /health - Health check")
    print("="*70)
    
    uvicorn.run(
        "mock_supervisor:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
