import type { Metadata } from "next";
import Navbar from './components/Navbar'
import "./globals.css";

export const metadata: Metadata = {
  title: "Clinical Trials Trends",
  description: "Shows trends in clinical trials data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">

      <body>
      <div>

      <Navbar />

      
        {children}
      </div>
      </body>
  
    
    </html>
  );
}
