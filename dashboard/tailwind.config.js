/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    fontFamily: {
      sans: ["Open Sans", "sans-serif"],
    },
    extend: {
      colors: {
        ccblack: "#070707",
        ccwhite: "#fbfbfb",
        ccblue: { dark: "#004AAD", light: "#416BB8" },
        ccgray: { dark: "#212121", light: "#eceef1" },
        ccorange: "#C36C27",
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
};
