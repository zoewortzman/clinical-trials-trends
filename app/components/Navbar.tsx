// import { useEffect, useState } from "react";
import Link from "next/link";

// Navbar at top of page that allows user to toggle between Data and Insights
export default function Navbar() {
    return (
        <main>
            <div className="container mx-auto flex justify-between items-center py-4 pr-8">
                <h1 className="text-xl font-semibold text-gray-700">Clinical Trials Trends</h1>
                <div className="flex space-x-4"> 
                    <Link
                        href={'/'}
                        className="block px-4 py-2 bg-gray-100 rounded text-black hover:bg-gray-200"
                    >
                        {'Data'}
                    </Link>

                    <Link
                        href={'/Insights'}
                        className="block px-4 py-2 bg-gray-100 rounded text-black hover:bg-gray-200"
                    >
                        {'Insights'}
                    </Link>
                </div>
            </div>
        </main>
    );
}
