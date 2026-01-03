import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Projects from './Projects';
import Periods from './Periods';
import PeriodWorkArea from './PeriodWorkArea';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0a0a0c',
      paper: '#16161a',
    },
    text: {
      primary: '#e0e0e0',
      secondary: '#888',
    },
    primary: {
      main: '#00f3ff',
    },
    secondary: {
      main: '#bc13fe',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#16161a',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div style={{ background: '#0a0a0c', minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<Projects />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:projectId/periods" element={<Periods />} />
            <Route path="/projects/:projectId/periods/:periodId" element={<PeriodWorkArea />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
