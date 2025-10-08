import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
} from '@mui/material';
import {
  MenuBook,
  Home,
  List,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <AppBar position="sticky" elevation={2}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <MenuBook />
        </IconButton>
        
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
          onClick={() => handleNavigation('/')}
        >
          龙族Ⅰ火之晨曦
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => handleNavigation('/')}
            sx={{
              backgroundColor: isActive('/') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            首页
          </Button>
          
          <Button
            color="inherit"
            startIcon={<List />}
            onClick={() => handleNavigation('/chapters')}
            sx={{
              backgroundColor: isActive('/chapters') ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            章节列表
          </Button>
          
          <IconButton color="inherit" aria-label="settings">
            <Settings />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
