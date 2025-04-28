import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
import requests
import logging
import chardet
import PyPDF2
from io import BytesIO
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Hugging Face
HF_API_KEY = os.getenv('HF_API_KEY')
# Using a more accessible model
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'instance/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(file):
    """Extract text from PDF files."""
    try:
        # Read the file content
        file.seek(0)
        content = file.read()

        # Extract text with PyPDF2
        pdf_file = BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text()
            if page_text:
                text += page_text + "\n\n"

        # Check if we got meaningful text
        if len(text.strip()) < 100:
            logger.warning("Minimal text extracted from PDF - might be scanned")
            # Here you would add OCR handling, but we'll skip for now

        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
            
        return text
    except Exception as e:
        logger.error(f"Error reading PDF: {str(e)}")
        raise

def extract_text_from_file(file):
    """Extract text from various file formats."""
    try:
        logger.info(f"Extracting text from file: {file.filename}")
        
        # Determine file type by extension
        file_name = file.filename.lower()
        
        # Process with appropriate parser based on file type
        if file_name.endswith('.pdf'):
            logger.info("Using PDF-specific extraction")
            return extract_text_from_pdf(file)
        else:
            # For other file types, try textract with encoding detection
            try:
                file.seek(0)
                content = file.read()
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, try to detect encoding
                encoding = chardet.detect(content)['encoding']
                logger.debug(f"Detected encoding: {encoding}")
                text = content.decode(encoding)
        
        if not text.strip():
            raise ValueError("No text could be extracted from the file")
            
        logger.debug(f"Extracted text length: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        raise

def analyze_resume(text):
    """Analyze resume using Hugging Face API with fallback to local analysis."""
    try:
        logger.info("Sending request to Hugging Face API")
        prompt = f"""Please analyze this resume and provide:
1. A score from 1-10
2. Brief feedback (2-3 sentences)

Resume content:
{text}"""

        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        logger.debug(f"API Response status: {response.status_code}")
        
        if response.status_code == 403:
            logger.error("Authentication failed. Please check your Hugging Face API key.")
            return "Error: Authentication failed. Please check your API key."
            
        if response.status_code != 200:
            logger.warning(f"API Error ({response.status_code}): Falling back to local analysis")
            return perform_local_analysis(text)
            
        result = response.json()[0]['summary_text']
        logger.info("Successfully received analysis from API")
        return result
    except Exception as e:
        logger.error(f"Error in API call: {str(e)}")
        return perform_local_analysis(text)

def perform_local_analysis(text):
    """Perform basic local analysis of the resume."""
    try:
        # Count sections and keywords
        sections = {
            'experience': len(re.findall(r'(?i)(experience|work history|employment)', text)),
            'education': len(re.findall(r'(?i)(education|academic|degree)', text)),
            'skills': len(re.findall(r'(?i)(skills|technical|proficient)', text)),
            'projects': len(re.findall(r'(?i)(projects|portfolio|work samples)', text))
        }
        
        # Calculate a basic score based on content
        score = min(10, sum(sections.values()) + 1)
        
        # Generate feedback based on content
        feedback = []
        if sections['experience'] > 0:
            feedback.append("Good job including work experience.")
        if sections['education'] > 0:
            feedback.append("Education section is present.")
        if sections['skills'] > 0:
            feedback.append("Skills section is included.")
        if sections['projects'] > 0:
            feedback.append("Projects or portfolio section is present.")
            
        if not feedback:
            feedback.append("Consider adding more sections to your resume.")
            
        return f"Score: {score}/10\nFeedback: {' '.join(feedback)}"
    except Exception as e:
        logger.error(f"Error in local analysis: {str(e)}")
        return "Unable to analyze resume at this time. Please try again later."

@app.route('/api/analyze', methods=['POST'])
def analyze():
    logger.info("Received analyze request")
    if 'file' not in request.files:
        logger.error("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("Empty filename provided")
        return jsonify({'error': 'No file selected'}), 400

    logger.info(f"Processing file: {file.filename}")
    try:
        text = extract_text_from_file(file)
        analysis = analyze_resume(text)
        logger.info("Analysis complete")
        return jsonify({'analysis': analysis})
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'error': 'Failed to process the file. Please make sure it is a valid PDF, DOCX, or TXT file and try again.'
        }), 400

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True) 