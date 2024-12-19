import React, { useEffect, useState, useContext } from "react";
import { Container, Form, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import axios from "axios";
import ProductsGrid from "../components/ProductsGrid";
import "../App.css";
import "../styles/Home.css";
import "../styles/SellerHome.css";
import config from "../config";

function SellerHome() {
  const [products, setProducts] = useState(null);
  const [sellerData, setSellerData] = useState(null);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  
  const { seller_id } = useParams();

  useEffect(() => {
    const fetchSellerDataAndProducts = async () => {
      try {
        const seller = await axios.get(
          `${config.BACKEND_BASE_URL}/users/${seller_id}`
        );
        setSellerData(seller.data.user);

        const sellerProducts = await axios.get(
          `${config.BACKEND_BASE_URL}/products/products-by-seller`,
          {
            params: { seller_id: seller_id },
          }
        );
        setProducts(sellerProducts.data.products);
      } catch (error) {
        console.error("Error fetching products:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };

    if (seller_id) {
      fetchSellerDataAndProducts();
    }
  }, [seller_id]);

  const handleSearch = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.get(
        `${config.BACKEND_BASE_URL}/products/search/`,
        {
          params: { query: searchQuery, seller_id: seller_id },
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
        {error && <section>{error}</section>}

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

      <ProductsGrid products={products} isAuthenticated={true} />

    </Container>
  );
}

export default SellerHome;
