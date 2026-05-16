import os
from dotenv import load_dotenv
import pandas as pd
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("notion_key"))
db_id = os.getenv("database")

def get_words():
    results = []
    has_more = True
    start_cursor = None

    # 1. Retrieve the database to get its underlying Data Source ID
    db_info = notion.databases.retrieve(database_id=db_id)
    data_source_id = db_info["data_sources"][0]["id"]

    # Handle pagination to get all rows
    while has_more:
        # 2. Query the data_source instead of the database
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=start_cursor
        )
        
        results.extend(response.get("results"))
        has_more = response.get("has_more")
        start_cursor = response.get("next_cursor")

    # Extracting the "Word" column
    rows = []
    for page in results:
        props = page["properties"]
        # Find the 'title' type property automatically
        title_key = [k for k, v in props.items() if v['type'] == 'title'][0]
        word = props[title_key]["title"][0]["plain_text"] if props[title_key]["title"] else ""
        rows.append(word)

    return pd.DataFrame(rows, columns=["Word"])