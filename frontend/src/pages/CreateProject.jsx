import React from "react";
import { useAuth } from "../context/AuthContext";
import { Navigate } from "react-router-dom";
import ProjectForm from "../components/ProjectForm";
import Header from "../components/Header";

const CreateProjectPage = () => {
	const { user, loading } = useAuth();

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
					{/* Form is already styled correctly in the ProjectForm component */}
					<ProjectForm />
				</div>
			</main>
		</div>
	);
};

export default CreateProjectPage;
