import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const ImageUpload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('cellpose');
  const [availableModels, setAvailableModels] = useState([
    { id: 'cellpose', name: 'Cellpose' }
  ]);
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  // 獲取可用的模型列表
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/models');
        setAvailableModels(response.data.models);
      } catch (error) {
        console.error('Error fetching models:', error);
      }
    };
    fetchModels();
  }, []);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);

    console.log('Selected files:', files);  // 調試信息

    // 生成預覽
    const newPreviews = await Promise.all(files.map(async (file) => {
      const fileExtension = file.name.split('.').pop().toLowerCase();
      console.log(`Processing file: ${file.name}`);  // 調試信息
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('Sending preview request...');  // 調試信息
        const response = await axios.post('http://localhost:8000/api/preview', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        console.log('Preview response:', response.data);  // 調試信息
        
        if (response.data.success) {
          return {
            file,
            name: file.name,  // 修正這裡：使用 file.name 而不是 file.filename
            channels: response.data.previews,
            shape: response.data.shape
          };
        }
      } catch (error) {
        console.error('Preview generation failed:', error);
      }
      
      // 如果預覽生成失敗，返回基本信息
      return {
        file,
        name: file.name,
        channels: []
      };
    }));

    console.log('New previews:', newPreviews);  // 調試信息
    setPreviews(newPreviews);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select files first!');
      return;
    }

    setUploading(true);
    try {
      const newResults = [];  // 存儲新的結果
      
      for (const file of selectedFiles) {
        console.log(`Uploading file: ${file.name}`);
        const formData = new FormData();
        formData.append('file', file);

        try {
          const response = await axios.post(
            `http://localhost:8000/api/upload?model_type=${selectedModel}`,
            formData,
            {
              headers: {
                'Content-Type': 'multipart/form-data',
              },
            }
          );

          console.log('Server response:', response.data);

          if (response.data.success) {
            newResults.push({
              filename: file.name,
              ...response.data.prediction
            });
          } else {
            throw new Error(response.data.error || 'Upload failed');
          }
        } catch (error) {
          console.error('Error processing file:', file.name, error);
          alert(`Error processing ${file.name}: ${error.message}`);
        }
      }
      
      setResults(newResults);  // 更新結果
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  // 清理預覽 URL
  React.useEffect(() => {
    return () => {
      // 不需要清理，因為使用的是 base64 數據
    };
  }, [previews]);

  return (
    <Card>
      <CardContent>
        <Box sx={{ textAlign: 'center', p: 3 }}>
          {/* 模型選擇下拉框 */}
          <FormControl sx={{ m: 1, minWidth: 200 }}>
            <InputLabel>Select Model</InputLabel>
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              label="Select Model"
            >
              {availableModels.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* 文件上傳按鈕 */}
          <input
            accept=".tif,.tiff,.npy"
            style={{ display: 'none' }}
            id="raised-button-file"
            multiple
            type="file"
            onChange={handleFileSelect}
          />
          <label htmlFor="raised-button-file">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              sx={{ mb: 2, ml: 2 }}
            >
              Select Files
            </Button>
          </label>
          
          {previews.length > 0 && (
            <Grid container spacing={2} sx={{ mt: 2 }}>
              {previews.map((preview, fileIndex) => (
                <Grid item xs={12} key={fileIndex}>
                  <Paper elevation={3} sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      {preview.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Shape: {preview.shape?.join(' × ')}
                    </Typography>
                    <Grid container spacing={2}>
                      {preview.channels.map((channel, channelIndex) => (
                        <Grid item xs={12} sm={6} key={channelIndex}>
                          <Paper variant="outlined" sx={{ p: 1 }}>
                            <Typography variant="subtitle2" gutterBottom>
                              Channel {channel.channel}
                            </Typography>
                            <Box
                              sx={{
                                width: '100%',
                                paddingTop: '100%',
                                position: 'relative',
                                overflow: 'hidden',
                                borderRadius: 1,
                                bgcolor: '#f5f5f5'
                              }}
                            >
                              <img
                                src={channel.preview}
                                alt={`Channel ${channel.channel}`}
                                style={{
                                  position: 'absolute',
                                  top: 0,
                                  left: 0,
                                  width: '100%',
                                  height: '100%',
                                  objectFit: 'contain'
                                }}
                              />
                            </Box>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}

          {previews.length > 0 && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={uploading}
              sx={{ mt: 2 }}
            >
              {uploading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Upload and Process'
              )}
            </Button>
          )}
        </Box>

        {/* 結果顯示部分 */}
        {results.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Results
            </Typography>
            <Grid container spacing={2}>
              {results.map((result, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {result.filename}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Model: {result.model_name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Cells Detected: {result.num_cells}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Processing Time: {result.processing_time}
                      </Typography>
                      {result.mask_preview && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Segmentation Result:
                          </Typography>
                          <Box
                            sx={{
                              width: '100%',
                              paddingTop: '100%',
                              position: 'relative',
                              overflow: 'hidden',
                              borderRadius: 1,
                              bgcolor: '#f5f5f5'
                            }}
                          >
                            <img
                              src={result.mask_preview}
                              alt="Segmentation Result"
                              style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                                objectFit: 'contain'
                              }}
                            />
                          </Box>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ImageUpload; 