function ProfileCard() {
	return (
		<div className="bg-[#1a1a1a] text-white rounded-lg p-4 shadow-md flex justify-around items-center animate-moveRight">
			<div className="detail">
				<p className="whitespace-nowrap font-semibold">
					<a
						href="/profile"
						className="text-white hover:text-yellow-400 no-underline"
					>
						John Doe <i className="bi bi-pencil ml-1 text-base"></i>
					</a>
				</p>
				<p>123456</p>
				<p>CSE - A</p>
			</div>
		</div>
	);
}

export default ProfileCard;
