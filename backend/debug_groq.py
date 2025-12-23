import asyncio
from groq import AsyncGroq
import os

async def main():
    client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY", "dummy"))
    print(f"Client dir: {dir(client)}")
    try:
        print(f"Client audio: {client.audio}")
    except AttributeError as e:
        print(f"Error accessing audio: {e}")

if __name__ == "__main__":
    asyncio.run(main())
