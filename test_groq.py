"""Test Groq API key"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Testing Groq API key: {api_key[:20]}...")

try:
    client = Groq(api_key=api_key)
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello! API is working!'"
            }
        ],
        temperature=1,
        max_tokens=50,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    print("✅ SUCCESS! Groq API is working!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPlease check:")
    print("1. Your API key is correct")
    print("2. Get a new key from: https://console.groq.com/keys")
    print("3. Update .env file with: GROQ_API_KEY=your_actual_key")
