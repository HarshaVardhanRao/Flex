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
		<div className="w-[90%] mx-auto my-8 flex flex-col gap-6">
			<Header />
			<ProfileCard />
			<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
				<Section title="Projects" data={dummyData} />
				<Section title="Foreign Languages" data={[]} />
				<Section title="Technical Certifications" data={[]} />
			</div>
		</div>
	);
}

export default Dashboard;
