import React, { useState, useEffect, useMemo } from "react";
import Chart from "react-apexcharts";
import axios from "axios";
import { Container, Col } from "react-bootstrap";
import "../styles/SellerStatistics.css";

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
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [totalRevenue, setTotalRevenue] = useState(0);
  const [productNames, setProductNames] = useState([]);
  const [categories, setCategories] = useState([]);
  const [bestSeller, setBestSeller] = useState({});
  const [dataLoaded, setDataLoaded] = useState(false);

  const token = useMemo(() => localStorage.getItem("token"), []);

  const [pieChartData, setPieChartData] = useState({
    series: [],
    options: {
      chart: { type: "pie", height: 350 },
      labels: [],
      dataLabels: {
        enabled: true,
        formatter: (val, opts) =>
          `${opts.w.globals.series[opts.seriesIndex]} units`,
      },
      tooltip: {
        y: { formatter: (val) => `${val} units` },
      },
      legend: { position: "bottom" },
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
    const fetchStatistics = async () => {
      try {
        const monthRequest = { month: "2024-10" };
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

        const {
          item_unit_prices = {},
          product_categories = {},
          product_quantities = {},
          total_revenue = 0,
          total_transactions = 0,
        } = response.data;

        const categories = Object.values(product_categories);
        const productNames = Object.keys(product_quantities);
        const categoryQuantities = getCategoryQuantities(
          product_categories,
          product_quantities
        );

        const productRevenues = getProductRevenues(
          product_quantities,
          item_unit_prices
        );
        setPieChartData({
          ...pieChartData,
          series: Object.values(categoryQuantities),
          options: {
            ...pieChartData.options,
            labels: Object.keys(categoryQuantities),
          },
        });

        setChartData({
          series: [
            { name: "Revenue (USD)", data: Object.values(productRevenues) },
          ],
        });

        setProductNames(productNames);
        setCategories(categories);
        setTotalRevenue(total_revenue);
        setTotalTransactions(total_transactions);
        setBestSeller(getBestSellerProduct(product_quantities));

        setDataLoaded(true);
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    };

    fetchStatistics();
  }, [token]);

  return (
    <Container fluid className="seller-stats-wrapper">
      <Container>
        <h3>Total monthly revenue: ${formatNumber(totalRevenue)}</h3>
        <h3>Total number of transactions: {totalTransactions}</h3>
        {dataLoaded && (
          <h3>
            Bestseller product this month: {Object.keys(bestSeller)} (
            {Object.values(bestSeller)} pieces sold)
          </h3>
        )}

        {dataLoaded && (
          <Col md={6} className="chart-container">
            <Chart
              type="pie"
              width="100%"
              height={350}
              series={pieChartData.series.length ? pieChartData.series : [0]}
              options={{
                title: {
                  text: "Products sold by category ",
                },
                noData: { text: "Empty Data" },
                labels: categories,
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
