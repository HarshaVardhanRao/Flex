import axios from "axios";

// Base URL for API requests
const API_BASE_URL = "http://localhost:8000";

// Function to get CSRF token from cookies
function getCsrfToken() {
	const name = "csrftoken";
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
	return null;
}

// Create an axios instance with default config
const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
	withCredentials: true, // Important for handling cookies/sessions
});

// Add request interceptor to include CSRF token
apiClient.interceptors.request.use((config) => {
	// Add CSRF token for non-GET requests
	if (config.method !== "get") {
		const csrfToken = getCsrfToken();
		if (csrfToken) {
			config.headers["X-CSRFToken"] = csrfToken;
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
		if (
			error.response &&
			(error.response.status === 401 || error.response.status === 403)
		) {
			// Only redirect for API calls that aren't already auth-related
			const isAuthEndpoint =
				error.config.url.includes("/login/") ||
				error.config.url.includes("/logout/") ||
				error.config.url.includes("/current-user/");

			if (!isAuthEndpoint) {
				console.log(
					"Session expired or unauthorized. Redirecting to login page."
				);
				// We could trigger a redirect here if needed
			}
		}
		return Promise.reject(error);
	}
);

// API service object with methods for different API endpoints
const ApiService = {
	// Authentication
	login: (username, password) => {
		return apiClient.post("/api/login/", { username, password });
	},

	logout: () => {
		// Even if there's an error, we want to proceed with logout
		return apiClient.post("/api/logout/").catch((error) => {
			console.warn(
				"Logout API request failed, but proceeding with local logout",
				error
			);
			// Return a resolved promise so the logout flow continues
			return Promise.resolve({
				data: { message: "Local logout successful" },
			});
		});
	},

	getCurrentUser: () => {
		return apiClient.get("/api/current-user/");
	},

	// Student data
	getStudents: () => {
		return apiClient.get("/api/students/");
	},

	getStudentDetail: (rollno) => {
		return apiClient.get(`/api/student/${rollno}/`);
	},

	// Technologies
	getTechnologies: () => {
		return apiClient.get("/api/technologies/");
	},

	createTechnology: (techData) => {
		return apiClient.post("/api/technologies/create/", techData);
	},

	// Projects
	getProjects: () => {
		return apiClient.get("/api/projects/");
	},

	// Get a single project by ID
	getProjectById: (id) => {
		return apiClient.get(`/api/projects/${id}/`);
	},

	createProject: (projectData) => {
		// Convert project data to the format expected by the API
		const formData = new FormData();

		// Handle basic fields
		formData.append("name", projectData.name);
		formData.append("description", projectData.description);
		formData.append("year_and_sem", projectData.year_and_sem);
		formData.append("status", projectData.status);

		if (projectData.github_link) {
			formData.append("github_link", projectData.github_link);
		}

		// Handle technologies - existing and new
		if (projectData.technologies) {
			projectData.technologies.forEach((tech) => {
				if (typeof tech === "object" && tech.isNew) {
					// Send new technologies as separate parameter
					formData.append("new_technologies", tech.name);
				} else {
					// Send existing technologies by ID
					formData.append("technologies", tech);
				}
			});
		}

		// Handle contributors - existing and new
		if (projectData.contributors) {
			projectData.contributors.forEach((contributor) => {
				if (typeof contributor === "object" && contributor.isNew) {
					// Send new contributors as separate parameter
					formData.append("new_contributors", contributor.name);
				} else {
					// Send existing contributors by ID
					formData.append("contributors", contributor);
				}
			});
		}

		return apiClient.post("/api/projects/create/", formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
		});
	},
	// Update an existing project
	updateProject: (id, projectData) => {
		// Format data for the edit_project endpoint
		console.log(projectData);
		const formData = new FormData();

		// Handle basic fields
		formData.append("id", id);
		formData.append("name", projectData.name);
		formData.append("description", projectData.description);
		formData.append("year_and_sem", projectData.year_and_sem);
		formData.append("status", projectData.status);

		if (projectData.github_link) {
			formData.append("github_link", projectData.github_link);
		}

		// Handle technologies - existing and new
		if (projectData.technologies) {
			projectData.technologies.forEach((tech) => {
				if (typeof tech === "object" && tech.isNew) {
					// Send new technologies as separate parameter
					formData.append("new_technologies", tech.name);
				} else {
					// Send existing technologies by ID
					formData.append("technologies", tech);
				}
			});
		}

		// Handle contributors - existing and new
		if (projectData.contributors) {
			projectData.contributors.forEach((contributor) => {
				if (typeof contributor === "object" && contributor.isNew) {
					// Send new contributors as separate parameter
					formData.append("new_contributors", contributor.name);
				} else {
					// Send existing contributors by ID
					formData.append("contributors", contributor);
				}
			});
		}

		return apiClient.post("/edit_project", formData, {
			headers: {
				// No Content-Type header to let the browser set it with the boundary parameter for FormData
				Accept: "application/json",
				"X-Requested-With": "XMLHttpRequest",
			},
			withCredentials: true, // Ensure cookies are sent with the request
		});
	},

	deleteProject: (id) => {
		return apiClient.get(`/delete_project/${id}`);
	},

	// Certificates
	getCertificates: () => {
		return apiClient.get("/api/certificates/");
	},

	createCertificate: (certificateData) => {
		// Use the FormData directly, as it's already properly formatted by the component
		return apiClient.post("/api/certificates/create/", certificateData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
		});
	},

	deleteCertificate: (id) => {
		return apiClient.delete(`/delete_certification/${id}`);
	},

	// Generic helper for handling API errors
	handleApiError: (error) => {
		if (error.response) {
			// The request was made and the server responded with a status code
			// that falls out of the range of 2xx
			console.error("API Error Response:", error.response.data);
			return {
				status: error.response.status,
				data: error.response.data,
			};
		} else if (error.request) {
			// The request was made but no response was received
			console.error("API No Response:", error.request);
			return {
				status: 503, // Service Unavailable
				data: { detail: "No response from server" },
			};
		} else {
			// Something happened in setting up the request that triggered an Error
			console.error("API Request Error:", error.message);
			return {
				status: 500,
				data: { detail: error.message },
			};
		}
	},
};

export default ApiService;
