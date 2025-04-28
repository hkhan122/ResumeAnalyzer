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
import json

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
    """Analyze resume using BART model with structured prompting."""
    try:
        logger.info("Sending request to Hugging Face API")
        
        # Create a focused prompt for analysis
        prompt = f"""Analyze this resume and provide structured feedback:

{text}

Provide a detailed analysis in the following format:

OVERALL SCORE (1-10):
[Score and brief justification]

STRENGTHS:
[Key strengths with examples]

AREAS FOR IMPROVEMENT:
[Specific areas needing improvement]

SECTION ANALYSIS:
[Format, Experience, Education, Skills, Projects]

RECOMMENDATIONS:
[Top 3 actionable improvements]

Analysis:"""

        # BART-specific parameters
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,
                "min_length": 200,
                "do_sample": False
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        logger.debug(f"API Response status: {response.status_code}")
        logger.debug(f"API Response content: {response.text}")
        
        if response.status_code == 403:
            logger.error("Authentication failed. Please check your Hugging Face API key.")
            return "Error: Authentication failed. Please check your API key."
            
        if response.status_code != 200:
            logger.warning(f"API Error ({response.status_code}): Falling back to local analysis")
            return perform_local_analysis(text)
            
        # Parse the response
        try:
            result = response.json()[0]["summary_text"]
            
            # Clean up the response if needed
            if not result.strip():
                logger.warning("Empty response received, falling back to local analysis")
                return perform_local_analysis(text)
                
            logger.info("Successfully received analysis from API")
            return result.strip()
            
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing API response: {str(e)}")
            return perform_local_analysis(text)
            
    except Exception as e:
        logger.error(f"Error in API call: {str(e)}")
        return perform_local_analysis(text)

