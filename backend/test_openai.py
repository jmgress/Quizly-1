import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in environment variables or .env file")
    exit(1)

# Get model from environment (default to gpt-4o-mini if not specified)
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

print(f"Testing OpenAI API connection with model: {model}")
client = openai.OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, please respond with a simple greeting."}],
        max_tokens=50
    )
    
    print(f"\nSuccess! API responded with model {model}:")
    print(response.choices[0].message.content)
    print(f"\nYour OpenAI API key is working correctly with model: {model}")
except Exception as e:
    error_str = str(e)
    print(f"\nError: {error_str}")
    
    if "insufficient_quota" in error_str:
        print("\n⚠️ API KEY QUOTA EXCEEDED!")
        print("Your OpenAI account has insufficient credits or has exceeded its quota.")
        print("Please check your billing details at: https://platform.openai.com/account/billing")
        print("You may need to add payment information or create a new API key.")
    else:
        print("\nPlease check your API key and internet connection.")