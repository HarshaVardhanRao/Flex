function ProfileCard({ studentData }) {
	// Extract student details from props
	const { first_name, last_name, roll_no, dept, section } = studentData || {};

	return (
		<div className="bg-flex-dark text-white rounded-lg p-4 shadow-flex flex justify-around items-center animate-moveRight">
			<div className="detail">
				<p className="whitespace-nowrap font-semibold">
					<a
						href="/profile"
						className="text-white hover:text-flex-yellow transition-colors no-underline"
					>
						{first_name} {last_name || ""}{" "}
						<i className="bi bi-pencil ml-1 text-base"></i>
					</a>
				</p>
				<p>{roll_no}</p>
				<p>
					{dept} - {section}
				</p>
			</div>
		</div>
	);
}

export default ProfileCard;
