from fastapi import FastAPI, UploadFile, Form, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from collections import Counter
from docx import Document
from PyPDF2 import PdfReader
import re
import json
import os

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Replace with specific domains if needed.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
    words = re.findall(r"\b[\w‘']+\b", text.lower())
    stop_words_in_text = [word for word in words if word in UZBEK_STOP_WORDS]
    stop_words_in_text = list(set(stop_words_in_text))
    return stop_words_in_text

# Function to remove stop words from Uzbek text
def remove_stop_words(text):
    words = re.findall(r"\b[\w‘']+\b", text)
    filtered_text = ' '.join(word for word in words if word.lower() not in UZBEK_STOP_WORDS)
    return filtered_text

# Function to find the most and least frequent words
def find_frequent_words(text):
    words = re.findall(r"\b[\w‘']+\b", text.lower())
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

    # Write to output.json
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    return "output.json"

# Load stop words from a predefined file
@app.on_event("startup")
def load_stop_words_on_startup():
    global UZBEK_STOP_WORDS
    stop_words_file = "uz.txt"
    if os.path.exists(stop_words_file):
        UZBEK_STOP_WORDS = load_stop_words(stop_words_file)

# Request schema for analysis
class TextAnalysisRequest(BaseModel):
    text: Optional[str] = None
    input_file: Optional[UploadFile] = None
    save_output: bool = False

@app.post("/analyze/")
async def analyze_text(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    save_output: bool = Form(False)
):
    if not text and not file:
        raise HTTPException(status_code=400, detail="Either 'text' or 'file' must be provided.")

    # Read text from file if uploaded
    if file:
        try:
            file_contents = await file.read()
            file_path = f"temp_{file.filename}"
            with open(file_path, "wb") as temp_file:
                temp_file.write(file_contents)
            text = read_text_from_file(file_path)
            os.remove(file_path)  # Cleanup temporary file
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Analyze text
    stop_words = find_stop_words(text)
    text_without_stop_words = remove_stop_words(text)
    most_frequent, least_frequent = find_frequent_words(text)

    result = {
        "Original text": text,
        "Stop words": stop_words,
        "Edited text": text_without_stop_words,
        "Most frequent words": most_frequent,
        "Least frequent words": least_frequent
    }

    if save_output:
        output_file = write_results_to_files(text, stop_words, text_without_stop_words, most_frequent, least_frequent)
        result["Output file"] = output_file

    return result

@app.get("/stop-words/")
def get_stop_words():
    return {"Stop words": UZBEK_STOP_WORDS}
