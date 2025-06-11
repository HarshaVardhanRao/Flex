import React from "react";
import { useAuth } from "../context/AuthContext";
import { Navigate, useLocation } from "react-router-dom";
import CertificateForm from "../components/CertificateForm";
import Header from "../components/Header";

const AddCertificatePage = () => {
	const { user, loading } = useAuth();
	const location = useLocation();
	const defaultCategory = location.state?.category || "technical";

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
					{/* Pass category from location state to the form */}
					<CertificateForm defaultCategory={defaultCategory} />
				</div>
			</main>
		</div>
	);
};

export default AddCertificatePage;
