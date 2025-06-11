import React, { useState, useEffect, useRef } from "react";

const Autocomplete = ({
	suggestions,
	placeholder,
	onSelect,
	selectedItems = [],
	label,
	className = "",
	id,
	allowNew = true,
}) => {
	const [inputValue, setInputValue] = useState("");
	const [filteredSuggestions, setFilteredSuggestions] = useState([]);
	const [isVisible, setIsVisible] = useState(false);
	const wrapperRef = useRef(null);

	// Filter suggestions based on input value
	useEffect(() => {
		if (!inputValue.trim()) {
			setFilteredSuggestions([]);
			return;
		}

		const filtered = suggestions.filter(
			(suggestion) =>
				!selectedItems.includes(suggestion.id) &&
				suggestion.name.toLowerCase().includes(inputValue.toLowerCase())
		);

		setFilteredSuggestions(filtered);
	}, [inputValue, suggestions, selectedItems]);

	// Handle click outside to close dropdown
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (
				wrapperRef.current &&
				!wrapperRef.current.contains(event.target)
			) {
				setIsVisible(false);
			}
		};

		document.addEventListener("mousedown", handleClickOutside);
		return () => {
			document.removeEventListener("mousedown", handleClickOutside);
		};
	}, []);

	const handleInputChange = (e) => {
		setInputValue(e.target.value);
		setIsVisible(true);
	};

	const handleSuggestionClick = (suggestion) => {
		onSelect(suggestion);
		setInputValue("");
		setIsVisible(false);
	};

	const handleAddNew = () => {
		if (!inputValue.trim()) return;

		// Create a new item with the input value
		const newItem = {
			id: `new-${Date.now()}`, // Temporary ID for new items
			name: inputValue.trim(),
			isNew: true, // Flag to identify newly created items
		};

		onSelect(newItem);
		setInputValue("");
		setIsVisible(false);
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter") {
			e.preventDefault();

			// If there's a filtered suggestion, select the first one
			if (filteredSuggestions.length > 0) {
				handleSuggestionClick(filteredSuggestions[0]);
			} else if (allowNew && inputValue.trim()) {
				handleAddNew();
			}
		}
	};

	return (
		<div className="relative" ref={wrapperRef}>
			{label && (
				<label className="block text-white mb-2" htmlFor={id}>
					{label}
				</label>
			)}
			<input
				type="text"
				id={id}
				value={inputValue}
				onChange={handleInputChange}
				onFocus={() => setIsVisible(true)}
				onKeyDown={handleKeyDown}
				placeholder={placeholder}
				className={`w-full p-2 bg-neutral-800 border border-gray-700 rounded text-white focus:outline-none focus:border-flex-yellow ${className}`}
			/>

			{isVisible && (
				<div className="absolute z-10 w-full mt-1 bg-flex-dark border border-gray-700 rounded shadow-flex max-h-48 overflow-y-auto">
					{filteredSuggestions.length > 0 ? (
						filteredSuggestions.map((suggestion) => (
							<div
								key={suggestion.id}
								className="p-2 cursor-pointer hover:bg-gray-700 text-white"
								onClick={() =>
									handleSuggestionClick(suggestion)
								}
							>
								{suggestion.first_name || suggestion.name}
							</div>
						))
					) : inputValue.trim() && allowNew ? (
						<div
							className="p-2 cursor-pointer hover:bg-gray-700 text-flex-yellow"
							onClick={handleAddNew}
						>
							Add "{inputValue}"
						</div>
					) : (
						<div className="p-2 text-gray-400">
							No suggestions found
						</div>
					)}
				</div>
			)}
		</div>
	);
};

export default Autocomplete;
