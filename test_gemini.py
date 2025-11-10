"""Test Gemini API"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "Generate a JSON with keys: subject, greeting, body, closing for an email about 'Project completed'"
    response = model.generate_content(prompt)
    print("\nGemini Response:")
    print(response.text)
