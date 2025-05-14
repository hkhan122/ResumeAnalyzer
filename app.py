import os
from flask import Flask, request, jsonify, render_template
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

# Configure Mistral.ai
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
API_URL = "https://api.mistral.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

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
    """Analyze resume using Mistral-7B-Instruct-v0.3 with chunked processing."""
    try:
        logger.info("Preprocessing text for analysis")
        
        # Clean and normalize the text
        text = text.strip()
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
        
        # Split text into sections based on common resume headers
        sections = {
            'experience': extract_section(text, r'(?i)(experience|work history|employment)'),
            'education': extract_section(text, r'(?i)(education|academic|degree)'),
            'skills': extract_section(text, r'(?i)(skills|technical|proficient)'),
            'projects': extract_section(text, r'(?i)(projects|portfolio|work samples)')
        }
        
        # Analyze each section
        section_analyses = {}
        for section_name, section_text in sections.items():
            if section_text:
                section_analyses[section_name] = analyze_section(section_name, section_text)
        
        # Combine analyses
        combined_analysis = combine_analyses(section_analyses)
        
        logger.info("Successfully analyzed resume")
        return combined_analysis
            
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        return perform_local_analysis(text)

def extract_section(text, pattern):
    """Extract a specific section from the resume text."""
    try:
        # Find the section header
        match = re.search(pattern, text)
        if not match:
            return None
            
        start_idx = match.start()
        # Find the next section or end of text
        next_section = re.search(r'(?i)(experience|work history|employment|education|academic|degree|skills|technical|proficient|projects|portfolio|work samples)', text[start_idx + 1:])
        
        if next_section:
            end_idx = start_idx + 1 + next_section.start()
        else:
            end_idx = len(text)
            
        return text[start_idx:end_idx].strip()
    except Exception as e:
        logger.error(f"Error extracting section: {str(e)}")
        return None

def analyze_section(section_name, text):
    """Analyze a specific section of the resume."""
    try:
        prompt = f"""<s>[INST] You are a professional resume analyst. Analyze this {section_name} section and provide feedback in this exact format:

SECTION:
{text}

ANALYSIS:
Score (1-10): [number]
Strengths: [2-3 specific points]
Areas for Improvement: [2-3 specific points]
Recommendations: [2-3 specific recommendations]

Do not summarize the section. Only provide analysis and feedback.[/INST]"""

        payload = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 300,
            "top_p": 0.9
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return None
            
        result = response.json()["choices"][0]["message"]["content"]
        return result.strip()
        
    except Exception as e:
        logger.error(f"Error analyzing section: {str(e)}")
        return None

# def combine_analyses(section_analyses):
#     """Combine analyses from different sections into a cohesive report."""
#     try:
#         # Calculate overall score
#         scores = []
#         for analysis in section_analyses.values():
#             if analysis:
#                 # Try different score patterns
#                 score_match = (
#                     re.search(r'Score \(1-10\): (\d+)', analysis) or  # Pattern 1
#                     re.search(r'SCORE: (\d+)', analysis) or           # Pattern 2
#                     re.search(r'Score: (\d+)', analysis)              # Pattern 3
#                 )
#                 if score_match:
#                     scores.append(float(score_match.group(1)))
        
#         overall_score = sum(scores) / len(scores) if scores else 0
        
#         # Format the combined analysis
#         combined = f"""Score: {overall_score:.1f}/10

# DETAILED ANALYSIS
# {'=' * 50}"""

#         # Add each section's analysis with improved formatting
#         for section_name, analysis in section_analyses.items():
#             if analysis:
#                 # Extract score using multiple patterns
#                 score_match = (
#                     re.search(r'Score \(1-10\): (\d+)', analysis) or  # Pattern 1
#                     re.search(r'SCORE: (\d+)', analysis) or           # Pattern 2
#                     re.search(r'Score: (\d+)', analysis)              # Pattern 3
#                 )
#                 section_score = score_match.group(1) if score_match else "N/A"
                
#                 # Extract strengths
#                 strengths_match = re.search(r'Strengths:(.*?)(?=Areas for Improvement:|$)', analysis, re.DOTALL)
#                 strengths = strengths_match.group(1).strip() if strengths_match else "No strengths identified"
                
#                 # Extract areas for improvement
#                 improvements_match = re.search(r'Areas for Improvement:(.*?)(?=Recommendations:|$)', analysis, re.DOTALL)
#                 improvements = improvements_match.group(1).strip() if improvements_match else "No areas for improvement identified"
                
#                 # Extract recommendations
#                 recommendations_match = re.search(r'Recommendations:(.*?)$', analysis, re.DOTALL)
#                 recommendations = recommendations_match.group(1).strip() if recommendations_match else "No recommendations provided"
                
#                 # Format section
#                 combined += f"""

# {section_name.upper()} SECTION
# {'-' * 50}
# Score: {section_score}/10

# Strengths:
# {strengths}

# Areas for Improvement:
# {improvements}

# Recommendations:
# {recommendations}
# """
        
#         return combined
        
#     except Exception as e:
#         logger.error(f"Error combining analyses: {str(e)}")
#         return "Error combining analyses. Please try again."

def combine_analyses(section_analyses):
    """Combine analyses from different sections into structured JSON."""
    try:
        scores = []
        parsed_sections = {}

        for section_name, analysis in section_analyses.items():
            if analysis:
                # Extract score
                score_match = (
                    re.search(r'Score \(1-10\): (\d+)', analysis) or
                    re.search(r'SCORE: (\d+)', analysis) or
                    re.search(r'Score: (\d+)', analysis)
                )
                score = int(score_match.group(1)) if score_match else None
                if score:
                    scores.append(score)

                # Extract parts
                strengths = re.search(r'Strengths:(.*?)(?=Areas for Improvement:|$)', analysis, re.DOTALL)
                improvements = re.search(r'Areas for Improvement:(.*?)(?=Recommendations:|$)', analysis, re.DOTALL)
                recommendations = re.search(r'Recommendations:(.*?)$', analysis, re.DOTALL)

                parsed_sections[section_name] = {
                    "score": score,
                    "strengths": strengths.group(1).strip() if strengths else "",
                    "improvements": improvements.group(1).strip() if improvements else "",
                    "recommendations": recommendations.group(1).strip() if recommendations else ""
                }

        overall_score = sum(scores) / len(scores) if scores else 0

        return {
            "overall_score": round(overall_score, 1),
            "sections": parsed_sections
        }

    except Exception as e:
        logger.error(f"Error combining analyses: {str(e)}")
        return {
            "overall_score": 0,
            "sections": {}
        }


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

@app.route('/')
def index():
    return render_template('index.html')

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
        print("=== Data Sent to Frontend ===")
        print(analysis) 

        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'error': 'Failed to process the file. Please make sure it is a valid PDF, DOCX, or TXT file and try again.'
        }), 400

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True) 