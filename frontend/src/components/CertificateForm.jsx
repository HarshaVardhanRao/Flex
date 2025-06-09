import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ApiService from "../services/api";
import ErrorBanner from "./ErrorBanner";
import Autocomplete from "./Autocomplete";
import TagList from "./TagList";

const CertificateForm = ({ defaultCategory = "technical" }) => {
	const navigate = useNavigate();
	const [formData, setFormData] = useState({
		title: "",
		source: "",
		category: defaultCategory,
		year_and_sem: "",
		certificate: null,
		course_link: "",
		rank: "",
		recognition: "",
		event_type: "others",
		fest_name: "",
		course_provider: "",
		domain: "",
		duration: "",
		technologies: [], // This will store technology objects now, not just IDs
	});

	const [technologies, setTechnologies] = useState([]);
	const [yearAndSemOptions, setYearAndSemOptions] = useState([]);
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);

	// Update category when defaultCategory prop changes
	useEffect(() => {
		setFormData((prev) => ({
			...prev,
			category: defaultCategory,
		}));
	}, [defaultCategory]);

	useEffect(() => {
		// Fetch technologies for selection
		const fetchTechnologies = async () => {
			try {
				// Assuming you have an API endpoint to get technologies
				const response = await ApiService.getTechnologies();
				setTechnologies(response.data || []);
			} catch (error) {
				console.error("Error fetching technologies:", error);
			}
		};

		// Set year and semester options
		setYearAndSemOptions([
			"I-I",
			"I-II",
			"II-I",
			"II-II",
			"III-I",
			"III-II",
			"IV-I",
			"IV-II",
		]);

		fetchTechnologies();
	}, []);

	// Handle change for most form fields
	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData({
			...formData,
			[name]: value,
		});
	};

	// Special handler for file input
	const handleFileChange = (e) => {
		setFormData({
			...formData,
			certificate: e.target.files[0],
		});
	};

	// Handle adding a new technology
	const handleAddTechnology = (tech) => {
		setFormData((prev) => ({
			...prev,
			technologies: [...prev.technologies, tech],
		}));
	};

	// Handle removing a technology
	const handleRemoveTechnology = (techToRemove) => {
		setFormData((prev) => ({
			...prev,
			technologies: prev.technologies.filter(
				(tech) => tech.id !== techToRemove.id
			),
		}));
	};

	// Get label for technology tag
	const getTechnologyLabel = (tech) => {
		return tech.name || tech;
	};

	// Determine whether to show technology section based on category
	const showTechnologies = formData.category === "technical";

	// Determine which recognition fields to show
	const handleRecognitionTypeChange = (type) => {
		if (type === "rank") {
			setFormData({
				...formData,
				recognition: "", // Clear recognition when rank is selected
			});
		} else if (type === "recognition") {
			setFormData({
				...formData,
				rank: "", // Clear rank when recognition is selected
			});
		}
	};

	// Handle form submission
	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError("");

		const formDataToSubmit = new FormData();

		// Add all form fields to FormData except technologies
		Object.keys(formData).forEach((key) => {
			if (key === "technologies") {
				// For technologies, we handle them separately below
				return;
			} else if (key === "certificate" && formData[key]) {
				// For certificate file
				formDataToSubmit.append("certificate", formData[key]);
			} else if (formData[key]) {
				// Add other fields, but only if they're not empty
				formDataToSubmit.append(key, formData[key]);
			}
		});

		// Handle technologies with both existing and new entries
		formData.technologies.forEach((tech) => {
			if (tech.isNew) {
				formDataToSubmit.append("new_technologies", tech.name);
			} else {
				formDataToSubmit.append("technologies", tech.id);
			}
		});

		try {
			await ApiService.createCertificate(formDataToSubmit);
			navigate("/dashboard");
		} catch (error) {
			console.error("Error creating certificate:", error);
			setError(
				error.response?.data?.detail ||
					"Failed to create certificate. Please try again."
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="container mx-auto p-4">
			<h1 className="text-3xl font-bold mb-6 text-flex-yellow text-center">
				Add Certificate
			</h1>

			{error && <ErrorBanner message={error} />}

			<form
				onSubmit={handleSubmit}
				className="bg-flex-dark p-6 rounded-lg shadow-flex max-w-2xl mx-auto"
			>
				{/* Basic Certificate Information */}
				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="title">
						Certificate Title*
					</label>
					<input
						type="text"
						id="title"
						name="title"
						value={formData.title}
						onChange={handleChange}
						required
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="source">
						Source / Issuer*
					</label>
					<input
						type="text"
						id="source"
						name="source"
						value={formData.source}
						onChange={handleChange}
						required
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
						placeholder="e.g., Coursera, Udemy, NPTEL"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="category">
						Category*
					</label>
					<select
						id="category"
						name="category"
						value={formData.category}
						onChange={handleChange}
						required
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					>
						<option value="technical">Technical</option>
						<option value="foreign">Foreign Language</option>
					</select>
				</div>

				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="year_and_sem"
					>
						Year and Semester*
					</label>
					<select
						id="year_and_sem"
						name="year_and_sem"
						value={formData.year_and_sem}
						onChange={handleChange}
						required
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					>
						<option value="">Select Year and Semester</option>
						{yearAndSemOptions.map((option) => (
							<option key={option} value={option}>
								{option}
							</option>
						))}
					</select>
				</div>

				{/* Certificate Upload */}
				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="certificate"
					>
						Upload Certificate (PDF/PNG/JPG)*
					</label>
					<input
						type="file"
						id="certificate"
						name="certificate"
						accept=".pdf,.png,.jpg,.jpeg"
						onChange={handleFileChange}
						required
						className="w-full p-2 text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-flex-yellow file:text-flex-black hover:file:bg-flex-yellow-dark"
					/>
				</div>

				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="course_link"
					>
						Course Link (optional)
					</label>
					<input
						type="url"
						id="course_link"
						name="course_link"
						value={formData.course_link}
						onChange={handleChange}
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
						placeholder="https://www.example.com/course"
					/>
				</div>

				{/* Course Details */}
				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="course_provider"
					>
						Course Provider (optional)
					</label>
					<input
						type="text"
						id="course_provider"
						name="course_provider"
						value={formData.course_provider}
						onChange={handleChange}
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="domain">
						Domain / Field of Study (optional)
					</label>
					<input
						type="text"
						id="domain"
						name="domain"
						value={formData.domain}
						onChange={handleChange}
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					/>
				</div>

				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="duration">
						Duration (optional)
					</label>
					<input
						type="text"
						id="duration"
						name="duration"
						value={formData.duration}
						onChange={handleChange}
						className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
						placeholder="e.g., 4 weeks, 2 months"
					/>
				</div>

				{/* Recognition Section */}
				<div className="mb-6 border-t border-gray-700 pt-4">
					<h3 className="text-xl text-flex-yellow mb-4">
						Recognition (if applicable)
					</h3>

					<div className="mb-4">
						<label className="block text-white mb-2">
							Recognition Type
						</label>
						<div className="flex gap-4">
							<div className="flex items-center">
								<input
									type="radio"
									id="recognition_rank"
									name="recognition_type"
									checked={!!formData.rank}
									onChange={() =>
										handleRecognitionTypeChange("rank")
									}
									className="mr-2 accent-flex-yellow"
								/>
								<label
									htmlFor="recognition_rank"
									className="text-white"
								>
									Rank Achieved
								</label>
							</div>

							<div className="flex items-center">
								<input
									type="radio"
									id="recognition_other"
									name="recognition_type"
									checked={!!formData.recognition}
									onChange={() =>
										handleRecognitionTypeChange(
											"recognition"
										)
									}
									className="mr-2 accent-flex-yellow"
								/>
								<label
									htmlFor="recognition_other"
									className="text-white"
								>
									Other Recognition
								</label>
							</div>
						</div>
					</div>

					{formData.rank !== "" && (
						<div className="mb-4">
							<label
								className="block text-white mb-2"
								htmlFor="rank"
							>
								Rank Achieved
							</label>
							<input
								type="text"
								id="rank"
								name="rank"
								value={formData.rank}
								onChange={handleChange}
								className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
								placeholder="e.g., 1st, 2nd, Top 10%"
							/>
						</div>
					)}

					{formData.recognition !== "" && (
						<div className="mb-4">
							<label
								className="block text-white mb-2"
								htmlFor="recognition"
							>
								Recognition Details
							</label>
							<input
								type="text"
								id="recognition"
								name="recognition"
								value={formData.recognition}
								onChange={handleChange}
								className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
								placeholder="e.g., Special Mention, Excellence Award"
							/>
						</div>
					)}
				</div>

				{/* Technologies with Autocomplete (only for technical certificates) */}
				{showTechnologies && (
					<div className="mb-6">
						<label className="block text-white mb-2">
							Technologies Used
						</label>
						<Autocomplete
							id="technologies"
							suggestions={technologies}
							placeholder="Type to search or add new technologies..."
							onSelect={handleAddTechnology}
							selectedItems={formData.technologies.map(
								(tech) => tech.id
							)}
							allowNew={true}
						/>

						{formData.technologies.length > 0 && (
							<TagList
								items={formData.technologies}
								onRemove={handleRemoveTechnology}
								getItemLabel={getTechnologyLabel}
							/>
						)}

						{formData.technologies.length === 0 && (
							<p className="text-gray-400 mt-2 text-sm">
								No technologies selected. You can add relevant
								technologies.
							</p>
						)}
					</div>
				)}

				{/* Submit Button */}
				<div className="flex justify-between">
					<button
						type="button"
						onClick={() => navigate("/dashboard")}
						className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
					>
						Cancel
					</button>
					<button
						type="submit"
						className="px-4 py-2 bg-flex-yellow text-flex-black rounded hover:bg-flex-yellow-dark transition-colors"
						disabled={loading}
					>
						{loading ? "Submitting..." : "Submit Certificate"}
					</button>
				</div>
			</form>
		</div>
	);
};

export default CertificateForm;
