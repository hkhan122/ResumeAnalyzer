import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Button, 
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Analyzer() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const nav = useNavigate();

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setAnalysis(null);
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while analyzing the resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Button variant='contained' color='secondary' onClick={() => nav('/')} sx={{ mb : 2 }}>
        Return Home
      </Button>
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Resume Analyzer
        </Typography>
        
        <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                id="resume-upload"
              />
              <label htmlFor="resume-upload">
                <Button
                  variant="contained"
                  component="span"
                  fullWidth
                >
                  Select Resume (PDF, DOCX, or TXT)
                </Button>
              </label>
              
              {file && (
                <Typography variant="body1">
                  Selected file: {file.name}
                </Typography>
              )}
              
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={!file || loading}
                fullWidth
              >
                {loading ? 'Analyzing...' : 'Analyze Resume'}
              </Button>
            </Box>
          </form>

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
          {analysis?.sections && Object.entries(analysis.sections).map(([section, content]) => (
            <Paper key={section} elevation={1} sx={{ mb: 4, bgcolor: '#f9f9f9', p: 2 }}>
              <Typography variant="h5" gutterBottom>{section.toUpperCase()} SECTION</Typography>
              <Typography variant="subtitle1">Score: {content.score}/10</Typography>
              
              <Typography variant="subtitle2" sx={{ mt: 2 }}>Strengths:</Typography>
              <Typography variant="body2">{content.strengths}</Typography>

              <Typography variant="subtitle2" sx={{ mt: 2 }}>Areas for Improvement:</Typography>
              <Typography variant="body2">{content.improvements}</Typography>

              <Typography variant="subtitle2" sx={{ mt: 2 }}>Recommendations:</Typography>
              <Typography variant="body2">{content.recommendations}</Typography>
            </Paper>
          ))}
        </Paper>
      </Box>
    </Container>
  );
}

export default Analyzer; 