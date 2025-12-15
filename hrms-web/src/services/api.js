import axios from 'axios';

// Use /api path which nginx will proxy to the backend container
// This way frontend calls /api/* and nginx forwards to http://api:8000/api/*
const API_BASE_URL = '';
const ENVIRONMENT = process.env.REACT_APP_ENVIRONMENT || 'dev';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to log API calls
api.interceptors.request.use(
  (config) => {
    console.log(`📡 [${ENVIRONMENT.toUpperCase()}] API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error(`❌ [${ENVIRONMENT.toUpperCase()}] API Request Error:`, error);
    return Promise.reject(error);
  }
);

// Response interceptor to log responses
api.interceptors.response.use(
  (response) => {
    console.log(`✅ [${ENVIRONMENT.toUpperCase()}] API Response: ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ [${ENVIRONMENT.toUpperCase()}] API Error:`, error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// Employees API
export const employeesAPI = {
  getAll: (params = {}) => api.get('/api/v1/employees/', { params }),
  getById: (id) => api.get(`/api/v1/employees/${id}`),
  create: (data) => api.post('/api/v1/employees/', data),
  update: (id, data) => api.put(`/api/v1/employees/${id}`, data),
  delete: (id) => api.delete(`/api/v1/employees/${id}`),
  getByDepartment: (departmentId) => api.get(`/api/v1/employees/department/${departmentId}/employees`),
};

// Departments API
export const departmentsAPI = {
  getAll: () => api.get('/api/v1/departments/'),
  getById: (id) => api.get(`/api/v1/departments/${id}`),
  create: (data) => api.post('/api/v1/departments/', data),
  update: (id, data) => api.put(`/api/v1/departments/${id}`, data),
  delete: (id) => api.delete(`/api/v1/departments/${id}`),
  getStats: (id) => api.get(`/api/v1/departments/${id}/stats`),
};

// Leaves API
export const leavesAPI = {
  getAll: (params = {}) => api.get('/api/v1/leaves/', { params }),
  getById: (id) => api.get(`/api/v1/leaves/${id}`),
  create: (data) => api.post('/api/v1/leaves/', data),
  update: (id, data) => api.put(`/api/v1/leaves/${id}`, data),
  delete: (id) => api.delete(`/api/v1/leaves/${id}`),
  approve: (id, data) => api.post(`/api/v1/leaves/${id}/approve`, data),
  getEmployeeSummary: (employeeId) => api.get(`/api/v1/leaves/employee/${employeeId}/summary`),
};

export default api;
