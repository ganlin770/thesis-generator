import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8192
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
