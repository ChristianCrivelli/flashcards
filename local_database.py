import pandas as pd

def remove_duplicates(df: pd.DataFrame):
    try:
        csv_df = pd.read_csv("local_database.csv")
        csv_words = set(csv_df.iloc[:, 0].str.lower().dropna())
    except (pd.errors.EmptyDataError, FileNotFoundError):
        csv_df = pd.DataFrame()
        csv_words = set()

    mask = ~df.iloc[:, 0].str.lower().isin(csv_words)
    new_words_df = df[mask].reset_index(drop=True)

    # Append new words to the CSV
    if not new_words_df.empty:
        new_col = new_words_df.iloc[:, [0]]
        updated_csv_df = pd.concat([csv_df, new_col], ignore_index=True)
        updated_csv_df.to_csv("local_database.csv", index=False)

    return new_words_df