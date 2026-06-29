import time
import threading
from config import GEMINI_API_KEY

try:
    from google import genai
except ImportError:
    genai = None
    print("Install using: pip install google-genai")


# ---------------- RATE LIMITER ----------------
class RateLimiter:
    def __init__(self, requests_per_minute=15):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            now = time.time()

            self.request_times = [
                t for t in self.request_times
                if now - t < 60
            ]

            if len(self.request_times) >= self.requests_per_minute:
                sleep_time = 60 - (
                    now - self.request_times[0]
                )

                if sleep_time > 0:
                    print(
                        f"⏳ Rate limit reached. Waiting {sleep_time:.1f}s"
                    )
                    time.sleep(sleep_time)

            self.request_times.append(time.time())


rate_limiter = RateLimiter()


# ---------------- CLIENT INIT ----------------
client = None

# 2.0 Flash is more stable than 2.5 Flash sometimes
MODEL_NAME = "gemini-2.0-flash-lite"

try:
    if genai and GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini ready: {MODEL_NAME}")
    else:
        print(
            "⚠ Gemini not initialized "
            "(missing API key or package)"
        )

except Exception as e:
    print(f"❌ Gemini init error: {e}")


# ---------------- MAIN FUNCTION ----------------
def generate_answer(context, question, max_retries=5):

    if client is None:
        return (
            "Gemini not available. "
            "Check API key or installation."
        )

    rate_limiter.wait_if_needed()

    prompt = f"""
You are DocuTrust AI.

Rules:
1. Use ONLY the provided context.
2. If the answer is not present, reply:
   Not enough information in uploaded documents.
3. Give short and accurate answers.

Context:
{context}

Question:
{question}

Answer:
"""

    for attempt in range(max_retries):
        try:
            print(
                f"\n🤖 Gemini call "
                f"{attempt + 1}/{max_retries}"
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if (
                hasattr(response, "text")
                and response.text
            ):
                print("✅ Gemini response generated")
                return response.text.strip()

            return (
                "Not enough information in uploaded documents."
            )

        except Exception as e:
            err = str(e)
            print(f"❌ Gemini error: {err}")

            # Retryable errors
            is_retryable = any(
                x in err.lower()
                for x in [
                    "429",
                    "quota",
                    "resource_exhausted",
                    "rate",
                    "503",
                    "unavailable",
                ]
            )

            if (
                is_retryable
                and attempt < max_retries - 1
            ):
                wait = (2 ** attempt) * 10

                print(
                    f"⏳ Gemini busy. "
                    f"Retrying in {wait}s..."
                )

                time.sleep(wait)
                continue

            if is_retryable:
                return (
                    "Gemini service is currently busy. "
                    "Please try again after a few minutes."
                )

            return (
                "Gemini failed due to API/network issue."
            )

    return (
        "Gemini service is temporarily unavailable. "
        "Please try again later."
    )