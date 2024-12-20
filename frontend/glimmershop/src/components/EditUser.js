import React, { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import "../styles/LoginAndSignup.css";
import Modal from "./Modal";
import { Container, Form, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import config from "../config";

function EditUser() {
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [passwordLength, setPasswordLength] = useState(0);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      const sellerId = localStorage.getItem("seller_id");
      try {
        const response = await axios.get(
          `${config.BACKEND_BASE_URL}/users/${sellerId}`,
          { withCredentials: true }
        );
        const seller = response.data
        setFirstName(seller.first_name);
        setLastName(seller.last_name);
        setEmail(seller.email);
        setPasswordLength(seller.password_length || 0);
      } catch (error) {
        console.error("Error fetching seller data:", error);
        setError("Failed to fetch profile details. Please try again later.");
      }
    };

    fetchUserData();
  }, []);

  const handleDeleteProfile = () => {
    navigate(`/profile/delete`);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const formData = {};

    if (firstName) formData.first_name = firstName;
    if (lastName) formData.last_name = lastName;
    if (email) formData.email = email;
    if (password) formData.password = password;

    await axios
      .put(`${config.BACKEND_BASE_URL}/users/edit`, formData, {
        headers: {
          "Content-Type": "application/json",
        },
        withCredentials: true,
      })
      .then((response) => {
        setFirstName("");
        setLastName("");
        setEmail("");
        setPassword("");
        setPasswordLength(0);
        setError(null);

        setShowModal(true);
      })
      .catch((error) => {
        console.error("Update failed:", error);
        setError(error.response?.data?.detail || "An error occurred");
      });
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          <h1 className="login-form-h1">EDIT YOUR PROFILE</h1>
          <Form onSubmit={handleSubmit} className="form">
            <Form.Group controlId="formFirstName" className="form-group">
              <Form.Control
                type="text"
                placeholder={firstName || "First Name"}
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="form-control"
              />
            </Form.Group>
            <Form.Group controlId="formLastName" className="form-group">
              <Form.Control
                type="text"
                placeholder={lastName || "Last Name"}
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="form-control"
              />
            </Form.Group>
            <Form.Group controlId="formEmail" className="form-group">
              <Form.Control
                type="email"
                placeholder={email || "Email address"}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-control"
              />
            </Form.Group>
            <Form.Group controlId="formPassword" className="form-group">
              <Form.Control
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setPasswordLength(e.target.value.length);
                }}
                className="form-control"
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="login-btn">
              SAVE
            </Button>
          </Form>
          <Button className="sign-up-btn" onClick={handleDeleteProfile}>
            Delete your profile
          </Button>
          <Modal show={showModal} onClose={closeModal} title="Yay!">
            <section>You successfully updated your profile.</section>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default EditUser;
