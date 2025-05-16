import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';
import ErrorBanner from './ErrorBanner';

const CertificateForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    source: '',
    category: 'technical',
    year_and_sem: '',
    certificate: null,
    course_link: '',
    rank: '',
    recognition: '',
    event_type: 'others',
    fest_name: '',
    course_provider: '',
    domain: '',
    duration: '',
    technologies: []
  });
  
  const [technologies, setTechnologies] = useState([]);
  const [yearAndSemOptions, setYearAndSemOptions] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Fetch technologies for selection
    const fetchTechnologies = async () => {
      try {
        // Assuming you have an API endpoint to get technologies
        const response = await ApiService.getTechnologies();
        setTechnologies(response.data || []);
      } catch (error) {
        console.error('Error fetching technologies:', error);
      }
    };
    
    // Set year and semester options
    setYearAndSemOptions([
      "I-I", "I-II", "II-I", "II-II", "III-I", "III-II", "IV-I", "IV-II"
    ]);
    
    fetchTechnologies();
  }, []);
  
  // Handle change for most form fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Special handler for file input
  const handleFileChange = (e) => {
    setFormData({
      ...formData,
      certificate: e.target.files[0]
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
  
  // Determine whether to show technology section based on category
  const showTechnologies = formData.category === 'technical';
  
  // Determine which recognition fields to show
  const handleRecognitionTypeChange = (type) => {
    if (type === 'rank') {
      setFormData({
        ...formData,
        recognition: '',  // Clear recognition when rank is selected
      });
    } else if (type === 'recognition') {
      setFormData({
        ...formData,
        rank: '',  // Clear rank when recognition is selected
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
      if (!formData.title || !formData.source || !formData.year_and_sem) {
        throw new Error('Please fill all required fields');
      }
      // Validate that either rank or recognition is provided
      if (!formData.rank && !formData.recognition) {
        throw new Error('Please provide either a rank or a recognition');
      }
      // Validate technologies are only selected for technical category
      if (formData.category !== 'technical' && formData.technologies.length > 0) {
        throw new Error('Technologies can only be selected for Technical certificates');
      }
      // Prepare payload
      const payload = {
        ...formData,
        technologies: formData.technologies.map(id => parseInt(id)),
        category: formData.category, // should be 'technical' or 'foreign_language'
      };
      // Submit the form
      const response = await ApiService.createCertificate(payload);
      // Handle success
      alert('Certificate added successfully!');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.errors || err.message || 'An error occurred while submitting the form');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-3xl mx-auto">
      <h2 className="text-2xl font-semibold mb-6">Add New Certificate</h2>
      
      {error && <ErrorBanner message={error} />}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Certificate Title *</label>
          <input 
            type="text" 
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Certificate Title"
            required
          />
        </div>
        
        {/* Source/Provider */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Issuing Organization *</label>
          <input 
            type="text" 
            name="source"
            value={formData.source}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="e.g. Coursera, Udemy, Microsoft"
            required
          />
        </div>
        
        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Category *</label>
          <select 
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            required
          >
            <option value="technical">Technical</option>
            <option value="foreign_language">Foreign Language</option>
            <option value="co_curricular">Co-Curricular</option>
            <option value="extra_curricular">Extra-Curricular</option>
          </select>
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
        
        {/* Certificate File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Certificate File</label>
          <input 
            type="file" 
            name="certificate"
            onChange={handleFileChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            accept="application/pdf,image/*"
          />
          <p className="text-xs text-gray-500 mt-1">Upload your certificate as PDF or image</p>
        </div>
        
        {/* Course Link */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Course Link</label>
          <input 
            type="url" 
            name="course_link"
            value={formData.course_link}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="https://..."
          />
        </div>
        
        {/* Recognition Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Recognition Type *</label>
          <div className="flex space-x-4">
            <label className="inline-flex items-center">
              <input 
                type="radio" 
                name="recognition_type"
                checked={!!formData.rank}
                onChange={() => handleRecognitionTypeChange('rank')}
                className="form-radio"
              />
              <span className="ml-2">Rank</span>
            </label>
            <label className="inline-flex items-center">
              <input 
                type="radio" 
                name="recognition_type"
                checked={!!formData.recognition}
                onChange={() => handleRecognitionTypeChange('recognition')}
                className="form-radio"
              />
              <span className="ml-2">Recognition</span>
            </label>
          </div>
        </div>
        
        {/* Rank (conditionally displayed) */}
        {!formData.recognition && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Rank</label>
            <input 
              type="number" 
              name="rank"
              value={formData.rank}
              onChange={handleChange}
              min="1"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              placeholder="Your rank (if applicable)"
            />
          </div>
        )}
        
        {/* Recognition (conditionally displayed) */}
        {!formData.rank && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Recognition</label>
            <select 
              name="recognition"
              value={formData.recognition}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            >
              <option value="">Select Recognition</option>
              <option value="participation">Participation</option>
              <option value="appreciation">Appreciation</option>
              <option value="recommendation">Recommendation</option>
            </select>
          </div>
        )}
        
        {/* Event Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Event Type</label>
          <select 
            name="event_type"
            value={formData.event_type}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          >
            <option value="others">Others</option>
            <option value="hackathon">Hackathon</option>
            <option value="quiz">Quiz</option>
            <option value="workshop">Workshop/Webinar</option>
            <option value="techfest">Tech Fest</option>
            <option value="presentation">Presentation</option>
          </select>
        </div>
        
        {/* Fest Name (conditionally displayed for events) */}
        {['hackathon', 'quiz', 'techfest'].includes(formData.event_type) && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Fest/Event Name</label>
            <input 
              type="text" 
              name="fest_name"
              value={formData.fest_name}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              placeholder="Name of the event/fest"
            />
          </div>
        )}
        
        {/* Course Provider (for courses) */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Course Provider</label>
          <input 
            type="text" 
            name="course_provider"
            value={formData.course_provider}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Provider of the course (if applicable)"
          />
        </div>
        
        {/* Domain */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Domain/Field</label>
          <input 
            type="text" 
            name="domain"
            value={formData.domain}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Field of study or domain"
          />
        </div>
        
        {/* Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Duration</label>
          <input 
            type="text" 
            name="duration"
            value={formData.duration}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="e.g. 8 weeks, 3 months"
          />
        </div>
        
        {/* Technologies (only for technical category) */}
        {showTechnologies && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Technologies</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
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
        )}
        
        {/* Submit Button */}
        <div className="pt-4">
          <button 
            type="submit" 
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            disabled={loading}
          >
            {loading ? 'Submitting...' : 'Add Certificate'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CertificateForm;
