import React from 'react';
import { Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';

const Navigation = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Cell Annotation Tool
        </Typography>
        <Box>
          <Button
            color="inherit"
            component={Link}
            to="/"
          >
            Home
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/annotate"
          >
            Annotate
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation; 