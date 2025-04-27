# Resume Analyzer

A web application that uses AI to analyze and rate resumes on a scale of 1-10, providing constructive feedback.

## Features

- Upload resumes in PDF, DOCX, or TXT format
- AI-powered resume analysis and scoring
- Clean, modern user interface
- Detailed feedback and suggestions

## Tech Stack

- Frontend: React.js with Material-UI
- Backend: Flask (Python)
- AI: OpenAI GPT-4
- File Parsing: textract

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

3. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
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

## Note

Make sure both the backend (Flask) and frontend (React) servers are running simultaneously for the application to work properly. 