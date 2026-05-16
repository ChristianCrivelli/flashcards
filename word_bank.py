import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("notion_key"))
db_id = os.getenv("database")

def get_words() -> list[tuple[str, str]]:
    """
    Returns a list of (page_id, word) tuples from the Notion database.
    page_id is needed later to archive the entry once processed.
    """
    results = []
    has_more = True
    start_cursor = None

    # Retrieve the underlying Data Source ID (Notion API 2025-09-03+)
    db_info = notion.databases.retrieve(database_id=db_id)
    data_source_id = db_info["data_sources"][0]["id"]

    while has_more:
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=start_cursor
        )
        results.extend(response.get("results", []))
        has_more = response.get("has_more")
        start_cursor = response.get("next_cursor")

    words = []
    for page in results:
        props = page["properties"]
        title_key = next(k for k, v in props.items() if v['type'] == 'title')
        title_parts = props[title_key]["title"]
        if title_parts:
            word = title_parts[0]["plain_text"]
            words.append((page["id"], word))

    return words