import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Login() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const [isLoading, setIsLoading] = useState(false);

	const { login, user } = useAuth();
	const navigate = useNavigate();

	// Redirect if already logged in
	useEffect(() => {
		if (user) {
			navigate("/dashboard");
		}
	}, [user, navigate]);

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError("");
		setIsLoading(true);

		try {
			const result = await login(username, password);
			if (result && result.success) {
				// Navigate to dashboard on successful login
				navigate("/dashboard");
			} else {
				setError(
					(result && result.error) ||
						"Login failed. Please try again."
				);
			}
		} catch (err) {
			setError("An unexpected error occurred. Please try again.");
			console.error(err);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="min-h-screen flex items-center justify-center bg-flex-black">
			<div className="bg-flex-dark p-8 rounded-lg shadow-flex w-full max-w-md">
				<h2 className="text-3xl font-bold mb-6 text-center text-flex-yellow">
					MITS - FLEX Login
				</h2>

				{error && (
					<div className="bg-red-500 text-white p-3 rounded mb-4">
						{error}
					</div>
				)}

				<form onSubmit={handleSubmit}>
					<div className="mb-4">
						<label
							className="block text-gray-300 mb-2"
							htmlFor="username"
						>
							Username / Roll No
						</label>
						<input
							id="username"
							type="text"
							className="w-full p-3 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
						/>
					</div>

					<div className="mb-6">
						<label
							className="block text-gray-300 mb-2"
							htmlFor="password"
						>
							Password
						</label>
						<input
							id="password"
							type="password"
							className="w-full p-3 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
						/>
					</div>

					<button
						type="submit"
						className="w-full bg-flex-yellow text-flex-black font-semibold p-3 rounded hover:bg-flex-yellow-dark transition-colors"
						disabled={isLoading}
					>
						{isLoading ? "Logging in..." : "Login"}
					</button>
				</form>

				<div className="mt-4 text-center">
					<a
						href="#forgot-password"
						className="text-flex-yellow hover:text-flex-yellow-dark"
					>
						Forgot Password?
					</a>
				</div>
			</div>
		</div>
	);
}

export default Login;