def perform_local_analysis(text):
    """Perform sophisticated local analysis of the resume."""
    try:
        # Define patterns for different sections and metrics
        patterns = {
            'experience': {
                'section': r'(?i)(experience|work history|employment)',
                'metrics': r'(?i)(achieved|increased|reduced|improved|led|managed|developed|implemented)',
                'duration': r'(?i)(years?|months?|present|current)',
                'role': r'(?i)(senior|junior|lead|manager|director|engineer|developer|analyst)'
            },
            'education': {
                'section': r'(?i)(education|academic|degree|university|college)',
                'metrics': r'(?i)(gpa|grade|honors?|dean\'s list|scholarship)',
                'degree': r'(?i)(bachelor|master|phd|doctorate|bs|ms|ph\.d)',
                'field': r'(?i)(computer science|engineering|mathematics|physics|business)'
            },
            'skills': {
                'section': r'(?i)(skills|technical|proficient|expertise)',
                'programming': r'(?i)(python|java|c\+\+|javascript|typescript|ruby|go|rust)',
                'tools': r'(?i)(git|docker|kubernetes|aws|azure|gcp|jenkins)',
                'frameworks': r'(?i)(react|angular|vue|django|flask|spring|node\.js)'
            },
            'projects': {
                'section': r'(?i)(projects|portfolio|work samples)',
                'metrics': r'(?i)(github|repository|demo|implementation|contribution)',
                'impact': r'(?i)(users?|performance|efficiency|scalability|reliability)'
            }
        }

        # Analyze each section
        section_scores = {}
        section_details = {}
        
        for section, section_patterns in patterns.items():
            # Count section presence and content
            section_count = len(re.findall(section_patterns['section'], text))
            content_score = 0
            details = []
            
            # Check for specific metrics and keywords
            for metric, pattern in section_patterns.items():
                if metric != 'section':  # Skip the section pattern itself
                    matches = re.findall(pattern, text)
                    if matches:
                        content_score += len(matches)
                        details.extend(matches)
            
            # Calculate section score (0-10)
            base_score = min(10, section_count * 2)  # Base score for section presence
            content_bonus = min(5, content_score / 2)  # Bonus for detailed content
            section_scores[section] = base_score + content_bonus
            section_details[section] = list(set(details))  # Remove duplicates

        # Calculate overall score
        overall_score = sum(section_scores.values()) / len(section_scores)
        
        # Generate detailed feedback
        feedback = []
        
        # Experience feedback
        exp_score = section_scores['experience']
        exp_details = section_details['experience']
        if exp_score >= 8:
            feedback.append(f"Strong work experience section with {len(exp_details)} specific achievements and metrics.")
        elif exp_score >= 5:
            feedback.append(f"Good work experience section, but could benefit from more specific achievements and metrics.")
        else:
            feedback.append("Work experience section needs more detail about responsibilities and achievements.")
        
        # Education feedback
        edu_score = section_scores['education']
        edu_details = section_details['education']
        if edu_score >= 8:
            feedback.append(f"Comprehensive education section with {len(edu_details)} specific academic details.")
        elif edu_score >= 5:
            feedback.append("Education section is present but could include more details like GPA or coursework.")
        else:
            feedback.append("Education section needs more details about your academic background.")
        
        # Skills feedback
        skills_score = section_scores['skills']
        skills_details = section_details['skills']
        if skills_score >= 8:
            feedback.append(f"Well-organized skills section with {len(skills_details)} specific technical competencies.")
        elif skills_score >= 5:
            feedback.append("Skills section is present but could be more specific about technical abilities.")
        else:
            feedback.append("Skills section needs more specific technical skills and tools.")
        
        # Projects feedback
        proj_score = section_scores['projects']
        proj_details = section_details['projects']
        if proj_score >= 8:
            feedback.append(f"Strong projects section with {len(proj_details)} specific demonstrations of your work.")
        elif proj_score >= 5:
            feedback.append("Projects section is present but could include more details about your contributions.")
        else:
            feedback.append("Projects section needs more details about your role and contributions.")
        
        # Generate specific recommendations based on analysis
        recommendations = []
        
        # Experience recommendations
        if exp_score < 8:
            if len(exp_details) < 3:
                recommendations.append("Enhance work experience with specific achievements like: 'Led team of 5 developers to complete project 2 weeks ahead of schedule', 'Implemented automation that reduced processing time by 60%', 'Increased customer satisfaction scores from 75% to 92%'")
            if not any('led' in detail.lower() or 'managed' in detail.lower() for detail in exp_details):
                recommendations.append("Showcase leadership by adding: 'Managed cross-functional team of 8 members', 'Led daily standups and sprint planning', 'Mentored 3 junior developers'")
            if not any('metric' in detail.lower() or '%' in detail or '$' in detail for detail in exp_details):
                recommendations.append("Add quantifiable metrics: 'Reduced server costs by $15K annually', 'Improved application performance by 45%', 'Increased user engagement by 30%'")
        
        # Education recommendations
        if edu_score < 8:
            if not any('gpa' in detail.lower() for detail in edu_details):
                recommendations.append("Include academic achievements: 'GPA: 3.8/4.0', 'Dean's List 2020-2022', 'Summa Cum Laude'")
            if len(edu_details) < 2:
                recommendations.append("Add academic highlights: 'Relevant Coursework: Data Structures, Algorithms, Machine Learning', 'Senior Project: Developed AI-powered resume analyzer', 'Research Assistant: Published paper on NLP techniques'")
            if not any('honor' in detail.lower() or 'scholarship' in detail.lower() for detail in edu_details):
                recommendations.append("Highlight academic recognition: 'Recipient of Computer Science Excellence Scholarship', 'National Merit Scholar', 'Departmental Honors'")
        
        # Skills recommendations
        if skills_score < 8:
            if len(skills_details) < 5:
                recommendations.append("Expand technical skills with specific examples: 'Programming: Python (5+ years), Java, JavaScript', 'Cloud: AWS (EC2, S3, Lambda), Azure', 'DevOps: Docker, Kubernetes, Jenkins'")
            if not any('framework' in detail.lower() for detail in skills_details):
                recommendations.append("Add framework expertise: 'Web: React, Angular, Vue.js', 'Backend: Django, Flask, Spring Boot', 'Mobile: React Native, Flutter'")
            if not any('tool' in detail.lower() or 'platform' in detail.lower() for detail in skills_details):
                recommendations.append("Include development tools: 'Version Control: Git, GitHub, Bitbucket', 'CI/CD: Jenkins, GitHub Actions', 'Testing: JUnit, Selenium, PyTest'")
        
        # Projects recommendations
        if proj_score < 8:
            if len(proj_details) < 2:
                recommendations.append("Add detailed project descriptions: 'Developed full-stack e-commerce platform using React and Node.js', 'Built machine learning model for fraud detection with 95% accuracy', 'Created automated testing framework reducing QA time by 50%'")
            if not any('impact' in detail.lower() for detail in proj_details):
                recommendations.append("Showcase project impact: 'Deployed to production serving 10K+ users', 'Reduced server response time from 2s to 200ms', 'Implemented features increasing user retention by 25%'")
            if not any('contribution' in detail.lower() or 'role' in detail.lower() for detail in proj_details):
                recommendations.append("Highlight your role: 'Led backend development and database optimization', 'Implemented RESTful API endpoints', 'Designed and developed user authentication system'")
        
        # Format the response
        response = f"""Score: {overall_score:.1f}/10

Detailed Analysis:
{chr(10).join(f'- {item}' for item in feedback)}

Section Scores:
- Experience: {section_scores['experience']:.1f}/10
- Education: {section_scores['education']:.1f}/10
- Skills: {section_scores['skills']:.1f}/10
- Projects: {section_scores['projects']:.1f}/10

Recommendations:
{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations[:5]))}

Additional Tips:
- Use action verbs: 'Led', 'Developed', 'Implemented', 'Optimized', 'Designed'
- Include specific numbers and metrics whenever possible
- Focus on results and impact rather than just responsibilities
- Tailor content to the job you're applying for
- Keep descriptions concise but informative"""
        
        return response
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