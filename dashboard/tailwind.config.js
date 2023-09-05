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
        ccblack: { dark: "#070707", light: "#212121" },
        ccwhite: "#fbfbfb",
        ccblue: { dark: "#004AAD", light: "#416BB8" },
        ccgray: { dark: "#575758", light: "#eceef1" },
        ccindigo: "#423492",
        ccorange: "#C36C27",
        ccbeige: "#ecdcbc",
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
};
