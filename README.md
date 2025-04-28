# Resume Analyzer

A web application that uses AI to analyze and rate resumes on a scale of 1-10, providing constructive feedback.

## Features

- Upload resumes in PDF, DOCX, or TXT format
- AI-powered resume analysis and scoring using Hugging Face's BART model
- Local analysis fallback when AI service is unavailable
- Clean, modern user interface
- Detailed feedback and suggestions
- Robust PDF text extraction
- Automatic encoding detection for text files

## Tech Stack

- Frontend: React.js with Material-UI
- Backend: Flask (Python)
- AI: Hugging Face BART model
- PDF Processing: PyPDF2
- File Parsing: textract with encoding detection

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Hugging Face API key:
```
HF_API_KEY=your_hugging_face_api_key_here
```

4. Run the Flask server:
```bash
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Click "Select Resume" to choose a PDF, DOCX, or TXT file
3. Click "Analyze Resume" to get your resume analysis
4. View your score and feedback

## Features in Detail

### Resume Analysis
- AI-powered analysis using Hugging Face's BART model
- Local analysis fallback when AI service is unavailable
- Section detection (Experience, Education, Skills, Projects)
- Content-based scoring system

### File Processing
- Robust PDF text extraction using PyPDF2
- Support for DOCX and TXT files
- Automatic encoding detection for text files
- Error handling and logging

## Note

Make sure both the backend (Flask) and frontend (React) servers are running simultaneously for the application to work properly.

## Troubleshooting

If you encounter issues with PDF extraction:
1. Ensure the PDF is not password-protected
2. For scanned PDFs, consider using OCR software to convert to text first
3. Check the logs for specific error messages

If the AI analysis service is unavailable:
- The system will automatically fall back to local analysis
- Local analysis provides basic scoring and section detection
- Try again later when the AI service is available 