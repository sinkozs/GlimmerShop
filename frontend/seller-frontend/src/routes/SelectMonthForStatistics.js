import React, { useEffect, useState } from "react";
import { Container } from "react-bootstrap";
import "../styles/SellerStatistics.css";

function SelectMonthForStatistics({
  setSelectedMonth,
  setSelectedYear,
  defaultMonth,
  defaultYear,
}) {
  const [currentSelectedMonth, setCurrentSelectedMonth] = useState(defaultMonth);
  const [currentSelectedYear, setCurrentSelectedYear] = useState(defaultYear);

  const months = [
    { name: "January", value: "01" },
    { name: "February", value: "02" },
    { name: "March", value: "03" },
    { name: "April", value: "04" },
    { name: "May", value: "05" },
    { name: "June", value: "06" },
    { name: "July", value: "07" },
    { name: "August", value: "08" },
    { name: "September", value: "09" },
    { name: "October", value: "10" },
    { name: "November", value: "11" },
    { name: "December", value: "12" },
  ];

  const startYear = 2024;
  const endYear = new Date().getFullYear();
  const years = Array.from(
    { length: endYear - startYear + 1 },
    (v, i) => startYear + i
  );

  const handleMonthChange = (event) => {
    const newMonth = event.target.value;
    setCurrentSelectedMonth(newMonth);
    setSelectedMonth(newMonth);
  };

  const handleYearChange = (event) => {
    const newYear = event.target.value;
    setCurrentSelectedYear(newYear);
    setSelectedYear(newYear);
  };

  useEffect(() => {
    setCurrentSelectedMonth(defaultMonth);
    setCurrentSelectedYear(defaultYear);
    setSelectedMonth(defaultMonth);
    setSelectedYear(defaultYear);
  }, [defaultMonth, defaultYear, setSelectedMonth, setSelectedYear]);

  return (
    <Container className="select-date-form">
      <label>
        Month: 
        <select value={currentSelectedMonth} onChange={handleMonthChange}>
          {months.map((m) => (
            <option key={m.value} value={m.value}>
              {m.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        Year:
        <select value={currentSelectedYear} onChange={handleYearChange}>
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </label>
    </Container>
  );
}

export default SelectMonthForStatistics;
