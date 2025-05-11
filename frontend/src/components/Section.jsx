function Section({ title, data = [], onAddClick }) {
	return (
		<div className="bg-[#1a1a1a] text-white p-6 rounded-lg shadow-lg shadow-yellow-400 animate-moveUp">
			<h2 className="text-center text-2xl text-yellow-400 mb-4">
				{title}
			</h2>
			<hr className="border-yellow-400 mb-4" />
			<ul className="max-h-[300px] overflow-y-auto bg-black p-2 rounded-lg space-y-4">
				{data.length === 0 ? (
					<li className="text-gray-400">No data available.</li>
				) : (
					data.map((item, idx) => (
						<li key={idx}>
							<h5 className="text-yellow-400 font-semibold">
								{item.title}
							</h5>
							<p>{item.description}</p>
							<p>
								<a
									href={item.github_link}
									target="_blank"
									rel="noopener noreferrer"
									className="text-yellow-400"
								>
									<i className="bi bi-github"></i>
								</a>
							</p>
							<div className="flex gap-2 mt-1">
								<button className="h-8 w-8 bg-[#1a1a1a] rounded-full flex items-center justify-center border border-gray-700">
									<i className="bi bi-pencil text-white text-sm"></i>
								</button>
								<button className="h-8 w-8 bg-[#1a1a1a] rounded-full flex items-center justify-center border border-gray-700">
									<i className="bi bi-x text-white text-sm"></i>
								</button>
							</div>
						</li>
					))
				)}
			</ul>
			<button
				className="mt-4 px-4 py-2 bg-yellow-400 text-black rounded hover:bg-yellow-500 flex items-center gap-2"
				onClick={onAddClick}
			>
				<i className="bi bi-plus text-white"></i> Add {title}
			</button>
		</div>
	);
}

export default Section;
