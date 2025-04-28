# Resume Analyzer

A powerful resume analysis tool that provides detailed feedback on your resume using advanced AI models. The analyzer evaluates various aspects of your resume and provides actionable recommendations for improvement.

## Features

- **Multi-Format Support**: Upload resumes in PDF, DOCX, or TXT format
- **Comprehensive Analysis**: Detailed evaluation of:
  - Work Experience
  - Education
  - Skills
  - Projects
- **Structured Feedback**: Receive feedback in a clear, organized format including:
  - Overall score (1-10)
  - Section-specific analysis
  - Strengths and areas for improvement
  - Actionable recommendations
- **AI-Powered Analysis**: Utilizes Mistral-7B-Instruct-v0.3 for sophisticated resume analysis
- **Local Fallback**: Includes a robust local analysis system when API is unavailable

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ResumeAnalyzer.git
cd ResumeAnalyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
HF_API_KEY=your_huggingface_api_key
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Access the web interface at `http://localhost:5000`

3. Upload your resume file (PDF, DOCX, or TXT)

4. Receive detailed analysis including:
   - Overall score
   - Section-by-section analysis
   - Specific strengths and areas for improvement
   - Actionable recommendations

## Analysis Features

### Experience Analysis
- Evaluates work history presentation
- Checks for quantifiable achievements
- Assesses leadership and management experience
- Provides specific improvement suggestions

### Education Analysis
- Reviews academic background presentation
- Checks for relevant coursework and projects
- Evaluates academic achievements
- Suggests enhancements for academic section

### Skills Analysis
- Assesses technical skills presentation
- Evaluates tool and framework proficiency
- Checks for relevant certifications
- Provides suggestions for skills enhancement

### Projects Analysis
- Reviews project descriptions
- Evaluates impact and results
- Checks for specific contributions
- Suggests improvements for project presentation

## Response Format

The analyzer provides feedback in the following format:

```
OVERALL SCORE: X.X/10

DETAILED ANALYSIS:
[Section-specific analyses]

FINAL RECOMMENDATIONS:
1. [Specific recommendation]
2. [Specific recommendation]
3. [Specific recommendation]
```

## Error Handling

The system includes robust error handling:
- Graceful fallback to local analysis if API is unavailable
- Section-specific error handling
- Clear error messages for common issues
- Automatic retry mechanisms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 