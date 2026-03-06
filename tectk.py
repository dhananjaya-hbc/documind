# test_key.py (delete after)

import asyncio
from openai import AsyncOpenAI

# PASTE YOUR NEW KEY HERE
NEW_KEY = "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"
async def test():
    client = AsyncOpenAI(
        api_key=NEW_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    # Try multiple free models
    models = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "arcee-ai/trinity-large-preview:free",
        "mistralai/mistral-7b-instruct:free",
    ]

    for model in models:
        try:
            r = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=20,
            )
            print(f"✅ {model}")
            print(f"   Response: {r.choices[0].message.content}")
        except Exception as e:
            print(f"❌ {model}")
            print(f"   Error: {e}")
        print()

asyncio.run(test())