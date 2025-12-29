from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import docx
import PyPDF2
import json
import os

# -----------------------
# Paths
# -----------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
KEYWORDS_PATH = os.path.join(BASE_DIR, "keywords.json")

# -----------------------
# Load keywords
# -----------------------
with open(KEYWORDS_PATH, "r") as f:
    KEYWORDS = json.load(f)["Data Analyst"]

# -----------------------
# Initialize FastAPI
# -----------------------
app = FastAPI(title="Resume Keyword Analyzer")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -----------------------
# Routes
# -----------------------
@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# -----------------------
# Function to extract text
# -----------------------
def extract_text(file: UploadFile):
    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text
    else:
        return None

# -----------------------
# Analyze Resume
# -----------------------
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
