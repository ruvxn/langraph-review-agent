import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

assert NOTION_API_KEY, "Missing NOTION_API_KEY in environment"
assert NOTION_DATABASE_ID, "Missing NOTION_DATABASE_ID in environment"

client = Client(auth=NOTION_API_KEY)

# Fetch DB to verify access and property names
db = client.databases.retrieve(NOTION_DATABASE_ID)
print(" Connected to Notion database:")
print("  title:", " ".join([t["plain_text"] for t in db["title"]]))
print("  properties:", list(db["properties"].keys()))

# small test row
page = client.pages.create(
    parent={"database_id": NOTION_DATABASE_ID},
    properties={
        "ReviewID": {"title": [{"text": {"content": "PING-TEST"}}]},
        "Reviewer": {"rich_text": [{"text": {"content": "system"}}]},
        "Date": {"date": {"start": "2025-01-01"}},
        "ReviewText": {"rich_text": [{"text": {"content": "Connectivity check"}}]},
        "ErrorSummary": {"rich_text": [{"text": {"content": "None"}}]},
        "ErrorType": {"multi_select": []},
        "Criticality": {"select": {"name": "None"}},
        "Rationale": {"rich_text": [{"text": {"content": "Smoke test"}}]},
    },
)
print(" Test page created:", page["id"])
