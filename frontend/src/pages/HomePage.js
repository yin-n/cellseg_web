import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import ImageUpload from '../components/ImageUpload/ImageUpload';

const HomePage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cell Image Annotation
        </Typography>
        <Typography variant="body1" paragraph>
          Upload your cell images for annotation and AI-assisted segmentation.
        </Typography>
        <ImageUpload />
      </Box>
    </Container>
  );
};

export default HomePage; 