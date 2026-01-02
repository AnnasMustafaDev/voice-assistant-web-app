"""LLM client with tool calling."""

import json
from typing import Optional
from groq import Groq
from app.config import get_settings
from app.tools import get_tools_schema, execute_tool


settings = get_settings()

SYSTEM_PROMPT = """You are a real-time AI voice receptionist.

Your job:
- Speak naturally and concisely
- Help users with information, orders, and status lookups
- Ask clarifying questions only when required
- Never mention internal systems, APIs, or tools

You have access to tools for:
- Retrieving business information
- Placing orders
- Looking up existing orders

Rules:
- If a user intent can be fulfilled with a tool, call it
- If information is missing, ask for it before calling a tool
- Keep responses short and suitable for voice output
- Do not return raw JSON to the user

Conversation history is provided. Respond only with what the user should hear."""


class LLMClient:
    """Groq LLM client with tool calling."""
    
    def __init__(self):
        """Initialize Groq client."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        self.tools_schema = get_tools_schema()
    
    async def chat_with_tools(
        self,
        messages: list[dict],
        max_iterations: int = 5
    ) -> str:
        """
        Chat with LLM, allowing tool calls.
        
        Args:
            messages: Conversation history
            max_iterations: Max tool call iterations
            
        Returns:
            Final text response
        """
        current_messages = messages.copy()
        
        for iteration in range(max_iterations):
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=self.tools_schema,
                tool_choice="auto",
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            
            # Extract response
            choice = response.choices[0]
            message = choice.message
            
            # Check if we got text content
            if message.content:
                return message.content
            
            # Check for tool calls
            if not message.tool_calls:
                break
            
            # Add assistant message to history
            current_messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute tools
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                result = await execute_tool(tool_name, **tool_args)
                
                # Add tool result to history
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        
        # Return empty if no response
        return ""
    
    async def simple_chat(self, messages: list[dict]) -> str:
        """
        Simple chat without tool calls.
        
        Args:
            messages: Conversation history
            
        Returns:
            Text response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        
        return response.choices[0].message.content or ""
