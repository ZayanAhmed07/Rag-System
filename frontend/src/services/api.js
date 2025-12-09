import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message;
    return Promise.reject(new Error(message));
  }
);

// Query Service
export const queryService = {
  query: (queryText, options = {}) =>
    client.post('/query', { query: queryText, ...options }),

  streamQuery: async function* (queryText, options = {}) {
    const response = await fetch(`${API_BASE_URL}/query/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: queryText, ...options }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value);
      }
    } finally {
      reader.releaseLock();
    }
  },

  getStats: () => client.get('/stats'),
};

// Ingest Service
export const ingestService = {
  uploadDocument: (file, documentType = 'pdf') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    return client.post('/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getDocuments: (skip = 0, limit = 10) =>
    client.get(`/documents?skip=${skip}&limit=${limit}`),

  deleteDocument: (documentId) =>
    client.delete(`/documents/${documentId}`),

  searchDocuments: (query) =>
    client.get(`/documents/search?q=${query}`),
};

// Evaluation Service
export const evaluationService = {
  evaluate: (queryText, response, groundTruth, retrievedDocs = []) =>
    client.post('/evaluate', {
      query: queryText,
      response,
      ground_truth: groundTruth,
      retrieved_docs: retrievedDocs,
    }),

  getEvaluationResults: (skip = 0, limit = 10) =>
    client.get(`/evaluation/results?skip=${skip}&limit=${limit}`),

  getMetrics: () => client.get('/evaluation/metrics'),
};

// Settings Service
export const settingsService = {
  getSettings: () => client.get('/settings'),

  updateSettings: (settings) =>
    client.put('/settings', settings),

  getSystemInfo: () => client.get('/system/info'),
};

export default client;
