"use client";
import Table from "./components/Table";

// Displays table with all clinical trials
export default function Home() {
  return (<div className="bg-blue-700 text-white p-10">
      <div className="overflow-x-auto">
        <Table />
      </div>
  </div>
  )
}
