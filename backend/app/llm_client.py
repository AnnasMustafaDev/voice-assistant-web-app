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

You have access to tools:
1. get_business_info(topic) - Get business info (topic: "hours", "location", "menu", "pricing")
2. place_order(customer_name, item, quantity) - Place an order
3. lookup_order(order_id) - Look up an order status

IMPORTANT: When you need to use a tool:
1. Clearly state what you're doing first (e.g., "Let me look that up for you")
2. Call the function in this format: TOOL[function_name](arg1, arg2)
3. Then provide the response based on the result

For example:
- User: "What's the menu?"
- You: "Let me get the menu for you. TOOL[get_business_info](menu)"
- Response: [system returns menu data]
- You: "We have burgers, pizza, salads, drinks, and desserts. Can I help you with anything else?"

Keep responses short and suitable for voice output.
Conversation history is provided. Respond naturally as if in a phone call."""


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
        
        Uses text-based tool calling since Groq's native tool calling is unreliable.
        
        Args:
            messages: Conversation history
            max_iterations: Max tool call iterations
            
        Returns:
            Final text response
        """
        current_messages = messages.copy()
        
        for iteration in range(max_iterations):
            try:
                # Call LLM (without tool schema - use text-based tool calling)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=current_messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )
                
                # Extract response
                response_text = response.choices[0].message.content
                
                if not response_text:
                    break
                
                # Check for tool calls in text format: TOOL[function_name](args)
                import re
                tool_pattern = r'TOOL\[(\w+)\]\((.*?)\)'
                matches = re.findall(tool_pattern, response_text)
                
                if not matches:
                    # No tool calls - return response
                    return response_text
                
                # Add assistant message to history
                current_messages.append({
                    "role": "assistant",
                    "content": response_text
                })
                
                # Execute found tools
                tool_results = {}
                for tool_name, args_str in matches:
                    print(f"[LLM] Found tool call: {tool_name}({args_str})")
                    
                    # Parse arguments - simple CSV parsing for positional args
                    # Remove quotes and split by comma
                    args_list = []
                    for arg in args_str.split(','):
                        arg = arg.strip().strip('"\'')
                        args_list.append(arg)
                    
                    # Execute tool
                    try:
                        if args_list and args_list[0]:
                            result = await execute_tool(tool_name, *args_list)
                        else:
                            result = await execute_tool(tool_name)
                        print(f"[LLM] Tool result: {result}")
                        tool_results[f"{tool_name}({args_str})"] = result
                    except TypeError:
                        # Try as kwargs if positional fails
                        try:
                            # Parse as key=value pairs
                            kwargs = {}
                            for arg in args_str.split(','):
                                if '=' in arg:
                                    key, val = arg.split('=', 1)
                                    kwargs[key.strip()] = val.strip().strip('"\'')
                            result = await execute_tool(tool_name, **kwargs)
                            tool_results[f"{tool_name}({args_str})"] = result
                        except Exception as e:
                            print(f"[LLM] Tool execution failed: {e}")
                            tool_results[f"{tool_name}({args_str})"] = {"error": str(e)}
                
                if not tool_results:
                    # No tools were executed, return response as-is
                    return response_text
                
                # Add tool results to history and ask LLM for final response
                tool_info = "Tool results:\n"
                for tool_call, result in tool_results.items():
                    tool_info += f"  {tool_call}: {json.dumps(result)}\n"
                
                current_messages.append({
                    "role": "user",
                    "content": tool_info + "\nBased on these tool results, provide a natural response to the user's request."
                })
                
                # Get final response from LLM
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=current_messages,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )
                
                final_text = final_response.choices[0].message.content
                
                # Remove any remaining tool call markers from response
                final_text = re.sub(tool_pattern, '', final_text).strip()
                
                return final_text if final_text else response_text
            
            except Exception as e:
                # Log the error and return error message
                error_msg = str(e)
                print(f"[LLM] Error: {error_msg}")
                return f"I encountered an error processing your request. Please try again."
        
        # Return empty if no response
        return ""
    
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
                tool_args = tool_call.function.arguments
                
                # Parse arguments - handle both string and dict formats
                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)
                
                print(f"[LLM] Executing tool: {tool_name} with args: {tool_args}")
                
                # Execute tool
                result = await execute_tool(tool_name, **tool_args)
                print(f"[LLM] Tool result: {result}")
                
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
        print(f"LLM Response: {response}")
        
        return response.choices[0].message.content or ""
