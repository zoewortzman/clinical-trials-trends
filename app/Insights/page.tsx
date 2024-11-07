"use client";
import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Tooltip,
  Cell
} from "recharts";

// Each row of returned data is an object with this interface
interface StudyData {
  study_title: string;
  study_identifier: string;
  conditions: string;
  sponsor: string;
  source: string;
  created_at: string;
}

// Insights displays the number of studies from each source, a pie chart of common conditions, and a breakdown of clinical trials by sponsor
export default function Insights() {
  const [usCount, setUsCount] = useState(null);
  const [euCount, setEuCount] = useState(null);
  const [table, setTable] = useState<StudyData[]>([]);
  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28BEA", "#8DD1E1", "#FF6666", "#84DEDD", "#83A6ED", "#8884D8"];

  // load clinical trial counts by source
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const response = await fetch("/api/insights");
        const data = await response.json();
        setUsCount(data.usCount);
        setEuCount(data.euCount);
      } catch (error) {
        console.error("Error fetching data", error);
      }
    };

    fetchCounts();
  }, []);

  // load all clinical trials for visualizations
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
          setTable(result.data);
        } else {
          console.warn("No rows found in the response:", result);
        }
      } catch (error) {
        console.error("Error fetching table", error);
      }
    };
    fetchTable();
  }, []);

  // Counts number of studies for each sponsor
  const sponsorCount = table.reduce<{ [key: string]: number }>((acc, study) => {
    acc[study.sponsor] = (acc[study.sponsor] || 0) + 1;
    return acc;
  }, {});
  
  // Object to store sponsory names and count
  const chartData = Object.entries(sponsorCount)
    .map(([sponsor, count]) => ({ sponsor, count }))
    .sort((a, b) => b.count - a.count); 
  

  // finds 10 most common conditions, some conditions are seperated by '|', these are considered unique observations
  const getTopConditions = (table: StudyData[]) => {
    const conditionCount: { [key: string]: number } = {};

    table.forEach((item: StudyData) => {
      const conditions = item.conditions.split('|'); 
      conditions.forEach((condition: string) => {
        conditionCount[condition] = (conditionCount[condition] || 0) + 1;
      });
    });

    // Sorts conditions by frequency
    const sortedConditions = Object.entries(conditionCount)
      .sort((a, b) => b[1] - a[1]) 
      .slice(0, 10) 
      .map(([condition, count]) => ({ name: condition, value: count }));

    return sortedConditions;
  };

  const topConditions = getTopConditions(table);

  // display insights
  return (
    <main className="overflow-x-auto">
      <div className="px-20">
        {euCount !== null && usCount !== null ? (
          <ul className="list-disc text-gray-700">
            <li className="text-gray-700">
              {" "}
              The are {usCount} studies from ClinicalTrials.gov.
            </li>
            <li className="text-gray-700">
              {" "}
              The are {euCount} studies from EudraCT.
            </li>
          </ul>
        ) : (
          <p>Loading...</p>
        )}
      </div>

      {topConditions && topConditions.length > 0 && (
        <div className="mt-10">
          <p className="text-xl font-semibold text-gray-800 text-center pt-10">Top 10 Conditions across all recent studies</p>
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={topConditions}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={150}
                label
              >
                {topConditions.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-10 mb-20">
      <p className="text-xl font-semibold text-gray-800 text-center pt-10"> Frequency of sponsors across all studies</p>
      {sponsorCount && chartData && (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="sponsor" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
        
      )}
      </div>


    </main>
  );
}
