import "./globals.css";
import { Lato } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export const metadata = {
  title: "Climate Cabinet - Inflation Reduction Act (IRA) Credits",
  description:
    "Interactive map showing tax credit areas from the Inflation Reduction Act",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <main className="w-full">
          <div className="w-full p-5">
            <Header />
          </div>
          <div>
            {children}
          </div>
          <div className="p-5">
            <Footer />
          </div>
        </main>
      </body>
    </html>
  );
}
