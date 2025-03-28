import React, { useState, useContext } from "react";
import "../App.css";
import "../styles/Form.css";
import Modal from "../components/Modal";
import { Container, Form, Button } from "react-bootstrap";
import apiClient from "../utils/apiConfig";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function DeleteUser() {
  const [confirmDeletion, setConfirmDeletion] = useState("");
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      if (confirmDeletion && confirmDeletion === "delete profile") {
        const response = await apiClient.delete(
          `/users/me`
        );
        if (response.status === 200) {
          setShowModal(true);
        }
      } else {
        console.log("Incorrect");
      }
    } catch (error) {
      console.error("Error deleting user:", error);
      setError("Failed to delete user. Please try again.");
    }
  };

  const closeModal = () => {
    setShowModal(false);
    logout();
  };

  const handleBackToEditProfile = () => {
    navigate(`/profile/edit`);
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="form-container">
        <Container fluid className="form-content">
          <h1 className="form-h1">DELETE YOUR PROFILE</h1>
          <Form onSubmit={handleSubmit} className="form">
            <p>
              To confirm the deletion of your profile, please type 'delete
              profile.'
            </p>
            <Form.Group controlId="formFirstName" className="form-group">
              <Form.Control
                type="text"
                placeholder={"delete profile"}
                value={confirmDeletion}
                onChange={(e) => setConfirmDeletion(e.target.value)}
                className="form-control"
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="login-btn">
              SUBMIT
            </Button>
            <Button className="sign-up-btn" onClick={handleBackToEditProfile}>
              Back to Edit Profile
            </Button>
          </Form>
          <Modal
            show={showModal}
            onClose={closeModal}
            title="Profile Deleted Successfully"
          >
            <section>
              You successfully deleted your profile. You can always create a new
              profile if you wish.
            </section>
            <Button onClick={closeModal}>Close</Button>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default DeleteUser;