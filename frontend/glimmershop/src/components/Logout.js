import React, { useState } from "react";
import axios from "axios";
import "../App.css";
import "../styles/LoginAndSignup.css";
import { useNavigate } from "react-router-dom";
import { Container, Button } from "react-bootstrap";

function Logout() {
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogout = (event) => {
    event.preventDefault();

    const token = localStorage.getItem("token");
    if (token) {
      axios
        .post(
          "http://127.0.0.1:8000/auth/logout",
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/x-www-form-urlencoded",
            },
          }
        )
        .then((response) => {
          localStorage.removeItem("token");

          console.log("Successful logout!");
          navigate("/");
        })
        .catch((error) => {
          console.error("Logout failed:", error);
          setError(error.response?.data?.detail || "An unexpected error occurred.");
        });
    } else {
      console.error("No token found");
    }
  };

  return (
    <Container>
      <Button onClick={handleLogout}>Logout</Button>
      {error && <section>{error}</section>}
    </Container>
  );
}

export default Logout;
