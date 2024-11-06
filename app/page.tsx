"use client";
import Table from "./components/Table";

export default function Home() {
  return (<div className="bg-blue-700 text-white p-10">
      <div className="overflow-x-auto">
        <Table />
      </div>
  </div>
  )
}
