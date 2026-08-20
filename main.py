from local_database import load_known_words, is_known_word, mark_word_known, try_archive_notion_page
from definition import get_definition
from word_bank import get_words
import os
import csv
import signal

FLASHCARDS_FILE = 'flashcards.csv'

def append_to_csv(word, definition):
    file_exists = os.path.exists(FLASHCARDS_FILE) and os.path.getsize(FLASHCARDS_FILE) > 0
    with open(FLASHCARDS_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Word', 'Definition'])
        writer.writerow([word, definition])
        f.flush()
        os.fsync(f.fileno())

# Get word bank from Notion (returns list of (page_id, word) tuples for
# every non-archived row — including any word stuck there by a previous
# failed archive attempt; see issue #3).
word_bank = get_words()
print(f"Words fetched from Notion: {len(word_bank)}")

# local_database.csv (not flashcards.csv) is the persistent source of truth
# for "already processed" words. flashcards.csv is an ephemeral per-run
# export you import into Anki and then delete, so it can't be relied on to
# survive across runs. Load the known-words set once so the loop below
# checks membership in memory instead of re-reading the CSV per word.
# See issues #4 and #7.
known_words = load_known_words()

succeeded = 0
skipped = 0
failed = 0
cleaned_up = 0

for page_id, word in word_bank:
    if is_known_word(word, known_words):
        # Already known locally, but Notion still has this page
        # un-archived — almost certainly a previous run's archive attempt
        # failed and only printed a warning. Retry it now instead of
        # leaving it stuck in Notion forever with no record of it having
        # happened. See issue #3.
        if try_archive_notion_page(word, page_id):
            cleaned_up += 1
        print(f"Skipping '{word}' (already processed)")
        skipped += 1
        continue

    try:
        definition = get_definition(word)

        # Critical section: the flashcards.csv append and the local
        # "known" mark must land together. If a Ctrl+C landed between
        # them, the word could end up in flashcards.csv without being
        # marked known — reprocessed and duplicated into Anki on a later
        # run — or marked known without ever being exported, silently
        # dropping it. Deferring SIGINT here closes that gap (it can't
        # protect against a hard kill/power loss, but that's a much rarer
        # trigger than an impatient Ctrl+C on a slow run). See issue #7.
        old_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            append_to_csv(word, definition)
            mark_word_known(word, known_words)
        finally:
            signal.signal(signal.SIGINT, old_handler)

        try_archive_notion_page(word, page_id)
        print(f"✓ '{word}' saved")
        succeeded += 1
    except Exception as e:
        print(f"✗ Failed on '{word}': {e}")
        failed += 1

summary = f"\nDone. {succeeded} saved, {skipped} skipped, {failed} failed."
if cleaned_up:
    summary += f" ({cleaned_up} stray Notion page(s) cleaned up.)"
print(summary)
