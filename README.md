# Resume Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful resume analysis tool that provides detailed feedback on your resume using advanced AI models. The analyzer evaluates various aspects of your resume and provides actionable recommendations for improvement.

## Features

- **Modern Web Interface**:
  - Clean, responsive design
  - Drag-and-drop file upload
  - Real-time analysis feedback
  - Interactive score display
  - Mobile-friendly layout

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
- **Professional Formatting**: Clean, well-structured output with clear section separation

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Mistral.ai API key

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

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
MISTRAL_API_KEY=your_mistral_api_key
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Access the web interface at `http://localhost:5000`

3. Upload your resume:
   - Drag and drop your file into the upload area, or
   - Click to browse and select your file
   - Supported formats: PDF, DOCX, TXT

4. View your analysis:
   - Overall score with visual display
   - Section-by-section breakdown
   - Detailed strengths and areas for improvement
   - Actionable recommendations

## Project Structure

```
ResumeAnalyzer/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── templates/         # HTML templates
│   └── index.html     # Modern web interface
├── instance/          # Uploaded files storage
└── README.md         # Project documentation
```

## User Interface Features

### Upload Experience
- Drag-and-drop file upload
- File type validation
- Visual feedback during upload
- Clear error messages

### Analysis Display
- Prominent overall score
- Section-specific scores
- Expandable analysis sections
- Formatted lists for easy reading
- Responsive design for all devices

### Interactive Elements
- Hover effects on interactive elements
- Loading animations during analysis
- Clear section separation
- Easy-to-read typography

## Analysis Features

### Experience Analysis
- Evaluates work history presentation
- Checks for quantifiable achievements
- Assesses leadership and management experience
- Provides specific improvement suggestions
- Scores based on content quality and impact

### Education Analysis
- Reviews academic background presentation
- Checks for relevant coursework and projects
- Evaluates academic achievements
- Suggests enhancements for academic section
- Considers degree relevance and timeline

### Skills Analysis
- Assesses technical skills presentation
- Evaluates tool and framework proficiency
- Checks for relevant certifications
- Provides suggestions for skills enhancement
- Analyzes skill depth and breadth

### Projects Analysis
- Reviews project descriptions
- Evaluates impact and results
- Checks for specific contributions
- Suggests improvements for project presentation
- Assesses technical complexity

## Response Format

The analyzer provides feedback in a modern, visually appealing format:

```
Score: X.X/10

DETAILED ANALYSIS
==================================================

EXPERIENCE SECTION
--------------------------------------------------
Score: X/10

Strengths:
- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

Areas for Improvement:
- [Area for improvement 1]
- [Area for improvement 2]
- [Area for improvement 3]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

EDUCATION SECTION
--------------------------------------------------
Score: X/10

Strengths:
- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

Areas for Improvement:
- [Area for improvement 1]
- [Area for improvement 2]
- [Area for improvement 3]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

SKILLS SECTION
--------------------------------------------------
Score: X/10

Strengths:
- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

Areas for Improvement:
- [Area for improvement 1]
- [Area for improvement 2]
- [Area for improvement 3]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

PROJECTS SECTION
--------------------------------------------------
Score: X/10

Strengths:
- [Specific strength 1]
- [Specific strength 2]
- [Specific strength 3]

Areas for Improvement:
- [Area for improvement 1]
- [Area for improvement 2]
- [Area for improvement 3]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]
```

The analysis is displayed in a clean, modern interface with:
- A prominent overall score at the top
- Clear section separation with visual dividers
- Consistent formatting across all sections
- Easy-to-read bullet points
- Responsive layout that works on all devices

## Scoring System

- Each section is scored on a scale of 1-10
- Scores are based on:
  - Content quality and relevance
  - Achievement quantification
  - Professional presentation
  - Technical depth
  - Impact demonstration
- Overall score is calculated as an average of section scores
- Detailed feedback explains the scoring rationale

## Error Handling

The system includes robust error handling:
- Graceful fallback to local analysis if API is unavailable
- Section-specific error handling
- Clear error messages for common issues
- Automatic retry mechanisms
- Score extraction from multiple formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 