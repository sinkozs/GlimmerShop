import React, { useEffect, useState } from "react";
import { Container, Form, Button, ListGroup } from "react-bootstrap";
import axios from "axios";
import "../styles/FilterBySeller.css";

function FilterBySeller({ selectedSeller, resetFilter, onSellerSelected }) {
  const [isSellerFilterExpanded, setIsSellerFilterExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sellers, setSellers] = useState([]);
  const [products, setProducts] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (resetFilter) {
      onSellerSelected([]);
    }
  }, [resetFilter, onSellerSelected]);

  const fetchSellers = async (query) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/users/search/`,
        {
          params: { query },
        }
      );
      setSellers(response.data);
      setShowDropdown(true);
    } catch (error) {
      console.error("Error searching sellers:", error);
      setError("Failed to search sellers. Please try again later.");
      setShowDropdown(false);
    }
  };

  const fetchSellerProducts = async (sellerId) => {
    try {
        console.log(sellerId)
      const sellerProducts = await axios.get(
        `http://127.0.0.1:8000/products/products-by-seller`,
        {
          params: { seller_id: sellerId },
        }
      );
      console.log(sellerProducts.data)
      setProducts(sellerProducts.data);
    } catch (error) {
      console.error("Error fetching products:", error);
      setError("Failed to fetch product details. Please try again later.");
    }
  };

  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (query.length > 0) {
      fetchSellers(query);
    } else {
      setShowDropdown(false);
    }
  };

  const handleSellerSelect = (seller) => {
    setSearchQuery(`${seller.first_name} ${seller.last_name}`);
    setShowDropdown(false);
    fetchSellerProducts(seller.id);
  };

  const toggleFilterBtn = () =>
    setIsSellerFilterExpanded(!isSellerFilterExpanded);

  return (
    <Container fluid className="filters-section-wrapper">
      <Button onClick={toggleFilterBtn} className="filter-expand-btn">
        Seller
        <span className="expand-icon">
          {isSellerFilterExpanded ? "-" : "+"}
        </span>
      </Button>

      {isSellerFilterExpanded && (
        <Container>
          <Form>
            <Form.Control
              type="text"
              className="filter-seller-searchbar"
              placeholder="Search sellers by name"
              value={searchQuery}
              onChange={handleInputChange}
            />
          </Form>

          {showDropdown && (
            <ListGroup className="search-dropdown">
              {sellers.length > 0 ? (
                sellers.map((seller, index) => (
                  <ListGroup.Item
                    key={index}
                    onClick={() => handleSellerSelect(seller)}
                    style={{ cursor: "pointer" }}
                    className="dropdown-item"
                  >
                    {seller.first_name} {seller.last_name}
                  </ListGroup.Item>
                ))
              ) : (
                <ListGroup.Item>No sellers found</ListGroup.Item>
              )}
            </ListGroup>
          )}
          {error && <p className="error-message">{error}</p>}
        </Container>
      )}
    </Container>
  );
}

export default FilterBySeller;
