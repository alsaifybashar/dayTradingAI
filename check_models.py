import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No GEMINI_API_KEY found.")
else:
    genai.configure(api_key=api_key)
    print("Available Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
