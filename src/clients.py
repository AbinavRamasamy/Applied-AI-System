import logging
import os

from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

load_dotenv()
gemini_key = os.environ.get("GEMINI_API_KEY")
tavily_key = os.environ.get("TAVILY_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY is missing from your environment variables.")
if not tavily_key:
    raise ValueError("TAVILY_API_KEY is missing from your environment variables.")

google_client = genai.Client(api_key=gemini_key)
tavily_client = TavilyClient(api_key=tavily_key)

GEMMA_MODEL = "gemma-4-31b-it"
