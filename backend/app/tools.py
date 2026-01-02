"""Tool definitions and execution."""

import json
from typing import Any, Callable
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str
    description: str
    required: bool = True


@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    parameters: list[ToolParameter]
    func: Callable


# Tool implementations
def get_business_info(topic: str) -> dict:
    """Get business information."""
    data = _load_business_data()
    
    topic_lower = topic.lower()
    
    if topic_lower in ["hours", "open", "close", "timing"]:
        return {"hours": data.get("hours", {})}
    
    if topic_lower in ["location", "address", "where"]:
        return {"location": data.get("location", "")}
    
    if topic_lower in ["menu", "items", "food", "drink"]:
        return {"menu": data.get("menu", [])}
    
    if topic_lower in ["price", "pricing", "cost", "cost"]:
        return {"pricing": data.get("pricing", {})}
    
    # Default: return general info
    return {
        "name": data.get("name", ""),
        "hours": data.get("hours", {}),
        "location": data.get("location", ""),
        "phone": data.get("phone", ""),
    }


def place_order(customer_name: str, item: str, quantity: int) -> dict:
    """Place a new order."""
    data = _load_business_data()
    
    # Validate item exists
    menu = data.get("menu", [])
    item_found = any(m.get("name", "").lower() == item.lower() for m in menu)
    
    if not item_found:
        return {
            "success": False,
            "error": f"Item '{item}' not found on menu",
            "available_items": [m.get("name", "") for m in menu]
        }
    
    # Create order
    order_id = f"ORD-{len(data.get('orders', [])) + 1:05d}"
    order = {
        "id": order_id,
        "customer_name": customer_name,
        "item": item,
        "quantity": quantity,
        "status": "pending"
    }
    
    # Append to orders
    orders = data.get("orders", [])
    orders.append(order)
    _save_business_data({**data, "orders": orders})
    
    return {
        "success": True,
        "order_id": order_id,
        "message": f"Order {order_id} placed successfully for {customer_name}"
    }


def lookup_order(order_id: str) -> dict:
    """Look up an existing order."""
    data = _load_business_data()
    orders = data.get("orders", [])
    
    for order in orders:
        if order.get("id") == order_id:
            return {
                "success": True,
                "order": order
            }
    
    return {
        "success": False,
        "error": f"Order {order_id} not found"
    }


def _load_business_data() -> dict:
    """Load business data from JSON file."""
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    data_dir.mkdir(exist_ok=True)
    
    data_file = data_dir / "business_data.json"
    
    if data_file.exists():
        with open(data_file, "r") as f:
            return json.load(f)
    
    return {}


def _save_business_data(data: dict) -> None:
    """Save business data to JSON file."""
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    data_dir.mkdir(exist_ok=True)
    
    data_file = data_dir / "business_data.json"
    
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2)


# Tool registry
TOOLS: dict[str, Tool] = {
    "get_business_info": Tool(
        name="get_business_info",
        description="Get general business info like hours, location, pricing, menu",
        parameters=[
            ToolParameter(
                name="topic",
                type="string",
                description="Topic to get info about (hours, location, menu, pricing, etc)",
                required=True
            )
        ],
        func=get_business_info
    ),
    "place_order": Tool(
        name="place_order",
        description="Place a new order for a customer",
        parameters=[
            ToolParameter(
                name="customer_name",
                type="string",
                description="Name of the customer",
                required=True
            ),
            ToolParameter(
                name="item",
                type="string",
                description="Item to order",
                required=True
            ),
            ToolParameter(
                name="quantity",
                type="number",
                description="Quantity to order",
                required=True
            )
        ],
        func=place_order
    ),
    "lookup_order": Tool(
        name="lookup_order",
        description="Look up an existing order by ID",
        parameters=[
            ToolParameter(
                name="order_id",
                type="string",
                description="Order ID to look up",
                required=True
            )
        ],
        func=lookup_order
    ),
}


def get_tools_schema() -> list[dict]:
    """Get tool schema for LLM."""
    schema = []
    
    for tool in TOOLS.values():
        tool_schema = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        for param in tool.parameters:
            tool_schema["parameters"]["properties"][param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                tool_schema["parameters"]["required"].append(param.name)
        
        schema.append(tool_schema)
    
    return schema


async def execute_tool(tool_name: str, **kwargs) -> Any:
    """Execute a tool."""
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    tool = TOOLS[tool_name]
    
    try:
        return tool.func(**kwargs)
    except Exception as e:
        return {"error": str(e)}
