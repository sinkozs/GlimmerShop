import React, { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import "../styles/LoginAndSignup.css";
import Modal from "./Modal";
import { Container, Form, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";

function DeleteProduct() {
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const seller_id = localStorage.getItem("sellerId");
  const token = localStorage.getItem("token");
  const { product_id } = useParams();

  useEffect(() => {
    const deleteProduct = async () => {
      console.log({ product_id });
      try {
        await axios.delete(
          `http://localhost:8000/products/delete/${product_id}`
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
