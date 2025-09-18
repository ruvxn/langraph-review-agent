import os
from datetime import date
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

DB_ID = os.environ.get("NOTION_DATABASE_ID")
API_KEY = os.environ.get("NOTION_API_KEY")
assert DB_ID and API_KEY, "Missing NOTION_DATABASE_ID or NOTION_API_KEY"

client = Client(auth=API_KEY)

# Fake sample resembling EnrichedError structure
sample = {
    "review_id": "REV-DEMO-002",
    "reviewer": "Dee",
    "date": date.today().isoformat(),  
    "review_text": "Mobile app doesnt work  when switching workspaces. Lost a draft once.",
    "error_summary": "Mobile app crashes when switching workspaces",
    "error_type": ["Mobile", "Crash"],     
    "criticality": "Critical",             
    "rationale": "User reports reproducible crash while switching workspaces.",
    "hash": "demo-hash-002",               # just a stub for now
}

props = {
    "ReviewID":     {"title":     [{"text": {"content": sample["review_id"]}}]},
    "Reviewer":     {"rich_text": [{"text": {"content": sample["reviewer"]}}]},
    "Date":         {"date":      {"start": sample["date"]}},
    "ReviewText":   {"rich_text": [{"text": {"content": sample["review_text"]}}]},
    "ErrorSummary": {"rich_text": [{"text": {"content": sample["error_summary"]}}]},
    "ErrorType":    {"multi_select": [{"name": t} for t in sample["error_type"]]},
    "Criticality":  {"select": {"name": sample["criticality"]}},
    "Rationale":    {"rich_text": [{"text": {"content": sample["rationale"]}}]},
    "Hash":         {"rich_text": [{"text": {"content": sample["hash"]}}]},
}

page = client.pages.create(parent={"database_id": DB_ID}, properties=props)
print("Inserted demo row:", page["id"])
