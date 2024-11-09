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
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showModal, setShowModal] = useState(false);
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

  const addNewCategory = async (newCategoryName) => {
    try {
      console.log(newCategoryName);

      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/categories/new/${newCategoryName}`,
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      const newCategoryId = response.data;
      console.log(newCategoryId)

      fetchProductCategories();
    } catch (error) {
      console.error("Failed to add new category:", error);
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
        addNewCategory(query);
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

  const addExistingCategoryToProduct = async (e) => {
    e.preventDefault();
    try {
      const requestData = {
        product_id: product_id,
        category_id: selectedCategoryId,
      };

      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/categories/add-category-to-product`,
        requestData,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if (response.status === 200) {
        setModalText(response.data.message);
        setShowModal(true);
        fetchProductCategories();
      }
    } catch (error) {
      console.error("Error adding category to product:", error);
      setError("Failed to add category to product. Please try again later.");
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

        <h3 className="category-h3">Add a new category to the product</h3>
        <Container fluid className="login-form-content">
          <Form>
            <Form.Control
              type="text"
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
                  >
                    {category.category_name}
                  </ListGroup.Item>
                ))
              ) : (
                <ListGroup.Item>
                  {" "}
                  <Button
                    className="admin-btn"
                    variant="danger"
                    onClick={(e) => {
                      e.stopPropagation();
                      addNewCategory(searchQuery);
                    }}
                  >
                    Create new category
                  </Button>{" "}
                </ListGroup.Item>
              )}
            </ListGroup>
          )}

          {error && <section className="error-message">{error}</section>}

          <Button
            onClick={addExistingCategoryToProduct}
            variant="primary"
            type="submit"
            className="login-btn"
          >
            SAVE
          </Button>

          <Modal show={showModal} onClose={closeModal} title="Success!">
            <section>{modalText}</section>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewCategoryToProduct;
