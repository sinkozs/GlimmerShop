import React, { useState, useEffect } from "react";
import "../App.css";
import "../styles/LoginAndSignup.css";
import Modal from "../components/Modal";
import { Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import apiClient from "../utils/apiConfig";

function DeleteProduct() {
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const { product_id } = useParams();

  useEffect(() => {
    const deleteProduct = async () => {
      try {
        await apiClient.delete(
          `/products/delete/${product_id}`
        );
      } catch (error) {
        console.error("Error when deleting product:", error);
        setError("Failed to delete product. Please try again later.");
      }
    };

    deleteProduct();
  }, []);

  const toggleModal = () => {
    setShowModal(!showModal);
  };

  return (
    <Modal show={showModal} onHide={toggleModal}>
      <Modal.Header closeButton>
        <Modal.Title>Do you want to delete this product?</Modal.Title>
      </Modal.Header>

      <Modal.Footer>
        <Button variant="primary" onClick={toggleModal}>
          Submit
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default DeleteProduct;
