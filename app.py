import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import textract
import tempfile

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'instance/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_file(file_path):
    """Extract text from various file formats."""
    try:
        text = textract.process(file_path).decode('utf-8')
        return text
    except Exception as e:
        return str(e)

def analyze_resume(text):
    """Analyze resume using OpenAI GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer. Analyze the resume and provide a score from 1-10 and constructive feedback."},
                {"role": "user", "content": f"Please analyze this resume and provide:\n1. A score from 1-10\n2. Brief feedback (2-3 sentences)\n\nResume content:\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        text = extract_text_from_file(temp_file.name)
        os.unlink(temp_file.name)  # Clean up the temporary file

    if not text:
        return jsonify({'error': 'Could not extract text from file'}), 400

    analysis = analyze_resume(text)
    return jsonify({'analysis': analysis})

if __name__ == '__main__':
    app.run(debug=True) 