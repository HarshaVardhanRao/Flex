import axios from 'axios';

// Base URL for API requests
const API_BASE_URL = 'http://localhost:8000';

// Function to get CSRF token from cookies
function getCsrfToken() {
  const name = 'csrftoken';
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for handling cookies/sessions
});

// Add request interceptor to include CSRF token
apiClient.interceptors.request.use(config => {
  // Add CSRF token for non-GET requests
  if (config.method !== 'get') {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  return config;
});

// Add response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle session timeout or unauthorized access
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      // Only redirect for API calls that aren't already auth-related
      const isAuthEndpoint = 
        error.config.url.includes('/login/') ||
        error.config.url.includes('/logout/') || 
        error.config.url.includes('/current-user/');
      
      if (!isAuthEndpoint) {
        console.log('Session expired or unauthorized. Redirecting to login page.');
        // We could trigger a redirect here if needed
      }
    }
    return Promise.reject(error);
  }
);

// API service object with methods for different API endpoints
const ApiService = {  // Authentication
  login: (username, password) => {
    return apiClient.post('/api/login/', { username, password });
  },
    logout: () => {
    // Even if there's an error, we want to proceed with logout
    return apiClient.post('/api/logout/')
      .catch(error => {
        console.warn('Logout API request failed, but proceeding with local logout', error);
        // Return a resolved promise so the logout flow continues
        return Promise.resolve({ data: { message: "Local logout successful" } });
      });
  },
  
  getCurrentUser: () => {
    return apiClient.get('/api/current-user/');
  },
  
  // Student data
  getStudents: () => {
    return apiClient.get('/api/students/');
  },
  
  getStudentDetail: (rollno) => {
    return apiClient.get(`/api/student/${rollno}/`);
  },
  
  // Technologies
  getTechnologies: () => {
    return apiClient.get('/api/technologies/');
  },
  
  // Projects
  getProjects: () => {
    return apiClient.get('/api/projects/');
  },
  
  createProject: (projectData) => {
    // Project data should include title, description, year_and_sem, github_link, status, technologies, contributors
    return apiClient.post('/api/projects/create/', projectData);
  },
  
  // Certificates
  getCertificates: () => {
    return apiClient.get('/api/certificates/');
  },
  
  createCertificate: (certificateData) => {
    // Certificate data should include all required fields
    // If certificate file is included, it needs to be sent as FormData
    const formData = new FormData();
    
    // Add all fields to the FormData
    Object.keys(certificateData).forEach(key => {
      // Handle arrays (like technologies) specially
      if (Array.isArray(certificateData[key])) {
        certificateData[key].forEach(item => {
          formData.append(`${key}`, item);
        });
      } else {
        formData.append(key, certificateData[key]);
      }
    });
    
    return apiClient.post('/api/certificates/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // Generic helper for handling API errors
  handleApiError: (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data);
      return {
        status: error.response.status,
        data: error.response.data,
      };
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API No Response:', error.request);
      return {
        status: 503, // Service Unavailable
        data: { detail: 'No response from server' },
      };
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Request Error:', error.message);
      return {
        status: 500,
        data: { detail: error.message },
      };
    }
  }
};

export default ApiService;
