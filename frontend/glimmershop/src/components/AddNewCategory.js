import React, { useState } from "react";
import axios from "axios";
import "../App.css";
import "../styles/AddNewProduct.css";
import "../styles/LoginAndSignup.css";
import Modal from "./Modal";
import { Container, Form, Button } from "react-bootstrap";
import config from "../config";

function AddNewCategory() {
  const [name, setName] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const categoryData = {
      name: name,
    };

    try {
      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/categories/new`,
        categoryData,
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      if (response.status === 200) {
        console.log("New category successfully added");
        setName("");
      }

      setShowModal(true);
    } catch (error) {
      console.error("There was an error adding category!", error);
      setError(error.response?.data?.detail || "An unexpected error occurred");
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          <>
            <Form onSubmit={handleSubmit} className="form">
              <Form.Group controlId="categoryName" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Category name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="form-control"
                />
              </Form.Group>

              <Button variant="primary" type="submit" className="login-btn">
                SAVE
              </Button>
            </Form>
            <Modal show={showModal} onClose={closeModal} title="Yay!">
              <section>You successfully uploaded the new category.</section>
            </Modal>
          </>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewCategory;
