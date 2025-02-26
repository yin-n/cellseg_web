import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadImage = (formData) => {
  return api.post('/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const saveAnnotation = (imageId, annotationData) => {
  return api.post(`/save-annotation/${imageId}`, annotationData);
};

export const getImageData = (imageId) => {
  return api.get(`/image/${imageId}`);
}; 