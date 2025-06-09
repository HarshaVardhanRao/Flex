import { useNavigate } from "react-router-dom";
import ApiService from "../services/api";

function Section({ title, data = [], onAddClick }) {
	const navigate = useNavigate();
	return (
		<div className="bg-flex-dark text-white p-6 rounded-lg shadow-flex animate-moveUp">
			<h2 className="text-center text-3xl font-bold text-flex-yellow mb-4">
				{title}
			</h2>
			<hr className="border-flex-yellow mb-4" />
			<ul className="h-[300px] overflow-y-auto bg-flex-black p-2 rounded-lg space-y-4 scrollbar-none overflow-auto">
				{data.length === 0 ? (
					<li className="text-gray-400">No data available.</li>
				) : (
					data.map((item, idx) => (
						<>
							<li key={idx}>
								<h5 className="text-flex-yellow font-semibold">
									{item.title}
								</h5>
								<p>{item.description}</p>
								<p>
									<a
										href={item.github_link}
										target="_blank"
										rel="noopener noreferrer"
										className="text-flex-yellow hover:text-flex-yellow-dark"
									>
										<i className="bi bi-github"></i>
									</a>
								</p>
								<div className="flex gap-2 mt-1">
									{/* Edit button - only for projects */}
									<button
										className="h-8 w-8 bg-primary rounded-[10px] flex items-center justify-center border border-gray-700 hover:bg-flex-yellow transition-all"
										onClick={() => {
											if (
												title === "Projects" &&
												item.id
											) {
												navigate(
													`/dashboard/edit-project/${item.id}`
												);
											}
										}}
									>
										<i className="bi bi-pencil text-flex-yellow text-lg hover:text-white transition-all"></i>
									</button>
									{/* Delete button */}
									<button
										className="h-8 w-8 bg-primary rounded-[10px] flex items-center justify-center border border-gray-700 hover:bg-white transition-all"
										onClick={() => {
											// Confirm deletion
											if (
												window.confirm(
													`Are you sure you want to delete this ${title.slice(
														0,
														-1
													)}?`
												)
											) {
												// Handle deletion based on section type
												if (
													title === "Projects" &&
													item.id
												) {
													ApiService.deleteProject(
														item.id
													)
														.then((response) => {
															if (
																response.status ===
																200
															) {
																// Handle successful deletion (e.g., show a success message)
																alert(
																	"Project deleted successfully"
																);
																// Optionally, refresh the page or update the UI
																navigate(
																	"/dashboard"
																);
															}
														})
														.catch((error) => {
															// Handle error (e.g., show an error message)
															console.error(
																"Error deleting project:",
																error
															);
														});
												} else if (
													(title ===
														"Technical Certifications" ||
														title ===
															"Foreign Languages") &&
													item.id
												) {
													ApiService.deleteCertification(
														item.id
													)
														.then((response) => {
															if (
																response.status ===
																200
															) {
																alert(
																	"Certification deleted successfully"
																);
																// Optionally, refresh the page or update the UI
																navigate(
																	"/dashboard"
																);
															}
														})
														.catch((error) => {
															console.error(
																"Error deleting certification:",
																error
															);
														});
												}
											}
										}}
									>
										<i className="bi bi-x text-red-600 text-lg transition-all font-bold"></i>
									</button>
								</div>
							</li>
							{idx < data.length - 1 && (
								<hr className="border-gray-700" />
							)}
						</>
					))
				)}
			</ul>
			<button
				className="mt-4 px-4 py-2 bg-flex-yellow text-flex-black rounded-[20px] hover:bg-flex-yellow-dark transition-colors flex items-center gap-2"
				onClick={onAddClick}
			>
				<i className="bi bi-plus text-black"></i> Add {title}
			</button>
		</div>
	);
}

export default Section;
