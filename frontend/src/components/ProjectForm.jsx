import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import ErrorBanner from './ErrorBanner';
import { useAuth } from '../context/AuthContext';

const ProjectForm = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    year_and_sem: '',
    github_link: '',
    status: 'Initialized',
    technologies: [],
    contributors: []
  });
  
  const [technologies, setTechnologies] = useState([]);
  const [students, setStudents] = useState([]);
  const [yearAndSemOptions, setYearAndSemOptions] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Fetch technologies and students for selection
    const fetchData = async () => {
      try {
        // Fetch technologies
        const techResponse = await ApiService.getTechnologies();
        setTechnologies(techResponse.data || []);
        
        // Fetch students for contributors
        const studentsResponse = await ApiService.getStudents();
        setStudents(studentsResponse.data || []);
        
        // If current user is a student, add them to contributors by default
        if (user) {
          setFormData(prev => ({
            ...prev,
            contributors: [user.id]
          }));
        }
      } catch (error) {
        console.error('Error fetching form data:', error);
        setError('Failed to load form data. Please try again later.');
      }
    };
    
    // Set year and semester options
    setYearAndSemOptions([
      "I-I", "I-II", "II-I", "II-II", "III-I", "III-II", "IV-I", "IV-II"
    ]);
    
    fetchData();
  }, [user]);
  
  // Handle change for text inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Handle technology selection with checkboxes
  const handleTechChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setFormData({
        ...formData,
        technologies: [...formData.technologies, value]
      });
    } else {
      setFormData({
        ...formData,
        technologies: formData.technologies.filter(tech => tech !== value)
      });
    }
  };
  
  // Handle contributors selection with checkboxes
  const handleContributorChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setFormData({
        ...formData,
        contributors: [...formData.contributors, value]
      });
    } else {
      // If current user is deselecting themselves, don't allow it
      if (value === user?.id) {
        return;
      }
      setFormData({
        ...formData,
        contributors: formData.contributors.filter(id => id !== value)
      });
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Validate form
      if (!formData.title || !formData.description || !formData.year_and_sem) {
        throw new Error('Please fill all required fields');
      }
      
      // Validate GitHub link format if provided
      if (formData.github_link && !formData.github_link.match(/^https?:\/\/github\.com\/[\w-]+\/[\w.-]+\/?$/)) {
        throw new Error('Please enter a valid GitHub repository URL');
      }
      
      // Ensure at least one contributor is selected
      if (formData.contributors.length === 0) {
        throw new Error('Please select at least one contributor');
      }
      
      // Convert contributors and technologies to integer IDs
      const payload = {
        ...formData,
        contributors: formData.contributors.map(id => parseInt(id)),
        technologies: formData.technologies.map(id => parseInt(id)),
      };
      
      // Submit the form
      const response = await ApiService.createProject(payload);
      
      // Handle success
      alert('Project created successfully!');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.errors || err.message || 'An error occurred while submitting the form');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-3xl mx-auto">
      <h2 className="text-2xl font-semibold mb-6">Create New Project</h2>
      
      {error && <ErrorBanner message={error} />}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Project Title *</label>
          <input 
            type="text" 
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Project Title"
            required
          />
        </div>
        
        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Description *</label>
          <textarea 
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Provide a detailed description of your project"
            required
          />
        </div>
        
        {/* Year and Semester */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Year and Semester *</label>
          <select 
            name="year_and_sem"
            value={formData.year_and_sem}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            required
          >
            <option value="">Select Year & Semester</option>
            {yearAndSemOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        
        {/* GitHub Link */}
        <div>
          <label className="block text-sm font-medium text-gray-700">GitHub Repository</label>
          <input 
            type="url" 
            name="github_link"
            value={formData.github_link}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="https://github.com/username/project"
          />
          <p className="text-xs text-gray-500 mt-1">Format: https://github.com/username/repository</p>
        </div>
        
        {/* Project Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Project Status</label>
          <select 
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          >
            <option value="Initialized">Initialized</option>
            <option value="In_progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
        
        {/* Technologies */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Technologies Used</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-60 overflow-y-auto p-2 border border-gray-200 rounded">
            {technologies.map(tech => (
              <label key={tech.id} className="inline-flex items-center">
                <input 
                  type="checkbox" 
                  value={tech.id}
                  checked={formData.technologies.includes(tech.id)}
                  onChange={handleTechChange}
                  className="form-checkbox"
                />
                <span className="ml-2">{tech.name}</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Contributors */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Contributors *</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-60 overflow-y-auto p-2 border border-gray-200 rounded">
            {students.map(student => (
              <label key={student.id} className="inline-flex items-center">
                <input 
                  type="checkbox" 
                  value={student.id}
                  checked={formData.contributors.includes(student.id)}
                  onChange={handleContributorChange}
                  disabled={student.id === user?.id} // Disable current user to prevent deselection
                  className="form-checkbox"
                />
                <span className="ml-2">{student.first_name} ({student.roll_no})</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Submit Button */}
        <div className="pt-4">
          <button 
            type="submit" 
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={loading}
          >
            {loading ? 'Creating Project...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProjectForm;
