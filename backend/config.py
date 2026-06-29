import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("API KEY START:", GEMINI_API_KEY[:10] if GEMINI_API_KEY else "NO KEY FOUND")