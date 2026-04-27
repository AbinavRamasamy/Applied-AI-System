"""
Boot-time setup: add the project root to sys.path, set fake env vars, and stub
out real API clients so that importing any src.* module never makes a network
call or fails on missing keys.
"""
import sys
from pathlib import Path

# Make `src` importable regardless of where pytest is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
from unittest.mock import MagicMock, patch

os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["TAVILY_API_KEY"] = "test-tavily-key"

patch("google.genai.Client", return_value=MagicMock()).start()
patch("tavily.TavilyClient", return_value=MagicMock()).start()
