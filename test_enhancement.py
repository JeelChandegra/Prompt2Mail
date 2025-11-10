"""Test the email enhancement directly"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

main_idea = "Project completed successfully"
tone = "professional"

prompt = f"""You are a professional email writing assistant. Given a short main idea, create a polished, concise, and natural-sounding email.

Main idea: {main_idea}
Tone: {tone}

Generate a complete professional email with:
1. A clear, specific subject line (no "Subject:" prefix)
2. Appropriate greeting
3. Well-structured body (2-4 sentences, clear and concise)
4. Professional closing

Return ONLY a valid JSON object with these exact keys: "subject", "greeting", "body", "closing"

Example format:
{{"subject": "Project Update - Q4 Results", "greeting": "Hello,", "body": "I wanted to share some exciting news about our Q4 performance. Our team exceeded targets by 15% and secured three new major clients. The detailed report is attached for your review.", "closing": "Best regards"}}

Now generate the email:"""

print("Sending prompt to Gemini...\n")

model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(prompt)
text = response.text.strip()

print(f"Raw response:\n{text}\n")
print("=" * 80)

# Extract JSON
if "```json" in text:
    text = text.split("```json")[1].split("```")[0].strip()
elif "```" in text:
    text = text.split("```")[1].split("```")[0].strip()

print(f"\nExtracted JSON:\n{text}\n")
print("=" * 80)

result = json.loads(text)
print(f"\nParsed result:")
print(f"Subject: {result['subject']}")
print(f"Greeting: {result['greeting']}")
print(f"Body: {result['body']}")
print(f"Closing: {result['closing']}")

print("\n" + "=" * 80)
print("Full email that would be sent:")
print("=" * 80)
full_body = f"{result['greeting']}\n\n{result['body']}\n\n{result['closing']},\nJeel Chandegra"
print(full_body)
