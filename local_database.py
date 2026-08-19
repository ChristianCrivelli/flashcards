import os
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion_key = os.getenv("notion_key")
if not notion_key:
    raise RuntimeError("Missing 'notion_key' in .env")

notion = Client(auth=notion_key)
LOCAL_DB_FILE = 'local_database.csv'

def load_known_words() -> set:
    """
    Load the full set of already-processed words from disk.

    Call this once per run and reuse the result (pass it into is_known_word
    and mark_word_done) instead of letting each of them reload the CSV, which
    made processing a word bank O(n^2) in file I/O. See issue #4.
    """
    try:
        df = pd.read_csv(LOCAL_DB_FILE)
        return set(df.iloc[:, 0].astype(str).str.strip().str.lower().dropna())
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return set()

def is_known_word(word: str, known_words: set = None) -> bool:
    """
    Return True if this word has already been processed.

    Pass in a `known_words` set from load_known_words() to check against
    an in-memory set instead of re-reading the CSV; if omitted, it's loaded
    fresh (handy for one-off calls, but avoid this inside a loop).
    """
    if known_words is None:
        known_words = load_known_words()
    return word.strip().lower() in known_words

def _file_ends_with_newline(path: str) -> bool:
    with open(path, 'rb') as f:
        f.seek(-1, os.SEEK_END)
        return f.read(1) == b'\n'

def mark_word_done(word: str, page_id: str, known_words: set = None):
    """
    Record the word as processed locally and archive it from Notion.
    Called only after the word has been successfully saved to the CSV.

    If a `known_words` set is passed in, it's updated in place after the
    write so the caller's in-memory copy stays accurate without another
    disk read.
    """
    word = word.strip()
    normalized = word.lower()

    if known_words is None:
        known_words = load_known_words()

    # 1. Add to local database
    if normalized not in known_words:
        file_exists = os.path.exists(LOCAL_DB_FILE) and os.path.getsize(LOCAL_DB_FILE) > 0
        # Guard against a prior run leaving the file without a trailing
        # newline (e.g. process killed mid-write) — appending straight onto
        # that would silently merge two words into one corrupted row. See
        # issue #2.
        needs_leading_newline = file_exists and not _file_ends_with_newline(LOCAL_DB_FILE)
        with open(LOCAL_DB_FILE, mode='a', newline='', encoding='utf-8') as f:
            if not file_exists:
                f.write('Word\n')
            elif needs_leading_newline:
                f.write('\n')
            f.write(f'{word}\n')
        known_words.add(normalized)

    # 2. Archive the page in Notion
    try:
        notion.pages.update(page_id=page_id, archived=True)
    except Exception as e:
        print(f"Warning: could not archive '{word}' from Notion (page_id={page_id}): {e}")