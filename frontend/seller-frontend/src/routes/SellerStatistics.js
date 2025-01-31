import React, { useState, useEffect } from "react";
import Chart from "react-apexcharts";
import { Container, Col } from "react-bootstrap";
import "./SelectMonthForStatistics.js";
import "../styles/SellerStatistics.css";
import SelectMonthForStatistics from "./SelectMonthForStatistics.js";
import Modal from "../components/Modal";
import apiClient from "../utils/apiConfig";

function formatNumber(num) {
  return num ? num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.") : "0";
}


function getBestSellerProduct(productQuantities) {
  let bestSeller = null;
  let maxQuantity = -Infinity;

  for (const product in productQuantities) {
    if (productQuantities.hasOwnProperty(product)) {
      const quantity = productQuantities[product];
      if (quantity > maxQuantity) {
        maxQuantity = quantity;
        bestSeller = product;
      }
    }
  }

  return { [bestSeller]: maxQuantity };
}

function getProductRevenues(productQuantities, unitPrices) {
  const productRevenues = {};

  for (const productName in productQuantities) {
    if (productQuantities.hasOwnProperty(productName)) {
      const quantity = productQuantities[productName];
      const price = unitPrices[productName];

      if (productName) {
        productRevenues[productName] = quantity * price;
      }
    }
  }

  return productRevenues;
}

function SellerStatistics() {
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear().toString();
  const currentMonth = (currentDate.getMonth() + 1).toString().padStart(2, "0");

  const [selectedYear, setSelectedYear] = useState(currentYear);
  const [selectedMonth, setSelectedMonth] = useState(currentMonth);

  const [totalTransactions, setTotalTransactions] = useState(0);
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [productNames, setProductNames] = useState([]);
  const [bestSeller, setBestSeller] = useState({});
  const [dataLoaded, setDataLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [noTransactionsFoundModal, setNoTransactionsFoundModal] =
    useState(false);

  const [pieChartData, setPieChartData] = useState({
    series: [],
    options: {
      chart: {
        type: "pie",
        height: 350,
      },
      labels: [],
      dataLabels: {
        enabled: true,
      },
      legend: {
        position: "bottom",
        onItemHover: {
          highlightDataSeries: false,
        },
      },
      tooltip: {
        y: {
          formatter: (val) => `${val} items`,
        },
      },
    },
  });

  const [chartData, setChartData] = useState({
    series: [{ name: "Product", data: [] }],
    options: {
      chart: { type: "bar", height: 350 },
      plotOptions: {
        bar: { horizontal: false, columnWidth: "55%", endingShape: "rounded" },
      },
      dataLabels: { enabled: false },
      xaxis: { categories: [] },
      yaxis: { title: { text: "Earnings (USD)" } },
      fill: { opacity: 1 },
      tooltip: { y: { formatter: (val) => val } },
    },
  });

  useEffect(() => {
    if (selectedMonth && selectedYear) {
      const fetchStatistics = async () => {
        try {
          const monthRequest = {
            year: `${selectedYear}`,
            month: `${selectedMonth.padStart(2, "0")}`,
          };

          const response = await apiClient.post(
            `/seller-statistics/get-monthly-transactions`,
            monthRequest
          );

          if (response.status === 204) {
            setError(
              `No transactions were found in ${monthRequest.month}/${monthRequest.year}`
            );
            setNoTransactionsFoundModal(true);
          } else {
            const {
              item_unit_prices = {},
              product_categories = {}, // Format: {earrings: 2, rings: 1, bracelets: 1}
              product_quantities = {},
              total_revenue = 0,
              total_transactions = 0,
            } = response.data;

            const categoryNames = Object.keys(product_categories);
            const categoryQuantities = Object.values(product_categories);

            setPieChartData({
              series: categoryQuantities,
              options: {
                chart: {
                  type: "pie",
                },
                labels: categoryNames,
                legend: {
                  position: "bottom",
                },
                dataLabels: {
                  enabled: true,
                },
                tooltip: {
                  y: {
                    formatter: (val) => `${val} items`,
                  },
                },
              },
            });

            const productNames = Object.keys(product_quantities);
            const productRevenues = getProductRevenues(
              product_quantities,
              item_unit_prices
            );

            setChartData({
              series: [
                { name: "Revenue (USD)", data: Object.values(productRevenues) },
              ],
              options: {
                xaxis: {
                  categories: Object.keys(productRevenues),
                },
              },
            });

            setProductNames(productNames);
            setTotalRevenue(total_revenue);
            setTotalTransactions(total_transactions);
            setBestSeller(getBestSellerProduct(product_quantities));

            setDataLoaded(true);
          }
        } catch (error) {
          console.error("Error fetching statistics:", error);
        }
      };

      fetchStatistics();
    }
  }, [selectedMonth, selectedYear]);

  const closeModal = () => {
    setNoTransactionsFoundModal(false);
  };

  return (
    <Container fluid className="seller-stats-wrapper">
      <Container className="wrapper">
        <h1>Monthly statistics</h1>
        <SelectMonthForStatistics
          setSelectedMonth={setSelectedMonth}
          setSelectedYear={setSelectedYear}
          defaultMonth={currentMonth}
          defaultYear={currentYear}
        />

        <Modal
          show={noTransactionsFoundModal}
          onClose={closeModal}
          title="No transactions were found!"
        >
          <section>{error}</section>
        </Modal>
        {dataLoaded && (
          <>
            <h3>Total monthly revenue: ${formatNumber(totalRevenue)}</h3>
            <h3>Total number of transactions: {totalTransactions}</h3>
            <h3>
              Bestseller product this month: {Object.keys(bestSeller)} (
              {Object.values(bestSeller)} pieces sold)
            </h3>
          </>
        )}

        {dataLoaded && (
          <Col md={6} className="chart-container">
            <Chart
              type="pie"
              width="100%"
              height={350}
              series={pieChartData.series}
              options={pieChartData.options}
            />
          </Col>
        )}
        {dataLoaded && (
          <Col md={6} className="chart-container">
            <Chart
              type="bar"
              width="100%"
              height={350}
              series={chartData.series}
              options={{
                title: {
                  text: "Earnings by Product",
                },
                noData: { text: "Empty Data" },
                labels: productNames,
              }}
            />
          </Col>
        )}
      </Container>
    </Container>
  );
}

export default SellerStatistics;
