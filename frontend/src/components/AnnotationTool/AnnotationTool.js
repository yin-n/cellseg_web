import React, { useEffect, useRef, useState } from 'react';
import { Box, Button, ButtonGroup } from '@mui/material';
import { Canvas, Polygon } from 'fabric';

const AnnotationTool = ({ imageId }) => {
  const canvasRef = useRef(null);
  const [canvas, setCanvas] = useState(null);
  const [activeShape, setActiveShape] = useState('polygon');

  useEffect(() => {
    // 初始化 canvas
    const fabricCanvas = new Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#f0f0f0'
    });

    setCanvas(fabricCanvas);

    // 清理函數
    return () => {
      fabricCanvas.dispose();
    };
  }, []);

  const addShape = () => {
    if (!canvas) return;

    if (activeShape === 'polygon') {
      const polygon = new Polygon([
        { x: 100, y: 100 },
        { x: 200, y: 100 },
        { x: 200, y: 200 },
        { x: 100, y: 200 }
      ], {
        fill: 'rgba(255, 0, 0, 0.3)',
        stroke: 'red',
        strokeWidth: 2,
        selectable: true,
        hasControls: true
      });
      
      canvas.add(polygon);
      canvas.renderAll();
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <ButtonGroup variant="contained">
        <Button
          onClick={addShape}
          variant={activeShape === 'polygon' ? 'contained' : 'outlined'}
        >
          Add Polygon
        </Button>
      </ButtonGroup>
      
      <Box sx={{ border: '1px solid #ccc' }}>
        <canvas ref={canvasRef} />
      </Box>
    </Box>
  );
};

export default AnnotationTool; 