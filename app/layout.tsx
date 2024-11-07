import type { Metadata } from "next";
import Navbar from './components/Navbar'
import "./globals.css";

export const metadata: Metadata = {
  title: "Clinical Trials Trends",
  description: "Shows trends in clinical trials data",
};

// displays navbar with tabs "Data" and "Insights"
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
