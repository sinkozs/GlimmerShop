import React, { useEffect, useState } from "react";
import { Container, Form, Button, ListGroup } from "react-bootstrap";
import "../styles/FilterBySeller.css";
import apiClient from "../utils/apiConfig";

function FilterBySeller({ resetFilter, onSellerSelected }) {
  const [isSellerFilterExpanded, setIsSellerFilterExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sellers, setSellers] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (resetFilter) {
      onSellerSelected(null);
    }
  }, [resetFilter, onSellerSelected]);

  const fetchSellers = async (query) => {
    try {
      const response = await apiClient.get(
        `/users/sellers/search/`,
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
    onSellerSelected(seller.id);
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
          {error && <section className="error-message">{error}</section>}
        </Container>
      )}
    </Container>
  );
}

export default FilterBySeller;
