import React, { useEffect, useState } from "react";
import "../App.css";
import "../styles/Home.css";
import "../styles/SellerHome.css";
import Modal from "../components/Modal";
import { Container, Form, Button } from "react-bootstrap";
import { useLocation } from "react-router-dom";
import axios from "axios";
import ProductsGrid from "../components/ProductsGrid";

function SellerHome() {
  const [products, setProducts] = useState(null);
  const [sellerData, setSellerData] = useState(null);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const location = useLocation();
  const { sellerId } = location.state || {};

  useEffect(() => {
    const fetchSellerDataAndProducts = async () => {
      try {
        const seller = await axios.get(
          `http://localhost:8000/users/public/${sellerId}`
        );
        console.log(seller.first_name);
        setSellerData(seller.data);

        const sellerProducts = await axios.get(
          `http://127.0.0.1:8000/products/products-by-seller`,
          {
            params: { seller_id: sellerId },
          }
        );
        setProducts(sellerProducts.data);
      } catch (error) {
        console.error("Error fetching event details:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };
    if (sellerId) {
      fetchSellerDataAndProducts();
    }
  }, [sellerId]);

  const handleSearch = async (event) => {
    event.preventDefault();
    try {
      console.log(searchQuery);
      const response = await axios.get(
        `http://127.0.0.1:8000/products/search`,
        {
          params: { query: searchQuery, seller_id: sellerId },
        }
      );
      setProducts(response.data);
    } catch (error) {
      console.error("Error searching products:", error);
      setError("Failed to search products. Please try again later.");
    }
  };

  return (
    <Container fluid className="seller-home-wrapper">
      <Container fluid className="seller-home-header-section">
        {sellerData && <h1>Hello {sellerData.first_name}!</h1>}
        {error && <p>{error}</p>}

        <Form onSubmit={handleSearch} className="seller-home-searchbar">
          <Form.Control
            type="text"
            placeholder="Search products by name"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button type="submit" className="submit-search-btn">
            Search
          </Button>
        </Form>
      </Container>

      <ProductsGrid products={products} />
    </Container>
  );
}

export default SellerHome;
