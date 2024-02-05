import "./globals.css";
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
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="h-full">
        <div className="flex justify-center max-w-screen-xl mx-auto bg-ccwhite">
          <main className="w-screen">
            {/* <div className="max-w-7xl mx-auto py-5">
              <Header />
            </div> */}
            {children}
            {/* <div className="w-full py-5">
              <Footer />
            </div> */}
          </main>
        </div>
      </body>
    </html>
  );
}
