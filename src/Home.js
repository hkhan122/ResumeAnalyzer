import React, { useEffect, useState } from "react";
import {
    Box,
    Container,
    Typography,
    Paper,
    Button,
    List,
    ListItem,
    ListItemText
} from "@mui/material"
import { Link } from "react-router-dom";
import axios from "axios";

function HomePage() {
    const [files, setFiles] = useState([]);
  
    useEffect(() => {
      axios.get('http://localhost:5000/api/resumes')
        .then(res => setFiles(res.data.files))
        .catch(err => console.error("Failed to fetch resumes", err));
    }, []);
  
    return (
      <Container maxWidth="md">
        <Typography variant="h3" gutterBottom align="center">Welcome to RateMyResume</Typography>
  
        <Paper sx={{ my: 4 }}>
          {files.length === 0 ? (
            <Typography>No resumes uploaded yet.</Typography>
          ) : (
            <List>
              {files.map((file, idx) => (
                <ListItem key={idx} divider>
                  <ListItemText primary={file} />
                  <Button
                    href={`http://localhost:5000/api/download/${file}`}
                    target="_blank"
                    rel="noreferrer"
                    variant="outlined"
                  >
                    Download
                  </Button>
                </ListItem>
              ))}
            </List>
          )}
          <Box mt={4} textAlign="center">
            <Button variant="contained" component={Link} to="/analyze">
              Upload and Analyze a Resume
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }
  
  export default HomePage;