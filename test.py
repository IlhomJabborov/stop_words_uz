import re
from collections import Counter
from docx import Document
from PyPDF2 import PdfReader
import json

status_input = False
status_output = False
# Define a list of Uzbek stop words
UZBEK_STOP_WORDS = []

# Function to load stop words from a .txt file
def load_stop_words(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = [line.strip().lower() for line in file if line.strip()]
    return stop_words

# Function to read text from .txt, .docx, or .pdf files
def read_text_from_file(file_path):

    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        return '\n'.join([page.extract_text() for page in reader.pages])
    else:
        raise ValueError("Unsupported file format. Please use .txt, .docx, or .pdf.")

# Function to find stop words in Uzbek text
def find_stop_words(text):

    words = re.findall(r"\b[\w']+\b", text.lower())
    stop_words_in_text = [word for word in words if word in UZBEK_STOP_WORDS]
    stop_words_in_text = list(set(stop_words_in_text))
    return stop_words_in_text

# Function to remove stop words from Uzbek text
def remove_stop_words(text):

    words = re.findall(r"\b[\w']+\b", text)
    filtered_text = ' '.join(word for word in words if word.lower() not in UZBEK_STOP_WORDS)
    return filtered_text

# Function to find the most and least frequent words
def find_frequent_words(text):

    words = re.findall(r"\b[\w']+\b", text.lower())
    word_counts = Counter(words)

    most_frequent = word_counts.most_common(5)
    least_frequent = word_counts.most_common()[:-6:-1]

    return most_frequent, least_frequent

# Function to write results to output files
def write_results_to_files(original_text, stop_words, edited_text, most_frequent, least_frequent):

    results = {
        "Original text": original_text,
        "Stop words": stop_words,
        "Edited text": edited_text,
        "Most frequent words": most_frequent,
        "Least frequent words": least_frequent
    }

    # Write to output.txt
    with open("output.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write(f"Original text:\n{original_text}\n\n")
        txt_file.write(f"Stop words:\n{', '.join(stop_words)}\n\n")
        txt_file.write(f"Edited text:\n{edited_text}\n\n")
        txt_file.write(f"Most frequent words:\n{most_frequent}\n\n")
        txt_file.write(f"Least frequent words:\n{least_frequent}\n")

    # Write to output.json
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    return "output.txt", "output.json"

# Main function
def main():
    global UZBEK_STOP_WORDS

    print("Enter the path to the stop words file:")
    stop_words_file = "uz.txt"
    UZBEK_STOP_WORDS = load_stop_words(stop_words_file)

    if status_input == True:
        print("Enter the path to the input file (.txt, .docx, .pdf):")
        input_file = input().strip()

        try:
            text = read_text_from_file(input_file)
        except ValueError as e:
            print(e)
            return
    elif status_input == False:
        print("Input text:")
        text = input()


    # Find and display stop words
    stop_words = find_stop_words(text)
    print("\nStop words found:", stop_words)

    # Remove and display text without stop words
    text_without_stop_words = remove_stop_words(text)
    print("\nText without stop words:", text_without_stop_words)

    # Find and display most and least frequent words
    most_frequent, least_frequent = find_frequent_words(text)
    print("\nTop 5 most frequent words:", most_frequent)
    print("Top 5 least frequent words:", least_frequent)

    if status_output == True:
    # Write results to output files
        output_files = write_results_to_files(text, stop_words, text_without_stop_words, most_frequent, least_frequent)
        print("\nResults written to output.txt and output.json.")

if __name__ == "__main__":
    main()
