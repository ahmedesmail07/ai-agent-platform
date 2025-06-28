import os

import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable is not set")
    print("Please set it in your .env file or environment")
    exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    # store=True,
    messages=[{"role": "user", "content": "write a haiku about ai"}],
)

print(completion.choices[0].message)
