import os
from dotenv import load_dotenv
import pandas as pd
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("notion_key"))
db_id = os.getenv("database")


def clear_database():
    has_more = True
    start_cursor = None

    # 1. Retrieve the underlying Data Source ID (just like in get_words)
    db_info = notion.databases.retrieve(database_id=db_id)
    data_source_id = db_info["data_sources"][0]["id"]

    deleted_count = 0
    print("Fetching and deleting rows... This might take a moment depending on the size.")

    # Handle pagination to make sure we get every single row
    while has_more:
        # 2. Query the data_source to get the current batch of rows
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=start_cursor
        )
        
        results = response.get("results", [])
        
        # 3. Loop through the results and archive (delete) each page
        for page in results:
            notion.pages.update(
                page_id=page["id"], 
                archived=True
            )
            deleted_count += 1
            
        has_more = response.get("has_more")
        start_cursor = response.get("next_cursor")

    print(f"Successfully cleared {deleted_count} words from the database!")