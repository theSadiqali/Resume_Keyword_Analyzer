from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import docx
import PyPDF2
import json
import os

app = FastAPI(title="Resume Keyword Analyzer")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Base directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve frontend files
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Load keyword list
KEYWORDS_FILE = os.path.join(BASE_DIR, "../../keywords.json")
with open(KEYWORDS_FILE, "r") as f:
    KEYWORDS = json.load(f)["Data Analyst"]

# Function to extract text from PDF or DOCX
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    else:
        return None

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    text = extract_text(file)
    if not text:
        return {"error": "File format not supported. Upload PDF or DOCX."}

    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    score = round(len(matched_keywords) / len(KEYWORDS) * 100, 2)

    return {
        "filename": file.filename,
        "score": score,
        "matched_keywords": matched_keywords
    }
