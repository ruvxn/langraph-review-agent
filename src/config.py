from dotenv import load_dotenv
import os

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "./data/tech_service_reviews_500_with_names_ratings.csv")

# LLM – we’ll use Ollama first
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Optional placeholders for later (Notion, OpenAI). Ignore for now.
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
