import React, { useState, useEffect, useMemo } from "react";
import Chart from "react-apexcharts";
import axios from "axios";
import { Container, Col } from "react-bootstrap";
import "./SelectMonthForStatistics.js";
import "../styles/SellerStatistics.css";
import SelectMonthForStatistics from "./SelectMonthForStatistics.js";
import Modal from "./Modal";

function formatNumber(num) {
  return num ? num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.") : "0";
}

function getCategoryQuantities(productCategories, productQuantities) {
  const categoryQuantities = {};

  for (const productName in productQuantities) {
    if (productQuantities.hasOwnProperty(productName)) {
      const quantity = productQuantities[productName];
      const category = productCategories[productName];

      if (category) {
        categoryQuantities[category] = quantity;
      }
    }
  }

  return categoryQuantities;
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
  const [categories, setCategories] = useState([]);
  const [bestSeller, setBestSeller] = useState({});
  const [dataLoaded, setDataLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [noTransactionsFoundModal, setNoTransactionsFoundModal] =
    useState(false);

  const token = useMemo(() => localStorage.getItem("token"), []);

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

          if (response.status === 204) {
            setError(`No transactions were found in ${monthRequest.month}/${monthRequest.year}`);
            setNoTransactionsFoundModal(true);
          } else {
            const {
              item_unit_prices = {},
              product_categories = {},
              product_quantities = {},
              total_revenue = 0,
              total_transactions = 0,
            } = response.data;

            const productNames = Object.keys(product_quantities);
            const categoryQuantities = getCategoryQuantities(
              product_categories,
              product_quantities
            );

            const productRevenues = getProductRevenues(
              product_quantities,
              item_unit_prices
            );

            const categoryKeys = Object.keys(categoryQuantities);
            const categoryValues = Object.values(categoryQuantities);

            if (categoryKeys.length && categoryValues.length) {
              setPieChartData({
                series: categoryValues,
                options: {
                  labels: categoryKeys,
                },
              });
            }

            setChartData({
              series: [
                { name: "Revenue (USD)", data: Object.values(productRevenues) },
              ],
            });

            setProductNames(productNames);
            setTotalRevenue(total_revenue);
            setTotalTransactions(total_transactions);
            setBestSeller(getBestSellerProduct(product_quantities));
            setCategories(Object.values(product_categories));

            setDataLoaded(true);
          }
        } catch (error) {
          console.error("Error fetching statistics:", error);
        }
      };

      fetchStatistics();
    }
  }, [selectedMonth, selectedYear, token]);

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
          <p>{error}</p>
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
              options={{
                title: {
                  text: "Products sold by category ",
                },
                labels: categories,
                noData: { text: "Empty Data" },
              }}
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
