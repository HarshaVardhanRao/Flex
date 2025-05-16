import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function Header() {
	const { user, logout } = useAuth();
	const navigate = useNavigate();
		const handleLogout = async () => {
		try {
			// Set loading state if needed
			const result = await logout();
			// Always navigate to login page, even if the backend logout had issues
			navigate("/login");
		} catch (error) {
			console.error("Error during logout:", error);
			// If there's any error, still try to navigate away
			navigate("/login");
		}
	};
	
	return (
		<header className="bg-[#1a1a1a] text-white p-2 px-[5rem] py-[0.5rem] flex justify-between items-center shadow-md animate-moveDown">
			<div className="flex items-center">
				<img src="/static/logo.png" alt="Profile" className="h-[80px] rounded-full" />
			</div>
			
			<div className="flex items-center justify-center gap-2">
				<h1 className="text-[2rem] font-regular text-yellow-400">
					MITS - FLEX
				</h1>
			</div>
			
			{user && (
				<div className="flex items-center">
					<button
						onClick={handleLogout}
						className="bg-yellow-400 text-black px-4 py-2 rounded hover:bg-yellow-500"
					>
						Logout
					</button>
				</div>
			)}
		</header>
	);
}

export default Header;
