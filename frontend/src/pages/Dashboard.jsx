import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import ProfileCard from "../components/ProfileCard";
import Section from "../components/Section";
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
					.filter(
						(project) =>
							project.contributors &&
							Array.isArray(project.contributors) &&
							project.contributors.includes(user.id)
					)
					.map((project) => ({
            id: project.id,
						title: project.title || "Untitled Project",
						description:
							project.description || "No description available",
						github_link: project.github_link || "#",
					}));

				setProjects(studentProjects);

				// Fetch certificates
				const certificatesResponse = await ApiService.getCertificates();

				// Filter certificates by category and student
				const studentCertificates = certificatesResponse.data.filter(
					(cert) => cert.rollno === user.rollno
				);

				const techCerts = studentCertificates
					.filter((cert) => cert.category === "Technical")
					.map((cert) => ({
						title: cert.name || "Untitled Certificate",
						description: cert.issuer || "No issuer specified",
						github_link: "#", // Certificates don't typically have GitHub links
						id: cert.id,
					}));

				const langCerts = studentCertificates
					.filter((cert) => cert.category === "Foreign Language")
					.map((cert) => ({
						title: cert.name || "Untitled Certificate",
						description: cert.issuer || "No issuer specified",
						github_link: "#",
						id: cert.id,
					}));

				setTechnicalCerts(techCerts);
				setForeignLanguages(langCerts);

				setLoading(false);
			} catch (err) {
				console.error("Error fetching data:", err);
				const errorMessage =
					err.response?.data?.detail ||
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
						<p className="text-xl text-flex-yellow">
							Loading data...
						</p>
					</div>
				) : error ? (
					<div className="text-center py-10">
						<p className="text-xl text-red-400">{error}</p>
					</div>
				) : !user ? (
					<div className="text-center py-10">
						<p className="text-xl text-flex-yellow">
							Please log in to view your dashboard
						</p>
					</div>
				) : (
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
						<Section
							title="Projects"
							data={projects}
							onAddClick={() =>
								navigate("/dashboard/create-project")
							}
						/>
						<Section
							title="Technical Certifications"
							data={technicalCerts}
							onAddClick={() =>
								navigate("/dashboard/add-certificate", {
									state: { category: "technical" },
								})
							}
						/>
						<Section
							title="Foreign Languages"
							data={foreignLanguages}
							onAddClick={() =>
								navigate("/dashboard/add-certificate", {
									state: { category: "foreign" },
								})
							}
						/>
					</div>
				)}
			</div>
		</div>
	);
}

export default Dashboard;
