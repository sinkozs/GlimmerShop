import React, { useState, useContext } from "react";
import "../App.css";
import "../styles/LoginAndSignup.css";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Container, Form, Button } from "react-bootstrap";
import Modal from "./Modal";
import apiClient from "../utils/apiConfig";

function LoginAndSignup() {
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [passwordLength, setPasswordLength] = useState("");
  const [isSeller, setIsSeller] = useState(false);
  const [error, setError] = useState(null);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showSuccessfulSignupModal, setShowSuccessfulSignupModal] =
    useState(false);
  const [showPasswordReminderModal, setShowPasswordReminderModal] =
    useState(false);

  const navigate = useNavigate();

  const handleForgotPassword = () => {
    setIsForgotPassword(true);
  };

  const handleBackToLogin = () => {
    setIsForgotPassword(false);
    setIsSignup(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const formData = new URLSearchParams();
    formData.append("grant_type", "password");
    formData.append("username", email);
    formData.append("password", password);

    try {
      const response = await apiClient.post(
        `/auth/login?is_seller=true`,
        formData,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          withCredentials: true,
        }
      );

      const sellerId = response.data.seller_id;
      localStorage.setItem("seller_id", sellerId);

      setEmail("");
      setPassword("");

      login();
      navigate(`/seller/${sellerId}`, { state: { sellerId } });
    } catch (error) {
      if (error.response) {
        setError(error.response.data.detail);
        setShowModal(true);
      } else if (error.request) {
        setError("No response from server. Please try again.");
        setShowModal(true);
      } else {
        setError("An unexpected error occurred. Please try again.");
        setShowModal(true);
      }
    }
  };

  const handleForgotPasswordSubmit = async (event) => {
    event.preventDefault();
    const encodedEmail = encodeURIComponent(email);

    try {
      await apiClient.post(
        `/auth/forgotten-password?email=${encodedEmail}`
      );
      setEmail("");
      setError(null);
      setShowPasswordReminderModal(true);
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "An error occurred sending the reset email"
      );
      setShowModal(true);
    }
  };

  const handleSignUpSubmit = async (event) => {
    event.preventDefault();

    const formData = {
      first_name: firstName,
      last_name: lastName,
      password: password,
      email: email,
      is_seller: isSeller,
      password_length: password.length,
    };

    try {
      const response = await apiClient.post(
        `/users/create`,
        formData
      );
      setFirstName("");
      setLastName("");
      setEmail("");
      setPassword("");
      setPasswordLength("");
      setIsSeller(false);
      setError(null);
      setShowSuccessfulSignupModal(true);
    } catch (error) {
      console.error("Signup failed:", error);
      setError(error.response?.data?.detail || "An error occurred");
      setShowModal(true);
    }
  };

  const closeSuccessfulSignupModal = () => {
    setShowSuccessfulSignupModal(false);
    setIsSignup(false);
  };

  const closePasswordReminderModal = () => {
    setShowPasswordReminderModal(false);
    setIsForgotPassword(false);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          {isForgotPassword ? (
            <>
              <h1 className="login-form-h1">Forgot Your Password?</h1>
              <section>
                We’ll send instructions to reset your password to the email
                below.
              </section>
              <Form onSubmit={handleForgotPasswordSubmit} className="form">
                <Form.Group controlId="formEmail" className="form-group">
                  <Form.Control
                    type="text"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Button variant="primary" type="submit" className="login-btn">
                  RESET PASSWORD
                </Button>
              </Form>
              <Button onClick={handleBackToLogin} className="back-to-login-btn">
                Back to Login
              </Button>
              <Modal show={showModal} onClose={closeModal} title="Error">
                <section>{error}</section>
              </Modal>
              <Modal
                show={showPasswordReminderModal}
                onClose={closePasswordReminderModal}
                title="Email Sent!"
              >
                <section>
                  Password reset instructions have been sent to your email.
                  Please check your inbox.
                </section>
              </Modal>
            </>
          ) : isSignup ? (
            <>
              <h1 className="login-form-h1">SIGN UP</h1>
              <Form onSubmit={handleSignUpSubmit} className="form">
                <Form.Group controlId="formFirstName" className="form-group">
                  <Form.Control
                    type="text"
                    placeholder="First Name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Form.Group controlId="formLastName" className="form-group">
                  <Form.Control
                    type="text"
                    placeholder="Last Name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Form.Group controlId="formEmail" className="form-group">
                  <Form.Control
                    type="email"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Form.Group controlId="formPassword" className="form-group">
                  <Form.Control
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Form.Group controlId="formIsSeller" className="form-group">
                  <Form.Check
                    type="checkbox"
                    label="I am a seller"
                    checked={isSeller}
                    onChange={(e) => setIsSeller(e.target.checked)}
                    className="form-check"
                  />
                </Form.Group>
                <Button variant="primary" type="submit" className="login-btn">
                  SIGN UP
                </Button>
              </Form>
              <Modal
                show={showSuccessfulSignupModal}
                onClose={closeSuccessfulSignupModal}
                title="Yay!"
              >
                <section>
                  You successfully signed up to Glimmershop. Please check your
                  inbox and verify your account.
                </section>
              </Modal>

              <Button onClick={handleBackToLogin} className="back-to-login-btn">
                Back to Login
              </Button>
            </>
          ) : (
            <>
              <h1 className="login-form-h1">WELCOME BACK</h1>
              <Form onSubmit={handleSubmit} className="form">
                <Form.Group controlId="formEmail" className="form-group">
                  <Form.Control
                    type="email"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>

                <Form.Group controlId="formPassword" className="form-group">
                  <Form.Control
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="form-control"
                  />
                </Form.Group>
                <Button variant="primary" type="submit" className="login-btn">
                  LOG IN
                </Button>
              </Form>
              <Modal show={showModal} onClose={closeModal} title="Login Error">
                <section>{error}</section>
              </Modal>
              <Container fluid className="login-form-footer">
                <Button
                  onClick={() => setIsSignup(true)}
                  className="sign-up-btn"
                >
                  Not a Glimmershop seller? Join now!
                </Button>

                <Button onClick={handleForgotPassword} className="sign-up-btn">
                  Forgot your password?
                </Button>
              </Container>
            </>
          )}
        </Container>
      </Container>
    </Container>
  );
}

export default LoginAndSignup;
