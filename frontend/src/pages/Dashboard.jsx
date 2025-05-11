import Header from "../components/Header";
import ProfileCard from "../components/ProfileCard";
import Section from "../components/Section";

function Dashboard() {
	const dummyData = [
		{
			title: "AI Project",
			description: "A neural net for image classification",
			github_link: "#",
		},
	];

	return (
		<div className="mx-auto flex flex-col gap-6">
			<Header />
			<div className="min-w-[90%] mx-auto py-4 flex flex-col gap-6">
				{/* <ProfileCard /> */}
				<div className="grid grid-cols-1 md:grid-cols-3 gapx-7">
					<Section title="Projects" data={dummyData} />
					<Section title="Foreign Languages" data={[]} />
					<Section title="Technical Certifications" data={[]} />
				</div>
			</div>
		</div>
	);
}

export default Dashboard;
