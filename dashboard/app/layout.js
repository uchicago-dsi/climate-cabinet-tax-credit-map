import "./globals.css";
import { Inter, Roboto, Lato } from "next/font/google";

// import Google fonts
const inter = Inter({ subsets: ["latin"] });
const roboto = Roboto({ subsets: ["latin"], weight: "100" });

export const metadata = {
  title: "Climate Cabinet - Inflation Reduction Act (IRA) Credits",
  description:
    "Interactive map showing tax credit areas from the Inflation Reduction Act",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
