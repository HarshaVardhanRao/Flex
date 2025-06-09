import React from "react";

const TagList = ({ items, onRemove, getItemLabel }) => {
  console.log("TagList rendered with items:", items);
	return (
		<div className="flex flex-wrap gap-2 mt-2">
			{items.map((item) => (
				<div
					key={item.id || item}
					className="flex items-center bg-flex-yellow text-flex-black px-2 py-1 rounded-full"
				>
					<span className="mr-1">{getItemLabel(item)}</span>
					<button
						type="button"
						onClick={() => onRemove(item)}
						className="text-flex-black hover:text-gray-800 focus:outline-none"
					>
						<svg
							className="w-4 h-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			))}
		</div>
	);
};

export default TagList;
