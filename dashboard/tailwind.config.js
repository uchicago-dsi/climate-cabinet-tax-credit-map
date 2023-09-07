/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    fontFamily: {
      sans: ["Lato", "sans-serif"],
    },
    extend: {
      colors: {
        ccgray: { dark: "#333333", light: "#737373" },
        ccorange: "#C36C27",
      },
    },
  },
  plugins: [
    require("daisyui"),
    require("@tailwindcss/typography")
  ],
};
