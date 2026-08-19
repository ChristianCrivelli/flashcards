from local_database import load_known_words, is_known_word, mark_word_done
from definition import get_definition
from word_bank import get_words
import os
import csv

FLASHCARDS_FILE = 'flashcards.csv'

def append_to_csv(word, definition):
    file_exists = os.path.exists(FLASHCARDS_FILE) and os.path.getsize(FLASHCARDS_FILE) > 0
    with open(FLASHCARDS_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Word', 'Definition'])
        writer.writerow([word, definition])

# Get word bank from Notion (returns list of (page_id, word) tuples)
word_bank = get_words()
print(f"Words fetched from Notion: {len(word_bank)}")

# Load the known-words set once so the loop below checks membership in
# memory instead of re-reading/re-parsing the CSV for every word. See issue #4.
known_words = load_known_words()

succeeded = 0
skipped = 0
failed = 0

for page_id, word in word_bank:
    if is_known_word(word, known_words):
        print(f"Skipping '{word}' (already processed)")
        skipped += 1
        continue

    try:
        definition = get_definition(word)
        append_to_csv(word, definition)
        mark_word_done(word, page_id, known_words)
        print(f"✓ '{word}' saved")
        succeeded += 1
    except Exception as e:
        print(f"✗ Failed on '{word}': {e}")
        failed += 1

print(f"\nDone. {succeeded} saved, {skipped} skipped, {failed} failed.")