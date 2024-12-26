import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Container, Form, Button, ListGroup, Table } from "react-bootstrap";
import Modal from "./Modal";
import config from "../config";
import "../styles/LoginAndSignup.css";
import "../styles/Category.css";

function AddNewCategoryToProduct() {
  const [currentCategories, setCurrentCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [newCategoryName, setNewCategoryName] = useState("");
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalText, setModalText] = useState("");
  const [error, setError] = useState(null);
  const { product_id } = useParams();

  const fetchProductCategories = async () => {
    try {
      const response = await axios.get(
        `${config.BACKEND_BASE_URL}/categories/product-categories`,
        {
          params: { product_id },
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );
      setCurrentCategories(response.data);
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    }
  };

  useEffect(() => {
    fetchProductCategories();
  }, [product_id]);

  const handleCategoryDelete = async (categoryId) => {
    try {
      const requestData = {
        product_id: product_id,
        category_id: categoryId,
      };

      const response = await axios.delete(
        `${config.BACKEND_BASE_URL}/categories/delete-category-from-product`,
        {
          data: requestData,
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      if (response.status === 200) {
        fetchProductCategories();
      }
    } catch (error) {
      console.error("Failed to delete product category:", error);
    }
  };

  const fetchCategories = async (query) => {
    try {
      const response = await axios.get(
        `${config.BACKEND_BASE_URL}/categories/search`,
        { params: { query } }
      );
      setCategories(response.data);
      setShowDropdown(true);

      if (response.data.length == 0) {
        console.log("empty");
      }
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

  const handleAddCategoryToProduct = async (e) => {
    e.preventDefault();
    try {
      let categoryId = selectedCategoryId;

      if (!selectedCategoryId && newCategoryName) {
        const newCategoryRequest = {};
        if (newCategoryName !== "")
          newCategoryRequest.category_name = newCategoryName;
        try {
          const newCategoryResponse = await axios.post(
            `${config.BACKEND_BASE_URL}/categories/new`,
            newCategoryRequest,
            {
              headers: { "Content-Type": "application/json" },
              withCredentials: true,
            }
          );
          categoryId = newCategoryResponse.data;
        } catch (error) {
          setModalTitle("Error");
          setModalText(error.response.data.detail);
          setShowModal(true);
          return;
        }
      }

      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/categories/add-category-to-product`,
        {
          product_id: product_id,
          category_id: categoryId,
        },
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      if (response.status === 200) {
        setModalTitle("Success");
        setModalText(response.data.message);
        setShowModal(true);
        fetchProductCategories();
      }
    } catch (error) {
      setModalTitle("Error");
      setModalText(error.response.data.detail);
      setShowModal(true);
    }
  };

  const closeModal = () => setShowModal(false);

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <h1 className="login-form-h1">PRODUCT CATEGORIES</h1>
        <h3 className="category-h3">Current Categories</h3>
        {currentCategories.length > 0 ? (
          <Table className="category-table">
            <tbody>
              {currentCategories.map((categoryMap, index) => {
                const [categoryId, categoryName] =
                  Object.entries(categoryMap)[0];
                return (
                  <tr key={index}>
                    <td className="category-table-text">{categoryName}</td>
                    <td>
                      <Button
                        className="admin-btn"
                        variant="danger"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCategoryDelete(categoryId);
                        }}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        ) : (
          <p>No categories available.</p>
        )}

        <Container fluid>
          <h3 className="category-h3">
            Add an existing category to the product
          </h3>
          <Form>
            <Form.Control
              type="text"
              placeholder="Search categories by name"
              value={searchQuery}
              onChange={handleInputChange}
              className="form-control"
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
                  >
                    {category.category_name}
                  </ListGroup.Item>
                ))
              ) : (
                <ListGroup.Item>No categories found</ListGroup.Item>
              )}
            </ListGroup>
          )}

          <Container fluid>
            <h3 className="category-h3">Add a new category</h3>
            <Form.Group controlId="newCategoryName" className="form-group">
              <Form.Control
                type="text"
                placeholder="New Category Name"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                className="form-control"
              />
            </Form.Group>
          </Container>

          {error && <section className="error-message">{error}</section>}

          <Button
            onClick={handleAddCategoryToProduct}
            variant="primary"
            type="submit"
            className="login-btn"
          >
            SAVE
          </Button>

          <Modal show={showModal} onClose={closeModal} title={modalTitle}>
            <section>{modalText}</section>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewCategoryToProduct;
