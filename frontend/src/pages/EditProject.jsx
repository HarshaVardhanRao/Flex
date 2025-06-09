import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { Navigate, useParams, useNavigate } from "react-router-dom";
import ProjectForm from "../components/ProjectForm";
import Header from "../components/Header";
import ApiService from "../services/api";
import ErrorBanner from "../components/ErrorBanner";

const EditProjectPage = () => {
	const { user, loading } = useAuth();
	const { projectId } = useParams();
	const navigate = useNavigate();
	const [project, setProject] = useState(null);
	const [error, setError] = useState("");
	const [isLoading, setIsLoading] = useState(true);

	// Load project data when component mounts
	useEffect(() => {
		const fetchProject = async () => {
			if (!projectId) {
				setError("No project ID provided");
				setIsLoading(false);
				return;
			}

			try {
				const response = await ApiService.getProjectById(projectId);
				setProject(response.data);
			} catch (err) {
				console.error("Failed to fetch project:", err);
				setError("Failed to load project. Please try again.");
			} finally {
				setIsLoading(false);
			}
		};

		fetchProject();
	}, [projectId]);

	// If auth is loading, show a loading state
	if (loading) {
		return (
			<div className="flex justify-center items-center h-screen text-flex-yellow">
				Loading...
			</div>
		);
	}

	// Redirect to login if user is not authenticated
	if (!user) {
		return <Navigate to="/login" replace={true} />;
	}

	return (
		<div className="min-h-screen bg-flex-black">
			<Header />
			<main className="py-10 px-4 sm:px-6 lg:px-8">
				<div className="max-w-7xl mx-auto">
					{error && <ErrorBanner message={error} />}

					{isLoading ? (
						<div className="flex justify-center items-center h-64 text-flex-yellow">
							Loading project data...
						</div>
					) : project ? (
						<ProjectForm action="edit" projectData={project} />
					) : (
						!error && (
							<div className="bg-red-800 text-white p-4 rounded-md">
								Project not found
							</div>
						)
					)}
				</div>
			</main>
		</div>
	);
};

export default EditProjectPage;
