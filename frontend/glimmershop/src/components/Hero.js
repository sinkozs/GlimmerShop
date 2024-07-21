import React from "react";
import "../styles/Hero.css";
import heroImage from "../../public/images/hero1.jpg";
import { Button, Row, Col, Container } from "react-bootstrap";

function Hero() {
  return (
      <Container className="hero-section">
            className="hero-image"
            style={{
              backgroundImage: `url(${heroImage})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
    </Container>
  );
}

export default Hero;
