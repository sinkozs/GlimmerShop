import React, { useState, useEffect } from "react";
import { Container, Card, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import Modal from "./Modal";
import "../styles/ProductsByCategory.css";
import "../App.css";
import "../styles/Home.css";
import "../styles/TrendingJewelry.css";
import "../styles/Modal.css";
import apiClient from "../utils/apiConfig";

function ProductsGrid({ products, isAuthenticated }) {
  const navigate = useNavigate();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);

  const [error, setError] = useState(null);

  const handleCardClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const handleEditClick = (productId) => {
    navigate(`/products/edit/${productId}`);
  };

  const handleDeleteClick = (productId) => {
    setProductToDelete(productId);
    setShowDeleteModal(true);
  };

  const closeModal = () => {
    setShowDeleteModal(false);
    setShowSuccessModal(false);
    setTimeout(() => {
      window.location.reload();
    }, 100);
  };

  const confirmDelete = async () => {
    try {
      await apiClient.delete(`/products/delete/${productToDelete}`, {
        headers: {
          "Content-Type": "application/json",
        },
        withCredentials: true,
      });

      setShowDeleteModal(false);
      setShowSuccessModal(true);
    } catch (error) {
      console.error("Failed to delete the product:", error);
      setError("Failed to delete the product.");
    }
  };

  return (
    <Container fluid className="category-products-wrapper">
      <Container fluid className="category-products-grid">
        {products.map((product, idx) => (
          <Card
            key={idx}
            className="category-products-card"
            onClick={() => handleCardClick(product.id)}
          >
            <Card.Body className="trending-card-body">
              <Container className="image-container">
                <Card.Img
                  variant="top"
                  className="trending-card-image"
                  src={`${apiClient.defaults.baseURL}/${product.image_path}`}
                />
                <Card.Img
                  variant="top"
                  className="trending-card-hover"
                  src={`${apiClient.defaults.baseURL}/${product.image_path2}`}
                />
              </Container>
            </Card.Body>
            <Card.Footer className="card-footer">
              <Card.Text className="footer-text">{product.name}</Card.Text>
              <Card.Text className="footer-text-price">
                ${product.price}
                {isAuthenticated && (
                  <Container className="admin-btn">
                    <Button
                      variant="primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditClick(product.id);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="danger"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick(product.id);
                      }}
                    >
                      Delete
                    </Button>
                  </Container>
                )}
              </Card.Text>
            </Card.Footer>
          </Card>
        ))}
      </Container>


      <Modal show={showDeleteModal} onClose={closeModal} title="Warning!">
        <section>Are you sure you want to delete this product?</section>
        <Container className="modal-footer">
          <button className="modal-btn confirm-btn" onClick={confirmDelete}>
            Confirm
          </button>
          <button className="modal-btn" onClick={closeModal}>
            Cancel
          </button>
        </Container>
      </Modal>

      <Modal show={showSuccessModal} onClose={closeModal} title="Success">
        <section>You successfully deleted the product.</section>
        <Container className="modal-footer">
          <button className="modal-btn" onClick={closeModal}>
            OK
          </button>
        </Container>
      </Modal>
    </Container>
  );
}

export default ProductsGrid;
