/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
	theme: {
		extend: {
			colors: {
				"flex-black": "#000000",
				"flex-dark": "#1a1a1a",
				"flex-yellow": "#f1c40f",
				"flex-yellow-dark": "#f39c12",
			},
			boxShadow: {
				md: "0px 4px 12px rgba(241, 196, 15, 0.5)",
				"dark-sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
				flex: "0 4px 12px rgba(241, 196, 15, 0.4)",
			},
			animation: {
				moveUp: "moveUp 0.3s ease-in-out forwards",
				moveDown: "moveDown 0.3s ease-in-out forwards",
				moveRight: "moveRight 0.5s ease-in",
				moveLeft: "moveLeft 0.3s linear forwards",
				blur: "blur 0.3s ease-in-out forwards",
				scaleani: "scaleani 0.3s ease-in-out forwards",
			},
			keyframes: {
				moveUp: {
					"0%": { transform: "translateY(150px)", opacity: "0" },
					"100%": { transform: "translateY(0)", opacity: "1" },
				},
				moveDown: {
					"0%": { transform: "translateY(-10vh)", opacity: "0" },
					"100%": { transform: "translateY(0)", opacity: "1" },
				},
				moveRight: {
					"0%": { transform: "translateX(-90vw)", opacity: "0" },
					"100%": { transform: "translateX(0)", opacity: "1" },
				},
				moveLeft: {
					"0%": { transform: "translateX(150px)", opacity: "0" },
					"100%": { transform: "translateX(0)", opacity: "1" },
				},
				blur: {
					"0%": { backdropFilter: "blur(0px)" },
					"100%": { backdropFilter: "blur(8px)" },
				},
				scaleani: {
					"0%": { transform: "scale(0.8)", opacity: "0" },
					"100%": { transform: "scale(1)", opacity: "1" },
				},
			},
		},
	},
	plugins: [],
};
