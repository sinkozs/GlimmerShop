import React, { useState, useEffect } from "react";
import Chart from "react-apexcharts";
import axios from "axios";
import { Container, Col } from "react-bootstrap";
import "../styles/SellerStatistics.css";

function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");
}

function SellerStatistics() {
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [totalRevenue, setTotalRevenue] = useState(0);
  const token = localStorage.getItem("token");

  const [chartData, setChartData] = useState({
    series: [
      {
        name: "Quantity Sold",
        data: [],
      },
    ],
    options: {
      chart: {
        type: "bar",
        height: 350,
      },
      plotOptions: {
        bar: {
          horizontal: false,
          columnWidth: "55%",
          endingShape: "rounded",
        },
      },
      dataLabels: {
        enabled: false,
      },
      xaxis: {
        categories: [],
      },
      yaxis: {
        title: {
          text: "Quantity Sold",
        },
      },
      fill: {
        opacity: 1,
      },
      tooltip: {
        y: {
          formatter: function (val) {
            return val + " units";
          },
        },
      },
    },
  });

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        let monthRequest = { month: "2024-10" };
        const response = await axios.post(
          `http://localhost:8000/seller-statistics/get-monthly-transactions`,
          monthRequest,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );
          
        const quantities = response.data.product_quantities;
        const categories = response.data.product_categories;
        const unitPrices = response.data.item_unit_prices;
        const productNames = Object.keys(quantities);
        const productQuantities = Object.values(quantities);
        const productCategories = Object.values(categories)
        const productPrice = Object.values(unitPrices);

        console.log(productCategories)

        const productRevenues = productQuantities.map((quantity, index) => {
          return quantity * productPrice[index];
        });

        const updatedCategories = productNames.map((name, index) => {
          return `${name} ($${formatNumber(productRevenues[index])})`;
        });

        setChartData((prevData) => ({
          ...prevData,
          series: [
            {
              ...prevData.series[0],
              data: productQuantities,
            },
          ],
          options: {
            ...prevData.options,
            xaxis: {
              ...prevData.options.xaxis,
              categories: updatedCategories,
            },
          },
        }));

        setTotalRevenue(response.data.total_revenue);
        setTotalTransactions(response.data.total_transactions);
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    };
    fetchStatistics();
  }, []);

  return (
    <Container fluid className="seller-stats-wrapper">
      <Container>
        <h3>Total monthly revenue: ${formatNumber(totalRevenue)}</h3>
        <h3>Total number of transactions: {totalTransactions}</h3>

        <Col md={6} className="chart-container">
          <h3 className="chart-title">Products Sold</h3>
          <Chart
            type="bar"
            width="100%"
            height={350}
            series={chartData.series}
            options={chartData.options}
          />
        </Col>
      </Container>
    </Container>
  );
}

export default SellerStatistics;
