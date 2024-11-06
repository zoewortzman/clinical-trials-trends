import type { Metadata } from "next";
import Navbar from './components/Navbar'
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

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
