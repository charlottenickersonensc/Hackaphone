import React from 'react';
import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MusicNoteIcon from '@mui/icons-material/MusicNote';

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <MusicNoteIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Hackaphone Visualisations
        </Typography>
        <Box>
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/"
          >
            Accueil
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;