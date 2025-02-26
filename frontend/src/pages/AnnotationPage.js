import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Paper, Typography, Box } from '@mui/material';
import AnnotationTool from '../components/AnnotationTool/AnnotationTool';

const AnnotationPage = () => {
  const { imageId } = useParams();
  const [imageData, setImageData] = useState(null);

  useEffect(() => {
    // TODO: 如果有 imageId，從後端加載圖像數據
    if (imageId) {
      console.log('Loading image:', imageId);
    }
  }, [imageId]);

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h5" gutterBottom>
          Image Annotation
          {imageId && ` - Image ID: ${imageId}`}
        </Typography>
        
        <Box sx={{ mt: 2 }}>
          {!imageId ? (
            <Typography color="text.secondary">
              Please upload an image from the home page to start annotation.
            </Typography>
          ) : (
            <AnnotationTool imageId={imageId} />
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default AnnotationPage; 