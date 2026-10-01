import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    client = AsyncGroq(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Respond with 'hello world' in valid JSON format: {\"message\": \"hello world\"}",
                }
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
        )
        print("Success! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Raw Exception:")
        print(repr(e))

if __name__ == "__main__":
    asyncio.run(test_groq())
