import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ChapterListPage from './pages/ChapterListPage';
import ChapterReaderPage from './pages/ChapterReaderPage';

function App() {
  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chapters" element={<ChapterListPage />} />
        <Route path="/chapter/:id" element={<ChapterReaderPage />} />
      </Routes>
    </Box>
  );
}

export default App;
