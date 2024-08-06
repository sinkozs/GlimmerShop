import React, { useState } from "react";
import axios from "axios";
import "../App.css";
import "../styles/LoginAndSignup.css";
import { useNavigate } from "react-router-dom";
import { Container, Form, Button } from "react-bootstrap";

function LoginAndSignup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [isSeller, setIsSeller] = useState(false);
  const [error, setError] = useState(null);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [isSignup, setIsSignup] = useState(false);

  const navigate = useNavigate();

  const handleForgotPassword = () => {
    setIsForgotPassword(true);
  };

  const handleBackToLogin = () => {
    setIsForgotPassword(false);
    setIsSignup(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    const formData = new URLSearchParams();
    formData.append("grant_type", "password");
    formData.append("username", email);
    formData.append("password", password);

    axios
      .post("http://127.0.0.1:8000/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      })
      .then((response) => {
        const token = response.data.user_token;
        localStorage.setItem("token", token);

        console.log("Login successful:", token);
        setEmail("");
        setPassword("");

        const sellerId = response.data.user_id;
        navigate(`/seller/${sellerId}`, { state: { sellerId } });
      })
      .catch((error) => {
        console.error("Login failed:", error);
        setError(error.response.data.detail);
      });
  };

  const handleForgotPasswordSubmit = (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("user_email", email);

    axios
      .post("http://127.0.0.1:8000/auth/forgotten-password", formData)
      .then((response) => {
        setEmail("");
        setError(null);
        setIsForgotPassword(false);
      })
      .catch((error) => {
        console.error("Password reset failed:", error);
        setError(error.response.data.detail);
      });
  };

  const handleSignUpSubmit = (event) => {
    event.preventDefault();

    const formData = {
      first_name: firstName,
      last_name: lastName,
      password: password,
      email: email,
      is_seller: isSeller,
    };

    axios
      .post("http://127.0.0.1:8000/users/new", formData)
      .then((response) => {
        setFirstName("");
        setLastName("");
        setEmail("");
        setPassword("");
        setIsSeller(false);
        setError(null);
        setIsSignup(false);
      })
      .catch((error) => {
        console.error("Signup failed:", error);
        setError(error.response.data.detail);
      });
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          {isForgotPassword ? (
            <>
              <h1 className="login-form-h1">Forgot Your Password?</h1>
              <p>
                We’ll send instructions to reset your password to the email
                below.
              </p>
              <Form onSubmit={handleForgotPasswordSubmit} className="form">
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
                <Button variant="primary" type="submit" className="login-btn">
                  RESET PASSWORD
                </Button>
              </Form>
              <Button onClick={handleBackToLogin} className="back-to-login-btn">
                Back to Login
              </Button>
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
