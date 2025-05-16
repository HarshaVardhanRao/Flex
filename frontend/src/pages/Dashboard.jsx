import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ProfileCard from "../components/ProfileCard";
import Section from "../components/Section";
import ErrorBanner from "../components/ErrorBanner";
import ApiService from "../services/api";
import { useAuth } from "../context/AuthContext";

function Dashboard() {
	const [projects, setProjects] = useState([]);
	const [foreignLanguages, setForeignLanguages] = useState([]);
	const [technicalCerts, setTechnicalCerts] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);
	
	// Get authentication context
	const { user, loading: authLoading } = useAuth();
	const navigate = useNavigate();

	useEffect(() => {
		// Fetch student data
		const fetchData = async () => {
			// If we're still loading auth data or no user, return early
			if (authLoading || !user) return;
					try {
				setLoading(true);
				setError(null);
				
				// Now fetch the projects
				const projectsResponse = await ApiService.getProjects();
				
				// Filter projects for this student
				const studentProjects = projectsResponse.data
					.filter(project => project.contributors && Array.isArray(project.contributors) && project.contributors.includes(user.id))
					.map(project => ({
						title: project.name || "Untitled Project",
						description: project.description || "No description available",
						github_link: project.github_link || "#",
						id: project.id
					}));
				
				setProjects(studentProjects);
				
				// Fetch certificates
				const certificatesResponse = await ApiService.getCertificates();
				
				// Filter certificates by category and student
				const studentCertificates = certificatesResponse.data
					.filter(cert => cert.rollno === user.rollno);
					
				const techCerts = studentCertificates
					.filter(cert => cert.category === "Technical")
					.map(cert => ({
						title: cert.name || "Untitled Certificate",
						description: cert.issuer || "No issuer specified",
						github_link: "#", // Certificates don't typically have GitHub links
						id: cert.id
					}));
				
				const langCerts = studentCertificates
					.filter(cert => cert.category === "Foreign Language")
					.map(cert => ({
						title: cert.name || "Untitled Certificate",
						description: cert.issuer || "No issuer specified",
						github_link: "#",
						id: cert.id
					}));
				
				setTechnicalCerts(techCerts);
				setForeignLanguages(langCerts);
				
				setLoading(false);
			} catch (err) {
				console.error("Error fetching data:", err);
				const errorMessage = err.response?.data?.detail || 
				                    "Failed to fetch data. Please check your connection and try again.";
				setError(errorMessage);
				setLoading(false);
			}
		};
		
		fetchData();
	}, [user, authLoading]);
	return (
		<div className="mx-auto flex flex-col gap-6">
			<Header />
			<div className="min-w-[90%] mx-auto py-4 flex flex-col gap-6">
				{user && <ProfileCard studentData={user} />}
				
				{authLoading || loading ? (
					<div className="text-center py-10">
						<p className="text-xl text-yellow-400">Loading data...</p>
					</div>
				) : error ? (
					<div className="text-center py-10">
						<p className="text-xl text-red-400">{error}</p>
					</div>
				) : !user ? (
					<div className="text-center py-10">
						<p className="text-xl text-yellow-400">Please log in to view your dashboard</p>
					</div>
				) : (
					<div className="grid grid-cols-1 md:grid-cols-3 gap-7">
						<Section 
							title="Projects" 
							data={projects} 
							onAddClick={() => navigate("/create-project")}
						/>
						<Section 
							title="Foreign Languages" 
							data={foreignLanguages}
							onAddClick={() => navigate("/add-certificate")}
						/>
						<Section 
							title="Technical Certifications" 
							data={technicalCerts}
							onAddClick={() => navigate("/add-certificate")}
						/>
					</div>
				)}
			</div>
			<main className="flex-1 py-6 px-4 sm:px-6 lg:px-8">
				{/* Main content */}
				<div className="max-w-7xl mx-auto">
					{error && <ErrorBanner message={error} />}

					{/* Profile section */}
					<div className="mb-8">
						{user && <ProfileCard user={user} />}
					</div>

					{/* Action Buttons */}
					<div className="mb-8 flex flex-wrap gap-4">
						<Link
							to="/create-project"
							className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
						>
							<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
								<path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
							</svg>
							Create New Project
						</Link>
						<Link
							to="/add-certificate"
							className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
						>
							<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
								<path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
							</svg>
							Add New Certificate
						</Link>
					</div>

					{/* Projects section */}
					<div className="mb-8">
						<h2 className="text-2xl font-semibold mb-4">Your Projects</h2>
						{loading ? (
							<p className="text-center py-4">Loading projects...</p>
						) : projects.length === 0 ? (
							<p className="text-center py-4">No projects found. Create a new project to get started.</p>
						) : (
							<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
								{projects.map(project => (
									<div key={project.id} className="bg-white shadow-md rounded-lg p-4">
										<h3 className="text-xl font-semibold mb-2">{project.title}</h3>
										<p className="text-gray-700 mb-4">{project.description}</p>
										<div className="flex justify-between">
											<a href={project.github_link} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-900">
												View on GitHub
											</a>
										</div>
									</div>
								))}
							</div>
						)}
					</div>

					{/* Certificates section */}
					<div className="mb-8">
						<h2 className="text-2xl font-semibold mb-4">Your Certificates</h2>
						{loading ? (
							<p className="text-center py-4">Loading certificates...</p>
						) : foreignLanguages.length === 0 && technicalCerts.length === 0 ? (
							<p className="text-center py-4">No certificates found. Add a new certificate to get started.</p>
						) : (
							<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
								{foreignLanguages.map(cert => (
									<div key={cert.id} className="bg-white shadow-md rounded-lg p-4">
										<h3 className="text-xl font-semibold mb-2">{cert.title}</h3>
										<p className="text-gray-700 mb-4">{cert.description}</p>
									</div>
								))}
								{technicalCerts.map(cert => (
									<div key={cert.id} className="bg-white shadow-md rounded-lg p-4">
										<h3 className="text-xl font-semibold mb-2">{cert.title}</h3>
										<p className="text-gray-700 mb-4">{cert.description}</p>
									</div>
								))}
							</div>
						)}
					</div>
				</div>
			</main>
		</div>
	);
}

export default Dashboard;
