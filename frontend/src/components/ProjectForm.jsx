import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ApiService from "../services/api";
import ErrorBanner from "./ErrorBanner";
import { useAuth } from "../context/AuthContext";
import Autocomplete from "./Autocomplete";
import TagList from "./TagList";

const ProjectForm = ({ action = "create", projectData = null }) => {
	const navigate = useNavigate();
	const { user } = useAuth();

	// Set initial form data, either from provided projectData or default values
	const [formData, setFormData] = useState({
		title: projectData?.title || "",
		description: projectData?.description || "",
		year_and_sem: projectData?.year_and_sem || "",
		github_link: projectData?.github_link || "",
		status: projectData?.status || "Initialized",
		technologies: projectData?.technologies || [], // This will store technology objects now, not just IDs
		contributors: projectData?.contributors || [], // This will store contributor objects now, not just IDs
	});

	const [technologies, setTechnologies] = useState([]);
	const [students, setStudents] = useState([]);
	const [yearAndSemOptions, setYearAndSemOptions] = useState([]);
	const [error, setError] = useState("");
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
        if (action === "create") {
          // If creating a new project, add current user as a contributor
          setFormData((prev) => ({
            ...prev,
            contributors: [user],
          }));
        }
			} catch (error) {
				console.error("Error fetching form data:", error);
				setError("Failed to load form data. Please try again later.");
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

		fetchData();
	}, [user]);

	// Effect to populate form data when editing an existing project
	useEffect(() => {
		if (action === "edit" && projectData) {
			setFormData({
				title: projectData.title || "",
				description: projectData.description || "",
				year_and_sem: projectData.year_and_sem || "",
				github_link: projectData.github_link || "",
				status: projectData.status || "Initialized",
				technologies: projectData.technologies || [],
				contributors: projectData.contributors || [],
			});
		}
	}, [action, projectData]);

	// Handle change for text inputs
	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData({
			...formData,
			[name]: value,
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

	// Handle adding a contributor
	const handleAddContributor = (contributor) => {
		setFormData((prev) => ({
			...prev,
			contributors: [...prev.contributors, contributor],
		}));
	};

	// Handle removing a contributor
	const handleRemoveContributor = (contributorToRemove) => {
		// Prevent removing current user
		if (contributorToRemove.id === user?.id) {
			return;
		}

		setFormData((prev) => ({
			...prev,
			contributors: prev.contributors.filter(
				(contributor) => contributor.id !== contributorToRemove.id
			),
		}));
	};

	// Get label for technology tag
	const getTechnologyLabel = (tech) => {
		return tech.name || tech;
	};

	// Get label for contributor tag
	const getContributorLabel = (contributor) => {
		if (typeof contributor === "string" || contributor instanceof String)
			return contributor;
		return `${contributor.name || ""} ${contributor.last_name || ""}`;
	};

	// Handle form submission
	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError("");

		try {
			// Format data for API - extract IDs and handle new items
			const formattedData = {
				name: formData.title,
				description: formData.description,
				year_and_sem: formData.year_and_sem,
				github_link: formData.github_link,
				status: formData.status,
				technologies: formData.technologies.map((tech) => {
					// If it's a new technology, send the name
					if (tech.isNew) {
						return { name: tech.name };
					}
					// Otherwise send the ID
					return tech.id;
				}),
				contributors: formData.contributors.map((contributor) => {
					// If it's a new contributor, send the name/details
					if (contributor.isNew) {
						return { name: contributor.name };
					}
					// Otherwise send the ID
					return contributor.id;
				}),
			};

			if (action === "edit" && projectData?.id) {
				// Update existing project
				await ApiService.updateProject(projectData.id, formattedData);
				// Success message or handling
				console.log("Project updated successfully");
			} else {
				// Create new project
				await ApiService.createProject(formattedData);
				// Success message or handling
				console.log("Project created successfully");
			}

			// Redirect back to dashboard
			navigate("/dashboard");
		} catch (error) {
			console.error(
				`Error ${action === "edit" ? "updating" : "creating"} project:`,
				error
			);
			setError(
				error.response?.data?.detail ||
					`Failed to ${
						action === "edit" ? "update" : "create"
					} project. Please try again.`
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="container mx-auto p-4">
			<h1 className="text-3xl font-bold mb-6 text-flex-yellow text-center">
				{action === "edit" ? "Edit Project" : "Create New Project"}
			</h1>

			{error && <ErrorBanner message={error} />}

			<form
				onSubmit={handleSubmit}
				className="bg-flex-dark p-6 rounded-lg shadow-flex max-w-2xl mx-auto"
			>
				{/* Title */}
				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="title">
						Project Title*
					</label>
					<input
						type="text"
						id="title"
						name="title"
						value={formData.title}
						onChange={handleChange}
						required
						className="w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					/>
				</div>

				{/* Description */}
				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="description"
					>
						Description*
					</label>
					<textarea
						id="description"
						name="description"
						value={formData.description}
						onChange={handleChange}
						required
						rows="4"
						className="w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					></textarea>
				</div>

				{/* Year and Semester */}
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
						className="w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					>
						<option value="">Select Year and Semester</option>
						{yearAndSemOptions.map((option) => (
							<option key={option} value={option}>
								{option}
							</option>
						))}
					</select>
				</div>

				{/* GitHub Link */}
				<div className="mb-4">
					<label
						className="block text-white mb-2"
						htmlFor="github_link"
					>
						GitHub Link (optional)
					</label>
					<input
						type="url"
						id="github_link"
						name="github_link"
						value={formData.github_link}
						onChange={handleChange}
						className="w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
						placeholder="https://github.com/username/repository"
					/>
				</div>

				{/* Status */}
				<div className="mb-4">
					<label className="block text-white mb-2" htmlFor="status">
						Project Status*
					</label>
					<select
						id="status"
						name="status"
						value={formData.status}
						onChange={handleChange}
						required
						className="w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
					>
						<option value="Initialized">Initialized</option>
						<option value="In Progress">In Progress</option>
						<option value="Completed">Completed</option>
					</select>
				</div>

				{/* Technologies with Autocomplete */}
				<div className="mb-4">
					<label className="block text-white mb-2">
						Technologies Used*
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
							No technologies selected. Add at least one
							technology.
						</p>
					)}
				</div>
				{/* Contributors with Autocomplete */}
				<div className="mb-6">
					<label className="block text-white mb-2">
						Contributors*
					</label>
					<Autocomplete
						id="contributors"
						suggestions={students}
						placeholder="Type to search or add new contributors..."
						onSelect={handleAddContributor}
						selectedItems={formData.contributors.map(
							(contributor) => contributor.id
						)}
						allowNew={true}
					/>

					{formData.contributors.length > 0 && (
						<TagList
							items={formData.contributors}
							onRemove={handleRemoveContributor}
							getItemLabel={getContributorLabel}
						/>
					)}

					{formData.contributors.length === 0 && (
						<p className="text-gray-400 mt-2 text-sm">
							No contributors selected. Add at least one
							contributor.
						</p>
					)}
				</div>

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
						{loading
							? action === "edit"
								? "Updating..."
								: "Creating..."
							: action === "edit"
							? "Update Project"
							: "Create Project"}
					</button>
				</div>
			</form>
		</div>
	);
};

export default ProjectForm;
