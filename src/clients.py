import os
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

load_dotenv()
gemini_key = os.environ.get("GEMINI_API_KEY")
travily_key = os.environ.get("TRAVILY_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY is missing from your environment variables.")
if not travily_key:
    raise ValueError("GEMINI_API_KEY is missing from your environment variables.")

        
google_client = genai.Client(api_key=gemini_key,)
travily_client = TavilyClient(api_key=travily_key,)

FLASH_MODEL = "gemini-3.1-flash-lite-preview"
GEMMA_MODEL = "gemma-4-31b-it"
