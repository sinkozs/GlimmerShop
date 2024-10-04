import React, { useEffect, useState } from "react";
import { Container, Form, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import axios from "axios";
import ProductsGrid from "../components/ProductsGrid";
import "../App.css";
import "../styles/Home.css";
import "../styles/SellerHome.css";

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
          `http://localhost:8000/users/public/${seller_id}`
        );
        setSellerData(seller.data);

        const sellerProducts = await axios.get(
          `http://127.0.0.1:8000/products/products-by-seller`,
          {
            params: { seller_id: seller_id },
          }
        );
        setProducts(sellerProducts.data);
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
        `http://127.0.0.1:8000/products/search/`,
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

      <ProductsGrid products={products} isAuthenticated={true} />

    </Container>
  );
}

export default SellerHome;
