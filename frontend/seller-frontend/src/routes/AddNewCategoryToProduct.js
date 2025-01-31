import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import {
  Container,
  Form,
  Button,
  ListGroup,
  Table,
  Spinner,
} from "react-bootstrap";
import Modal from "../components/Modal";
import apiClient from "../utils/apiConfig";
import "../styles/Form.css";
import "../styles/Category.css";
import { debounce } from "lodash";

function AddNewCategoryToProduct() {
  const [currentCategories, setCurrentCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [newCategoryName, setNewCategoryName] = useState("");
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [selectedCategoryToDelete, setSelectedCategoryToDelete] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalText, setModalText] = useState("");
  const [error, setError] = useState(null);
  const { product_id } = useParams();
  const [isLoading, setIsLoading] = useState(false);

  const fetchProductCategories = async () => {
    try {
      const category = await apiClient.get(
        `/categories/product-categories/${product_id}`
      );
      const categoryEntries = Object.entries(category.data);

      if (categoryEntries.length === 1) {
        setCurrentCategories([
          {
            id: categoryEntries[0][0],
            name: categoryEntries[0][1],
          },
        ]);
      } else {
        setCurrentCategories(
          categoryEntries.map((entry) => ({
            id: entry[0],
            name: entry[1],
          }))
        );
      }
    } catch (error) {
      console.error("Failed to fetch categories:", error);
    }
  };

  useEffect(() => {
    fetchProductCategories();
  }, [product_id]);

  const handleCategoryDelete = (categoryId) => {
    setSelectedCategoryToDelete(categoryId);
    setModalTitle("Warning");
    setModalText("Do you want to delete this category?");
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      const response = await apiClient.delete(
        `/categories/delete-category-from-product`,
        {
          data: {
            product_id: product_id,
            category_id: selectedCategoryToDelete,
          },
        }
      );

      if (response.status === 200) {
        await fetchProductCategories();
        setShowDeleteModal(false);
      }
    } catch (error) {
      console.error("Failed to delete product category:", error);
      setModalTitle("Error");
      setModalText("Failed to delete category");
    }
  };

  const debouncedFetch = useCallback(
    debounce(async (query) => {
      if (!query) {
        setCategories([]);
        setShowDropdown(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get(`/categories/search/`, {
          params: { query: query },
        });
        setCategories(response.data);
        setShowDropdown(true);
      } catch (error) {
        console.error("Error searching categories:", error);
        setError("Failed to search categories");
      } finally {
        setIsLoading(false);
      }
    }, 300),
    []
  );

  const handleInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    debouncedFetch(query);
  };

  const handleAddExistingCategoryToProduct = async (e) => {
    e.preventDefault();
    try {
      let categoryId = selectedCategoryId;

      const response = await apiClient.post(
        `/categories/add-category-to-product`,
        {
          product_id: product_id,
          category_id: categoryId,
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

  const handleAddNewCategoryToProduct = async (e) => {
    e.preventDefault();
    try {
      const newCategoryRequest = {};
      if (newCategoryName !== "") {
        newCategoryRequest.category_name = newCategoryName;
      }
      try {
        const newCategoryResponse = await apiClient.post(
          `/categories/new`,
          newCategoryRequest
        );
        var categoryId = newCategoryResponse.data;

        const response = await apiClient.post(
          `/categories/add-category-to-product`,
          {
            product_id: product_id,
            category_id: categoryId,
          }
        );
        
        if (response.status === 200) {
          setModalTitle("Success");
          setModalText(response.data.message);
          setShowModal(true);
          fetchProductCategories();
          setNewCategoryName("");
        }
      } catch (error) {
        setModalTitle("Error");
        setModalText(error.response.data.detail);
        setShowModal(true);
      }
    } catch (error) {
      setModalTitle("Error");
      setModalText(error.response.data.detail);
      setShowModal(true);
    }
  };

  const closeModal = () => setShowModal(false);
  const closeDeleteModal = () => setShowDeleteModal(false);

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="form-container">
        <h1 className="form-h1">PRODUCT CATEGORIES</h1>
        <h3 className="category-h3">Current Categories</h3>
        {currentCategories.length > 0 ? (
          <Table className="category-table">
            <tbody>
              {currentCategories.map((category) => (
                <tr key={category.id}>
                  <td className="category-table-text">{category.name}</td>
                  <td>
                    <Button
                      className="admin-btn"
                      variant="danger"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCategoryDelete(category.id);
                      }}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
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
          {isLoading && (
            <div className="text-center mt-2">
              <Spinner animation="border" size="sm" />
            </div>
          )}
          {showDropdown && (
            <ListGroup className="search-dropdown">
              {categories.length > 0 ? (
                categories.map((category) => (
                  <ListGroup.Item
                    key={category.id}
                    onClick={() => {
                      setSelectedCategoryId(category.id);
                      setSearchQuery(category.category_name);
                      setShowDropdown(false);
                    }}
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
          <Button
            onClick={handleAddExistingCategoryToProduct}
            variant="primary"
            type="submit"
            className="login-btn"
          >
            ADD
          </Button>
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
            onClick={handleAddNewCategoryToProduct}
            variant="primary"
            type="submit"
            className="login-btn"
          >
            SAVE
          </Button>

          <Modal show={showModal} onClose={closeModal} title={modalTitle}>
            <section>{modalText}</section>
          </Modal>

          <Modal show={showDeleteModal} onClose={closeDeleteModal} title={modalTitle}>
            <section>{modalText}</section>
            <Container className="modal-footer">
              <button
                className="modal-btn confirm-btn"
                onClick={handleConfirmDelete}
              >
                Confirm
              </button>
            </Container>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewCategoryToProduct;