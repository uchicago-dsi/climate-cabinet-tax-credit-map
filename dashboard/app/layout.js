import "./globals.css";
import { Lato } from "next/font/google";

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
