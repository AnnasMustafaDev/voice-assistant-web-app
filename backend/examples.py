"""
API testing and example script.

Run this to test the backend API:
    python examples.py
"""

import asyncio
import json
import httpx
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Client setup
client = httpx.AsyncClient(base_url=BASE_URL)


async def test_health():
    """Test health endpoint."""
    print("\n=== Health Check ===")
    response = await client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


async def test_tenant_creation():
    """Test tenant creation."""
    print("\n=== Creating Tenant ===")
    payload = {
        "name": "Tony's Restaurant",
        "industry": "hospitality",
        "language": "en"
    }
    response = await client.post("/tenants", json=payload)
    print(f"Status: {response.status_code}")
    tenant = response.json()
    print(f"Response: {json.dumps(tenant, indent=2, default=str)}")
    return tenant


async def test_agent_creation(tenant_id):
    """Test agent creation."""
    print(f"\n=== Creating Agent for Tenant {tenant_id} ===")
    payload = {
        "tenant_id": str(tenant_id),
        "name": "Front Desk Receptionist",
        "type": "receptionist",
        "voice": "en-US-Neural2-A",
        "system_prompt": "You are a professional restaurant receptionist. Help guests with reservations."
    }
    response = await client.post("/agents", json=payload)
    print(f"Status: {response.status_code}")
    agent = response.json()
    print(f"Response: {json.dumps(agent, indent=2, default=str)}")
    return agent


async def test_chat(tenant_id, agent_id):
    """Test text chat."""
    print(f"\n=== Text Chat Test ===")
    payload = {
        "tenant_id": str(tenant_id),
        "agent_id": str(agent_id),
        "message": "Hello, I'd like to make a reservation for 4 people this Saturday at 7 PM"
    }
    response = await client.post("/chat/message", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, default=str)}")
    return result


async def test_knowledge_ingest(tenant_id):
    """Test knowledge ingestion."""
    print(f"\n=== Ingesting Knowledge Document ===")
    payload = {
        "tenant_id": str(tenant_id),
        "source": "menu",
        "title": "Restaurant Menu 2024",
        "content": """
        APPETIZERS
        - Bruschetta: $8
        - Calamari: $12
        - Shrimp Cocktail: $14
        
        MAIN COURSES
        - Spaghetti Carbonara: $18
        - Grilled Salmon: $24
        - Ribeye Steak: $28
        - Chicken Parmigiana: $20
        
        DESSERTS
        - Tiramisu: $8
        - Panna Cotta: $7
        - Gelato: $6
        
        We're open Monday-Thursday 5-10 PM, Friday-Saturday 5-11 PM, Sunday 5-9 PM.
        Location: 123 Main Street, Downtown
        Phone: (555) 123-4567
        """
    }
    response = await client.post("/knowledge/ingest", json=payload)
    print(f"Status: {response.status_code}")
    doc = response.json()
    print(f"Response: {json.dumps(doc, indent=2, default=str)}")
    return doc


async def test_knowledge_search(tenant_id):
    """Test knowledge search."""
    print(f"\n=== Searching Knowledge Base ===")
    response = await client.get(
        "/knowledge/search",
        params={
            "tenant_id": str(tenant_id),
            "query": "What are your main courses and prices?",
            "top_k": 3
        }
    )
    print(f"Status: {response.status_code}")
    results = response.json()
    print(f"Response: {json.dumps(results, indent=2, default=str)}")
    return results


async def test_knowledge_list(tenant_id):
    """Test knowledge listing."""
    print(f"\n=== Listing Knowledge Documents ===")
    response = await client.get(
        "/knowledge/list",
        params={
            "tenant_id": str(tenant_id),
            "source": "menu"
        }
    )
    print(f"Status: {response.status_code}")
    docs = response.json()
    print(f"Response: {json.dumps(docs, indent=2, default=str)}")
    return docs


async def test_tenant_get(tenant_id):
    """Test get tenant."""
    print(f"\n=== Getting Tenant {tenant_id} ===")
    response = await client.get(f"/tenants/{tenant_id}")
    print(f"Status: {response.status_code}")
    tenant = response.json()
    print(f"Response: {json.dumps(tenant, indent=2, default=str)}")
    return tenant


async def test_agent_get(agent_id):
    """Test get agent."""
    print(f"\n=== Getting Agent {agent_id} ===")
    response = await client.get(f"/agents/{agent_id}")
    print(f"Status: {response.status_code}")
    agent = response.json()
    print(f"Response: {json.dumps(agent, indent=2, default=str)}")
    return agent


async def test_tenant_update(tenant_id):
    """Test tenant update."""
    print(f"\n=== Updating Tenant {tenant_id} ===")
    payload = {
        "industry": "fine_dining",
        "language": "it"
    }
    response = await client.patch(f"/tenants/{tenant_id}", json=payload)
    print(f"Status: {response.status_code}")
    tenant = response.json()
    print(f"Response: {json.dumps(tenant, indent=2, default=str)}")
    return tenant


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Reception Voice Agent - API Test Suite")
    print("=" * 60)
    
    try:
        # Health check
        await test_health()
        
        # Create tenant
        tenant = await test_tenant_creation()
        tenant_id = tenant["id"]
        
        # Get tenant
        await test_tenant_get(tenant_id)
        
        # Update tenant
        await test_tenant_update(tenant_id)
        
        # Create agent
        agent = await test_agent_creation(tenant_id)
        agent_id = agent["id"]
        
        # Get agent
        await test_agent_get(agent_id)
        
        # Ingest knowledge
        await test_knowledge_ingest(tenant_id)
        
        # List knowledge
        await test_knowledge_list(tenant_id)
        
        # Search knowledge
        await test_knowledge_search(tenant_id)
        
        # Chat
        await test_chat(tenant_id, agent_id)
        
        # More chats with context
        await test_chat(tenant_id, agent_id)
        await test_chat(tenant_id, agent_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
