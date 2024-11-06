import { useEffect, useState } from "react";
export default function Table() {
  const [data, setData] = useState([]);
  useEffect(() => {
    const fetchTable = async () => {
      try {
        const response = await fetch("/api/fetch-trials", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const result = await response.json();
        console.log("Fetched table:", result);
        if (result.data) {
          setData(result.data);
        } else {
          console.warn("No rows found in the response:", result);
        }
      } catch (error) {
        console.error("Error fetching table", error);
      }
    };
    fetchTable();
  }, []);

  return (
    <main className="p-10">
      <h2 className="text-2xl font-bold mb-4">Clinical Trials</h2>
      <table className="table-auto w-full border-collapse">
        <thead className="bg-blue-500 text-white">
          <tr>
            {data.length > 0 &&
              Object.keys(data[0]).map((header) => (
                <th
                  className="border-b px-4 py-2 text-left font-bold"
                  key={header}
                >
                  {header.replace("_", " ").toUpperCase()} 
                </th>
              ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              {Object.keys(item).map((key) => (
                <td
                  className="border-b px-4 py-2 text-left"
                  key={key}
                >
                  {item[key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
