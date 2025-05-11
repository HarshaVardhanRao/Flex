function Header() {
	return (
		<header className="bg-[#1a1a1a] text-white p-2 px-[5rem] py-[0.5rem] flex justify-between items-center shadow-md animate-moveDown">
			<img src="/static/logo.png" alt="Profile" className="h-[80px] rounded-full" />
			<div className="flex items-center justify-center gap-2">
				<h1 className="text-[2rem] font-regular text-yellow-400">
					MITS - FLEX
				</h1>
			</div>
		</header>
	);
}

export default Header;
