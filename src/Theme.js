// src/theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#F2F2F2',
    },
    secondary: {
      main: '#EAE4D5',
    },
    background: {
      default: '#F2F2F2',
      paper: '#DDDDDD',
    },
    text: {
      primary: '#000000',
      secondary: '#555555',
    },
  },
});

export default theme;
