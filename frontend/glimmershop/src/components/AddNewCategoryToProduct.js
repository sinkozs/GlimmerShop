import React, { useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Container, Form, Button, ListGroup } from "react-bootstrap";
import Modal from "./Modal";
import config from "../config";

function AddNewCategoryToProduct() {
  const [categoryName, setCategoryName] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const { product_id } = useParams();

  const fetchCategories = async (query) => {
    try {
      const response = await axios.get(
        `${config.BACKEND_BASE_URL}/categories/search`,
        { params: { query } }
      );
      setCategories(response.data);
      setShowDropdown(true);
    } catch (error) {
      console.error("Error searching categories:", error);
      setError("Failed to search categories. Please try again later.");
      setShowDropdown(false);
    }
  };

  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length > 0) {
      fetchCategories(query);
    } else {
      setShowDropdown(false);
    }
  };

  const handleCategorySelect = (category) => {
    setSearchQuery(category.category_name);
    setSelectedCategoryId(category.id);
    setShowDropdown(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log(product_id);
      console.log(selectedCategoryId);

      const requestData = {
        product_id: product_id,
        category_id: selectedCategoryId,
      };

      await axios.post(
        `${config.BACKEND_BASE_URL}/categories/add-category-to-product`,
        requestData,
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      setShowModal(true);
    } catch (error) {
      console.error("Error adding category to product:", error);
      setError("Failed to add category to product. Please try again later.");
    }
  };

  const closeModal = () => setShowModal(false);

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <h3>Search categories</h3>
        <Container fluid className="login-form-content">
          <Form>
            <Form.Control
              type="text"
              className="filter-category-searchbar"
              placeholder="Search categories by name"
              value={searchQuery}
              onChange={handleInputChange}
            />
          </Form>

          {showDropdown && (
            <ListGroup className="search-dropdown">
              {categories.length > 0 ? (
                categories.map((category) => (
                  <ListGroup.Item
                    key={category.id}
                    onClick={() => handleCategorySelect(category)}
                    style={{ cursor: "pointer" }}
                    className="dropdown-item"
                  >
                    {category.category_name}
                  </ListGroup.Item>
                ))
              ) : (
                <ListGroup.Item>No categories found</ListGroup.Item>
              )}
            </ListGroup>
          )}

          {error && <section className="error-message">{error}</section>}

          <Button
            onClick={handleSubmit}
            variant="primary"
            type="submit"
            className="login-btn"
          >
            Add Category
          </Button>

          <Modal show={showModal} onClose={closeModal} title="Success!">
            <section>
              You successfully added the category to the product.
            </section>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewCategoryToProduct;
