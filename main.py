from local_database import remove_duplicates
from clean_notion import clear_database
from definition import get_definition
from word_bank import get_words

import pandas as pd
import csv
import os

# Get word bank
word_bank =  get_words()

# Check Words Against File
word_bank = remove_duplicates(word_bank)
print(f"New words to process: {len(word_bank)}")

# Getting the Defention
word_bank['Definition'] = word_bank['Word'].apply(get_definition)

# Writting the File
word_bank.to_csv('flashcards.csv', mode='a', index=False, header=not os.path.exists('flashcards.csv'))

clear_database()