function Header() {
	return (
		<header className="bg-[#1a1a1a] text-white p-4 px-12 flex justify-between items-center shadow-md shadow-yellow-400 animate-moveDown">
			<img src="/logo.png" alt="Profile" className="h-20 rounded-full" />
			<div className="flex items-center justify-center gap-2">
				<h1 className="text-2xl font-bold text-yellow-400">
					MITS - FLEX
				</h1>
			</div>
		</header>
	);
}

export default Header;
