function ProfileCard({ studentData }) {
	// Extract student details from props
	const { first_name, last_name, rollno, dept, section } = studentData || {};
	
	return (
		<div className="bg-[#1a1a1a] text-white rounded-lg p-4 shadow-md flex justify-around items-center animate-moveRight">
			<div className="detail">
				<p className="whitespace-nowrap font-semibold">
					<a
						href="/profile"
						className="text-white hover:text-yellow-400 no-underline"
					>
						{first_name} {last_name || ''} <i className="bi bi-pencil ml-1 text-base"></i>
					</a>
				</p>
				<p>{rollno}</p>
				<p>{dept} - {section}</p>
			</div>
		</div>
	);
}

export default ProfileCard;
