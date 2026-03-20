"""
word_counter.py
===============
A versatile word analysis tool for text files of any size.

Features:
  1. word_count_summary()  — count specific word(s) in a file
  2. top_n_words()         — find the most frequent words in a file
  3. analyse_folder()      — analyse every .txt file in a folder
  4. save_to_csv()         — export any results to a CSV file

Usage:
  Run this file directly to see examples, or import functions into your own script.
"""

import re
import os
import csv
from collections import Counter


# ---------------------------------------------------------------------------
# STOPWORDS — common words to filter out for meaningful analysis
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "it", "its", "as", "be",
    "was", "are", "were", "has", "have", "had", "do", "does", "did",
    "not", "no", "so", "up", "out", "he", "she", "they", "we", "i",
    "you", "his", "her", "their", "our", "my", "this", "that", "these",
    "those", "than", "then", "when", "what", "which", "who", "how",
    "all", "been", "would", "could", "should", "will", "can", "into",
    "about", "just", "more", "also", "there", "where", "here", "some",
    "any", "over", "after", "before", "between", "through", "while"
}


# ---------------------------------------------------------------------------
# CORE HELPER
# ---------------------------------------------------------------------------

def extract_words(file_path, remove_stopwords=False):
    """Read a text file and return a list of lowercase words.

    Args:
        file_path (str): Path to the .txt file.
        remove_stopwords (bool): If True, common words are filtered out.

    Returns:
        list[str]: Lowercase words extracted from the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    words = re.findall(r"[A-Za-z0-9_]+", text)
    words = [w.lower() for w in words]

    if remove_stopwords:
        words = [w for w in words if w not in STOPWORDS]

    return words


# ---------------------------------------------------------------------------
# FEATURE 1: Count specific word(s)
# ---------------------------------------------------------------------------

def word_count_summary(file_path, search_terms):
    """Count occurrences of one word or a list of words in a text file.

    Args:
        file_path (str): Path to the text file.
        search_terms (str | list): A single word or a list of words.

    Returns:
        str: A summary sentence (single word) or a formatted table (list).
    """
    words = extract_words(file_path)

    # Single word
    if isinstance(search_terms, str):
        target = search_terms.lower()
        count = sum(1 for w in words if w == target)
        return f"The word '{search_terms}' appears {count} time(s)."

    # List of words
    if not search_terms:
        return "No search terms were provided."

    counts = []
    total = 0
    for term in search_terms:
        c = sum(1 for w in words if w == term.lower())
        counts.append((term, c))
        total += c

    max_word_len  = max(len("WORD"),  *(len(w) for w, _ in counts))
    max_count_len = max(len("COUNT"), *(len(str(c)) for _, c in counts))
    ww = max_word_len + 2
    cw = max_count_len + 2

    sep    = f"|{'-' * (ww + 1)}|{'-' * (cw + 1)}|"
    header = f"| {'WORD'.ljust(ww)}| {'COUNT'.rjust(cw)}|"
    lines  = [header, sep]

    for w, c in counts:
        lines.append(f"| {w.ljust(ww)}| {str(c).rjust(cw)}|")

    lines += [sep, f"| {'TOTAL'.ljust(ww)}| {str(total).rjust(cw)}|", sep]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# FEATURE 2: Top N most frequent words
# ---------------------------------------------------------------------------

def top_n_words(file_path, n=10, remove_stopwords=True):
    """Find the most frequently occurring words in a text file.

    Args:
        file_path (str): Path to the text file.
        n (int): How many top words to return (default 10).
        remove_stopwords (bool): Filter out common words (default True).

    Returns:
        str: A formatted table of the top N words and their counts.
    """
    words = extract_words(file_path, remove_stopwords=remove_stopwords)

    if not words:
        return "No words found in the file."

    most_common = Counter(words).most_common(n)

    max_word_len  = max(len("WORD"),  *(len(w) for w, _ in most_common))
    max_count_len = max(len("COUNT"), *(len(str(c)) for _, c in most_common))
    ww = max_word_len + 2
    cw = max_count_len + 2

    sep    = f"|{'-' * (ww + 1)}|{'-' * (cw + 1)}|"
    header = f"| {'WORD'.ljust(ww)}| {'COUNT'.rjust(cw)}|"
    title  = f"  Top {n} words in: {os.path.basename(file_path)}"
    lines  = [title, header, sep]

    for word, count in most_common:
        lines.append(f"| {word.ljust(ww)}| {str(count).rjust(cw)}|")

    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# FEATURE 3: Analyse all .txt files in a folder
# ---------------------------------------------------------------------------

def analyse_folder(folder_path, search_terms=None, n=10, remove_stopwords=True):
    """Analyse every .txt file in a folder.

    If search_terms is provided, counts those words in each file.
    Otherwise, prints the top N words for each file.

    Args:
        folder_path (str): Path to a folder containing .txt files.
        search_terms (str | list | None): Word(s) to search, or None for top-N mode.
        n (int): Number of top words to show (used only when search_terms is None).
        remove_stopwords (bool): Filter stopwords in top-N mode.

    Returns:
        dict: {filename: result_string} for each .txt file found.
    """
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    if not txt_files:
        print(f"No .txt files found in '{folder_path}'.")
        return {}

    results = {}
    for filename in sorted(txt_files):
        file_path = os.path.join(folder_path, filename)
        if search_terms is not None:
            result = word_count_summary(file_path, search_terms)
        else:
            result = top_n_words(file_path, n=n, remove_stopwords=remove_stopwords)
        results[filename] = result
        print(f"\n{'=' * 50}")
        print(f"File: {filename}")
        print('=' * 50)
        print(result)

    return results


# ---------------------------------------------------------------------------
# FEATURE 4: Save results to CSV
# ---------------------------------------------------------------------------

def save_to_csv(file_path, output_csv, search_terms=None, n=10, remove_stopwords=True):
    """Analyse a text file and save the word counts to a CSV file.

    Args:
        file_path (str): Path to the text file to analyse.
        output_csv (str): Path where the CSV should be saved.
        search_terms (str | list | None): Specific words to count,
            or None to use top-N frequency mode.
        n (int): Number of top words (used only when search_terms is None).
        remove_stopwords (bool): Filter stopwords in top-N mode.
    """
    if search_terms is not None:
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        words = extract_words(file_path)
        rows = [(term, sum(1 for w in words if w == term.lower()))
                for term in search_terms]
    else:
        filtered = extract_words(file_path, remove_stopwords=remove_stopwords)
        rows = Counter(filtered).most_common(n)

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["word", "count"])
        writer.writerows(rows)

    print(f"Results saved to: {output_csv}")


# ---------------------------------------------------------------------------
# EXAMPLE USAGE
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    FILE   = "word_counter.txt"   # ← change to your .txt file
    FOLDER = "."                  # ← change to a folder of .txt files

    print("--- Feature 1: Count specific words ---")
    print(word_count_summary(FILE, "hope"))
    print()
    print(word_count_summary(FILE, ["hope", "the", "and"]))

    print("\n--- Feature 2: Top 10 most frequent words (stopwords removed) ---")
    print(top_n_words(FILE, n=10, remove_stopwords=True))

    print("\n--- Feature 2b: Top 10 with stopwords included ---")
    print(top_n_words(FILE, n=10, remove_stopwords=False))

    print("\n--- Feature 3: Analyse all .txt files in a folder ---")
    analyse_folder(FOLDER, n=5)

    print("\n--- Feature 4: Save top 10 words to CSV ---")
    save_to_csv(FILE, "word_counts.csv", n=10)
