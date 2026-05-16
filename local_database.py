import os
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("notion_key"))
LOCAL_DB_FILE = 'local_database.csv'

def _load_known_words() -> set:
    try:
        df = pd.read_csv(LOCAL_DB_FILE)
        return set(df.iloc[:, 0].str.lower().dropna())
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return set()

def is_known_word(word: str) -> bool:
    """Return True if this word has already been processed."""
    return word.lower() in _load_known_words()

def mark_word_done(word: str, page_id: str):
    """
    Record the word as processed locally and archive it from Notion.
    Called only after the word has been successfully saved to the CSV.
    """
    # 1. Add to local database
    known = _load_known_words()
    if word.lower() not in known:
        file_exists = os.path.exists(LOCAL_DB_FILE) and os.path.getsize(LOCAL_DB_FILE) > 0
        with open(LOCAL_DB_FILE, mode='a', newline='', encoding='utf-8') as f:
            if not file_exists:
                f.write('Word\n')
            f.write(f'{word}\n')

    # 2. Archive the page in Notion
    try:
        notion.pages.update(page_id=page_id, archived=True)
    except Exception as e:
        print(f"Warning: could not archive '{word}' from Notion (page_id={page_id}): {e}")