/***
 * Defines the root layout inherited by other pages in the application.
 */

import "./globals.css";

export const metadata = {
  title: "Climate Cabinet Tax Credit Bonus Map Widget",
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
        <div className="flex justify-center max-w-screen-xl mx-auto">
          <main className="w-screen">{children}</main>
        </div>
      </body>
    </html>
  );
}
