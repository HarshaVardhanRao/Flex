function ProfileCard() {
	return (
		<div className="bg-[#1a1a1a] text-white rounded-lg p-4 shadow-lg shadow-yellow-400 flex justify-around items-center animate-moveRight">
			<a
				href="/profile"
				className="text-yellow-400 hidden sm:flex w-1/2 items-center justify-start no-underline"
			>
				<i className="bi bi-person-vcard-fill text-6xl"></i>
			</a>
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
