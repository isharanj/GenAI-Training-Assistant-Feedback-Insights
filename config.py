"""Central configuration. Values come from environment variables (.env), never hard-coded."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DOCS_DIR = ROOT / "docs"
INDEX_DIR = ROOT / "index"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500      # characters
CHUNK_OVERLAP = 50    # characters
TOP_K = 4

# LLM settings: choose ONE company-approved provider in .env
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()   # anthropic | openai | azure_openai
LLM_MODEL = os.getenv("LLM_MODEL", "")                           # model / deployment name
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "400"))

SYSTEM_PROMPT = """You are the Training Team assistant. Answer ONLY from the context below.
If the answer is not in the context, say: "I don't have that information - please contact the Training Team."
Be concise (max 5 sentences). End with "Sources:" and list the document names used.
Never ask for or repeat personal data (employee IDs, emails, scores).
CONTEXT:
{retrieved_chunks}
QUESTION: {user_question}"""

REFUSAL = "I don't have that information - please contact the Training Team."
