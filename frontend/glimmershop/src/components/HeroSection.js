import React from "react";
import "../App.css";
import "../styles/Home.css";
import heroImage from "../images/hero5.jpg";
import { NavLink } from "react-router-dom";

import { Container } from "react-bootstrap";

function HeroSection() {
  return (
    <Container fluid className="page-wrapper">
      <Container
        fluid
        className="hero-container"
        style={{ backgroundImage: `url(${heroImage})` }}
      >
        <Container fluid className="hero-section-text">
          <h1>SILVER STORY</h1>
          <NavLink to="/" className="hero-navlink-h3">Shop now</NavLink>
        </Container>
      </Container>
    </Container>
  );
}

export default HeroSection;
