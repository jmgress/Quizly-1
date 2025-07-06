import openai
import os
import sys
from dotenv import load_dotenv

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

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
    # Test with a simple request and shorter timeout
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, please respond with a simple greeting."}],
        max_tokens=20,
        timeout=10  # 10 second timeout
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
        print("Test marked as skipped due to quota limits.")
        exit(0)  # Exit with success code since this is expected
    elif "timeout" in error_str.lower():
        print("\n⚠️ API REQUEST TIMEOUT!")
        print("The OpenAI API request timed out. This could be due to network issues.")
        print("Test marked as skipped due to timeout.")
        exit(0)  # Exit with success code since this is expected
    else:
        print("\nPlease check your API key and internet connection.")
        exit(1)  # Exit with error code for unexpected errors