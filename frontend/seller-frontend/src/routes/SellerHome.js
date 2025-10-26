import React, { useEffect, useState } from "react";
import { Container, Form, Button } from "react-bootstrap";
import { useParams, useNavigate } from "react-router-dom";
import Modal from "../components/Modal";
import ProductsGrid from "../components/ProductsGrid";
import "../App.css";
import "../styles/SellerHome.css";
import apiClient from "../utils/apiConfig";

function SellerHome() {
  const [products, setProducts] = useState([]);
  const [sellerData, setSellerData] = useState(null);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNoProductsModal, setShowNoProductsModal] = useState(false);
  const [showNoSearchResultsModal, setShowNoSearchResultsModal] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const navigate = useNavigate();

  const { seller_id } = useParams();

  useEffect(() => {
    console.log("reloaaad")
    const fetchSellerDataAndProducts = async () => {
      try {
        const seller = await apiClient.get(`/users/${seller_id}`);
        setSellerData(seller.data);
        const sellerProducts = await apiClient.get(
          "/products/seller-dashboard",
          {
            params: { seller_id: seller_id },
          }
        );
        if (sellerProducts.data.length === 0) {
          setShowNoProductsModal(true);
        }
        setProducts(sellerProducts.data);
      } catch (error) {
        console.error("Error fetching products:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };

    if (seller_id) {
      fetchSellerDataAndProducts();
    }
  }, [seller_id, showNoSearchResultsModal, refreshTrigger]);

  const handleSearch = async (event) => {
    event.preventDefault();
    try {
      const response = await apiClient.get("/products/search/", {
        params: { query: searchQuery, seller_id: seller_id },
      });
      if (response.data.length === 0) {
        setShowNoSearchResultsModal(true);
      }
      setProducts(response.data);
    } catch (error) {
      console.error("Error searching products:", error);
      setError("Failed to search products. Please try again later.");
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setRefreshTrigger(prev => prev + 1)
  };

  const closeNoProductsModal = () => {
    setShowNoProductsModal(false);
  };

  const closeNoSearchResultsModal = () => {
    setShowNoSearchResultsModal(false);
    clearSearch();
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
          <Button
            type="button"
            className="submit-search-btn clear-search-btn"
            onClick={clearSearch}
          >
            Clear
          </Button>
        </Form>

        <Modal
          show={showNoProductsModal}
          onClose={closeNoProductsModal}
          title="No products found!"
        >
          <section>You haven't added any products yet.</section>
          <Button
            onClick={() => navigate("/products/new")}
            className="login-btn"
          >
            Add Your First Product
          </Button>
        </Modal>

        <Modal
          show={showNoSearchResultsModal}
          onClose={closeNoSearchResultsModal}
          title="No results found!"
        >
          <section>No products match your search query.</section>
        </Modal>
      </Container>

      {products && products.length > 0 && (
        <ProductsGrid products={products} isAuthenticated={true} />
      )}
    </Container>
  );
}

export default SellerHome;
