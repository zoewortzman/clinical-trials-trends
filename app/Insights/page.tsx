'use client'
import { useState, useEffect } from 'react';

export default function Insights() {
    const [elderlyCount, setElderlyCount] = useState(null);
    const [totalCount, setTotalCount] = useState(null);
    const [percentageElderly, setPercentageElderly] = useState(''); 

    useEffect(() => {
      const fetchElderlyPercentage = async () => {
        try {
          const response = await fetch('/api/insights');
          const data = await response.json();
          setElderlyCount(data.elderlyCount);
          setTotalCount(data.totalCount);
        } catch (error) {
          console.error("Error fetching data", error);
        }
      };

      fetchElderlyPercentage();
    }, []); 

    useEffect(() => {
      if (elderlyCount !== null && totalCount !== null) {
        const calcPercentage = (elderlyCount / totalCount) * 100;
        setPercentageElderly(calcPercentage.toFixed(2)); 
      }
    }, [elderlyCount, totalCount]);  

    return (
      <div className="px-20">
        {percentageElderly !== null ? (
          <ul className="list-disc text-gray-700">
            <li className="text-gray-700">{percentageElderly}% of studies involve elderly patients</li>
          </ul>
        ) : (
          <p>Loading...</p> 
        )}
      </div>
    );
}
