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

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      setAnalysis(response.data.analysis);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while analyzing the resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
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

          {analysis && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" gutterBottom>
                Analysis Results
              </Typography>
              <Paper elevation={2} sx={{ p: 3, bgcolor: '#f5f5f5' }}>
                <Typography variant="body1" style={{ whiteSpace: 'pre-line' }}>
                  {analysis}
                </Typography>
              </Paper>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
}

export default App; 