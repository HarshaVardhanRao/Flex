import {
	BrowserRouter as Router,
	Routes,
	Route,
	Navigate,
} from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import CreateProject from "./pages/CreateProject";
import EditProject from "./pages/EditProject";
import AddCertificate from "./pages/AddCertificate";
import "./App.css";
import { AuthProvider } from "./context/AuthContext";
import { useAuth } from "./context/AuthContext";

// Protected route component
const ProtectedRoute = ({ children }) => {
	const { user, loading } = useAuth();

	if (loading) {
		return (
			<div className="min-h-screen flex flex-col items-center justify-center bg-flex-black">
				<div className="animate-pulse text-flex-yellow text-2xl mb-4">
					Loading...
				</div>
				<div className="w-16 h-1 bg-flex-yellow rounded-full animate-pulse"></div>
			</div>
		);
	}

	if (!user) {
		// Redirect to login if not authenticated
		return <Navigate to="/login" replace />;
	}

	return children;
};

function AppRoutes() {
	return (
		<Router>
			<div className="text-white">
				<Routes>
					<Route path="/login" element={<Login />} />
					<Route
						path="/dashboard"
						element={
							<ProtectedRoute>
								<Dashboard />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/dashboard/create-project"
						element={
							<ProtectedRoute>
								<CreateProject />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/dashboard/add-certificate"
						element={
							<ProtectedRoute>
								<AddCertificate />
							</ProtectedRoute>
						}
					/>
					<Route
						path="/dashboard/edit-project/:projectId"
						element={
							<ProtectedRoute>
								<EditProject />
							</ProtectedRoute>
						}
					/>
					{/* Redirect root to dashboard */}
					<Route
						path="/"
						element={<Navigate to="/dashboard" replace />}
					/>
				</Routes>
			</div>
		</Router>
	);
}

function App() {
	return (
		<AuthProvider>
			<AppRoutes />
		</AuthProvider>
	);
}

export default App;
